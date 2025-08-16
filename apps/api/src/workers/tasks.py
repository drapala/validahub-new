"""
Celery tasks for async job processing.
"""

import os
import json
import logging
import tempfile
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import io
import boto3
from botocore.exceptions import (
    ClientError,
    EndpointConnectionError,
    ConnectTimeoutError,
    ReadTimeoutError,
    ConnectionClosedError
)

from .celery_app import celery_app, DatabaseTask, update_job_progress
from ..services.rule_engine_service import RuleEngineService
from ..core.pipeline.validation_pipeline import ValidationPipeline
from ..services.csv_validation_service import CSVValidationService
from ..services.storage_service import get_storage_service
from ..exceptions import TransientError
from ..telemetry.job_telemetry import get_job_telemetry
from ..telemetry.metrics import MetricsCollector, ValidationMetrics

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="validate_csv_job",
    autoretry_for=(TransientError, ConnectionError, TimeoutError),
    retry_backoff=2,
    retry_jitter=True,
    max_retries=5,
    time_limit=300,
    soft_time_limit=270
)
def validate_csv_job(
    self,
    job_id: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate CSV file using rule engine.
    
    Args:
        job_id: Job UUID
        params: {
            "input_uri": "s3://bucket/key.csv" or file path,
            "marketplace": "mercado_livre",
            "category": "electronics",
            "ruleset": "default",
            "auto_fix": true/false
        }
    
    Returns:
        {
            "result_ref": "s3://bucket/results/job_id.json",
            "summary": {...},
            "status": "success"
        }
    """
    
    task_id = self.request.id
    logger.info(f"Starting validate_csv_job: job_id={job_id}, task_id={task_id}")
    
    try:
        # Track start time for metrics
        start_time = datetime.utcnow()
        
        # Initialize services
        validation_service = CSVValidationService()
        storage_service = get_storage_service()
        telemetry = get_job_telemetry()
        
        # Update progress: Starting
        update_job_progress(task_id, 10, "Downloading input file")
        
        # Emit progress with enhanced metrics
        telemetry.emit_job_progress(
            job_id=job_id, 
            task_name="validate_csv_job", 
            progress=10, 
            message="Downloading input file", 
            params=params
        )
        
        # Get input file
        input_uri = params.get("input_uri")
        if not input_uri:
            raise ValueError("input_uri is required")
        
        # Download or read file using storage service
        csv_content = storage_service.download_file(input_uri)
        
        # Update progress: File loaded
        update_job_progress(task_id, 30, "File loaded, starting validation")
        
        # Emit progress with payload size metric
        progress_metrics = {
            "payload_size_bytes": len(csv_content.encode('utf-8'))
        }
        telemetry.emit_job_progress(
            job_id=job_id,
            task_name="validate_csv_job",
            progress=30,
            message=f"File loaded ({progress_metrics['payload_size_bytes']} bytes), starting validation",
            params={**params, "metrics": progress_metrics}
        )
        
        logger.info(f"Loaded CSV with {len(csv_content)} bytes")
        
        # Update progress: Validating
        update_job_progress(task_id, 50, "Validating data")
        telemetry.emit_job_progress(
            job_id=job_id,
            task_name="validate_csv_job",
            progress=50,
            message="Validating data",
            params=params
        )
        
        # Extract parameters
        marketplace = params.get("marketplace", "mercado_livre")
        category = params.get("category", "general")
        ruleset = params.get("ruleset", "default")
        auto_fix = params.get("auto_fix", False)
        
        # Validate ruleset against whitelist to prevent path traversal/injection
        ALLOWED_RULESETS = {"default", "strict", "lenient", "minimal", "comprehensive"}
        if ruleset not in ALLOWED_RULESETS:
            logger.warning(f"Invalid ruleset '{ruleset}' provided. Falling back to 'default'.")
            ruleset = "default"
        
        # Use domain service for validation
        validation_result, corrected_csv = validation_service.validate_csv_content(
            csv_content=csv_content,
            marketplace=marketplace,
            category=category,
            ruleset=ruleset,
            auto_fix=auto_fix
        )
        
        # Calculate standardized business metrics
        validation_metrics = MetricsCollector.collect_validation_metrics(
            csv_content=csv_content,
            validation_result=validation_result,
            processing_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000)
        )
        
        # Enrich with business context
        validation_metrics = MetricsCollector.enrich_with_business_context(
            validation_metrics, params
        )
        
        # Calculate error rates
        error_rates = MetricsCollector.calculate_error_rates(validation_metrics)
        
        # Convert to dict for serialization
        metrics = validation_metrics.to_dict()
        metrics.update(error_rates)
        
        # Update progress: Saving results with metrics
        update_job_progress(task_id, 80, "Saving validation results")
        
        # Emit progress with preliminary metrics
        telemetry.emit_job_progress(
            job_id=job_id,
            task_name="validate_csv_job",
            progress=80,
            message=f"Saving results ({validation_result['total_rows']} rows processed)",
            params={**params, "preliminary_metrics": {
                "total_rows": validation_result["total_rows"],
                "error_rows": validation_result["error_rows"]
            }}
        )
        
        # Add metadata to validation result
        validation_result["job_id"] = job_id
        validation_result["timestamp"] = datetime.utcnow().isoformat()
        
        # Save result to storage using storage service
        result_ref = storage_service.save_result(job_id, validation_result)
        
        # Save corrected data if available
        if corrected_csv:
            corrected_ref = storage_service.save_file(
                f"corrected/{job_id}.csv",
                corrected_csv.encode('utf-8')
            )
            validation_result["corrected_file"] = corrected_ref
        
        # Update progress: Complete
        update_job_progress(task_id, 100, "Validation completed")
        
        logger.info(f"Validation completed: job_id={job_id}, result_ref={result_ref}")
        
        return {
            "result_ref": result_ref,
            "summary": {
                "total_rows": validation_result["total_rows"],
                "valid_rows": validation_result["valid_rows"],
                "error_rows": validation_result["error_rows"],
                "warning_rows": validation_result["warning_rows"]
            },
            "status": "success",
            "marketplace": marketplace,
            "category": category,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Error in validate_csv_job: {e}", exc_info=True)
        
        # Check if it's a transient error that should be retried
        if _is_transient_error(e):
            raise TransientError(f"Transient error: {e}") from e
        
        # Non-transient error, fail the job
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="correct_csv_job",
    autoretry_for=(TransientError,),
    retry_backoff=2,
    max_retries=3
)
def correct_csv_job(
    self,
    job_id: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Apply corrections to CSV file."""
    # Similar to validate_csv_job but always with auto_fix=True
    params["auto_fix"] = True
    return validate_csv_job(self, job_id, params)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="sync_connector_job",
    autoretry_for=(TransientError,),
    retry_backoff=2,
    max_retries=3
)
def sync_connector_job(
    self,
    job_id: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Sync data from external connector."""
    
    task_id = self.request.id
    logger.info(f"Starting sync_connector_job: job_id={job_id}")
    
    # Placeholder for connector sync logic
    update_job_progress(task_id, 50, "Syncing connector (mock)")
    
    return {
        "result_ref": f"s3://validahub/results/{job_id}.json",
        "status": "success",
        "message": "Connector sync not yet implemented"
    }


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="generate_report_job"
)
def generate_report_job(
    self,
    job_id: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate analytics report."""
    
    task_id = self.request.id
    logger.info(f"Starting generate_report_job: job_id={job_id}")
    
    # Placeholder for report generation
    update_job_progress(task_id, 100, "Report generated (mock)")
    
    return {
        "result_ref": f"s3://validahub/reports/{job_id}.pdf",
        "status": "success"
    }


# Helper functions

def _is_aws_transient_error(error: Exception) -> bool:
    """
    Check if error is an AWS-specific transient error.
    """
    # Check for specific AWS transient errors
    if isinstance(error, ClientError):
        error_code = error.response.get('Error', {}).get('Code', '')
        transient_error_codes = [
            'ThrottlingException',
            'TooManyRequestsException',
            'RequestLimitExceeded',
            'ServiceUnavailable',
            'RequestTimeout',
            'InternalServerError',
            'InternalError'
        ]
        if error_code in transient_error_codes:
            return True
    
    # AWS connection errors
    aws_transient_types = (
        EndpointConnectionError,
        ConnectTimeoutError,
        ReadTimeoutError,
        ConnectionClosedError,
    )
    if isinstance(error, aws_transient_types):
        return True
    
    return False


def _is_network_transient_error(error: Exception) -> bool:
    """
    Check if error is a network-related transient error.
    """
    # Standard Python transient exception types
    transient_types = (
        ConnectionError,      # Network connection errors
        TimeoutError,        # Operation timeouts
        BrokenPipeError,     # Broken network pipe
        ConnectionResetError, # Connection reset by peer
        ConnectionAbortedError, # Connection aborted
    )
    
    if isinstance(error, transient_types):
        return True
    
    # Check for specific OSError types that are transient
    if isinstance(error, OSError):
        # errno values that indicate transient network issues
        import errno
        transient_errno = [
            errno.EAGAIN,      # Resource temporarily unavailable
            errno.EWOULDBLOCK, # Operation would block
            errno.EINPROGRESS, # Operation in progress
            errno.ETIMEDOUT,   # Connection timed out
            errno.ECONNRESET,  # Connection reset by peer
            errno.ECONNREFUSED, # Connection refused
            errno.EHOSTUNREACH, # No route to host
            errno.ENETUNREACH,  # Network unreachable
            errno.ENETDOWN,     # Network is down
        ]
        if hasattr(error, 'errno') and error.errno in transient_errno:
            return True
    
    return False


def _is_transient_error(error: Exception) -> bool:
    """
    Check if error is transient and should be retried.
    
    Uses exception type checking for reliable detection of transient errors.
    String matching is avoided to prevent false positives.
    """
    # Check AWS-specific transient errors
    if _is_aws_transient_error(error):
        return True
    
    # Check network-related transient errors
    if _is_network_transient_error(error):
        return True
    
    # Default: not a transient error
    # Avoid string matching to prevent false positives
    logger.debug(f"Error not identified as transient: {type(error).__name__}: {error}")
    return False