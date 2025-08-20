"""
Service responsible for querying jobs.
Follows Single Responsibility Principle.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from ..schemas.job import JobOut, JobResultOut, JobListQuery, JobListResponse
from ..models.job import Job, JobStatus, JobResult
from ..core.result import Result, Ok, Err, JobError
from ..infrastructure.repositories.job_repository import JobRepository
from ..infrastructure.queue_publisher import QueuePublisher

logger = logging.getLogger(__name__)


class JobQueryService:
    """
    Service responsible for querying and retrieving jobs.
    
    This service handles:
    - Finding jobs by various criteria
    - Listing jobs with pagination
    - Getting job results
    - Synchronizing status with queue
    """
    
    def __init__(
        self,
        repository: JobRepository,
        queue_publisher: Optional[QueuePublisher] = None
    ):
        """
        Initialize service with dependencies.
        
        Args:
            repository: Job repository for data access
            queue_publisher: Optional queue publisher for status sync
        """
        self.repository = repository
        self.queue_publisher = queue_publisher
    
    def get_job(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Result[JobOut, JobError]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job UUID string
            user_id: Optional user ID for authorization
            
        Returns:
            Result containing JobOut or error
        """
        try:
            job_uuid = uuid.UUID(job_id)
        except ValueError:
            logger.warning(f"Invalid job ID format: {job_id}")
            return Err(JobError.VALIDATION_ERROR)
        
        # Find job
        if user_id:
            try:
                user_uuid = uuid.UUID(user_id)
                result = self.repository.find_by_id_and_user(job_uuid, user_uuid)
            except ValueError:
                logger.warning(f"Invalid user ID format: {user_id}")
                return Err(JobError.VALIDATION_ERROR)
        else:
            result = self.repository.find_by_id(job_uuid)
        
        if result.is_err():
            return result
        
        job = result.unwrap()
        
        # Sync status if job is active
        if self._should_sync_status(job):
            self._sync_job_status(job)
        
        return Ok(JobOut.model_validate(job))
    
    def list_jobs(
        self,
        user_id: str,
        query: JobListQuery
    ) -> Result[JobListResponse, JobError]:
        """
        List jobs for a user with filtering and pagination.
        
        Args:
            user_id: User ID to list jobs for
            query: Query parameters
            
        Returns:
            Result containing JobListResponse or error
        """
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            logger.warning(f"Invalid user ID format: {user_id}")
            return Err(JobError.VALIDATION_ERROR)
        
        # Get jobs from repository
        offset = (query.page - 1) * query.page_size
        result = self.repository.list_by_user(
            user_id=user_uuid,
            status=query.status,
            task_name=query.task_name,
            queue=query.queue,
            created_after=query.created_after,
            created_before=query.created_before,
            limit=query.page_size,
            offset=offset,
            order_by=query.sort_by or "created_at",
            order_desc=query.sort_desc
        )
        
        if result.is_err():
            return Err(result.unwrap_err())
        
        jobs = result.unwrap()
        
        # Get total count
        total = self.repository.count_by_user(
            user_id=user_uuid,
            status=query.status
        )
        
        # Convert to response
        response = JobListResponse(
            jobs=[JobOut.model_validate(job) for job in jobs],
            total=total,
            page=query.page,
            page_size=query.page_size
        )
        
        return Ok(response)
    
    def get_job_result(
        self,
        job_id: str,
        user_id: Optional[str] = None
    ) -> Result[JobResultOut, JobError]:
        """
        Get job result.
        
        Args:
            job_id: Job UUID string
            user_id: Optional user ID for authorization
            
        Returns:
            Result containing JobResultOut or error
        """
        # First get the job
        job_result = self.get_job(job_id, user_id)
        if job_result.is_err():
            return Err(job_result.unwrap_err())
        
        job_out = job_result.unwrap()
        
        # Check if job has completed
        if job_out.status != JobStatus.SUCCEEDED.value:
            logger.info(f"Job {job_id} has not succeeded, status: {job_out.status}")
            return Err(JobError.INVALID_STATUS)
        
        # Get result from database
        try:
            job_uuid = uuid.UUID(job_id)
            job_result_entity = self.repository.find_result_by_job_id(job_uuid)
            
            if job_result_entity:
                return Ok(JobResultOut.model_validate(job_result_entity))
            
            # If no result in DB but job succeeded, create minimal response
            if job_out.result_ref:
                return Ok(JobResultOut(
                    job_id=job_id,
                    result_type="reference",
                    result_data={"ref": job_out.result_ref},
                    created_at=job_out.finished_at or job_out.created_at
                ))
            
            return Err(JobError.NOT_FOUND)
            
        except Exception as e:
            logger.error(f"Failed to get job result: {e}")
            return Err(JobError.DATABASE_ERROR)
    
    def get_statistics(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get job statistics.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            Dictionary with statistics
        """
        stats = self.repository.get_statistics()
        
        # Add queue-specific stats if available
        if self.queue_publisher and hasattr(self.queue_publisher, 'get_queue_stats'):
            try:
                queue_stats = self.queue_publisher.get_queue_stats()
                stats['queue'] = queue_stats
            except Exception as e:
                logger.warning(f"Failed to get queue stats: {e}")
        
        return stats
    
    def _should_sync_status(self, job: Job) -> bool:
        """
        Check if job status should be synced with queue.
        
        Args:
            job: Job entity
            
        Returns:
            True if status should be synced
        """
        active_statuses = [
            JobStatus.QUEUED,
            JobStatus.RUNNING,
            JobStatus.RETRYING
        ]
        return job.status in active_statuses and job.celery_task_id is not None
    
    def _sync_job_status(self, job: Job) -> bool:
        """
        Sync job status with queue backend.
        
        Args:
            job: Job entity to sync
            
        Returns:
            True if status was updated
        """
        if not self.queue_publisher or not job.celery_task_id:
            return False
        
        try:
            status_info = self.queue_publisher.get_status(job.celery_task_id)
            if not status_info:
                return False
            
            # Map queue status to job status
            queue_status = status_info.get('status', '').lower()
            status_mapping = {
                'queued': JobStatus.QUEUED,
                'processing': JobStatus.RUNNING,
                'running': JobStatus.RUNNING,
                'completed': JobStatus.SUCCEEDED,
                'succeeded': JobStatus.SUCCEEDED,
                'failed': JobStatus.FAILED,
                'cancelled': JobStatus.CANCELLED,
                'retrying': JobStatus.RETRYING
            }
            
            new_status = status_mapping.get(queue_status)
            if new_status and new_status != job.status:
                job.status = new_status
                
                # Update progress if available
                if 'progress' in status_info and status_info['progress'] is not None:
                    job.progress = float(status_info['progress'])
                
                # Update message if available
                if 'message' in status_info and status_info['message']:
                    job.message = status_info['message']
                
                # Update error if failed
                if new_status == JobStatus.FAILED and 'error' in status_info:
                    job.error = status_info['error']
                
                # Update finished time if completed
                if new_status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED]:
                    if not job.finished_at:
                        job.finished_at = datetime.now(timezone.utc)
                
                # Save updates
                self.repository.update(job)
                
                logger.info(f"Synced job {job.id} status: {job.status}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to sync job status: {e}")
        
        return False