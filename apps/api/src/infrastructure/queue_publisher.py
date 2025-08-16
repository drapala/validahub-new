"""
Queue publisher abstraction for decoupling from specific queue implementations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Protocol
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class QueuePublisher(Protocol):
    """Protocol for queue publishers."""
    
    def publish(
        self,
        task_name: str,
        payload: Dict[str, Any],
        queue: str = "default",
        priority: int = 5,
        delay_seconds: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Publish a task to the queue.
        
        Args:
            task_name: Name of the task to execute
            payload: Task payload/parameters
            queue: Target queue name
            priority: Task priority (1-10)
            delay_seconds: Optional delay before processing
            correlation_id: Optional correlation ID for tracing
            
        Returns:
            Task ID for tracking
        """
        ...


class CeleryQueuePublisher:
    """Celery implementation of QueuePublisher."""
    
    def __init__(self, celery_app):
        """Initialize with Celery app instance."""
        self.celery_app = celery_app
        
    def publish(
        self,
        task_name: str,
        payload: Dict[str, Any],
        queue: str = "default",
        priority: int = 5,
        delay_seconds: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """Publish task to Celery queue."""
        
        # Map task name to full Celery task path
        task_mapping = {
            "validate_csv_job": "src.workers.tasks.validate_csv_job",
            "correct_csv_job": "src.workers.tasks.correct_csv_job",
            "sync_connector_job": "src.workers.tasks.sync_connector_job",
            "generate_report_job": "src.workers.tasks.generate_report_job"
        }
        
        # Use full task path for Celery
        celery_task_name = task_mapping.get(task_name, f"src.workers.tasks.{task_name}")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Prepare Celery options
        apply_options = {
            "queue": queue,
            "priority": priority,
            "task_id": str(uuid.uuid4())  # Celery task ID
        }
        
        if delay_seconds:
            apply_options["countdown"] = delay_seconds
            
        if correlation_id:
            apply_options["headers"] = {"correlation_id": correlation_id}
        
        # Send to Celery
        task = self.celery_app.send_task(
            celery_task_name,
            args=[job_id, payload],
            **apply_options
        )
        
        logger.info(
            f"Published task {task_name} to queue {queue} "
            f"with job_id={job_id}, celery_task_id={task.id}"
        )
        
        return task.id


class SQSQueuePublisher:
    """AWS SQS implementation of QueuePublisher (future)."""
    
    def __init__(self, sqs_client, queue_urls: Dict[str, str]):
        """Initialize with SQS client and queue URL mapping."""
        self.sqs = sqs_client
        self.queue_urls = queue_urls
        
    def publish(
        self,
        task_name: str,
        payload: Dict[str, Any],
        queue: str = "default",
        priority: int = 5,
        delay_seconds: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """Publish task to SQS queue."""
        
        import json
        
        # Get queue URL
        queue_url = self.queue_urls.get(queue)
        if not queue_url:
            raise ValueError(f"Unknown queue: {queue}")
        
        # Prepare message
        message_body = {
            "task_name": task_name,
            "payload": payload,
            "priority": priority,
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to SQS
        response = self.sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body),
            DelaySeconds=delay_seconds or 0,
            MessageAttributes={
                "task_name": {"StringValue": task_name, "DataType": "String"},
                "priority": {"StringValue": str(priority), "DataType": "Number"},
                "correlation_id": {"StringValue": correlation_id or "", "DataType": "String"}
            }
        )
        
        message_id = response["MessageId"]
        logger.info(f"Published task {task_name} to SQS queue {queue} with message_id={message_id}")
        
        return message_id


class InMemoryQueuePublisher:
    """In-memory queue for testing."""
    
    def __init__(self):
        """Initialize with empty queue."""
        self.queues: Dict[str, list] = {}
        
    def publish(
        self,
        task_name: str,
        payload: Dict[str, Any],
        queue: str = "default",
        priority: int = 5,
        delay_seconds: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """Add task to in-memory queue."""
        
        if queue not in self.queues:
            self.queues[queue] = []
            
        task_id = str(uuid.uuid4())
        
        task = {
            "id": task_id,
            "task_name": task_name,
            "payload": payload,
            "priority": priority,
            "delay_seconds": delay_seconds,
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Insert sorted by priority
        self.queues[queue].append(task)
        self.queues[queue].sort(key=lambda x: -x["priority"])
        
        logger.info(f"Published task {task_name} to in-memory queue {queue} with id={task_id}")
        
        return task_id
    
    def get_queue(self, queue: str = "default") -> list:
        """Get all tasks in a queue (for testing)."""
        return self.queues.get(queue, [])