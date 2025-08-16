"""
Authentication dependencies for API endpoints.
"""

import os
import logging
from typing import Optional
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def get_current_user_id() -> str:
    """
    Get current user ID from authentication context.
    
    DEVELOPMENT ONLY: Returns a mock user ID for development environments.
    In production, this should be replaced with proper authentication logic.
    
    Returns:
        str: User ID (UUID string format)
    
    Raises:
        RuntimeError: If mock authentication is attempted outside development
        HTTPException: If authentication fails in production
    """
    # Check if we're in a development environment
    env = os.environ.get("ENV", "development")
    is_development = env in ["development", "dev", "local", "test"]
    
    if is_development:
        # Return mock user ID for development
        mock_user_id = "00000000-0000-0000-0000-000000000001"
        logger.debug(f"Using mock user ID: {mock_user_id}")
        return mock_user_id
    
    # TODO: Implement proper authentication for production
    # This should:
    # 1. Extract and validate JWT/API key from request headers
    # 2. Verify token signature and expiration
    # 3. Extract user ID from token claims
    # 4. Optional: Check user permissions/roles
    
    # For now, raise an error to prevent unintentional production use
    raise RuntimeError(
        "Authentication not implemented for production. "
        "Please implement proper authentication before deploying to production."
    )


def get_optional_user_id() -> Optional[str]:
    """
    Get current user ID if available, otherwise return None.
    Useful for endpoints that support both authenticated and anonymous access.
    """
    try:
        return get_current_user_id()
    except (RuntimeError, HTTPException):
        return None


def require_admin_user() -> str:
    """
    Require admin user authentication.
    
    Returns:
        str: Admin user ID
    
    Raises:
        HTTPException: If user is not authenticated or not an admin
    """
    user_id = get_current_user_id()
    
    # TODO: Check if user has admin role
    # This would typically check against a database or token claims
    
    # For development, accept the mock user as admin
    if user_id == "00000000-0000-0000-0000-000000000001":
        return user_id
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required"
    )