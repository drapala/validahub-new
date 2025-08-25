"""
Service responsible for job idempotency management.
Follows Single Responsibility Principle.
"""

import uuid
from typing import Optional, Tuple
from datetime import datetime, timezone, timedelta

from core.logging_config import get_logger
from models.job import Job, JobStatus
from schemas.job import JobOut
from core.result import Result, Ok, Err, JobError
from infrastructure.repositories.job_repository import JobRepository
from telemetry.telemetry_service import TelemetryService

logger = get_logger(__name__)


class JobIdempotencyService:
    """
    Service responsible for managing job idempotency.
    
    This service handles:
    - Checking for duplicate jobs
    - Managing idempotency keys
    - Handling idempotency conflicts
    - Cleaning up expired idempotency keys
    """
    
    # Default idempotency key expiration (24 hours)
    DEFAULT_IDEMPOTENCY_TTL = timedelta(hours=24)
    
    def __init__(
        self,
        repository: JobRepository,
        telemetry: Optional[TelemetryService] = None,
        idempotency_ttl: Optional[timedelta] = None
    ):
        """
        Initialize service with dependencies.
        
        Args:
            repository: Job repository for data access
            telemetry: Optional telemetry service
            idempotency_ttl: TTL for idempotency keys
        """
        self.repository = repository
        self.telemetry = telemetry or TelemetryService()
        self.idempotency_ttl = idempotency_ttl or self.DEFAULT_IDEMPOTENCY_TTL
    
    def check_idempotency(
        self,
        user_id: str,
        idempotency_key: str,
        prefer_representation: bool = False
    ) -> Result[Optional[Tuple[JobOut, bool]], JobError]:
        """
        Check if a job with the given idempotency key already exists.
        
        Args:
            user_id: User UUID
            idempotency_key: Idempotency key to check
            prefer_representation: If True, return existing job even if in progress
            
        Returns:
            Result with:
            - None if no existing job found (new job can be created)
            - Tuple of (JobOut, False) if existing job found and should be returned
            - Error if conflict and prefer_representation is False
        """
        try:
            # Validate inputs
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                return Err(JobError(
                    code="INVALID_USER_ID",
                    message="Invalid user ID format"
                ))
            
            # Look for existing job with this idempotency key
            existing_job_result = self.repository.find_by_idempotency_key(
                user_uuid,
                idempotency_key
            )
            
            if existing_job_result.is_err():
                # No existing job found
                return Ok(None)
            
            existing_job = existing_job_result.unwrap()
            
            # Check if idempotency key has expired
            if self._is_idempotency_expired(existing_job):
                logger.info(f"Idempotency key expired for job {existing_job.id}")
                # Mark as expired and allow new job creation
                self._mark_idempotency_expired(existing_job)
                return Ok(None)
            
            # Handle based on prefer_representation flag
            if prefer_representation:
                # Return existing job regardless of state
                logger.info(f"Returning existing job {existing_job.id} for idempotency key")
                self._emit_idempotency_hit_telemetry(existing_job)
                return Ok((JobOut.model_validate(existing_job), False))
            
            # Check if job is in terminal state
            if self._is_terminal_state(existing_job.status):
                # Return existing completed job
                logger.info(f"Returning completed job {existing_job.id} for idempotency key")
                self._emit_idempotency_hit_telemetry(existing_job)
                return Ok((JobOut.model_validate(existing_job), False))
            
            # Job is still in progress - this is a conflict
            return Err(JobError(
                code="IDEMPOTENCY_CONFLICT",
                message=f"Job with idempotency_key already exists and is {existing_job.status.value}",
                details={
                    "existing_job_id": str(existing_job.id),
                    "status": existing_job.status.value
                }
            ))
            
        except Exception as e:
            logger.error(f"Failed to check idempotency: {e}")
            return Err(JobError(
                code="IDEMPOTENCY_CHECK_FAILED",
                message=f"Failed to check idempotency: {str(e)}"
            ))
    
    def reserve_idempotency_key(
        self,
        user_id: str,
        idempotency_key: str,
        task_name: str
    ) -> Result[str, JobError]:
        """
        Reserve an idempotency key for a new job.
        
        This creates a placeholder job to prevent race conditions.
        
        Args:
            user_id: User UUID
            idempotency_key: Idempotency key to reserve
            task_name: Task name for the job
            
        Returns:
            Result with job ID if reserved successfully
        """
        try:
            user_uuid = uuid.UUID(user_id)
            
            # Create placeholder job to reserve the key
            placeholder_job = Job(
                id=uuid.uuid4(),
                user_id=user_uuid,
                task_name=task_name,
                status=JobStatus.PENDING,  # Special status for reservation
                idempotency_key=idempotency_key,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Try to insert with idempotency key as unique constraint
            insert_result = self.repository.create_with_idempotency(placeholder_job)
            if insert_result.is_err():
                return Err(JobError(
                    code="RESERVATION_FAILED",
                    message="Failed to reserve idempotency key - already exists"
                ))
            
            logger.info(f"Reserved idempotency key for job {placeholder_job.id}")
            return Ok(str(placeholder_job.id))
            
        except Exception as e:
            logger.error(f"Failed to reserve idempotency key: {e}")
            return Err(JobError(
                code="RESERVATION_ERROR",
                message=f"Failed to reserve idempotency key: {str(e)}"
            ))
    
    def cleanup_expired_keys(
        self,
        batch_size: int = 100
    ) -> Result[int, str]:
        """
        Clean up expired idempotency keys.
        
        This should be run periodically to remove old idempotency constraints.
        
        Args:
            batch_size: Number of records to process at once
            
        Returns:
            Result with count of cleaned keys
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - self.idempotency_ttl
            
            # Find jobs with expired idempotency keys
            expired_jobs_result = self.repository.find_jobs_with_expired_idempotency(
                cutoff_time,
                batch_size
            )
            
            if expired_jobs_result.is_err():
                return Err(f"Failed to find expired jobs: {expired_jobs_result.err()}")
            
            expired_jobs = expired_jobs_result.unwrap()
            cleaned_count = 0
            
            for job in expired_jobs:
                # Clear idempotency key
                job.idempotency_key = None
                job.metadata = job.metadata or {}
                job.metadata['idempotency_expired_at'] = datetime.now(timezone.utc).isoformat()
                self.repository.update(job)
                cleaned_count += 1
            
            if cleaned_count > 0:
                self.repository.commit()
                logger.info(f"Cleaned {cleaned_count} expired idempotency keys")
                self._emit_cleanup_telemetry(cleaned_count)
            
            return Ok(cleaned_count)
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired keys: {e}")
            return Err(f"Cleanup failed: {str(e)}")
    
    def validate_idempotency_key(self, key: str) -> Result[bool, str]:
        """
        Validate idempotency key format and constraints.
        
        Args:
            key: Idempotency key to validate
            
        Returns:
            Result with True if valid
        """
        # Check length
        if len(key) < 8:
            return Err("Idempotency key must be at least 8 characters")
        
        if len(key) > 255:
            return Err("Idempotency key must not exceed 255 characters")
        
        # Check for valid characters (alphanumeric, dash, underscore)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', key):
            return Err("Idempotency key must contain only alphanumeric characters, dashes, and underscores")
        
        return Ok(True)
    
    # Private methods
    
    def _is_terminal_state(self, status: JobStatus) -> bool:
        """Check if status is terminal."""
        return status in [
            JobStatus.SUCCEEDED,
            JobStatus.FAILED,
            JobStatus.CANCELLED
        ]
    
    def _is_idempotency_expired(self, job: Job) -> bool:
        """Check if job's idempotency key has expired."""
        if not job.created_at:
            return False
        
        age = datetime.now(timezone.utc) - job.created_at
        return age > self.idempotency_ttl
    
    def _mark_idempotency_expired(self, job: Job):
        """Mark job's idempotency as expired."""
        try:
            job.metadata = job.metadata or {}
            job.metadata['idempotency_expired'] = True
            job.metadata['expired_at'] = datetime.now(timezone.utc).isoformat()
            self.repository.update(job)
            self.repository.commit()
        except Exception as e:
            logger.warning(f"Failed to mark idempotency as expired: {e}")
    
    def _emit_idempotency_hit_telemetry(self, job: Job):
        """Emit telemetry for idempotency cache hit."""
        try:
            self.telemetry.emit_event(
                event_type="job.idempotency_hit",
                data={
                    "job_id": str(job.id),
                    "user_id": str(job.user_id),
                    "task_name": job.task_name,
                    "status": job.status.value,
                    "age_seconds": (
                        datetime.now(timezone.utc) - job.created_at
                    ).total_seconds() if job.created_at else 0
                }
            )
        except Exception as e:
            logger.warning(f"Failed to emit idempotency telemetry: {e}")
    
    def _emit_cleanup_telemetry(self, cleaned_count: int):
        """Emit telemetry for idempotency cleanup."""
        try:
            self.telemetry.emit_event(
                event_type="idempotency.cleanup",
                data={
                    "cleaned_count": cleaned_count,
                    "ttl_hours": self.idempotency_ttl.total_seconds() / 3600,
                    "cleaned_at": datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to emit cleanup telemetry: {e}")