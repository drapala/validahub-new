"""
Repository pattern for Job data access.
Isolates database operations from business logic.
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func

from ...models.job import Job, JobStatus, JobResult
from ...core.result import Result, Ok, Err, JobError

logger = logging.getLogger(__name__)


class JobRepository:
    """
    Repository for Job entities.
    
    This class encapsulates all database operations for jobs,
    following the Repository pattern to isolate data access.
    """
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create(self, job: Job) -> Result[Job, JobError]:
        """
        Create a new job in the database.
        
        Args:
            job: Job entity to create
            
        Returns:
            Result containing the created job or error
        """
        try:
            self.db.add(job)
            # Flush to database to get auto-generated ID and ensure constraints are validated
            # within the current transaction without committing
            self.db.flush()
            return Ok(job)
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            return Err(JobError.DATABASE_ERROR)
    
    def find_by_id(self, job_id: uuid.UUID) -> Result[Job, JobError]:
        """
        Find a job by ID.
        
        Args:
            job_id: Job UUID
            
        Returns:
            Result containing the job or NOT_FOUND error
        """
        try:
            job = self.db.query(Job).filter(Job.id == job_id).first()
            if job:
                return Ok(job)
            return Err(JobError.NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to find job {job_id}: {e}")
            return Err(JobError.DATABASE_ERROR)
    
    def find_by_id_and_user(
        self, 
        job_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> Result[Job, JobError]:
        """
        Find a job by ID and user ID (for authorization).
        
        Args:
            job_id: Job UUID
            user_id: User UUID
            
        Returns:
            Result containing the job or error
        """
        try:
            job = self.db.query(Job).filter(
                and_(
                    Job.id == job_id,
                    Job.user_id == user_id
                )
            ).first()
            
            if not job:
                # Check if job exists but belongs to another user
                other_job = self.db.query(Job).filter(Job.id == job_id).first()
                if other_job:
                    return Err(JobError.UNAUTHORIZED)
                return Err(JobError.NOT_FOUND)
            
            return Ok(job)
        except Exception as e:
            logger.error(f"Failed to find job {job_id} for user {user_id}: {e}")
            return Err(JobError.DATABASE_ERROR)
    
    def find_by_idempotency_key(
        self, 
        user_id: uuid.UUID,
        idempotency_key: str
    ) -> Optional[Job]:
        """
        Find a job by idempotency key.
        
        Args:
            user_id: User UUID
            idempotency_key: Idempotency key
            
        Returns:
            Job if found, None otherwise
        """
        try:
            return self.db.query(Job).filter(
                and_(
                    Job.user_id == user_id,
                    Job.idempotency_key == idempotency_key
                )
            ).first()
        except Exception as e:
            logger.error(f"Failed to find job by idempotency key: {e}")
            return None
    
    def list_by_user(
        self,
        user_id: uuid.UUID,
        status: Optional[JobStatus] = None,
        task_name: Optional[str] = None,
        queue: Optional[str] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> Result[List[Job], JobError]:
        """
        List jobs for a user with filters.
        
        Args:
            user_id: User UUID
            status: Optional status filter
            task_name: Optional task name filter
            queue: Optional queue filter
            created_after: Optional date filter
            created_before: Optional date filter
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Field to order by
            order_desc: Whether to order descending
            
        Returns:
            Result containing list of jobs or error
        """
        try:
            query = self.db.query(Job).filter(Job.user_id == user_id)
            
            # Apply filters
            if status:
                query = query.filter(Job.status == status)
            if task_name:
                query = query.filter(Job.task_name == task_name)
            if queue:
                query = query.filter(Job.queue == queue)
            if created_after:
                query = query.filter(Job.created_at >= created_after)
            if created_before:
                query = query.filter(Job.created_at <= created_before)
            
            # Apply ordering
            order_field = getattr(Job, order_by, Job.created_at)
            if order_desc:
                query = query.order_by(desc(order_field))
            else:
                query = query.order_by(asc(order_field))
            
            # Apply pagination
            jobs = query.offset(offset).limit(limit).all()
            
            return Ok(jobs)
        except Exception as e:
            logger.error(f"Failed to list jobs for user {user_id}: {e}")
            return Err(JobError.DATABASE_ERROR)
    
    def count_by_user(
        self,
        user_id: uuid.UUID,
        status: Optional[JobStatus] = None
    ) -> int:
        """
        Count jobs for a user.
        
        Args:
            user_id: User UUID
            status: Optional status filter
            
        Returns:
            Number of jobs
        """
        try:
            query = self.db.query(Job).filter(Job.user_id == user_id)
            if status:
                query = query.filter(Job.status == status)
            return query.count()
        except Exception as e:
            logger.error(f"Failed to count jobs: {e}")
            return 0
    
    def update(self, job: Job) -> Result[Job, JobError]:
        """
        Update a job in the database.
        
        Args:
            job: Job entity with updates
            
        Returns:
            Result containing updated job or error
        """
        try:
            # Flush changes to database within current transaction
            # This ensures changes are persisted without committing the transaction
            self.db.flush()
            return Ok(job)
        except Exception as e:
            logger.error(f"Failed to update job {job.id}: {e}")
            return Err(JobError.DATABASE_ERROR)
    
    def delete(self, job: Job) -> Result[bool, JobError]:
        """
        Delete a job from the database.
        
        Args:
            job: Job entity to delete
            
        Returns:
            Result containing success boolean or error
        """
        try:
            # Delete associated results first
            self.db.query(JobResult).filter(JobResult.job_id == job.id).delete()
            # Delete job
            self.db.delete(job)
            # Flush deletion to ensure it's applied within the transaction
            self.db.flush()
            return Ok(True)
        except Exception as e:
            logger.error(f"Failed to delete job {job.id}: {e}")
            return Err(JobError.DATABASE_ERROR)
    
    def delete_older_than(
        self,
        older_than: datetime,
        status_filter: Optional[List[JobStatus]] = None
    ) -> Result[int, JobError]:
        """
        Delete jobs older than a specific date.
        
        Args:
            older_than: Delete jobs created before this date
            status_filter: Optional list of statuses to filter
            
        Returns:
            Result containing number of deleted jobs or error
        """
        try:
            query = self.db.query(Job).filter(Job.created_at < older_than)
            
            if status_filter:
                query = query.filter(Job.status.in_(status_filter))
            
            # Count before deletion
            count = query.count()
            
            # Delete associated results
            for job in query.all():
                self.db.query(JobResult).filter(JobResult.job_id == job.id).delete()
            
            # Delete jobs
            query.delete()
            # Flush bulk deletion to apply changes within the transaction
            self.db.flush()
            
            return Ok(count)
        except Exception as e:
            logger.error(f"Failed to delete old jobs: {e}")
            return Err(JobError.DATABASE_ERROR)
    
    def find_result_by_job_id(self, job_id: uuid.UUID) -> Optional[JobResult]:
        """
        Find job result by job ID.
        
        Args:
            job_id: Job UUID
            
        Returns:
            JobResult if found, None otherwise
        """
        try:
            return self.db.query(JobResult).filter(
                JobResult.job_id == job_id
            ).first()
        except Exception as e:
            logger.error(f"Failed to find job result for job {job_id}: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get job statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            total = self.db.query(Job).count()
            
            # Count by status
            status_counts = dict(
                self.db.query(Job.status, func.count(Job.id))
                .group_by(Job.status)
                .all()
            )
            
            # Count by queue (active jobs only)
            queue_counts = dict(
                self.db.query(Job.queue, func.count(Job.id))
                .filter(Job.status.in_([JobStatus.QUEUED, JobStatus.RUNNING]))
                .group_by(Job.queue)
                .all()
            )
            
            # Count by task
            task_counts = dict(
                self.db.query(Job.task_name, func.count(Job.id))
                .group_by(Job.task_name)
                .all()
            )
            
            return {
                "total": total,
                "by_status": status_counts,
                "by_queue": queue_counts,
                "by_task": task_counts
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}