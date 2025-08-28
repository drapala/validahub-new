"""
Service responsible for job status synchronization.
Follows Single Responsibility Principle.
"""

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from src.core.logging_config import get_logger
from src.models.job import Job, JobStatus
from src.core.result import Result, Ok, Err
from src.infrastructure.repositories.job_repository import JobRepository
from src.infrastructure.queue_publisher import QueuePublisher
from src.telemetry.telemetry_service import TelemetryService

logger = get_logger(__name__)


class JobStatusSyncService:
    """
    Service responsible for synchronizing job status with queue backend.
    
    This service handles:
    - Fetching status from queue backend
    - Updating job status in database
    - Handling status transitions
    - Status sync telemetry
    """
    
    # Status mapping from queue backend to JobStatus enum
    STATUS_MAP = {
        'queued': JobStatus.PENDING,
        'pending': JobStatus.PENDING,
        'processing': JobStatus.PROCESSING,
        'running': JobStatus.PROCESSING,
        'completed': JobStatus.SUCCESS,
        'success': JobStatus.SUCCESS,
        'failed': JobStatus.FAILED,
        'error': JobStatus.FAILED,
        'cancelled': JobStatus.CANCELLED,
        'revoked': JobStatus.CANCELLED,
        'retrying': JobStatus.PROCESSING,
        'retry': JobStatus.PROCESSING,
        'review': JobStatus.REVIEW
    }
    
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
            queue_publisher: Queue publisher for status queries
            telemetry: Optional telemetry service
        """
        self.repository = repository
        self.queue_publisher = queue_publisher
        self.telemetry = telemetry or TelemetryService()
    
    def sync_job_status(self, job: Job) -> Result[bool, str]:
        """
        Sync a single job's status with queue backend.
        
        Args:
            job: Job to sync
            
        Returns:
            Result with True if synced and updated, False if no change
        """
        try:
            # Skip if no queue task ID
            if not job.celery_task_id:
                return Ok(False)
            
            # Skip if job is in terminal state
            if self._is_terminal_state(job.status):
                return Ok(False)
            
            # Fetch status from queue
            status_result = self._fetch_queue_status(job.celery_task_id)
            if status_result.is_err():
                return status_result
            
            status_info = status_result.unwrap()
            if not status_info:
                # Task not found or no update needed
                return Ok(False)
            
            # Update job if status changed
            updated = self._update_job_from_status(job, status_info)
            if updated:
                self.repository.update(job)
                self._emit_sync_telemetry(job, status_info)
                logger.info(f"Synced job {job.id} status to {job.status.value}")
            
            return Ok(updated)
            
        except Exception as e:
            logger.error(f"Failed to sync job status: {e}")
            return Err(f"Status sync failed: {str(e)}")
    
    def sync_multiple_jobs(self, jobs: List[Job]) -> Result[Dict[str, bool], str]:
        """
        Sync status for multiple jobs.
        
        Args:
            jobs: List of jobs to sync
            
        Returns:
            Result with dict mapping job_id to sync result
        """
        try:
            results = {}
            
            for job in jobs:
                if self._should_sync_job(job):
                    sync_result = self.sync_job_status(job)
                    results[str(job.id)] = sync_result.unwrap_or(False)
                else:
                    results[str(job.id)] = False
            
            # Commit all updates at once
            self.repository.commit()
            
            synced_count = sum(1 for v in results.values() if v)
            logger.info(f"Synced {synced_count}/{len(jobs)} jobs")
            
            return Ok(results)
            
        except Exception as e:
            logger.error(f"Failed to sync multiple jobs: {e}")
            return Err(f"Batch sync failed: {str(e)}")
    
    def sync_user_active_jobs(self, user_id: str) -> Result[int, str]:
        """
        Sync all active jobs for a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            Result with count of synced jobs
        """
        try:
            user_uuid = uuid.UUID(user_id)
            
            # Get all active jobs for user
            active_jobs_result = self.repository.get_active_jobs_for_user(user_uuid)
            if active_jobs_result.is_err():
                return Err(f"Failed to get active jobs: {active_jobs_result.err()}")
            
            active_jobs = active_jobs_result.unwrap()
            if not active_jobs:
                return Ok(0)
            
            # Sync all active jobs
            sync_result = self.sync_multiple_jobs(active_jobs)
            if sync_result.is_err():
                return sync_result.map(lambda _: 0)
            
            results = sync_result.unwrap()
            synced_count = sum(1 for v in results.values() if v)
            
            return Ok(synced_count)
            
        except Exception as e:
            logger.error(f"Failed to sync user active jobs: {e}")
            return Err(f"User jobs sync failed: {str(e)}")
    
    def update_job_status_from_task(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        result_ref: Optional[str] = None,
        retry_count: Optional[int] = None
    ) -> Result[Job, str]:
        """
        Update job status from Celery task signals.
        
        This is called by Celery signal handlers to update job status.
        
        Args:
            job_id: Job UUID
            status: New status
            progress: Optional progress percentage
            message: Optional status message
            error: Optional error message
            result_ref: Optional result reference
            retry_count: Optional retry count
            
        Returns:
            Result with updated job
        """
        try:
            job_uuid = uuid.UUID(job_id)
            
            # Get job
            job_result = self.repository.get_by_id(job_uuid)
            if job_result.is_err():
                logger.warning(f"Job {job_id} not found for status update")
                return job_result
            
            job = job_result.unwrap()
            old_status = job.status
            
            # Update job fields
            job.status = status
            
            if progress is not None:
                job.progress = min(100.0, max(0.0, progress))
            
            if message:
                job.message = message
            
            if error:
                job.error = error
            
            if result_ref:
                job.result_ref = result_ref
            
            if retry_count is not None:
                job.retry_count = retry_count
            
            # Update timestamps based on status
            if status == JobStatus.RUNNING and not job.started_at:
                job.started_at = datetime.now(timezone.utc)
            
            if self._is_terminal_state(status) and not job.finished_at:
                job.finished_at = datetime.now(timezone.utc)
            
            job.updated_at = datetime.now(timezone.utc)
            
            # Save changes
            self.repository.update(job)
            self.repository.commit()
            
            # Emit telemetry for status change
            if old_status != status:
                self._emit_status_change_telemetry(job, old_status)
            
            logger.info(f"Updated job {job_id} status from {old_status.value} to {status.value}")
            return Ok(job)
            
        except Exception as e:
            logger.error(f"Failed to update job status from task: {e}")
            return Err(f"Status update failed: {str(e)}")
    
    # Private methods
    
    def _should_sync_job(self, job: Job) -> bool:
        """Check if job should be synced."""
        return (
            job.celery_task_id is not None and
            not self._is_terminal_state(job.status)
        )
    
    def _is_terminal_state(self, status: JobStatus) -> bool:
        """Check if status is terminal (no further transitions expected)."""
        return status in [
            JobStatus.SUCCEEDED,
            JobStatus.FAILED,
            JobStatus.CANCELLED
        ]
    
    def _fetch_queue_status(self, task_id: str) -> Result[Optional[Dict[str, Any]], str]:
        """Fetch status info from queue backend."""
        try:
            status_info = self.queue_publisher.get_status(task_id)
            return Ok(status_info)
        except Exception as e:
            return Err(f"Failed to fetch queue status: {str(e)}")
    
    def _update_job_from_status(self, job: Job, status_info: Dict[str, Any]) -> bool:
        """
        Update job fields from queue status info.
        
        Returns:
            True if job was modified, False otherwise
        """
        modified = False
        
        # Update status
        if 'status' in status_info:
            new_status = self.STATUS_MAP.get(
                status_info['status'].lower(),
                None
            )
            if new_status and new_status != job.status:
                job.status = new_status
                modified = True
                
                # Set progress to 100 if succeeded
                if new_status == JobStatus.SUCCEEDED:
                    job.progress = 100.0
        
        # Update progress
        if 'progress' in status_info and status_info['progress'] is not None:
            new_progress = float(status_info['progress'])
            if new_progress != job.progress:
                job.progress = new_progress
                modified = True
        
        # Update message
        if 'message' in status_info and status_info['message']:
            if status_info['message'] != job.message:
                job.message = status_info['message']
                modified = True
        
        # Update error
        if 'error' in status_info and status_info['error']:
            if status_info['error'] != job.error:
                job.error = status_info['error']
                modified = True
        
        # Update result reference
        if 'result' in status_info and status_info['result']:
            if isinstance(status_info['result'], dict):
                result_ref = status_info['result'].get('ref')
                if result_ref and result_ref != job.result_ref:
                    job.result_ref = result_ref
                    modified = True
        
        # Update timestamps
        if modified:
            job.updated_at = datetime.now(timezone.utc)
            
            if job.status == JobStatus.RUNNING and not job.started_at:
                job.started_at = datetime.now(timezone.utc)
            
            if self._is_terminal_state(job.status) and not job.finished_at:
                job.finished_at = datetime.now(timezone.utc)
        
        return modified
    
    def _emit_sync_telemetry(self, job: Job, status_info: Dict[str, Any]):
        """Emit telemetry for status sync."""
        try:
            self.telemetry.emit_event(
                event_type="job.status_synced",
                data={
                    "job_id": str(job.id),
                    "status": job.status.value,
                    "queue_status": status_info.get('status'),
                    "progress": job.progress,
                    "synced_at": datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to emit sync telemetry: {e}")
    
    def _emit_status_change_telemetry(self, job: Job, old_status: JobStatus):
        """Emit telemetry for status change."""
        try:
            self.telemetry.emit_event(
                event_type="job.status_changed",
                data={
                    "job_id": str(job.id),
                    "user_id": str(job.user_id),
                    "task_name": job.task_name,
                    "old_status": old_status.value,
                    "new_status": job.status.value,
                    "changed_at": datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to emit status change telemetry: {e}")