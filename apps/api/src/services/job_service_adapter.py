"""
Simple adapter for JobService to implement IJobService interface.
This adapter only delegates calls, without implementing business logic.
"""

from src.core.logging_config import get_logger
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from src.core.interfaces.job_service import IJobService, JobStatus as IJobStatus
from src.schemas.job import (
    JobCreate,
    JobOut,
    JobResultOut,
    JobListQuery,
    JobListResponse,
    JobStatusUpdate
)
from src.infrastructure.queue_publisher import QueuePublisher
from .job_service import JobService as LegacyJobService

logger = get_logger(__name__)


class JobServiceAdapter(IJobService):
    """
    Simple adapter that wraps the existing JobService to implement IJobService interface.
    
    This adapter follows the Single Responsibility Principle - it only adapts
    the interface, delegating all business logic to the underlying service.
    """
    
    def __init__(self, db: Session, queue_publisher: Optional[QueuePublisher] = None) -> None:
        """
        Initialize the adapter with database session and optional queue publisher.
        
        Args:
            db: SQLAlchemy database session
            queue_publisher: Optional queue publisher instance
        """
        self.service = LegacyJobService(db, queue_publisher)
    
    def create_job(
        self,
        user_id: str,
        job_data: JobCreate,
        correlation_id: Optional[str] = None,
        prefer_representation: bool = False
    ) -> Tuple[JobOut, bool]:
        """Create a new job - delegates to legacy service."""
        return self.service.create_job(
            user_id=user_id,
            job_data=job_data,
            correlation_id=correlation_id,
            prefer_representation=prefer_representation
        )
    
    def get_job(self, job_id: str, user_id: Optional[str] = None) -> Optional[JobOut]:
        """Get a job by ID - delegates to legacy service."""
        return self.service.get_job(job_id, user_id)
    
    def list_jobs(
        self,
        user_id: str,
        query: JobListQuery
    ) -> JobListResponse:
        """List jobs - delegates to legacy service."""
        return self.service.list_jobs(user_id, query)
    
    def cancel_job(
        self,
        job_id: str,
        user_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """Cancel a job - delegates to legacy service."""
        return self.service.cancel_job(job_id, user_id, reason)
    
    def update_job_status(
        self,
        job_id: str,
        status_update: JobStatusUpdate
    ) -> bool:
        """Update job status - delegates to legacy service."""
        return self.service.update_job_status(job_id, status_update)
    
    def get_job_result(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Optional[JobResultOut]:
        """Get job result - delegates to legacy service."""
        return self.service.get_job_result(job_id, user_id)
    
    def cleanup_old_jobs(
        self,
        older_than: datetime,
        status_filter: Optional[List[IJobStatus]] = None
    ) -> int:
        """Clean up old jobs - delegates to legacy service."""
        return self.service.cleanup_old_jobs(older_than, status_filter)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics - delegates to legacy service."""
        return self.service.get_queue_stats()
    
    def retry_job(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Tuple[JobOut, bool]:
        """Retry a failed job - delegates to legacy service."""
        return self.service.retry_job(job_id, user_id)