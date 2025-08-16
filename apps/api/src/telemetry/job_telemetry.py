"""
Job-specific telemetry helpers.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .emitter import get_telemetry_emitter

logger = logging.getLogger(__name__)


class JobTelemetry:
    """Helper class for emitting job telemetry events."""
    
    def __init__(self, emitter=None):
        """Initialize with optional emitter."""
        self.emitter = emitter or get_telemetry_emitter()
        self._start_times: Dict[str, float] = {}
        self._queue_times: Dict[str, float] = {}
        
    def emit_job_queued(
        self,
        job_id: str,
        task_name: str,
        params: Dict[str, Any],
        queue: str,
        priority: int,
        correlation_id: Optional[str] = None
    ) -> None:
        """Emit job.queued event when job is added to queue."""
        
        # Track queue time for wait time calculation
        self._queue_times[job_id] = time.time()
        
        # Extract context from params
        marketplace = params.get("marketplace", "unknown")
        category = params.get("category", "unknown")
        region = params.get("region", "default")
        
        partition_key = f"{marketplace}:{category}:{region}"
        
        # Standardized payload for job.queued
        payload = {
            "job_id": job_id,
            "task": task_name,
            "marketplace": marketplace,
            "category": category,
            "region": region,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "queue": queue,
            "priority": priority
        }
        
        self.emitter.emit(
            event="job.queued",
            payload=payload,
            partition_key=partition_key,
            correlation_id=correlation_id
        )
    
    def emit_job_started(
        self,
        job_id: str,
        task_name: str,
        params: Dict[str, Any],
        correlation_id: Optional[str] = None,
        parent_job_id: Optional[str] = None
    ) -> None:
        """Emit job.started event."""
        
        # Track start time for latency calculation
        self._start_times[job_id] = time.time()
        
        # Calculate queue wait time if available
        queue_wait_ms = None
        if job_id in self._queue_times:
            queue_wait_ms = int((time.time() - self._queue_times[job_id]) * 1000)
            del self._queue_times[job_id]
        
        # Extract context from params
        marketplace = params.get("marketplace", "unknown")
        category = params.get("category", "unknown")
        region = params.get("region", "default")
        
        partition_key = f"{marketplace}:{category}:{region}"
        
        # Standardized payload for job.started
        payload = {
            "job_id": job_id,
            "task": task_name,
            "marketplace": marketplace,
            "category": category,
            "region": region,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "params": params
        }
        
        # Add queue wait time if available
        if queue_wait_ms is not None:
            payload["queue_wait_ms"] = queue_wait_ms
        
        self.emitter.emit(
            event="job.started",
            payload=payload,
            partition_key=partition_key,
            correlation_id=correlation_id,
            parent_id=parent_job_id
        )
        
    def emit_job_completed(
        self,
        job_id: str,
        task_name: str,
        result: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """Emit job.completed event."""
        
        # Calculate latency
        latency_ms = None
        if job_id in self._start_times:
            latency_ms = int((time.time() - self._start_times[job_id]) * 1000)
            del self._start_times[job_id]
            
        # Extract context from result or use defaults
        marketplace = result.get("marketplace", "unknown")
        category = result.get("category", "unknown")
        region = result.get("region", "default")
        
        partition_key = f"{marketplace}:{category}:{region}"
        
        # Combine metrics with standardized fields
        all_metrics = {
            "latency_ms": latency_ms,
            "payload_size_bytes": metrics.get("payload_size_bytes") if metrics else None,
            "records_total": metrics.get("records_total") if metrics else None,
            "records_valid": metrics.get("records_valid") if metrics else None,
            "records_error": metrics.get("records_error") if metrics else None,
            "error_rate": metrics.get("error_rate") if metrics else None,
            "errors_by_field": metrics.get("errors_by_field") if metrics else None,
            **(metrics or {})
        }
        
        # Remove None values from metrics
        all_metrics = {k: v for k, v in all_metrics.items() if v is not None}
        
        # Standardized payload for job.completed
        payload = {
            "job_id": job_id,
            "task": task_name,
            "marketplace": marketplace,
            "category": category,
            "region": region,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": all_metrics,
            "result_summary": {
                "status": result.get("status", "success"),
                "result_ref": result.get("result_ref")
            }
        }
        
        self.emitter.emit(
            event="job.completed",
            payload=payload,
            partition_key=partition_key,
            correlation_id=correlation_id
        )
        
    def emit_job_failed(
        self,
        job_id: str,
        task_name: str,
        error: Exception,
        params: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> None:
        """Emit job.failed event."""
        
        # Calculate latency if available
        latency_ms = None
        if job_id in self._start_times:
            latency_ms = int((time.time() - self._start_times[job_id]) * 1000)
            # Keep start time for potential retry
            
        # Extract context
        marketplace = params.get("marketplace", "unknown")
        category = params.get("category", "unknown")
        region = params.get("region", "default")
        
        partition_key = f"{marketplace}:{category}:{region}"
        
        # Standardized payload for job.failed
        payload = {
            "job_id": job_id,
            "task": task_name,
            "marketplace": marketplace,
            "category": category,
            "region": region,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": {
                "type": error.__class__.__name__,
                "message": str(error)
            },
            "metrics": {
                "latency_ms": latency_ms
            } if latency_ms else {}
        }
        
        self.emitter.emit(
            event="job.failed",
            payload=payload,
            partition_key=partition_key,
            correlation_id=correlation_id
        )
        
    def emit_job_retrying(
        self,
        job_id: str,
        task_name: str,
        retry_count: int,
        max_retries: int,
        error: Exception,
        params: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> None:
        """Emit job.retrying event."""
        
        # Extract context
        marketplace = params.get("marketplace", "unknown")
        category = params.get("category", "unknown")
        region = params.get("region", "default")
        
        partition_key = f"{marketplace}:{category}:{region}"
        
        # Standardized payload for job.retrying
        payload = {
            "job_id": job_id,
            "task": task_name,
            "marketplace": marketplace,
            "category": category,
            "region": region,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "retry_count": retry_count,
            "max_retries": max_retries,
            "error": {
                "type": error.__class__.__name__,
                "message": str(error)
            }
        }
        
        self.emitter.emit(
            event="job.retrying",
            payload=payload,
            partition_key=partition_key,
            correlation_id=correlation_id
        )
        
    def emit_job_progress(
        self,
        job_id: str,
        task_name: str,
        progress: float,
        message: str,
        params: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> None:
        """Emit job.progress event."""
        
        # Extract context
        marketplace = params.get("marketplace", "unknown")
        category = params.get("category", "unknown")
        region = params.get("region", "default")
        
        partition_key = f"{marketplace}:{category}:{region}"
        
        # Standardized payload for job.progress
        payload = {
            "job_id": job_id,
            "task": task_name,
            "marketplace": marketplace,
            "category": category,
            "region": region,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "progress": progress,
            "message": message
        }
        
        self.emitter.emit(
            event="job.progress",
            payload=payload,
            partition_key=partition_key,
            correlation_id=correlation_id
        )


# Global instance
_job_telemetry: Optional[JobTelemetry] = None


def get_job_telemetry() -> JobTelemetry:
    """Get or create global job telemetry instance."""
    global _job_telemetry
    if _job_telemetry is None:
        _job_telemetry = JobTelemetry()
    return _job_telemetry