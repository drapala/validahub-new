"""
Storage service for file operations.
Abstracts file download/upload operations from business logic.
"""

import os
import json
from src.core.logging_config import get_logger
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime
import tempfile
from pathlib import Path

logger = get_logger(__name__)


class StorageService:
    """Service for handling file storage operations."""
    
    def __init__(self):
        """Initialize storage service with configuration."""
        # Use secure default temp directory
        default_temp_dir = os.path.join(tempfile.gettempdir(), "validahub")
        self.temp_dir = os.getenv("TEMP_STORAGE_PATH", default_temp_dir)
        
        # Ensure the temp_dir exists with secure permissions
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir, mode=0o700, exist_ok=True)
        else:
            # Ensure permissions are restrictive
            try:
                current_mode = os.stat(self.temp_dir).st_mode
                if (current_mode & 0o777) != 0o700:
                    os.chmod(self.temp_dir, 0o700)
            except OSError as e:
                logger.warning(f"Could not set permissions on temp directory: {type(e).__name__}: {e}")
        
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
            if not self._is_valid_s3_uri(uri):
                safe_hash = self._hash_string(uri) if uri else "unknown"
                logger.error(f"Invalid S3 URI format. File hash: {safe_hash}")
                raise ValueError("Invalid S3 URI format")
            return self._download_from_s3(uri)
        else:
            # For local files, check if it's an absolute path outside temp_dir
            if os.path.isabs(uri) and not self._is_safe_path(self.temp_dir, uri):
                # Absolute path outside temp_dir is not allowed
                safe_hash = self._hash_string(uri) if uri else "unknown"
                logger.error(f"Absolute path outside allowed directory. File hash: {safe_hash}")
                raise FileNotFoundError("File not found")
            
            # Check if path is safe (handles both relative and absolute paths)
            if self._is_safe_path(self.temp_dir, uri):
                if os.path.exists(uri):
                    return self._read_local_file(uri)
                else:
                    # Hash the URI for secure logging
                    safe_hash = self._hash_string(uri) if uri else "unknown"
                    logger.error(f"File not found or access denied. File hash: {safe_hash}")
                    raise FileNotFoundError("File not found")
            else:
                # Log sanitized error for security using hash
                safe_hash = self._hash_string(uri) if uri else "unknown"
                logger.error(f"File not found or access denied. File hash: {safe_hash}")
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
    
    def _hash_string(self, s: str) -> str:
        """Create a secure hash of a string for logging purposes."""
        return hashlib.sha256(s.encode()).hexdigest()[:16]
    
    def _is_valid_s3_uri(self, uri: str) -> bool:
        """
        Validate S3 URI format.
        
        Valid S3 URI format: s3://bucket-name/key/path
        Bucket naming rules:
        - 3-63 characters long
        - Lowercase letters, numbers, hyphens
        - Must start and end with letter or number
        - No consecutive periods or hyphens
        """
        import re
        
        if not uri.startswith("s3://"):
            return False
        
        # Remove the s3:// prefix
        path = uri[5:]
        
        # Split into bucket and key
        parts = path.split("/", 1)
        if not parts:
            return False
        
        bucket = parts[0]
        
        # Validate bucket name
        if len(bucket) < 3 or len(bucket) > 63:
            return False
        
        # Bucket name pattern
        bucket_pattern = r'^[a-z0-9][a-z0-9\-]*[a-z0-9]$'
        if not re.match(bucket_pattern, bucket):
            return False
        
        # No consecutive periods or hyphens
        if '..' in bucket or '--' in bucket:
            return False
        
        return True
    
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
            safe_hash = self._hash_string(path) if path else "unknown"
            logger.error(f"Attempted path traversal or access outside allowed directory. File hash: {safe_hash}")
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
        
        # Normalize the path to prevent traversal while preserving subdirectories
        normalized_path = os.path.normpath(path)
        # Remove any leading path separators to ensure it's relative
        if normalized_path.startswith(os.sep):
            normalized_path = normalized_path.lstrip(os.sep)
        file_path = os.path.join(self.temp_dir, normalized_path)
        
        # Validate the resolved path is within temp_dir
        resolved_path = os.path.realpath(file_path)
        if not self._is_safe_path(self.temp_dir, resolved_path):
            raise ValueError("Invalid path: potential path traversal detected")
        
        # Create subdirectories if needed
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
        
        with open(resolved_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"file://{resolved_path}"
    
    def _save_binary_to_local(self, content: bytes, path: str) -> str:
        """Save binary content to local file."""
        
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Normalize the path to prevent traversal while preserving subdirectories
        normalized_path = os.path.normpath(path)
        # Remove any leading path separators to ensure it's relative
        if normalized_path.startswith(os.sep):
            normalized_path = normalized_path.lstrip(os.sep)
        full_path = os.path.join(self.temp_dir, normalized_path)
        
        # Validate the resolved path is within temp_dir
        resolved_path = os.path.realpath(full_path)
        if not self._is_safe_path(self.temp_dir, resolved_path):
            raise ValueError("Invalid path: potential path traversal detected")
        
        # Create subdirectories if needed
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
        
        with open(resolved_path, "wb") as f:
            f.write(content)
        
        return f"file://{resolved_path}"


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service