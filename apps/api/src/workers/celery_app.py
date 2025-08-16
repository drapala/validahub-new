"""
Celery application configuration and factory.
"""

import os
from celery import Celery, Task, signals
from celery.signals import task_prerun, task_postrun, task_failure, task_retry
from datetime import datetime
import logging
from typing import Any, Dict
import uuid

from src.db.base import SessionLocal
from src.models.job import Job, JobStatus
from src.config import settings
from src.config.queue_config import get_queue_config
from src.telemetry.job_telemetry import get_job_telemetry

logger = logging.getLogger(__name__)

# Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", settings.database_url)


def create_celery_app() -> Celery:
    """Create and configure Celery application."""
    
    celery_app = Celery(
        "validahub",
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=["src.workers.tasks"]
    )
    
    # Load external queue configuration
    queue_config = get_queue_config()
    task_routes = queue_config.get_celery_task_routes()
    
    # Add full task names to routes
    full_task_routes = {}
    for task_name, route in task_routes.items():
        full_task_name = f"src.workers.tasks.{task_name}"
        full_task_routes[full_task_name] = route
    
    # Celery configuration
    celery_app.conf.update(
        # Serialization
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        
        # Task execution
        task_track_started=True,
        task_time_limit=300,  # 5 minutes hard limit
        task_soft_time_limit=270,  # 4.5 minutes soft limit
        task_acks_late=True,
        worker_prefetch_multiplier=1,  # Fair processing
        
        # Retry configuration
        task_retry_max=3,
        task_retry_backoff=2,  # Exponential backoff
        task_retry_backoff_max=600,  # Max 10 minutes
        task_retry_jitter=True,
        
        # Result backend
        result_expires=86400,  # 24 hours
        result_persistent=True,
        
        # Queue routing from external config
        task_routes=full_task_routes,
        
        # Queue configuration
        task_default_queue=queue_config.get_queue_name("default"),
        task_queues={
            "queue:free": {
                "routing_key": "free.#",
                "priority": 1,
            },
            "queue:pro": {
                "routing_key": "pro.#",
                "priority": 5,
            },
            "queue:business": {
                "routing_key": "business.#",
                "priority": 7,
            },
            "queue:enterprise": {
                "routing_key": "enterprise.#",
                "priority": 10,
            },
        },
    )
    
    return celery_app


# Create the Celery app instance
celery_app = create_celery_app()


class DatabaseTask(Task):
    """Base task with database session management."""
    
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


# Signal handlers for job status updates
@task_prerun.connect
def task_prerun_handler(task_id, task, args, kwargs, **kw):
    """Update job status when task starts."""
    try:
        db = SessionLocal()
        job = db.query(Job).filter(Job.celery_task_id == task_id).first()
        
        if job:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            job.message = "Task started"
            db.commit()
            logger.info(f"Job {job.id} started (task_id: {task_id})")
            
            # Emit telemetry event
            if len(args) >= 2:
                job_id = args[0]
                params = args[1] if isinstance(args[1], dict) else {}
                telemetry = get_job_telemetry()
                telemetry.emit_job_started(
                    job_id=job_id,
                    task_name=task.name.split('.')[-1],
                    params=params,
                    correlation_id=job.correlation_id
                )
        
        db.close()
    except Exception as e:
        logger.error(f"Error updating job status on task_prerun: {e}")


@task_postrun.connect
def task_postrun_handler(task_id, task, args, kwargs, retval, state, **kw):
    """Update job status when task completes."""
    try:
        db = SessionLocal()
        job = db.query(Job).filter(Job.celery_task_id == task_id).first()
        
        if job:
            if state == "SUCCESS":
                job.status = JobStatus.SUCCEEDED
                job.progress = 100.0
                job.message = "Task completed successfully"
                
                # Store result reference if returned
                if isinstance(retval, dict) and "result_ref" in retval:
                    job.result_ref = retval["result_ref"]
                    
                # Emit telemetry event
                if len(args) >= 2:
                    job_id = args[0]
                    telemetry = get_job_telemetry()
                    metrics = retval.get("metrics") if isinstance(retval, dict) else None
                    telemetry.emit_job_completed(
                        job_id=job_id,
                        task_name=task.name.split('.')[-1],
                        result=retval if isinstance(retval, dict) else {"status": "success"},
                        metrics=metrics,
                        correlation_id=job.correlation_id
                    )
            
            job.finished_at = datetime.utcnow()
            db.commit()
            logger.info(f"Job {job.id} completed (task_id: {task_id}, state: {state})")
        
        db.close()
    except Exception as e:
        logger.error(f"Error updating job status on task_postrun: {e}")


@task_failure.connect
def task_failure_handler(task_id, exception, args, kwargs, traceback, einfo, **kw):
    """Update job status when task fails."""
    try:
        db = SessionLocal()
        job = db.query(Job).filter(Job.celery_task_id == task_id).first()
        
        if job:
            job.status = JobStatus.FAILED
            job.error = str(exception)
            job.finished_at = datetime.utcnow()
            job.message = f"Task failed: {exception}"
            db.commit()
            logger.error(f"Job {job.id} failed (task_id: {task_id}): {exception}")
            
            # Emit telemetry event
            if len(args) >= 2:
                job_id = args[0]
                params = args[1] if isinstance(args[1], dict) else {}
                telemetry = get_job_telemetry()
                sender = kw.get('sender')
                telemetry.emit_job_failed(
                    job_id=job_id,
                    task_name=sender.name.split('.')[-1] if sender and hasattr(sender, 'name') else "unknown",
                    error=exception,
                    params=params,
                    correlation_id=job.correlation_id
                )
        
        db.close()
    except Exception as e:
        logger.error(f"Error updating job status on task_failure: {e}")


@task_retry.connect
def task_retry_handler(task_id, reason, einfo, **kw):
    """Update job status when task is retried."""
    try:
        db = SessionLocal()
        job = db.query(Job).filter(Job.celery_task_id == task_id).first()
        
        if job:
            job.status = JobStatus.RETRYING
            job.retry_count += 1
            job.message = f"Retrying: {reason}"
            db.commit()
            logger.warning(f"Job {job.id} retrying (task_id: {task_id}): {reason}")
            
            # Emit telemetry event
            telemetry = get_job_telemetry()
            request = kw.get('request')
            if request and hasattr(request, 'args') and len(request.args) >= 2:
                job_id = request.args[0]
                params = request.args[1] if isinstance(request.args[1], dict) else {}
                telemetry.emit_job_retrying(
                    job_id=job_id,
                    task_name=request.task.split('.')[-1] if hasattr(request, 'task') else "unknown",
                    retry_count=job.retry_count,
                    max_retries=job.max_retries,
                    error=einfo.exception if einfo else Exception(reason),
                    params=params,
                    correlation_id=job.correlation_id
                )
        
        db.close()
    except Exception as e:
        logger.error(f"Error updating job status on task_retry: {e}")


def get_current_job(task_id: str) -> Job:
    """Get current job from database by Celery task ID."""
    db = SessionLocal()
    job = db.query(Job).filter(Job.celery_task_id == task_id).first()
    db.close()
    return job


def update_job_progress(task_id: str, progress: float, message: str = None):
    """Update job progress from within a task."""
    try:
        db = SessionLocal()
        job = db.query(Job).filter(Job.celery_task_id == task_id).first()
        
        if job:
            job.progress = min(progress, 100.0)
            if message:
                job.message = message
            db.commit()
        
        db.close()
    except Exception as e:
        logger.error(f"Error updating job progress: {e}")