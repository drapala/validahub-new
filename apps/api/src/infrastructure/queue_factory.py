"""
Factory for creating queue publisher instances based on configuration.
"""

import os
import logging
import threading
from typing import Optional

from .queue_publisher import (
    QueuePublisher,
    CeleryQueuePublisher,
    SQSQueuePublisher,
    InMemoryQueuePublisher
)

logger = logging.getLogger(__name__)


def create_queue_publisher(backend: Optional[str] = None) -> QueuePublisher:
    """
    Create a queue publisher instance based on configuration.
    
    Args:
        backend: Optional backend type override. If not provided,
                uses QUEUE_BACKEND environment variable.
                Options: "celery", "sqs", "memory"
    
    Returns:
        QueuePublisher instance
    
    Raises:
        ValueError: If backend is not supported
    """
    
    # Determine backend from config or environment
    if backend is None:
        backend = os.environ.get("QUEUE_BACKEND", "celery").lower()
    
    logger.info(f"Creating queue publisher with backend: {backend}")
    
    if backend == "celery":
        # Import here to avoid circular dependency
        from src.workers.celery_app import celery_app
        return CeleryQueuePublisher(celery_app)
    
    elif backend == "sqs":
        # Create SQS client
        import boto3
        
        # Get SQS configuration from environment
        region = os.environ.get("AWS_REGION", "us-east-1")
        
        # Queue URL mapping from environment or config
        queue_urls = {
            "queue:free": os.environ.get("SQS_QUEUE_FREE_URL", ""),
            "queue:pro": os.environ.get("SQS_QUEUE_PRO_URL", ""),
            "queue:business": os.environ.get("SQS_QUEUE_BUSINESS_URL", ""),
            "queue:enterprise": os.environ.get("SQS_QUEUE_ENTERPRISE_URL", ""),
            "default": os.environ.get("SQS_QUEUE_DEFAULT_URL", "")
        }
        
        # Remove empty URLs
        queue_urls = {k: v for k, v in queue_urls.items() if v}
        
        if not queue_urls:
            raise ValueError("No SQS queue URLs configured")
        
        sqs_client = boto3.client("sqs", region_name=region)
        return SQSQueuePublisher(sqs_client, queue_urls)
    
    elif backend == "memory":
        # In-memory queue for testing
        return InMemoryQueuePublisher()
    
    else:
        raise ValueError(f"Unsupported queue backend: {backend}")


# Singleton instance (lazy initialization) with thread safety
_queue_publisher_instance: Optional[QueuePublisher] = None
_queue_publisher_lock = threading.Lock()


def get_queue_publisher() -> QueuePublisher:
    """
    Get the singleton queue publisher instance (thread-safe).
    
    Returns:
        QueuePublisher instance
    """
    global _queue_publisher_instance
    
    if _queue_publisher_instance is None:
        with _queue_publisher_lock:
            # Double-check locking pattern
            if _queue_publisher_instance is None:
                _queue_publisher_instance = create_queue_publisher()
    
    return _queue_publisher_instance


def set_queue_publisher(publisher: QueuePublisher) -> None:
    """
    Set the queue publisher instance (useful for testing).
    
    Args:
        publisher: QueuePublisher instance to use
    """
    global _queue_publisher_instance
    _queue_publisher_instance = publisher
    logger.info(f"Queue publisher set to: {type(publisher).__name__}")