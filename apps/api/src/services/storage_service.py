"""
Storage service for file operations.
Abstracts file download/upload operations from business logic.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageService:
    """Service for handling file storage operations."""
    
    def __init__(self):
        """Initialize storage service with configuration."""
        self.temp_dir = os.getenv("TEMP_STORAGE_PATH", "/tmp/validahub")
        self.s3_bucket = os.getenv("S3_BUCKET", "validahub")
        self._s3_client = None
    
    @property
    def s3_client(self):
        """Lazy load S3 client."""
        if self._s3_client is None and os.getenv("AWS_ACCESS_KEY_ID"):
            import boto3
            self._s3_client = boto3.client("s3")
        return self._s3_client
    
    def download_file(self, uri: str) -> str:
        """
        Download file from S3 or local path.
        
        Args:
            uri: File URI (s3://bucket/key or local path)
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For other download errors
        """
        
        if uri.startswith("s3://"):
            return self._download_from_s3(uri)
        elif self._is_safe_path(self.temp_dir, uri):
            if os.path.exists(uri):
                return self._read_local_file(uri)
            else:
                safe_name = os.path.basename(uri) if uri else "unknown"
                logger.error(f"File not found or access denied: {safe_name}")
                raise FileNotFoundError("File not found")
        else:
            # Log sanitized error for security (only filename, no full path)
            safe_name = os.path.basename(uri) if uri else "unknown"
            logger.error(f"File not found or access denied: {safe_name}")
            raise FileNotFoundError("File not found")
    
    def save_result(self, job_id: str, result: Dict[str, Any]) -> str:
        """
        Save job result to storage.
        
        Args:
            job_id: Job identifier
            result: Result data to save
            
        Returns:
            URI of saved result
        """
        
        result_json = json.dumps(result, indent=2, default=str)
        
        # Try S3 first if configured
        if self.s3_client:
            try:
                return self._save_to_s3(
                    content=result_json.encode("utf-8"),
                    key=f"results/{job_id}.json",
                    content_type="application/json"
                )
            except Exception as e:
                logger.error(f"Failed to save to S3: {e}")
        
        # Fallback to local storage
        return self._save_to_local(
            content=result_json,
            path=f"{job_id}.json"
        )
    
    def save_file(self, path: str, content: bytes) -> str:
        """
        Save binary file to storage.
        
        Args:
            path: Target path/key for the file
            content: File content as bytes
            
        Returns:
            URI of saved file
        """
        
        # Try S3 first if configured
        if self.s3_client:
            try:
                return self._save_to_s3(content=content, key=path)
            except Exception as e:
                logger.error(f"Failed to save file to S3: {e}")
        
        # Fallback to local storage
        return self._save_binary_to_local(content=content, path=path)
    
    # Private methods
    
    def _download_from_s3(self, uri: str) -> str:
        """Download file from S3."""
        
        if not self.s3_client:
            raise ValueError("S3 not configured")
        
        # Parse S3 URI
        parts = uri.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
        
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read().decode("utf-8")
        except self.s3_client.exceptions.NoSuchKey:
            logger.error("S3 object not found")
            raise FileNotFoundError("File not found in S3")
        except Exception as e:
            logger.error(f"Error downloading from S3: {type(e).__name__}")
            raise
    
    def _is_safe_path(self, base_dir: str, path: str) -> bool:
        """
        Check if path is safe and within allowed directory.
        
        Args:
            base_dir: Base directory that path must be within
            path: Path to validate
            
        Returns:
            True if path is safe, False otherwise
        """
        try:
            # Resolve both paths to absolute, normalized paths
            base = Path(base_dir).resolve()
            target = Path(path).resolve()
            
            # Check if target is within base directory (Python 3.8+ compatible)
            try:
                target.relative_to(base)
                return True
            except ValueError:
                return False
        except Exception:
            # If we can't resolve paths, consider it unsafe
            return False
    
    def _read_local_file(self, path: str) -> str:
        """Read local file with path validation."""
        
        # Validate path is within allowed directory
        if not self._is_safe_path(self.temp_dir, path):
            safe_name = os.path.basename(path) if path else "unknown"
            logger.error(f"Attempted path traversal or access outside allowed directory: {safe_name}")
            raise FileNotFoundError("File not found")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error("Local file not found")
            raise
        except Exception as e:
            logger.error(f"Error reading local file: {type(e).__name__}")
            raise
    
    def _save_to_s3(
        self, 
        content: bytes, 
        key: str, 
        content_type: Optional[str] = None
    ) -> str:
        """Save content to S3."""
        
        if not self.s3_client:
            raise ValueError("S3 not configured")
        
        put_args = {
            "Bucket": self.s3_bucket,
            "Key": key,
            "Body": content
        }
        
        if content_type:
            put_args["ContentType"] = content_type
        
        self.s3_client.put_object(**put_args)
        
        return f"s3://{self.s3_bucket}/{key}"
    
    def _save_to_local(self, content: str, path: str) -> str:
        """Save text content to local file."""
        
        os.makedirs(self.temp_dir, exist_ok=True)
        
        file_path = os.path.join(self.temp_dir, path)
        
        # Create subdirectories if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"file://{file_path}"
    
    def _save_binary_to_local(self, content: bytes, path: str) -> str:
        """Save binary content to local file."""
        
        os.makedirs(self.temp_dir, exist_ok=True)
        
        full_path = os.path.join(self.temp_dir, path)
        
        # Create subdirectories if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "wb") as f:
            f.write(content)
        
        return f"file://{full_path}"


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service