"""
Authentication dependencies for API endpoints.
"""

import os
import logging
from typing import Optional
from fastapi import HTTPException, status, Request, Depends

logger = logging.getLogger(__name__)

# Get environment at module level for safety checks
ENV = os.environ.get("ENV", "development").lower()


def get_current_user_id(request: Request) -> str:
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
    is_development = ENV in ["development", "dev", "local", "test"]
    
    if is_development:
        # Return mock user ID for development (can be overridden by env var)
        mock_user_id = os.environ.get(
            "MOCK_USER_ID", 
            "00000000-0000-0000-0000-000000000001"
        )
        
        # Additional safety checks: require TWO environment variables for mock auth
        allow_mock = os.environ.get("ALLOW_MOCK_AUTH") == "true"
        confirm_mock = os.environ.get("CONFIRM_MOCK_AUTH") == "true"
        
        if not (allow_mock and confirm_mock):
            logger.warning(
                "Mock authentication attempted without both ALLOW_MOCK_AUTH=true and CONFIRM_MOCK_AUTH=true. "
                "Set BOTH environment variables to exactly 'true' to enable mock auth in development."
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Set BOTH ALLOW_MOCK_AUTH=true and CONFIRM_MOCK_AUTH=true for development."
            )
        
        # Restrict mock auth to requests from localhost only
        client_host = request.client.host if request and request.client else None
        if client_host not in ("127.0.0.1", "::1", "localhost"):
            logger.warning(
                f"Mock authentication attempted from non-localhost IP: {client_host}. "
                "Mock authentication is only allowed from localhost."
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mock authentication is only allowed from localhost (127.0.0.1 or ::1)."
            )
        
        logger.debug(f"Using mock user ID: {mock_user_id}")
        return mock_user_id
    
    # TODO: Implement proper authentication for production
    # This should:
    # 1. Extract and validate JWT/API key from request headers
    # 2. Verify token signature and expiration
    # 3. Extract user ID from token claims
    # 4. Optional: Check user permissions/roles
    
    # Additional safety check: Ensure this code is not running in production
    # This will cause the application to fail fast if deployed without proper auth
    if ENV == "production" and not os.environ.get("PRODUCTION_AUTH_IMPLEMENTED"):
        import sys
        logger.critical(
            "CRITICAL: Production deployment detected without proper authentication! "
            "Set PRODUCTION_AUTH_IMPLEMENTED=true ONLY after implementing real authentication."
        )
        logger.critical(
            "CRITICAL: Production deployment detected without proper authentication! "
            "Set PRODUCTION_AUTH_IMPLEMENTED=true ONLY after implementing real authentication."
        )
        raise RuntimeError(
            "Production deployment detected without proper authentication! "
            "Set PRODUCTION_AUTH_IMPLEMENTED=true ONLY after implementing real authentication."
        )
    
    # For now, raise an HTTP error to prevent unintentional production use
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not implemented for production. Please implement proper authentication before deploying to production."
    )


def get_optional_user_id(request: Request) -> Optional[str]:
    """
    Get current user ID if available, otherwise return None.
    Useful for endpoints that support both authenticated and anonymous access.
    """
    try:
        return get_current_user_id(request)
    except (RuntimeError, HTTPException):
        return None


def require_admin_user(request: Request) -> str:
    """
    Require admin user authentication.
    
    Returns:
        str: Admin user ID
    
    Raises:
        HTTPException: If user is not authenticated or not an admin
    """
    user_id = get_current_user_id(request)
    
    # TODO: Check if user has admin role
    # This would typically check against a database or token claims
    
    # For development, accept the mock user as admin
    if user_id == "00000000-0000-0000-0000-000000000001":
        return user_id
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required"
    )