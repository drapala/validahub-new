"""
SQLAlchemy models for validation job processing.
"""

from sqlalchemy import (
    Column, String, DateTime, Enum as SQLEnum, Text, Integer, 
    JSON, UniqueConstraint, Index, Float, text, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.inspection import inspect
from datetime import datetime
import enum
import uuid

from src.db.base import Base
from src.models.utils import get_table_args


class JobStatus(str, enum.Enum):
    """Job processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REVIEW = "review"
    CANCELLED = "cancelled"


class JobChannel(str, enum.Enum):
    """E-commerce channels."""
    MERCADO_LIVRE = "mercado_livre"
    AMAZON = "amazon"
    B2W = "b2w"
    MAGALU = "magalu"
    SHOPEE = "shopee"
    VIA = "via"
    CASAS_BAHIA = "casas_bahia"


class JobType(str, enum.Enum):
    """Job types."""
    CATALOG_UPLOAD = "catalog_upload"
    PRICE_UPDATE = "price_update"
    STOCK_UPDATE = "stock_update"
    FULL_SYNC = "full_sync"
    VALIDATION_ONLY = "validation_only"


class ErrorSeverity(str, enum.Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Job(Base):
    """Job entity for validation processing."""
    
    __tablename__ = "jobs"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenant
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Seller info
    seller_id = Column(String, index=True, nullable=False)
    seller_name = Column(String, nullable=False)
    
    # Job classification
    channel = Column(SQLEnum(JobChannel), nullable=False)
    type = Column(SQLEnum(JobType), nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    
    # Processing metrics
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    success_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    warning_items = Column(Integer, default=0)
    
    # Performance
    duration_ms = Column(Integer)
    avg_item_time_ms = Column(Float)
    p95_time_ms = Column(Float)
    p99_time_ms = Column(Float)
    
    # Error tracking
    error_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    severity = Column(SQLEnum(ErrorSeverity))
    last_error = Column(Text)
    
    # File info
    file_name = Column(String)
    file_size_bytes = Column(Integer)
    file_url = Column(String)
    
    # Idempotency
    idempotency_key = Column(String(255), index=True)
    reprocess_count = Column(Integer, default=0)
    parent_job_id = Column(String, ForeignKey("jobs.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Metadata
    job_metadata = Column(JSON, default={})
    
    # Relationships
    tenant = relationship("Tenant", backref="jobs")
    items = relationship("JobItem", back_populates="job", cascade="all, delete-orphan")
    parent_job = relationship("Job", remote_side=[id], backref="reprocessed_jobs")
    
    # Constraints
    __table_args__ = (
        Index('idx_jobs_tenant_created', 'tenant_id', 'created_at'),
        Index('idx_jobs_tenant_status', 'tenant_id', 'status'),
        Index('idx_jobs_tenant_seller', 'tenant_id', 'seller_id'),
        Index(
            'uq_tenant_idempotency',
            'tenant_id',
            'idempotency_key',
            unique=True,
            postgresql_where=text('idempotency_key IS NOT NULL')
        ),
        {'extend_existing': True}
    )
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_items == 0:
            return 0.0
        return (self.success_items / self.total_items) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if job is complete."""
        return self.status in [JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.CANCELLED]
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "seller_id": self.seller_id,
            "seller_name": self.seller_name,
            "channel": self.channel.value if self.channel else None,
            "type": self.type.value if self.type else None,
            "status": self.status.value if self.status else None,
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "success_items": self.success_items,
            "failed_items": self.failed_items,
            "warning_items": self.warning_items,
            "success_rate": self.success_rate,
            "duration_ms": self.duration_ms,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "severity": self.severity.value if self.severity else None,
            "file_name": self.file_name,
            "file_size_bytes": self.file_size_bytes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "reprocess_count": self.reprocess_count,
        }


class JobItem(Base):
    """Individual item within a job."""
    
    __tablename__ = "job_items"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Item data
    sku = Column(String, nullable=False, index=True)
    title = Column(String)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    
    # Validation details
    field_errors = Column(JSON, default=list)
    business_errors = Column(JSON, default=list)
    warnings = Column(JSON, default=list)
    suggestions = Column(JSON, default=list)
    
    # Error categorization
    error_codes = Column(JSON, default=list)
    error_categories = Column(JSON, default=list)
    
    # Data tracking
    original_data = Column(JSON)
    corrected_data = Column(JSON)
    corrections_applied = Column(JSON, default=list)
    
    # Performance
    processing_time_ms = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="items")
    
    # Constraints
    __table_args__ = (
        Index('idx_job_items_job_status', 'job_id', 'status'),
        Index('idx_job_items_job_sku', 'job_id', 'sku'),
        {'extend_existing': True}
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "sku": self.sku,
            "title": self.title,
            "status": self.status.value if self.status else None,
            "field_errors": self.field_errors,
            "business_errors": self.business_errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "error_codes": self.error_codes,
            "error_categories": self.error_categories,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }