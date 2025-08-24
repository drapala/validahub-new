"""
Shared utilities for use cases and API endpoints.
Consolidates common functionality to avoid duplication.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import Header
from fastapi.responses import JSONResponse
import uuid
import contextvars
import hashlib
import re

from .logging_config import get_logger

logger = get_logger(__name__)

# Context variable for correlation ID
correlation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'correlation_id', 
    default=None
)


class DataFrameUtils:
    """Utility class for DataFrame operations."""
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame by handling NaN and inf values.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        # Explicitly immutable operations (inplace=False is default, but being explicit)
        df = df.replace([np.inf, -np.inf], None, inplace=False)
        df = df.where(pd.notnull(df), None, inplace=False)
        return df
    
    @staticmethod
    def dataframe_to_dict(df: Optional[pd.DataFrame]) -> Optional[List[Dict[str, Any]]]:
        """
        Convert DataFrame to dictionary format for JSON serialization.
        
        Args:
            df: DataFrame to convert
            
        Returns:
            List of dictionaries representing rows, or None if DataFrame is None
        """
        if df is None:
            return None
        
        # Clean the dataframe first
        df = DataFrameUtils.clean_dataframe(df)
        return df.to_dict('records')
    
    @staticmethod
    def dataframe_to_csv(df: Optional[pd.DataFrame]) -> Optional[str]:
        """
        Convert DataFrame to CSV string.
        
        Args:
            df: DataFrame to convert
            
        Returns:
            CSV string or None if DataFrame is None
        """
        if df is None:
            return None
        
        # Clean the dataframe first  
        df = DataFrameUtils.clean_dataframe(df)
        return df.to_csv(index=False)


# Correlation ID utilities
def get_correlation_id_from_header(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id")
) -> str:
    """
    Generate or return correlation ID for request tracking.
    
    This is a FastAPI dependency that can be used in route handlers.
    
    Args:
        x_correlation_id: Correlation ID from request header
        
    Returns:
        Existing correlation ID or newly generated UUID
    """
    correlation_id = x_correlation_id or str(uuid.uuid4())
    # Store in context for logging and telemetry
    set_correlation_id(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """
    Get correlation ID from current context.
    
    This function retrieves the correlation ID from the context variable,
    which is set by middleware or request handlers.
    
    Returns:
        Current correlation ID or None
    """
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """
    Set correlation ID in current context.
    
    Args:
        correlation_id: Correlation ID to set
    """
    correlation_id_var.set(correlation_id)


def clear_correlation_id() -> None:
    """Clear correlation ID from current context."""
    correlation_id_var.set(None)


# HTTP Response utilities
def problem_response(problem: Any) -> JSONResponse:
    """
    Create a problem+json response according to RFC 7807.
    
    Args:
        problem: ProblemDetail instance
        
    Returns:
        JSONResponse with problem+json content type
    """
    # Convert to dict and handle datetime serialization
    content = problem.model_dump(exclude_none=True) if hasattr(problem, 'model_dump') else problem.dict(exclude_none=True)
    
    # Convert datetime fields to ISO format strings
    datetime_fields = ["timestamp", "rate_limit_reset", "created_at", "updated_at"]
    for field in datetime_fields:
        if field in content and content[field]:
            if isinstance(content[field], datetime):
                content[field] = content[field].isoformat()
    
    return JSONResponse(
        status_code=problem.status,
        content=content,
        headers={"Content-Type": "application/problem+json"}
    )


def get_prefer_header(
    prefer: Optional[str] = Header(None)
) -> bool:
    """
    Check if client prefers representation on conflict.
    
    Parses the Prefer header according to RFC 7240.
    
    Args:
        prefer: Prefer header value
        
    Returns:
        True if client wants representation on conflict
    """
    return prefer == "return=representation" if prefer else False


# File utilities
def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    # Remove dangerous characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        extension = filename.split('.')[-1] if '.' in filename else ''
        base = filename[:max_length - len(extension) - 1]
        filename = f"{base}.{extension}" if extension else base
    return filename


def calculate_file_hash(file_path: str, algorithm: str = "md5", chunk_size: int = 8192) -> Optional[str]:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256)
        chunk_size: Size of chunks to read
        
    Returns:
        Hex digest of file hash or None on error
    """
    try:
        hash_func = getattr(hashlib, algorithm)()
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        logger.error(f"Failed to calculate file hash: {e}")
        return None


def format_bytes(num_bytes: int) -> str:
    """
    Format bytes into human-readable string.
    
    Args:
        num_bytes: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


# General utilities
def serialize_datetime(obj: Any) -> Any:
    """
    Serialize datetime objects to ISO format strings.
    
    Args:
        obj: Object to serialize
        
    Returns:
        ISO formatted string if datetime, otherwise original object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def parse_bool(value: Any) -> bool:
    """
    Parse various representations of boolean values.
    
    Args:
        value: Value to parse
        
    Returns:
        Boolean interpretation of value
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    return bool(value)


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        override: Dictionary with override values
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result