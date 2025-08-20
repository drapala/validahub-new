"""
Service responsible for job creation logic.
Follows Single Responsibility Principle.
"""

import uuid
import logging
from typing import Optional, Tuple
from datetime import datetime, timezone

from ..schemas.job import JobCreate, JobOut
from ..models.job import Job, JobStatus
from ..core.result import Result, Ok, Err, JobError
from ..core.validators.job_validator import JobValidator
from ..infrastructure.repositories.job_repository import JobRepository
from ..infrastructure.queue_publisher import QueuePublisher
from ..telemetry.job_telemetry import get_job_telemetry
from ..core.constants import (
    PARAM_MARKETPLACE,
    PARAM_CATEGORY,
    PARAM_REGION,
    DEFAULT_MARKETPLACE,
    DEFAULT_CATEGORY,
    DEFAULT_REGION,
    MAX_RETRY_COUNT
)

logger = logging.getLogger(__name__)


class JobCreationService:
    """
    Service responsible for creating jobs.
    
    This service handles:
    - Job validation
    - Idempotency checking
    - Job creation in database
    - Queue submission
    - Telemetry
    """
    
    def __init__(
        self,
        repository: JobRepository,
        validator: JobValidator,
        queue_publisher: QueuePublisher
    ):
        """
        Initialize service with dependencies.
        
        Args:
            repository: Job repository for data access
            validator: Job validator for business rules
            queue_publisher: Queue publisher for job submission
        """
        self.repository = repository
        self.validator = validator
        self.queue_publisher = queue_publisher
        self.telemetry = get_job_telemetry()
    
    def create_job(
        self,
        user_id: str,
        job_data: JobCreate,
        correlation_id: Optional[str] = None,
        prefer_representation: bool = False
    ) -> Result[Tuple[JobOut, bool], JobError]:
        """
        Create a new job with idempotency check.
        
        Args:
            user_id: User ID creating the job
            job_data: Job creation data
            correlation_id: Optional correlation ID for tracing
            prefer_representation: If True, return existing job on conflict
            
        Returns:
            Result containing (JobOut, is_new) or error
        """
        # Validate user ID format early
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            logger.warning(f"Invalid user ID format: {user_id}")
            return Err(JobError.VALIDATION_ERROR)
        
        # Validate job data
        validation_result = self.validator.validate_job_creation(job_data)
        if validation_result.is_err():
            return Err(validation_result.unwrap_err())
        
        # Check idempotency
        if job_data.idempotency_key:
            existing_result = self._handle_idempotency(
                user_uuid,
                job_data.idempotency_key,
                prefer_representation
            )
            if existing_result.is_ok():
                job_out, is_new = existing_result.unwrap()
                if not is_new:  # Found existing job
                    return Ok((job_out, False))
        
        # Get queue for plan
        queue = self.validator.get_queue_for_plan(job_data.plan)
        
        # Create job entity (pass validated UUID)
        job = self._create_job_entity(
            user_uuid=user_uuid,
            job_data=job_data,
            queue=queue,
            correlation_id=correlation_id
        )
        
        # Save to database
        save_result = self.repository.create(job)
        if save_result.is_err():
            return Err(save_result.unwrap_err())
        
        job = save_result.unwrap()
        
        # Submit to queue
        submit_result = self._submit_to_queue(job, job_data)
        if submit_result.is_err():
            # Update job status to failed
            job.status = JobStatus.FAILED
            job.error = "Failed to submit to queue"
            self.repository.update(job)
            return Err(submit_result.unwrap_err())
        
        # Update job with task ID
        task_id = submit_result.unwrap()
        job.celery_task_id = task_id
        update_result = self.repository.update(job)
        if update_result.is_err():
            logger.warning(f"Failed to update job {job.id} with task_id {task_id}")
        
        # Emit telemetry
        self._emit_job_created(job, job_data)
        
        return Ok((JobOut.model_validate(job), True))
    
    def _handle_idempotency(
        self,
        user_uuid: uuid.UUID,
        idempotency_key: str,
        prefer_representation: bool
    ) -> Result[Tuple[JobOut, bool], JobError]:
        """
        Handle idempotency check for job creation.
        
        Args:
            user_uuid: User UUID (already validated)
            idempotency_key: Idempotency key
            prefer_representation: Whether to return existing job
            
        Returns:
            Result with (JobOut, is_new) or None if no existing job
        """
        existing_job = self.repository.find_by_idempotency_key(
            user_uuid,
            idempotency_key
        )
        
        if not existing_job:
            return Err(JobError.NOT_FOUND)  # No existing job, continue creation
        
        # Check if we should return the existing job
        if prefer_representation:
            return Ok((JobOut.model_validate(existing_job), False))
        
        # Check job status
        if existing_job.status in [JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.RETRYING]:
            # Job is still processing, return conflict
            return Err(JobError.ALREADY_EXISTS)
        
        # Job is complete, return it
        return Ok((JobOut.model_validate(existing_job), False))
    
    def _create_job_entity(
        self,
        user_uuid: uuid.UUID,
        job_data: JobCreate,
        queue: str,
        correlation_id: Optional[str]
    ) -> Job:
        """
        Create a Job entity from creation data.
        
        Args:
            user_uuid: User UUID (already validated)
            job_data: Job creation data
            queue: Queue name
            correlation_id: Optional correlation ID
            
        Returns:
            Job entity
        """
        return Job(
            id=uuid.uuid4(),
            user_id=user_uuid,
            task_name=job_data.task,
            queue=queue,
            priority=job_data.priority,
            status=JobStatus.QUEUED,
            params_json=job_data.params,
            idempotency_key=job_data.idempotency_key,
            correlation_id=correlation_id or job_data.correlation_id,
            metadata=job_data.metadata or {},
            max_retries=MAX_RETRY_COUNT,
            retry_count=0,
            created_at=datetime.now(timezone.utc)
        )
    
    def _submit_to_queue(
        self,
        job: Job,
        job_data: JobCreate
    ) -> Result[str, JobError]:
        """
        Submit job to queue.
        
        Args:
            job: Job entity
            job_data: Job creation data
            
        Returns:
            Result with task ID or error
        """
        try:
            # Prepare job context
            job_context = {
                "job_id": str(job.id),
                "user_id": str(job.user_id),
                PARAM_MARKETPLACE: job_data.params.get(PARAM_MARKETPLACE, DEFAULT_MARKETPLACE),
                PARAM_CATEGORY: job_data.params.get(PARAM_CATEGORY, DEFAULT_CATEGORY),
                PARAM_REGION: job_data.params.get(PARAM_REGION, DEFAULT_REGION)
            }
            
            # Merge context with params
            task_payload = {**job_data.params, **job_context}
            
            # Publish to queue
            task_id = self.queue_publisher.publish(
                task_name=job_data.task,
                payload=task_payload,
                queue=job.queue,
                priority=job_data.priority,
                correlation_id=job.correlation_id
            )
            
            return Ok(task_id)
            
        except Exception as e:
            logger.error(f"Failed to submit job to queue: {e}")
            return Err(JobError.QUEUE_ERROR)
    
    def _emit_job_created(self, job: Job, job_data: JobCreate):
        """
        Emit telemetry for job creation.
        
        Args:
            job: Created job
            job_data: Job creation data
        """
        try:
            self.telemetry.emit_job_queued(
                job_id=str(job.id),
                task_name=job_data.task,
                params=job_data.params,
                queue=job.queue,
                priority=job_data.priority,
                correlation_id=job.correlation_id
            )
        except Exception as e:
            logger.warning(f"Failed to emit telemetry: {e}")