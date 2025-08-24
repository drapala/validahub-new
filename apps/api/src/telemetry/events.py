"""
Telemetry event definitions with versioning support.
All telemetry events should be defined here with proper schemas.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class EventVersion(str, Enum):
    """Event schema versions."""
    V1 = "1.0.0"
    V2 = "2.0.0"


class EventType(str, Enum):
    """Telemetry event types."""
    # Validation events
    VALIDATION_STARTED = "validation.started"
    VALIDATION_COMPLETED = "validation.completed"
    VALIDATION_FAILED = "validation.failed"
    VALIDATION_ROW_PROCESSED = "validation.row.processed"
    
    # Correction events
    CORRECTION_STARTED = "correction.started"
    CORRECTION_COMPLETED = "correction.completed"
    CORRECTION_APPLIED = "correction.applied"
    
    # Job events
    JOB_CREATED = "job.created"
    JOB_STARTED = "job.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    JOB_CANCELLED = "job.cancelled"
    
    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    API_REQUEST = "api.request"
    API_RESPONSE = "api.response"
    
    # Performance events
    PERFORMANCE_METRIC = "performance.metric"
    SLOW_QUERY = "performance.slow_query"
    MEMORY_HIGH = "performance.memory_high"
    
    # Business events
    FILE_UPLOADED = "file.uploaded"
    FILE_DOWNLOADED = "file.downloaded"
    RULE_LOADED = "rule.loaded"
    RULE_EXECUTED = "rule.executed"


class EventSeverity(str, Enum):
    """Event severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class BaseEvent(BaseModel):
    """Base telemetry event with common fields."""
    
    # Event metadata
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    event_version: EventVersion = EventVersion.V1
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Context
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    
    # Source
    service_name: str = "validahub-api"
    environment: str = Field(default="development")
    host: Optional[str] = None
    
    # Severity
    severity: EventSeverity = EventSeverity.INFO
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValidationEvent(BaseEvent):
    """Validation-specific event."""
    
    job_id: str
    marketplace: str
    category: Optional[str] = None
    ruleset: Optional[str] = None
    
    # Metrics
    total_rows: Optional[int] = None
    valid_rows: Optional[int] = None
    invalid_rows: Optional[int] = None
    processing_time_ms: Optional[int] = None
    
    # File info
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    file_hash: Optional[str] = None
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CorrectionEvent(BaseEvent):
    """Correction-specific event."""
    
    job_id: str
    validation_job_id: str
    marketplace: str
    
    # Metrics
    total_corrections: Optional[int] = None
    successful_corrections: Optional[int] = None
    failed_corrections: Optional[int] = None
    
    # Correction details
    correction_types: List[str] = Field(default_factory=list)
    auto_fix_rate: Optional[float] = None
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JobEvent(BaseEvent):
    """Job lifecycle event."""
    
    job_id: str
    job_type: str  # "validation", "correction", "export"
    status: str
    
    # Queue info
    queue_name: Optional[str] = None
    priority: Optional[int] = None
    retry_count: Optional[int] = None
    
    # Timing
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Result
    result_status: Optional[str] = None
    error_message: Optional[str] = None
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PerformanceEvent(BaseEvent):
    """Performance metric event."""
    
    metric_name: str
    metric_value: float
    metric_unit: str  # "ms", "bytes", "count", "percentage"
    
    # Context
    operation: Optional[str] = None
    resource: Optional[str] = None
    
    # Thresholds
    threshold_value: Optional[float] = None
    threshold_exceeded: bool = False
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict)


class APIEvent(BaseEvent):
    """API request/response event."""
    
    method: str
    path: str
    status_code: Optional[int] = None
    
    # Timing
    response_time_ms: Optional[int] = None
    
    # Request info
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Response info
    response_size_bytes: Optional[int] = None
    error_code: Optional[str] = None
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SystemEvent(BaseEvent):
    """System-level event."""
    
    component: str
    message: str
    
    # Error details
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # System metrics
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Event factory
def create_event(event_type: EventType, **kwargs) -> BaseEvent:
    """
    Factory function to create telemetry events.
    
    Args:
        event_type: Type of event to create
        **kwargs: Event-specific parameters
        
    Returns:
        Appropriate event instance
    """
    event_map = {
        EventType.VALIDATION_STARTED: ValidationEvent,
        EventType.VALIDATION_COMPLETED: ValidationEvent,
        EventType.VALIDATION_FAILED: ValidationEvent,
        EventType.VALIDATION_ROW_PROCESSED: ValidationEvent,
        
        EventType.CORRECTION_STARTED: CorrectionEvent,
        EventType.CORRECTION_COMPLETED: CorrectionEvent,
        EventType.CORRECTION_APPLIED: CorrectionEvent,
        
        EventType.JOB_CREATED: JobEvent,
        EventType.JOB_STARTED: JobEvent,
        EventType.JOB_COMPLETED: JobEvent,
        EventType.JOB_FAILED: JobEvent,
        EventType.JOB_CANCELLED: JobEvent,
        
        EventType.API_REQUEST: APIEvent,
        EventType.API_RESPONSE: APIEvent,
        
        EventType.PERFORMANCE_METRIC: PerformanceEvent,
        EventType.SLOW_QUERY: PerformanceEvent,
        EventType.MEMORY_HIGH: PerformanceEvent,
        
        EventType.SYSTEM_ERROR: SystemEvent,
        EventType.SYSTEM_WARNING: SystemEvent,
    }
    
    event_class = event_map.get(event_type, BaseEvent)
    return event_class(event_type=event_type, **kwargs)