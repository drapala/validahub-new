"""
Service responsible for job cancellation.
Follows Single Responsibility Principle.
"""

import uuid
from typing import Optional, List
from datetime import datetime, timezone

from src.core.logging_config import get_logger
from src.schemas.job import JobOut
from src.models.job import Job, JobStatus
from src.core.result import Result, Ok, Err, JobError
from src.infrastructure.repositories.job_repository import JobRepository
from src.infrastructure.queue_publisher import QueuePublisher
from src.telemetry.telemetry_service import TelemetryService

logger = get_logger(__name__)


class JobCancellationService:
    """
    Service responsible for cancelling jobs.
    
    This service handles:
    - Job cancellation validation
    - Queue task revocation
    - Status updates
    - Cancellation telemetry
    """
    
    def __init__(
        self,
        repository: JobRepository,
        queue_publisher: QueuePublisher,
        telemetry: Optional[TelemetryService] = None
    ):
        """
        Initialize service with dependencies.
        
        Args:
            repository: Job repository for data access
            queue_publisher: Queue publisher for task revocation
            telemetry: Optional telemetry service
        """
        self.repository = repository
        self.queue_publisher = queue_publisher
        self.telemetry = telemetry or TelemetryService()
    
    def cancel_job(
        self,
        job_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> Result[JobOut, JobError]:
        """
        Cancel a job.
        
        Args:
            job_id: Job UUID to cancel
            user_id: User ID for authorization
            reason: Optional cancellation reason
            
        Returns:
            Result with cancelled job or error
        """
        try:
            # Validate inputs
            try:
                job_uuid = uuid.UUID(job_id)
                user_uuid = uuid.UUID(user_id)
            except ValueError as e:
                logger.error(f"Invalid UUID format: {e}")
                return Err(JobError(
                    code="INVALID_ID",
                    message="Invalid job or user ID format"
                ))
            
            # Get job with authorization check
            job_result = self.repository.get_job_for_user(job_uuid, user_uuid)
            if job_result.is_err():
                return job_result
            
            job = job_result.unwrap()
            
            # Check if job can be cancelled
            if not self._can_cancel_job(job):
                return Err(JobError(
                    code="INVALID_STATE",
                    message=f"Cannot cancel job in {job.status.value} state"
                ))
            
            # Try to revoke task from queue
            if job.celery_task_id:
                revocation_result = self._revoke_queue_task(job.celery_task_id)
                if revocation_result.is_err():
                    logger.warning(f"Failed to revoke task {job.celery_task_id}: {revocation_result.err()}")
                    # Continue with cancellation even if revocation fails
            
            # Update job status
            update_result = self._update_job_cancelled_status(job, reason)
            if update_result.is_err():
                return update_result
            
            # Emit telemetry
            self._emit_cancellation_telemetry(job, reason)
            
            # Refresh and return
            refreshed_job = self.repository.refresh(job)
            
            logger.info(f"Successfully cancelled job {job_id} for user {user_id}")
            return Ok(JobOut.model_validate(refreshed_job))
            
        except Exception as e:
            logger.error(f"Unexpected error cancelling job {job_id}: {e}")
            return Err(JobError(
                code="CANCELLATION_FAILED",
                message=f"Failed to cancel job: {str(e)}"
            ))
    
    def bulk_cancel_jobs(
        self,
        user_id: str,
        job_ids: Optional[List[str]] = None,
        task_name: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Result[List[JobOut], JobError]:
        """
        Cancel multiple jobs at once.
        
        Args:
            user_id: User ID for authorization
            job_ids: Specific job IDs to cancel
            task_name: Cancel all jobs with this task name
            reason: Optional cancellation reason
            
        Returns:
            Result with list of cancelled jobs or error
        """
        try:
            user_uuid = uuid.UUID(user_id)
            
            # Get jobs to cancel
            if job_ids:
                # Cancel specific jobs
                job_uuids = [uuid.UUID(jid) for jid in job_ids]
                jobs_result = self.repository.get_jobs_by_ids(job_uuids, user_uuid)
            elif task_name:
                # Cancel all jobs with task name
                jobs_result = self.repository.get_cancellable_jobs_by_task(
                    user_uuid, 
                    task_name
                )
            else:
                return Err(JobError(
                    code="INVALID_REQUEST",
                    message="Must specify either job_ids or task_name"
                ))
            
            if jobs_result.is_err():
                return jobs_result
            
            jobs = jobs_result.unwrap()
            cancelled_jobs = []
            
            for job in jobs:
                if self._can_cancel_job(job):
                    # Revoke from queue
                    if job.celery_task_id:
                        self._revoke_queue_task(job.celery_task_id)
                    
                    # Update status
                    self._update_job_cancelled_status(job, reason)
                    cancelled_jobs.append(job)
            
            # Commit all changes
            self.repository.commit()
            
            # Emit bulk telemetry
            if cancelled_jobs:
                self._emit_bulk_cancellation_telemetry(cancelled_jobs, reason)
            
            logger.info(f"Bulk cancelled {len(cancelled_jobs)} jobs for user {user_id}")
            return Ok([JobOut.model_validate(job) for job in cancelled_jobs])
            
        except Exception as e:
            logger.error(f"Failed to bulk cancel jobs: {e}")
            return Err(JobError(
                code="BULK_CANCEL_FAILED",
                message=f"Failed to cancel jobs: {str(e)}"
            ))
    
    # Private methods
    
    def _can_cancel_job(self, job: Job) -> bool:
        """Check if job can be cancelled based on current status."""
        return job.status not in [
            JobStatus.SUCCEEDED,
            JobStatus.FAILED,
            JobStatus.CANCELLED
        ]
    
    def _revoke_queue_task(self, task_id: str) -> Result[bool, str]:
        """Revoke task from queue."""
        try:
            success = self.queue_publisher.cancel(task_id, terminate=False)
            if success:
                logger.info(f"Successfully revoked task {task_id}")
                return Ok(True)
            else:
                return Err(f"Queue reported failure to revoke task {task_id}")
        except Exception as e:
            return Err(f"Exception revoking task: {str(e)}")
    
    def _update_job_cancelled_status(
        self,
        job: Job,
        reason: Optional[str] = None
    ) -> Result[Job, JobError]:
        """Update job to cancelled status."""
        try:
            job.status = JobStatus.CANCELLED
            job.finished_at = datetime.now(timezone.utc)
            job.message = reason or "Job cancelled by user"
            job.updated_at = datetime.now(timezone.utc)
            
            self.repository.update(job)
            return Ok(job)
            
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            return Err(JobError(
                code="UPDATE_FAILED",
                message=f"Failed to update job status: {str(e)}"
            ))
    
    def _emit_cancellation_telemetry(self, job: Job, reason: Optional[str]):
        """Emit telemetry for job cancellation."""
        try:
            self.telemetry.emit_event(
                event_type="job.cancelled",
                data={
                    "job_id": str(job.id),
                    "user_id": str(job.user_id),
                    "task_name": job.task_name,
                    "reason": reason,
                    "cancelled_at": datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to emit cancellation telemetry: {e}")
    
    def _emit_bulk_cancellation_telemetry(
        self,
        jobs: List[Job],
        reason: Optional[str]
    ):
        """Emit telemetry for bulk cancellation."""
        try:
            self.telemetry.emit_event(
                event_type="jobs.bulk_cancelled",
                data={
                    "job_count": len(jobs),
                    "job_ids": [str(job.id) for job in jobs],
                    "user_id": str(jobs[0].user_id) if jobs else None,
                    "reason": reason,
                    "cancelled_at": datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to emit bulk cancellation telemetry: {e}")