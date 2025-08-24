"""
Refactored JobService as a coordinator.
Delegates to specialized services following Single Responsibility Principle.
"""

from typing import Optional, Tuple, List
from sqlalchemy.orm import Session

from ..core.logging_config import get_logger
from ..schemas.job import (
    JobCreate, JobOut, JobResultOut, JobListQuery,
    JobListResponse, JobStatusUpdate
)
from ..core.result import Result, Ok, Err, JobError
from ..infrastructure.repositories.job_repository import JobRepository
from ..infrastructure.queue_publisher import QueuePublisher
from ..infrastructure.queue_factory import get_queue_publisher
from ..core.validators.job_validator import JobValidator
from ..telemetry.telemetry_service import TelemetryService

# Import specialized services
from .job_creation_service import JobCreationService
from .job_query_service import JobQueryService
from .job_cancellation_service import JobCancellationService
from .job_status_sync_service import JobStatusSyncService
from .job_idempotency_service import JobIdempotencyService

logger = get_logger(__name__)


class JobServiceRefactored:
    """
    Refactored JobService that coordinates specialized services.
    
    This service acts as a facade/coordinator for:
    - Job creation (JobCreationService)
    - Job querying (JobQueryService)
    - Job cancellation (JobCancellationService)
    - Status synchronization (JobStatusSyncService)
    - Idempotency management (JobIdempotencyService)
    
    Each specialized service handles a single responsibility,
    making the system more maintainable and testable.
    """
    
    def __init__(
        self,
        db: Session,
        queue_publisher: Optional[QueuePublisher] = None,
        telemetry: Optional[TelemetryService] = None
    ):
        """
        Initialize the coordinator with all specialized services.
        
        Args:
            db: Database session
            queue_publisher: Optional queue publisher
            telemetry: Optional telemetry service
        """
        # Initialize shared dependencies
        self.db = db
        self.queue_publisher = queue_publisher or get_queue_publisher()
        self.telemetry = telemetry or TelemetryService()
        
        # Initialize repository
        self.repository = JobRepository(db)
        
        # Initialize validator
        self.validator = JobValidator()
        
        # Initialize specialized services
        self.creation_service = JobCreationService(
            repository=self.repository,
            validator=self.validator,
            queue_publisher=self.queue_publisher
        )
        
        self.query_service = JobQueryService(
            repository=self.repository,
            queue_publisher=self.queue_publisher
        )
        
        self.cancellation_service = JobCancellationService(
            repository=self.repository,
            queue_publisher=self.queue_publisher,
            telemetry=self.telemetry
        )
        
        self.status_sync_service = JobStatusSyncService(
            repository=self.repository,
            queue_publisher=self.queue_publisher,
            telemetry=self.telemetry
        )
        
        self.idempotency_service = JobIdempotencyService(
            repository=self.repository,
            telemetry=self.telemetry
        )
        
        logger.info("JobServiceRefactored initialized with specialized services")
    
    # Job Creation
    
    def create_job(
        self,
        user_id: str,
        job_data: JobCreate,
        correlation_id: Optional[str] = None,
        prefer_representation: bool = False
    ) -> Tuple[JobOut, bool]:
        """
        Create a new job with idempotency check.
        
        Delegates to JobCreationService and JobIdempotencyService.
        
        Args:
            user_id: User ID creating the job
            job_data: Job creation data
            correlation_id: Optional correlation ID
            prefer_representation: Return existing job on conflict
            
        Returns:
            Tuple of (JobOut, is_new)
        """
        # Check idempotency if key provided
        if job_data.idempotency_key:
            idempotency_result = self.idempotency_service.check_idempotency(
                user_id=user_id,
                idempotency_key=job_data.idempotency_key,
                prefer_representation=prefer_representation
            )
            
            if idempotency_result.is_ok():
                existing = idempotency_result.unwrap()
                if existing:
                    # Return existing job
                    return existing
            elif not prefer_representation:
                # Idempotency conflict
                error = idempotency_result.err()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=error.message
                )
        
        # Create new job
        creation_result = self.creation_service.create_job(
            user_id=user_id,
            job_data=job_data,
            correlation_id=correlation_id
        )
        
        if creation_result.is_err():
            error = creation_result.err()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error.message
            )
        
        job = creation_result.unwrap()
        return job, True
    
    # Job Querying
    
    def get_job(self, job_id: str, user_id: str) -> JobOut:
        """
        Get job by ID.
        
        Delegates to JobQueryService with automatic status sync.
        
        Args:
            job_id: Job UUID
            user_id: User ID for authorization
            
        Returns:
            Job details
        """
        query_result = self.query_service.get_job(job_id, user_id)
        
        if query_result.is_err():
            error = query_result.err()
            if error.code == "NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job not found"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error.message
            )
        
        job = query_result.unwrap()
        
        # Sync status if job is active
        if self._should_sync_status(job):
            self.status_sync_service.sync_job_status(
                self.repository.get_by_id(job.id).unwrap()
            )
            # Re-fetch after sync
            job = self.query_service.get_job(job_id, user_id).unwrap()
        
        return job
    
    def get_job_result(self, job_id: str, user_id: str) -> JobResultOut:
        """
        Get job result.
        
        Delegates to JobQueryService.
        
        Args:
            job_id: Job UUID
            user_id: User ID for authorization
            
        Returns:
            Job result details
        """
        result = self.query_service.get_job_result(job_id, user_id)
        
        if result.is_err():
            error = result.err()
            if error.code == "NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job not found"
                )
            elif error.code == "NOT_READY":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=error.message
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error.message
            )
        
        return result.unwrap()
    
    def list_jobs(
        self,
        user_id: str,
        query: JobListQuery
    ) -> JobListResponse:
        """
        List jobs with filtering and pagination.
        
        Delegates to JobQueryService with automatic status sync for active jobs.
        
        Args:
            user_id: User ID
            query: Query parameters
            
        Returns:
            Paginated job list
        """
        list_result = self.query_service.list_jobs(user_id, query)
        
        if list_result.is_err():
            error = list_result.err()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error.message
            )
        
        response = list_result.unwrap()
        
        # Sync status for active jobs
        active_jobs = [
            job for job in response.jobs
            if self._should_sync_status(job)
        ]
        
        if active_jobs:
            # Get full job objects for syncing
            job_ids = [job.id for job in active_jobs]
            jobs_to_sync = self.repository.get_jobs_by_ids(job_ids).unwrap_or([])
            self.status_sync_service.sync_multiple_jobs(jobs_to_sync)
            
            # Re-fetch after sync
            response = self.query_service.list_jobs(user_id, query).unwrap()
        
        return response
    
    # Job Cancellation
    
    def cancel_job(self, job_id: str, user_id: str) -> JobOut:
        """
        Cancel a job.
        
        Delegates to JobCancellationService.
        
        Args:
            job_id: Job UUID
            user_id: User ID for authorization
            
        Returns:
            Updated job details
        """
        cancel_result = self.cancellation_service.cancel_job(
            job_id=job_id,
            user_id=user_id,
            reason="Cancelled by user"
        )
        
        if cancel_result.is_err():
            error = cancel_result.err()
            if error.code == "NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job not found"
                )
            elif error.code == "INVALID_STATE":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=error.message
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error.message
            )
        
        return cancel_result.unwrap()
    
    def bulk_cancel_jobs(
        self,
        user_id: str,
        job_ids: Optional[List[str]] = None,
        task_name: Optional[str] = None
    ) -> List[JobOut]:
        """
        Cancel multiple jobs.
        
        Delegates to JobCancellationService.
        
        Args:
            user_id: User ID
            job_ids: Specific job IDs to cancel
            task_name: Cancel all jobs with this task name
            
        Returns:
            List of cancelled jobs
        """
        cancel_result = self.cancellation_service.bulk_cancel_jobs(
            user_id=user_id,
            job_ids=job_ids,
            task_name=task_name,
            reason="Bulk cancelled by user"
        )
        
        if cancel_result.is_err():
            error = cancel_result.err()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error.message
            )
        
        return cancel_result.unwrap()
    
    # Status Updates (Internal)
    
    def update_job_status(
        self,
        job_id: str,
        status_update: JobStatusUpdate
    ) -> None:
        """
        Update job status from Celery signals.
        
        Delegates to JobStatusSyncService.
        
        Args:
            job_id: Job UUID
            status_update: Status update data
        """
        update_result = self.status_sync_service.update_job_status_from_task(
            job_id=job_id,
            status=status_update.status,
            progress=status_update.progress,
            message=status_update.message,
            error=status_update.error,
            result_ref=status_update.result_ref,
            retry_count=status_update.retry_count
        )
        
        if update_result.is_err():
            logger.warning(f"Failed to update job status: {update_result.err()}")
    
    # Maintenance Operations
    
    def sync_all_active_jobs(self) -> int:
        """
        Sync all active jobs with queue backend.
        
        This should be called periodically to ensure consistency.
        
        Returns:
            Number of jobs synced
        """
        active_jobs_result = self.repository.get_all_active_jobs()
        if active_jobs_result.is_err():
            logger.error(f"Failed to get active jobs: {active_jobs_result.err()}")
            return 0
        
        active_jobs = active_jobs_result.unwrap()
        if not active_jobs:
            return 0
        
        sync_result = self.status_sync_service.sync_multiple_jobs(active_jobs)
        if sync_result.is_err():
            logger.error(f"Failed to sync jobs: {sync_result.err()}")
            return 0
        
        results = sync_result.unwrap()
        synced_count = sum(1 for v in results.values() if v)
        
        logger.info(f"Synced {synced_count}/{len(active_jobs)} active jobs")
        return synced_count
    
    def cleanup_expired_idempotency_keys(self) -> int:
        """
        Clean up expired idempotency keys.
        
        This should be called periodically.
        
        Returns:
            Number of keys cleaned
        """
        cleanup_result = self.idempotency_service.cleanup_expired_keys()
        if cleanup_result.is_err():
            logger.error(f"Failed to cleanup idempotency keys: {cleanup_result.err()}")
            return 0
        
        cleaned = cleanup_result.unwrap()
        if cleaned > 0:
            logger.info(f"Cleaned {cleaned} expired idempotency keys")
        
        return cleaned
    
    # Private helper methods
    
    def _should_sync_status(self, job: JobOut) -> bool:
        """Check if job status should be synced."""
        from ..models.job import JobStatus
        
        return job.status in [
            JobStatus.QUEUED,
            JobStatus.RUNNING,
            JobStatus.RETRYING
        ]


# Import guards for backward compatibility
from fastapi import HTTPException, status