"""
Centralized telemetry service for emitting and managing events.
"""

from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timezone
import json
import asyncio
from contextlib import asynccontextmanager
import time

from ..core.logging_config import get_logger
from ..core.settings import get_settings
from .events import BaseEvent, EventType, EventSeverity, create_event
from .emitters import (
    TelemetryEmitter,
    ConsoleTelemetryEmitter,
    FileTelemetryEmitter,
    KafkaTelemetryEmitter,
    CompositeTelemetryEmitter
)

logger = get_logger(__name__)


class TelemetryService:
    """
    Centralized telemetry service for managing event emission.
    
    Features:
    - Multiple emitter support (console, file, Kafka, etc.)
    - Event batching for performance
    - Async emission to avoid blocking
    - Context tracking (correlation ID, user, etc.)
    - Performance metrics
    """
    
    def __init__(self):
        """Initialize telemetry service."""
        self.settings = get_settings()
        self.emitters: List[TelemetryEmitter] = []
        self.context: Dict[str, Any] = {}
        self.event_buffer: List[BaseEvent] = []
        self.batch_size = 100
        self.flush_interval = 5  # seconds
        self._last_flush = time.time()
        self._setup_emitters()
        
    def _setup_emitters(self):
        """Setup telemetry emitters based on configuration."""
        # Always include console emitter in development
        if self.settings.environment.value == "development":
            self.emitters.append(ConsoleTelemetryEmitter())
        
        # File emitter for persistence
        if self.settings.telemetry.enable_file_output:
            self.emitters.append(FileTelemetryEmitter(
                file_path=self.settings.telemetry.output_file
            ))
        
        # Kafka emitter for streaming
        if self.settings.telemetry.enable_kafka:
            try:
                self.emitters.append(KafkaTelemetryEmitter(
                    bootstrap_servers=self.settings.kafka.bootstrap_servers,
                    topic=self.settings.kafka.telemetry_topic
                ))
            except Exception as e:
                logger.warning(f"Failed to setup Kafka emitter: {e}")
        
        # Create composite emitter
        if self.emitters:
            self.composite_emitter = CompositeTelemetryEmitter(self.emitters)
        else:
            # Fallback to console
            self.composite_emitter = ConsoleTelemetryEmitter()
    
    def set_context(self, **kwargs):
        """
        Set global context for all events.
        
        Args:
            **kwargs: Context fields (correlation_id, user_id, etc.)
        """
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear global context."""
        self.context.clear()
    
    @asynccontextmanager
    async def track_operation(
        self,
        operation: str,
        event_type: EventType = EventType.PERFORMANCE_METRIC,
        **kwargs
    ):
        """
        Context manager for tracking operation performance.
        
        Args:
            operation: Name of the operation
            event_type: Type of event to emit
            **kwargs: Additional event data
            
        Example:
            async with telemetry.track_operation("database_query"):
                # Perform operation
                pass
        """
        start_time = time.time()
        error = None
        
        try:
            yield
        except Exception as e:
            error = e
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Create performance event
            event = create_event(
                event_type,
                operation=operation,
                response_time_ms=duration_ms,
                metric_name=f"{operation}_duration",
                metric_value=duration_ms,
                metric_unit="ms",
                severity=EventSeverity.ERROR if error else EventSeverity.INFO,
                error_message=str(error) if error else None,
                **self.context,
                **kwargs
            )
            
            await self.emit(event)
    
    async def emit(self, event: BaseEvent):
        """
        Emit a telemetry event.
        
        Args:
            event: Event to emit
        """
        # Add global context to event
        for key, value in self.context.items():
            if hasattr(event, key) and getattr(event, key) is None:
                setattr(event, key, value)
        
        # Add to buffer
        self.event_buffer.append(event)
        
        # Check if we should flush
        if len(self.event_buffer) >= self.batch_size or \
           time.time() - self._last_flush > self.flush_interval:
            await self.flush()
    
    async def flush(self):
        """Flush buffered events."""
        if not self.event_buffer:
            return
        
        events_to_emit = self.event_buffer.copy()
        self.event_buffer.clear()
        self._last_flush = time.time()
        
        # Emit events asynchronously
        try:
            await self.composite_emitter.emit_batch(events_to_emit)
        except Exception as e:
            logger.error(f"Failed to emit telemetry batch: {e}")
    
    async def emit_validation_started(
        self,
        job_id: str,
        marketplace: str,
        file_name: str,
        file_size: int,
        **kwargs
    ):
        """Emit validation started event."""
        event = create_event(
            EventType.VALIDATION_STARTED,
            job_id=job_id,
            marketplace=marketplace,
            file_name=file_name,
            file_size_bytes=file_size,
            **self.context,
            **kwargs
        )
        await self.emit(event)
    
    async def emit_validation_completed(
        self,
        job_id: str,
        marketplace: str,
        total_rows: int,
        valid_rows: int,
        invalid_rows: int,
        processing_time_ms: int,
        **kwargs
    ):
        """Emit validation completed event."""
        event = create_event(
            EventType.VALIDATION_COMPLETED,
            job_id=job_id,
            marketplace=marketplace,
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            processing_time_ms=processing_time_ms,
            **self.context,
            **kwargs
        )
        await self.emit(event)
    
    async def emit_validation_failed(
        self,
        job_id: str,
        marketplace: str,
        error_message: str,
        **kwargs
    ):
        """Emit validation failed event."""
        event = create_event(
            EventType.VALIDATION_FAILED,
            job_id=job_id,
            marketplace=marketplace,
            severity=EventSeverity.ERROR,
            metadata={"error": error_message},
            **self.context,
            **kwargs
        )
        await self.emit(event)
    
    async def emit_job_event(
        self,
        event_type: EventType,
        job_id: str,
        job_type: str,
        status: str,
        **kwargs
    ):
        """Emit job lifecycle event."""
        event = create_event(
            event_type,
            job_id=job_id,
            job_type=job_type,
            status=status,
            **self.context,
            **kwargs
        )
        await self.emit(event)
    
    async def emit_api_request(
        self,
        method: str,
        path: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        **kwargs
    ):
        """Emit API request event."""
        event = create_event(
            EventType.API_REQUEST,
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent,
            **self.context,
            **kwargs
        )
        await self.emit(event)
    
    async def emit_api_response(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time_ms: int,
        **kwargs
    ):
        """Emit API response event."""
        event = create_event(
            EventType.API_RESPONSE,
            method=method,
            path=path,
            status_code=status_code,
            response_time_ms=response_time_ms,
            severity=EventSeverity.ERROR if status_code >= 500 else EventSeverity.INFO,
            **self.context,
            **kwargs
        )
        await self.emit(event)
    
    async def emit_system_error(
        self,
        component: str,
        message: str,
        error_type: Optional[str] = None,
        stack_trace: Optional[str] = None,
        **kwargs
    ):
        """Emit system error event."""
        event = create_event(
            EventType.SYSTEM_ERROR,
            component=component,
            message=message,
            error_type=error_type,
            stack_trace=stack_trace,
            severity=EventSeverity.ERROR,
            **self.context,
            **kwargs
        )
        await self.emit(event)
    
    async def emit_performance_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_unit: str,
        threshold_value: Optional[float] = None,
        **kwargs
    ):
        """Emit performance metric event."""
        threshold_exceeded = False
        if threshold_value is not None:
            threshold_exceeded = metric_value > threshold_value
        
        event = create_event(
            EventType.PERFORMANCE_METRIC,
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=metric_unit,
            threshold_value=threshold_value,
            threshold_exceeded=threshold_exceeded,
            severity=EventSeverity.WARNING if threshold_exceeded else EventSeverity.INFO,
            **self.context,
            **kwargs
        )
        await self.emit(event)
    
    async def close(self):
        """Close telemetry service and flush remaining events."""
        await self.flush()
        
        # Close all emitters
        for emitter in self.emitters:
            if hasattr(emitter, 'close'):
                await emitter.close()


# Global telemetry service instance
_telemetry_service: Optional[TelemetryService] = None


def get_telemetry_service() -> TelemetryService:
    """Get or create global telemetry service instance."""
    global _telemetry_service
    if _telemetry_service is None:
        _telemetry_service = TelemetryService()
    return _telemetry_service


async def emit_telemetry(event: BaseEvent):
    """
    Convenience function to emit telemetry event.
    
    Args:
        event: Event to emit
    """
    service = get_telemetry_service()
    await service.emit(event)