"""
Pydantic schemas for job queue system.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
import enum

from models.job import JobStatus, JobPriority


class JobPlan(str, enum.Enum):
    """User plan levels for queue routing."""
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class JobCreate(BaseModel):
    """Schema for creating a new job."""
    
    task: str = Field(..., description="Task name to execute", min_length=1, max_length=100)
    params: Dict[str, Any] = Field(default={}, description="Task parameters")
    priority: Optional[int] = Field(
        default=JobPriority.NORMAL.value,
        ge=1, 
        le=10,
        description="Job priority (1-10)"
    )
    plan: JobPlan = Field(default=JobPlan.FREE, description="User plan for queue routing")
    idempotency_key: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Idempotency key for duplicate prevention"
    )
    correlation_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Correlation ID for request tracing"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default={},
        description="Additional metadata"
    )
    
    @field_validator('params')
    @classmethod
    def validate_params(cls, v):
        """Ensure params are serializable."""
        import json
        try:
            json.dumps(v)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Params must be JSON serializable: {e}")
        return v


class JobOut(BaseModel):
    """Schema for job response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    task_name: str
    queue: str
    priority: int
    status: JobStatus
    progress: float = Field(ge=0, le=100)
    message: Optional[str] = None
    error: Optional[str] = None
    idempotency_key: Optional[str] = None
    correlation_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    
    @property
    def is_terminal(self) -> bool:
        """Check if job is in terminal state."""
        return self.status in [
            JobStatus.SUCCEEDED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
            JobStatus.EXPIRED
        ]


class JobResultOut(BaseModel):
    """Schema for job result response."""
    
    job_id: UUID
    status: JobStatus
    result_ref: Optional[str] = Field(
        default=None,
        description="Reference to result (S3 URI, etc)"
    )
    result_json: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Inline result for small payloads"
    )
    object_uri: Optional[str] = None
    size_bytes: Optional[int] = None
    error: Optional[str] = None
    finished_at: Optional[datetime] = None


class JobListQuery(BaseModel):
    """Query parameters for listing jobs."""
    
    status: Optional[JobStatus] = None
    task_name: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    order_by: str = Field(default="created_at_desc")


class JobListResponse(BaseModel):
    """Response for job listing."""
    
    jobs: List[JobOut]
    total: int
    limit: int
    offset: int
    has_more: bool


class JobStatusUpdate(BaseModel):
    """Internal schema for job status updates (from Celery)."""
    
    status: JobStatus
    progress: Optional[float] = None
    message: Optional[str] = None
    error: Optional[str] = None
    result_ref: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    retry_count: Optional[int] = None