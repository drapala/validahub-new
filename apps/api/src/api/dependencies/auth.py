"""
Authentication dependencies for API endpoints.
"""

import os
import jwt
from core.logging_config import get_logger
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone, timedelta

logger = get_logger(__name__)

# Security scheme for JWT Bearer authentication
security = HTTPBearer(auto_error=False)

# Get environment at module level for safety checks
ENV = os.environ.get("ENV", "development").lower()


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dict containing token claims
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    # Get JWT secret from environment (should be set in production)
    jwt_secret = os.environ.get("JWT_SECRET")
    if not jwt_secret and ENV == "production":
        logger.error("JWT_SECRET not configured in production")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication configuration error"
        )
    
    # Use a default secret for development (NOT for production!)
    if not jwt_secret:
        jwt_secret = "development-secret-key-not-for-production"
    
    try:
        # Decode and verify the token
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256", "RS256"],
            options={"verify_exp": True}
        )
        
        # Verify token has required fields
        if "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject"
            )
        
        # Check if token is not expired (redundant but explicit)
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            if datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


def get_current_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
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
    
    # Production authentication using JWT
    if ENV == "production" or os.environ.get("USE_JWT_AUTH") == "true":
        # Require bearer token in production
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verify and decode the JWT token
        try:
            payload = verify_jwt_token(credentials.credentials)
            user_id = payload.get("sub")  # Subject claim contains user ID
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: no user ID"
                )
            
            # Store user info in request state for logging/telemetry
            if hasattr(request, "state"):
                request.state.user_id = user_id
                request.state.user_claims = payload
            
            logger.debug(f"Authenticated user: {user_id}")
            return user_id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    # If we reach here in production without auth, it's a configuration error
    if ENV == "production":
        logger.critical("Production environment detected without authentication configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication not configured"
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