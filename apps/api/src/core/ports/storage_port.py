"""Storage port for file operations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator, BinaryIO, Optional


@dataclass
class StorageObject:
    """Metadata for a stored object."""
    
    key: str
    size: int
    last_modified: datetime
    content_type: Optional[str] = None
    metadata: Optional[dict] = None


class StoragePort(ABC):
    """
    Port for storage operations.
    Abstracts file/object storage (S3, local FS, etc).
    """
    
    @abstractmethod
    async def upload(
        self,
        key: str,
        content: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> StorageObject:
        """
        Upload content to storage.
        
        Args:
            key: Storage key/path
            content: Binary content to upload
            content_type: MIME type
            metadata: Optional metadata
            
        Returns:
            StorageObject with upload details
        """
        pass
    
    @abstractmethod
    async def download(self, key: str) -> AsyncIterator[bytes]:
        """
        Download content from storage.
        
        Args:
            key: Storage key/path
            
        Yields:
            Chunks of file content
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if object exists in storage.
        
        Args:
            key: Storage key/path
            
        Returns:
            True if object exists
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete object from storage.
        
        Args:
            key: Storage key/path
            
        Returns:
            True if deletion was successful
        """
        pass
    
    @abstractmethod
    async def list_objects(
        self,
        prefix: Optional[str] = None,
        limit: Optional[int] = None
    ) -> AsyncIterator[StorageObject]:
        """
        List objects in storage.
        
        Args:
            prefix: Filter by key prefix
            limit: Maximum number of objects
            
        Yields:
            StorageObject instances
        """
        pass
    
    @abstractmethod
    async def get_metadata(self, key: str) -> StorageObject:
        """
        Get object metadata without downloading content.
        
        Args:
            key: Storage key/path
            
        Returns:
            StorageObject metadata
        """
        pass
    
    @abstractmethod
    async def generate_presigned_url(
        self,
        key: str,
        expiration_seconds: int = 3600,
        operation: str = "GET"
    ) -> str:
        """
        Generate a presigned URL for direct access.
        
        Args:
            key: Storage key/path
            expiration_seconds: URL validity duration
            operation: HTTP operation (GET, PUT, etc)
            
        Returns:
            Presigned URL
        """
        pass