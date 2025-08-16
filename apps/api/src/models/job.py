"""
SQLAlchemy models for job queue system.
"""

from sqlalchemy import (
    Column, String, DateTime, Enum as SQLEnum, Text, Integer, 
    JSON, UniqueConstraint, Index, Float
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
import uuid

from src.db.base import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration."""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    RETRYING = "retrying"


class JobPriority(int, enum.Enum):
    """Job priority levels."""
    LOW = 1
    NORMAL = 5
    HIGH = 7
    CRITICAL = 10


class Job(Base):
    """Job queue model for async task tracking."""
    
    __tablename__ = "jobs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User/tenant info
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), index=True)
    
    # Job definition
    task_name = Column(String(100), nullable=False, index=True)
    queue = Column(String(50), nullable=False, default="queue:free")
    priority = Column(Integer, default=JobPriority.NORMAL.value)
    status = Column(
        SQLEnum(JobStatus, values_callable=lambda x: [e.value for e in x]), 
        nullable=False, 
        default=JobStatus.QUEUED,
        index=True
    )
    
    # Job data
    params_json = Column(JSON, nullable=False, default={})
    result_ref = Column(String(500))  # S3 URI or similar
    error = Column(Text)
    
    # Progress tracking
    progress = Column(Float, default=0.0)  # 0-100
    message = Column(Text)  # Current status message
    
    # Idempotency
    idempotency_key = Column(String(255), index=True)
    
    # Correlation
    correlation_id = Column(String(100), index=True)
    
    # Celery integration
    celery_task_id = Column(String(255), unique=True, index=True)
    
    # Retry tracking
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # Metadata
    job_metadata = Column(JSON, default={})
    
    # Constraints
    __table_args__ = (
        # Create a partial unique constraint that only applies when idempotency_key is not NULL
        Index(
            'uq_user_idempotency_nonnull',
            'user_id',
            'idempotency_key',
            unique=True,
            postgresql_where=(idempotency_key != None)
        ),
        Index('ix_jobs_user_status', 'user_id', 'status'),
        Index('ix_jobs_created_at_desc', created_at.desc()),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "organization_id": str(self.organization_id) if self.organization_id else None,
            "task_name": self.task_name,
            "queue": self.queue,
            "priority": self.priority,
            "status": self.status.value if self.status else None,
            "params": self.params_json,
            "result_ref": self.result_ref,
            "error": self.error,
            "progress": self.progress,
            "message": self.message,
            "idempotency_key": self.idempotency_key,
            "correlation_id": self.correlation_id,
            "celery_task_id": self.celery_task_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.job_metadata
        }


class JobResult(Base):
    """Separate table for large job results (optional)."""
    
    __tablename__ = "job_results"
    
    job_id = Column(UUID(as_uuid=True), primary_key=True)
    result_json = Column(JSON)
    object_uri = Column(String(500))  # S3/GCS URI for large results
    size_bytes = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())