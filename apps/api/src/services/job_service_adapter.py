"""
Adapter for JobService to implement IJobService interface.
This provides a clean interface while maintaining backward compatibility.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from ..core.interfaces.job_service import IJobService, JobStatus as IJobStatus
from ..models.job import Job, JobStatus, JobResult
from ..schemas.job import (
    JobCreate,
    JobOut,
    JobResultOut,
    JobListQuery,
    JobListResponse,
    JobStatusUpdate
)
from ..infrastructure.queue_publisher import QueuePublisher
from ..infrastructure.queue_factory import get_queue_publisher
from ..telemetry.job_telemetry import get_job_telemetry
from .job_service import JobService as LegacyJobService

logger = logging.getLogger(__name__)


class JobServiceAdapter(IJobService):
    """
    Adapter that wraps the existing JobService to implement IJobService interface.
    
    This allows gradual migration to the interface-based approach while
    maintaining all existing functionality.
    """
    
    def __init__(self, db: Session, queue_publisher: Optional[QueuePublisher] = None):
        """
        Initialize the adapter with database session and optional queue publisher.
        
        Args:
            db: SQLAlchemy database session
            queue_publisher: Optional queue publisher instance
        """
        self.db = db
        self.legacy_service = LegacyJobService(db, queue_publisher)
        self.telemetry = get_job_telemetry()
    
    def create_job(
        self,
        user_id: str,
        job_data: JobCreate,
        correlation_id: Optional[str] = None,
        prefer_representation: bool = False
    ) -> Tuple[JobOut, bool]:
        """
        Create a new job with idempotency check.
        
        Delegates to the legacy JobService.create_job method.
        """
        return self.legacy_service.create_job(
            user_id=user_id,
            job_data=job_data,
            correlation_id=correlation_id,
            prefer_representation=prefer_representation
        )
    
    def get_job(self, job_id: str, user_id: Optional[str] = None) -> Optional[JobOut]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job ID to retrieve
            user_id: Optional user ID for authorization check
            
        Returns:
            JobOut if found, None otherwise
        """
        # Use legacy service method if it exists, otherwise implement here
        if hasattr(self.legacy_service, 'get_job'):
            return self.legacy_service.get_job(job_id, user_id)
        
        # Direct implementation
        job = self.db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            return None
        
        # Check authorization if user_id provided
        if user_id and str(job.user_id) != user_id:
            logger.warning(f"User {user_id} attempted to access job {job_id} owned by {job.user_id}")
            return None
        
        return JobOut.model_validate(job)
    
    def list_jobs(
        self,
        user_id: str,
        query: JobListQuery
    ) -> JobListResponse:
        """
        List jobs for a user with filtering and pagination.
        
        Args:
            user_id: User ID to list jobs for
            query: Query parameters for filtering and pagination
            
        Returns:
            JobListResponse with jobs and pagination info
        """
        # Use legacy service method if it exists
        if hasattr(self.legacy_service, 'list_jobs'):
            return self.legacy_service.list_jobs(user_id, query)
        
        # Direct implementation
        base_query = self.db.query(Job).filter(Job.user_id == user_id)
        
        # Apply filters
        if query.status:
            base_query = base_query.filter(Job.status == query.status)
        
        if query.task_name:
            base_query = base_query.filter(Job.task_name == query.task_name)
        
        if query.queue:
            base_query = base_query.filter(Job.queue == query.queue)
        
        if query.created_after:
            base_query = base_query.filter(Job.created_at >= query.created_after)
        
        if query.created_before:
            base_query = base_query.filter(Job.created_at <= query.created_before)
        
        # Count total
        total = base_query.count()
        
        # Apply sorting
        if query.sort_by == "created_at":
            base_query = base_query.order_by(
                desc(Job.created_at) if query.sort_desc else Job.created_at
            )
        elif query.sort_by == "status":
            base_query = base_query.order_by(
                desc(Job.status) if query.sort_desc else Job.status
            )
        
        # Apply pagination
        offset = (query.page - 1) * query.page_size
        jobs = base_query.offset(offset).limit(query.page_size).all()
        
        return JobListResponse(
            jobs=[JobOut.model_validate(job) for job in jobs],
            total=total,
            page=query.page,
            page_size=query.page_size
        )
    
    def cancel_job(
        self,
        job_id: str,
        user_id: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Cancel a job.
        
        Args:
            job_id: Job ID to cancel
            user_id: Optional user ID for authorization check
            reason: Optional cancellation reason
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        # Use legacy service method if it exists
        if hasattr(self.legacy_service, 'cancel_job'):
            return self.legacy_service.cancel_job(job_id, user_id, reason)
        
        # Direct implementation
        job = self.db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            return False
        
        # Check authorization if user_id provided
        if user_id and str(job.user_id) != user_id:
            logger.warning(f"User {user_id} attempted to cancel job {job_id} owned by {job.user_id}")
            return False
        
        # Only cancel if job is cancellable
        if job.status not in [JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.RETRYING]:
            logger.warning(f"Cannot cancel job {job_id} in status {job.status}")
            return False
        
        # Cancel via queue publisher if task is running
        if job.celery_task_id and self.legacy_service.queue_publisher:
            cancelled = self.legacy_service.queue_publisher.cancel(
                job.celery_task_id,
                terminate=(job.status == JobStatus.RUNNING)
            )
            if not cancelled:
                logger.error(f"Failed to cancel task {job.celery_task_id} for job {job_id}")
        
        # Update job status
        job.status = JobStatus.CANCELLED
        job.finished_at = datetime.utcnow()
        job.message = reason or "Job cancelled by user"
        
        self.db.commit()
        
        # Emit telemetry
        self.telemetry.emit_job_cancelled(
            job_id=str(job_id),
            task_name=job.task_name,
            reason=reason,
            correlation_id=job.correlation_id
        )
        
        return True
    
    def update_job_status(
        self,
        job_id: str,
        status_update: JobStatusUpdate
    ) -> bool:
        """
        Update job status (typically called by workers).
        
        Args:
            job_id: Job ID to update
            status_update: Status update data
            
        Returns:
            True if update was successful, False otherwise
        """
        job = self.db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            return False
        
        # Update status
        if status_update.status:
            job.status = JobStatus(status_update.status)
        
        if status_update.progress is not None:
            job.progress = status_update.progress
        
        if status_update.message:
            job.message = status_update.message
        
        if status_update.error:
            job.error = status_update.error
        
        if status_update.result_ref:
            job.result_ref = status_update.result_ref
        
        # Update timestamps based on status
        if status_update.status == JobStatus.RUNNING and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status_update.status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED]:
            job.finished_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def get_job_result(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Optional[JobResultOut]:
        """
        Get job result.
        
        Args:
            job_id: Job ID to get result for
            user_id: Optional user ID for authorization check
            
        Returns:
            JobResultOut if available, None otherwise
        """
        # Use legacy service method if it exists
        if hasattr(self.legacy_service, 'get_job_result'):
            return self.legacy_service.get_job_result(job_id, user_id)
        
        # Direct implementation
        job = self.db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            return None
        
        # Check authorization if user_id provided
        if user_id and str(job.user_id) != user_id:
            return None
        
        # Check if job has result
        if job.status != JobStatus.SUCCEEDED or not job.result_ref:
            return None
        
        # Query result from JobResult table
        result = self.db.query(JobResult).filter(JobResult.job_id == job.id).first()
        
        if result:
            return JobResultOut.model_validate(result)
        
        # If no result in DB but has result_ref, create a minimal response
        return JobResultOut(
            job_id=str(job.id),
            result_type="reference",
            result_data={"ref": job.result_ref},
            created_at=job.finished_at or job.created_at
        )
    
    def cleanup_old_jobs(
        self,
        older_than: datetime,
        status_filter: Optional[List[IJobStatus]] = None
    ) -> int:
        """
        Clean up old jobs from the system.
        
        Args:
            older_than: Delete jobs older than this datetime
            status_filter: Optional list of statuses to filter by
            
        Returns:
            Number of jobs cleaned up
        """
        query = self.db.query(Job).filter(Job.created_at < older_than)
        
        if status_filter:
            # Convert interface status to model status
            model_statuses = [JobStatus(status.value) for status in status_filter]
            query = query.filter(Job.status.in_(model_statuses))
        
        # Count before deletion
        count = query.count()
        
        # Delete jobs and their results
        for job in query.all():
            # Delete associated results
            self.db.query(JobResult).filter(JobResult.job_id == job.id).delete()
            # Delete job
            self.db.delete(job)
        
        self.db.commit()
        
        logger.info(f"Cleaned up {count} old jobs created before {older_than}")
        
        return count
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get queue statistics.
        
        Returns:
            Dictionary with queue statistics
        """
        # Total jobs
        total = self.db.query(Job).count()
        
        # Jobs by status
        status_counts = dict(
            self.db.query(Job.status, func.count(Job.id))
            .group_by(Job.status)
            .all()
        )
        
        # Jobs by queue
        queue_counts = dict(
            self.db.query(Job.queue, func.count(Job.id))
            .filter(Job.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]))
            .group_by(Job.queue)
            .all()
        )
        
        # Jobs by task
        task_counts = dict(
            self.db.query(Job.task_name, func.count(Job.id))
            .group_by(Job.task_name)
            .all()
        )
        
        return {
            "total_jobs": total,
            "queued": status_counts.get(JobStatus.QUEUED, 0),
            "running": status_counts.get(JobStatus.RUNNING, 0),
            "succeeded": status_counts.get(JobStatus.SUCCEEDED, 0),
            "failed": status_counts.get(JobStatus.FAILED, 0),
            "cancelled": status_counts.get(JobStatus.CANCELLED, 0),
            "retrying": status_counts.get(JobStatus.RETRYING, 0),
            "by_queue": queue_counts,
            "by_task": task_counts
        }
    
    def retry_job(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Tuple[JobOut, bool]:
        """
        Retry a failed job.
        
        Args:
            job_id: Job ID to retry
            user_id: Optional user ID for authorization check
            
        Returns:
            Tuple of (JobOut, success) where success indicates if retry was initiated
        """
        job = self.db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            return None, False
        
        # Check authorization if user_id provided
        if user_id and str(job.user_id) != user_id:
            logger.warning(f"User {user_id} attempted to retry job {job_id} owned by {job.user_id}")
            return JobOut.model_validate(job), False
        
        # Only retry failed jobs
        if job.status != JobStatus.FAILED:
            logger.warning(f"Cannot retry job {job_id} in status {job.status}")
            return JobOut.model_validate(job), False
        
        # Check retry limit
        if job.retry_count >= job.max_retries:
            logger.warning(f"Job {job_id} has reached max retries ({job.max_retries})")
            return JobOut.model_validate(job), False
        
        # Create new job data for retry
        job_data = JobCreate(
            task=job.task_name,
            params=job.params_json,
            queue=job.queue,
            priority=job.priority,
            correlation_id=job.correlation_id,
            metadata={
                **job.metadata,
                "retry_of": str(job_id),
                "retry_count": job.retry_count + 1
            }
        )
        
        # Create new job (will get new ID)
        new_job, created = self.create_job(
            user_id=str(job.user_id),
            job_data=job_data,
            correlation_id=job.correlation_id
        )
        
        if created:
            # Update original job with retry info
            job.retry_count += 1
            job.message = f"Retried as job {new_job.id}"
            self.db.commit()
        
        return new_job, created