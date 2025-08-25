"""
SQLAlchemy models for job queue system.
"""

from sqlalchemy import (
    Column, String, DateTime, Enum as SQLEnum, Text, Integer, 
    JSON, UniqueConstraint, Index, Float, text
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.inspection import inspect
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
    __table_args__ = {'extend_existing': True}
    
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
        # NOTE: This uses PostgreSQL-specific partial index syntax (postgresql_where).
        # Database portability consideration: If migrating to another database system,
        # this constraint will need to be reimplemented using that database's equivalent
        # feature (e.g., filtered index in SQL Server, function-based index in Oracle,
        # or application-level enforcement for databases without partial index support).
        Index(
            'uq_user_idempotency_nonnull',
            'user_id',
            'idempotency_key',
            unique=True,
            postgresql_where=text('idempotency_key IS NOT NULL')
        ),
        Index('ix_jobs_user_status', 'user_id', 'status'),
        Index('ix_jobs_created_at_desc', created_at.desc()),
    )
    
    @property
    def is_terminal(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in [
            JobStatus.SUCCEEDED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
            JobStatus.EXPIRED
        ]
    
    def to_dict(self):
        """Convert to dictionary using SQLAlchemy inspection."""
        result = {}
        for column in inspect(self).mapper.column_attrs:
            value = getattr(self, column.key)
            # Handle special types
            if isinstance(value, uuid.UUID):
                result[column.key] = str(value)
            elif isinstance(value, datetime):
                result[column.key] = value.isoformat()
            elif isinstance(value, enum.Enum):
                result[column.key] = value.value
            else:
                result[column.key] = value
        
        # For backward compatibility, rename some fields
        if "params_json" in result:
            result["params"] = result.pop("params_json")
        if "job_metadata" in result:
            result["metadata"] = result.pop("job_metadata")
        
        return result


class JobResult(Base):
    """Separate table for large job results (optional)."""
    
    __tablename__ = "job_results"
    __table_args__ = {'extend_existing': True}
    
    job_id = Column(UUID(as_uuid=True), primary_key=True)
    result_json = Column(JSON)
    object_uri = Column(String(500))  # S3/GCS URI for large results
    size_bytes = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())