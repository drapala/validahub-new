"""
Queue publisher abstraction for decoupling from specific queue implementations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Protocol
from datetime import datetime
import uuid

from ..core.config import QueueConfig

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
    
    def cancel(self, task_id: str, terminate: bool = False) -> bool:
        """
        Cancel a queued or running task.
        
        Args:
            task_id: Task ID to cancel
            terminate: If True, forcefully terminate. If False, graceful cancellation.
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        ...
    
    def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a task.
        
        Args:
            task_id: Task ID to check
            
        Returns:
            Status info dict with keys: status, progress, message, error
            or None if task not found
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
        
        # Use configured task mapping
        celery_task_name = QueueConfig.get_celery_task_name(task_name)
        
        # Extract job ID from payload (required)
        job_id = payload.get("job_id")
        if not job_id:
            raise ValueError("Payload must contain a 'job_id' key")
        
        # Generate a single task ID for both Celery and job tracking
        task_id = str(uuid.uuid4())
        
        # Prepare Celery options
        apply_options = {
            "queue": queue,
            "priority": priority,
            "task_id": task_id  # Celery task ID
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
    
    def cancel(self, task_id: str, terminate: bool = False) -> bool:
        """Cancel a Celery task."""
        try:
            self.celery_app.control.revoke(
                task_id,
                terminate=terminate
            )
            logger.info(f"Cancelled task {task_id} (terminate={terminate})")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get Celery task status."""
        try:
            from celery.result import AsyncResult
            result = AsyncResult(task_id, app=self.celery_app)
            
            if result.state == 'PENDING':
                # Task not found or waiting
                return None
            
            status_map = {
                'PENDING': 'queued',
                'STARTED': 'processing',
                'SUCCESS': 'completed',
                'FAILURE': 'failed',
                'RETRY': 'processing',
                'REVOKED': 'cancelled'
            }
            
            return {
                'status': status_map.get(result.state, result.state.lower()),
                'progress': result.info.get('current', 0) if isinstance(result.info, dict) else None,
                'message': result.info.get('status', '') if isinstance(result.info, dict) else str(result.info),
                'error': (
                    result.info.get('exc_message', 'Task failed') if (result.state == 'FAILURE' and isinstance(result.info, dict))
                    else ('Task failed' if result.state == 'FAILURE' else None)
                )
            }
        except Exception as e:
            logger.error(f"Failed to get status for task {task_id}: {e}")
            return None


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
    
    def cancel(self, task_id: str, terminate: bool = False) -> bool:
        """Cancel an SQS message (not fully supported by SQS)."""
        # SQS doesn't support true task cancellation
        # Would need to implement a cancellation token pattern
        logger.warning(f"SQS cancellation not fully supported for task {task_id}")
        return False
    
    def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get SQS task status (limited support)."""
        # SQS doesn't maintain task state
        # Would need external state store (DynamoDB, Redis, etc.)
        logger.warning(f"SQS status checking not fully supported for task {task_id}")
        return None


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
    
    def cancel(self, task_id: str, terminate: bool = False) -> bool:
        """Cancel a task in the in-memory queue."""
        for queue_name, tasks in self.queues.items():
            for i, task in enumerate(tasks):
                if task['id'] == task_id:
                    del tasks[i]
                    logger.info(f"Cancelled task {task_id} from queue {queue_name}")
                    return True
        logger.warning(f"Task {task_id} not found in any queue")
        return False
    
    def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task in the in-memory queue."""
        for queue_name, tasks in self.queues.items():
            for task in tasks:
                if task['id'] == task_id:
                    return {
                        'status': 'queued',
                        'progress': 0,
                        'message': f"In queue {queue_name}",
                        'error': None
                    }
        return None