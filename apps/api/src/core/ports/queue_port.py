"""Queue port for asynchronous task processing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Dict, Optional


class MessagePriority(Enum):
    """Message priority levels."""
    
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class QueueMessage:
    """Queue message with metadata."""
    
    id: str
    body: Dict[str, Any]
    attributes: Dict[str, str]
    receipt_handle: Optional[str] = None
    correlation_id: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL
    retry_count: int = 0
    created_at: Optional[datetime] = None
    visible_after: Optional[datetime] = None


class QueuePort(ABC):
    """
    Port for queue operations.
    Abstracts message queue systems (SQS, RabbitMQ, Redis, etc).
    """
    
    @abstractmethod
    async def send_message(
        self,
        queue_name: str,
        message: Dict[str, Any],
        delay_seconds: int = 0,
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Send a message to a queue.
        
        Args:
            queue_name: Target queue name
            message: Message body
            delay_seconds: Visibility delay
            priority: Message priority
            correlation_id: Correlation ID for tracing
            attributes: Message attributes
            
        Returns:
            Message ID
        """
        pass
    
    @abstractmethod
    async def receive_messages(
        self,
        queue_name: str,
        max_messages: int = 1,
        wait_seconds: int = 0,
        visibility_timeout: int = 30
    ) -> List[QueueMessage]:
        """
        Receive messages from a queue.
        
        Args:
            queue_name: Source queue name
            max_messages: Maximum messages to receive
            wait_seconds: Long polling wait time
            visibility_timeout: Message visibility timeout
            
        Returns:
            List of queue messages
        """
        pass
    
    @abstractmethod
    async def delete_message(
        self,
        queue_name: str,
        receipt_handle: str
    ) -> bool:
        """
        Delete a message from the queue.
        
        Args:
            queue_name: Queue name
            receipt_handle: Message receipt handle
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def change_message_visibility(
        self,
        queue_name: str,
        receipt_handle: str,
        visibility_timeout: int
    ) -> bool:
        """
        Change message visibility timeout.
        
        Args:
            queue_name: Queue name
            receipt_handle: Message receipt handle
            visibility_timeout: New timeout in seconds
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def get_queue_attributes(
        self,
        queue_name: str
    ) -> Dict[str, Any]:
        """
        Get queue attributes and statistics.
        
        Args:
            queue_name: Queue name
            
        Returns:
            Queue attributes (size, delays, etc)
        """
        pass
    
    @abstractmethod
    async def purge_queue(self, queue_name: str) -> bool:
        """
        Delete all messages in a queue.
        
        Args:
            queue_name: Queue to purge
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def create_queue(
        self,
        queue_name: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a new queue.
        
        Args:
            queue_name: Queue name
            attributes: Queue configuration
            
        Returns:
            True if created successfully
        """
        pass