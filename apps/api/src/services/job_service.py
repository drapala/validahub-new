"""
Job service with idempotency and CRUD operations.
"""

import uuid
from src.core.logging_config import get_logger
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import HTTPException, status

from src.models.job import Job, JobStatus
from src.schemas.job import (
    JobCreate, JobOut, JobResultOut, JobListQuery, 
    JobListResponse, JobStatusUpdate, JobPlan
)
from src.infrastructure.queue_publisher import QueuePublisher
from src.infrastructure.queue_factory import get_queue_publisher
from src.telemetry.job_telemetry import get_job_telemetry
from src.core.config import ValidationConfig

logger = get_logger(__name__)


class JobService:
    """Service for managing asynchronous jobs with idempotency."""
    
    def __init__(self, db: Session, queue_publisher: Optional[QueuePublisher] = None):
        self.db = db
        self.queue_publisher = queue_publisher or get_queue_publisher()
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
        
        Args:
            user_id: User ID creating the job
            job_data: Job creation data
            correlation_id: Optional correlation ID from request
            prefer_representation: If True, return existing job on conflict
            
        Returns:
            Tuple of (JobOut, is_new) where is_new indicates if job was created
        """
        
        # Validate task name before any database operations
        self._validate_task_name(job_data.task)
        
        # Validate ruleset if it's a CSV validation/correction task
        if job_data.task in ["validate_csv_job", "correct_csv_job"]:
            ruleset = job_data.params.get("ruleset", "default")
            if not ValidationConfig.is_valid_ruleset(ruleset):
                allowed_rulesets = ValidationConfig.get_allowed_rulesets()
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid ruleset '{ruleset}'. Allowed values are: {allowed_rulesets}"
                )
        
        # Check idempotency if key provided
        idempotency_result = self._handle_idempotency_check(
            user_id=user_id,
            idempotency_key=job_data.idempotency_key,
            prefer_representation=prefer_representation
        )
        if idempotency_result is not None:
            return idempotency_result
        
        # Map plan to queue
        queue = self._get_queue_for_plan(job_data.plan)
        
        # Create new job
        job = Job(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            task_name=job_data.task,
            queue=queue,
            priority=job_data.priority,
            status=JobStatus.QUEUED,
            params_json=job_data.params,
            idempotency_key=job_data.idempotency_key,
            correlation_id=correlation_id or job_data.correlation_id,
            metadata=job_data.metadata or {},
            max_retries=3
        )
        
        self.db.add(job)
        self.db.flush()  # Get the ID before committing
        
        # Emit job.queued event for queue wait time tracking
        self.telemetry.emit_job_queued(
            job_id=str(job.id),
            task_name=job_data.task,
            params=job_data.params,
            queue=queue,
            priority=job_data.priority,
            correlation_id=job.correlation_id
        )
        
        # Submit to queue via publisher
        try:
            
            # Prepare job context for task
            job_context = {
                "job_id": str(job.id),
                "user_id": str(user_id),
                "marketplace": job_data.params.get("marketplace", "unknown"),
                "category": job_data.params.get("category", "unknown"),
                "region": job_data.params.get("region", "default")
            }
            
            # Merge context with params
            task_payload = {**job_data.params, **job_context}
            
            # Publish to queue
            task_id = self.queue_publisher.publish(
                task_name=job_data.task,
                payload=task_payload,
                queue=queue,
                priority=job_data.priority,
                correlation_id=job.correlation_id
            )
            
            # Store task ID for tracking
            job.celery_task_id = task_id
            
        except Exception as e:
            logger.error(f"Failed to submit job to queue: {e}")
            job.status = JobStatus.FAILED
            job.error = f"Failed to queue job: {e}"
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to queue job: {e}"
            )
        
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(f"Created job {job.id} for user {user_id}, task {job_data.task}")
        
        return JobOut.model_validate(job), True
    
    def get_job(self, job_id: str, user_id: str) -> JobOut:
        """
        Get job by ID.
        
        Args:
            job_id: Job UUID
            user_id: User ID for authorization
            
        Returns:
            Job details
        """
        
        job = self.db.query(Job).filter(
            and_(
                Job.id == uuid.UUID(job_id),
                Job.user_id == uuid.UUID(user_id)
            )
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Update status from Celery if running
        if job.status in [JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.RETRYING]:
            self._sync_job_status(job)
        
        return JobOut.model_validate(job)
    
    def get_job_result(self, job_id: str, user_id: str) -> JobResultOut:
        """
        Get job result.
        
        Args:
            job_id: Job UUID
            user_id: User ID for authorization
            
        Returns:
            Job result details
        """
        
        job = self.db.query(Job).filter(
            and_(
                Job.id == uuid.UUID(job_id),
                Job.user_id == uuid.UUID(user_id)
            )
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        if job.status != JobStatus.SUCCEEDED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Job is {job.status.value}, not succeeded"
            )
        
        # Check if we have a separate result record
        job_result = self.db.query(JobResult).filter(
            JobResult.job_id == job.id
        ).first()
        
        if job_result:
            return JobResultOut(
                job_id=job.id,
                status=job.status,
                result_ref=job.result_ref,
                result_json=job_result.result_json,
                object_uri=job_result.object_uri,
                size_bytes=job_result.size_bytes,
                finished_at=job.finished_at
            )
        else:
            # Return inline result
            return JobResultOut(
                job_id=job.id,
                status=job.status,
                result_ref=job.result_ref,
                finished_at=job.finished_at
            )
    
    def cancel_job(self, job_id: str, user_id: str) -> JobOut:
        """
        Cancel a job (best effort).
        
        Args:
            job_id: Job UUID
            user_id: User ID for authorization
            
        Returns:
            Updated job details
        """
        
        job = self.db.query(Job).filter(
            and_(
                Job.id == uuid.UUID(job_id),
                Job.user_id == uuid.UUID(user_id)
            )
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        if job.status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot cancel job in {job.status.value} state"
            )
        
        # Try to cancel task in queue
        if job.celery_task_id:
            try:
                queue_publisher = get_queue_publisher()
                success = queue_publisher.cancel(job.celery_task_id, terminate=False)
                if success:
                    logger.info(f"Revoked task {job.celery_task_id}")
                else:
                    logger.warning(f"Failed to revoke task {job.celery_task_id}")
            except Exception as e:
                logger.error(f"Failed to revoke task: {e}")
        
        # Update job status
        job.status = JobStatus.CANCELLED
        job.finished_at = datetime.utcnow()
        job.message = "Job cancelled by user"
        
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(f"Cancelled job {job.id} for user {user_id}")
        
        return JobOut.model_validate(job)
    
    def list_jobs(
        self,
        user_id: str,
        query: JobListQuery
    ) -> JobListResponse:
        """
        List jobs for a user with filtering and pagination.
        
        Args:
            user_id: User ID
            query: Query parameters
            
        Returns:
            Paginated job list
        """
        
        # Build base query
        q = self.db.query(Job).filter(Job.user_id == uuid.UUID(user_id))
        
        # Apply filters
        if query.status:
            q = q.filter(Job.status == query.status)
        
        if query.task_name:
            q = q.filter(Job.task_name == query.task_name)
        
        if query.created_after:
            q = q.filter(Job.created_at >= query.created_after)
        
        if query.created_before:
            q = q.filter(Job.created_at <= query.created_before)
        
        # Get total count
        total = q.count()
        
        # Apply ordering
        if query.order_by == "created_at_desc":
            q = q.order_by(desc(Job.created_at))
        elif query.order_by == "created_at_asc":
            q = q.order_by(Job.created_at)
        
        # Apply pagination
        jobs = q.offset(query.offset).limit(query.limit).all()
        
        # Sync status for active jobs
        for job in jobs:
            if job.status in [JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.RETRYING]:
                self._sync_job_status(job)
        
        return JobListResponse(
            jobs=[JobOut.model_validate(job) for job in jobs],
            total=total,
            limit=query.limit,
            offset=query.offset,
            has_more=(query.offset + query.limit) < total
        )
    
    def update_job_status(
        self,
        job_id: str,
        status_update: JobStatusUpdate
    ) -> None:
        """
        Internal method to update job status (called by Celery signals).
        
        Args:
            job_id: Job UUID
            status_update: Status update data
        """
        
        job = self.db.query(Job).filter(Job.id == uuid.UUID(job_id)).first()
        
        if not job:
            logger.warning(f"Job {job_id} not found for status update")
            return
        
        # Update fields
        job.status = status_update.status
        
        if status_update.progress is not None:
            job.progress = status_update.progress
        
        if status_update.message:
            job.message = status_update.message
        
        if status_update.error:
            job.error = status_update.error
        
        if status_update.result_ref:
            job.result_ref = status_update.result_ref
        
        if status_update.started_at:
            job.started_at = status_update.started_at
        
        if status_update.finished_at:
            job.finished_at = status_update.finished_at
        
        if status_update.retry_count is not None:
            job.retry_count = status_update.retry_count
        
        job.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Updated job {job_id} status to {status_update.status}")
    
    # Private methods
    
    def _check_idempotency(
        self,
        user_id: str,
        idempotency_key: str
    ) -> Optional[Job]:
        """Check if job with idempotency key exists."""
        
        return self.db.query(Job).filter(
            and_(
                Job.user_id == uuid.UUID(user_id),
                Job.idempotency_key == idempotency_key
            )
        ).first()
    
    def _handle_idempotency_check(
        self,
        user_id: str,
        idempotency_key: Optional[str],
        prefer_representation: bool
    ) -> Optional[Tuple[JobOut, bool]]:
        """Handle idempotency check and return result if job exists."""
        
        if not idempotency_key:
            return None
        
        existing_job = self._check_idempotency(user_id, idempotency_key)
        
        if existing_job:
            # Job already exists
            if not prefer_representation and not existing_job.is_terminal:
                # Conflict - job still in progress
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Job with idempotency_key already exists and is {existing_job.status.value}"
                )
            
            # Return existing job
            return JobOut.model_validate(existing_job), False
        
        return None
    
    def _get_queue_for_plan(self, plan: JobPlan) -> str:
        """Map user plan to queue name."""
        
        return {
            JobPlan.FREE: "queue:free",
            JobPlan.PRO: "queue:pro",
            JobPlan.BUSINESS: "queue:business",
            JobPlan.ENTERPRISE: "queue:enterprise"
        }.get(plan, "queue:free")
    
    def _validate_task_name(self, task_name: str) -> None:
        """Validate that task name is supported."""
        
        supported_tasks = [
            "validate_csv_job",
            "correct_csv_job",
            "sync_connector_job",
            "generate_report_job"
        ]
        
        if task_name not in supported_tasks:
            raise ValueError(f"Unknown task: {task_name}")
    
    def _sync_job_status(self, job: Job) -> bool:
        """
        Sync job status with the queue backend.
        
        Fetches current status from queue backend and updates job's status, progress,
        message, and error fields. Maps queue status to JobStatus enum values.
        
        Returns:
            True if sync succeeded and DB was updated, False if error or no action taken.
        """
        
        if not job.celery_task_id:
            return False
        
        try:
            queue_publisher = get_queue_publisher()
            status_info = queue_publisher.get_status(job.celery_task_id)
            
            if status_info is None:
                # Task not found or still pending
                return False
            
            # Map queue status to JobStatus
            status_map = {
                'queued': JobStatus.QUEUED,
                'processing': JobStatus.RUNNING,
                'completed': JobStatus.SUCCEEDED,
                'failed': JobStatus.FAILED,
                'cancelled': JobStatus.CANCELLED,
                'retrying': JobStatus.RETRYING
            }
            
            if 'status' in status_info:
                new_status = status_map.get(status_info['status'])
                if new_status:
                    job.status = new_status
                    if new_status == JobStatus.SUCCEEDED:
                        job.progress = 100.0
            
            if 'progress' in status_info and status_info['progress'] is not None:
                job.progress = float(status_info['progress'])
            
            if 'message' in status_info and status_info['message']:
                job.message = status_info['message']
            
            if 'error' in status_info and status_info['error']:
                job.error = status_info['error']
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync job status from queue backend: {e}")
            return False