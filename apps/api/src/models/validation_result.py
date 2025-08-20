"""
ValidationResult model for storing validation results.
"""

from sqlalchemy import Column, String, DateTime, Integer, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from src.db.base import Base


class ValidationResult(Base):
    """Model for storing validation results."""
    __tablename__ = "validation_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    file_id = Column(String, ForeignKey("files.id"), nullable=True)
    
    # Validation metadata
    marketplace = Column(String, nullable=False, index=True)
    category = Column(String, nullable=True, index=True)
    ruleset = Column(String, nullable=False, default="default")
    
    # Results summary
    total_rows = Column(Integer, nullable=False)
    valid_rows = Column(Integer, nullable=False)
    invalid_rows = Column(Integer, nullable=False)
    warning_rows = Column(Integer, nullable=False, default=0)
    
    # Error details (JSON)
    errors = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    
    # Processing info
    processing_time_ms = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="pending", index=True)
    error_message = Column(Text, nullable=True)
    
    # Output files
    result_file_url = Column(String, nullable=True)
    corrected_file_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    job = relationship("Job", backref="validation_results")
    file = relationship("File", backref="validation_results")