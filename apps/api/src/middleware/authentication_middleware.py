"""
Authentication middleware for API security.
Handles JWT validation and user context.
"""

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional, List, Dict, Any
import jwt
from datetime import datetime, timezone

from ..core.logging_config import get_logger
from ..core.settings import get_settings

logger = get_logger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle authentication.
    
    Features:
    - JWT token validation
    - User context injection
    - API key authentication
    - Public endpoint bypass
    """
    
    def __init__(
        self,
        app,
        public_paths: Optional[List[str]] = None,
        enable_api_key: bool = True,
        enable_jwt: bool = True
    ):
        """
        Initialize authentication middleware.
        
        Args:
            app: FastAPI application
            public_paths: List of paths that don't require authentication
            enable_api_key: Whether to enable API key authentication
            enable_jwt: Whether to enable JWT authentication
        """
        super().__init__(app)
        self.settings = get_settings()
        self.public_paths = public_paths or [
            "/health",
            "/health/ready",
            "/health/live",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register"
        ]
        self.enable_api_key = enable_api_key
        self.enable_jwt = enable_jwt
    
    def _is_public_path(self, path: str) -> bool:
        """
        Check if path is public.
        
        Args:
            path: Request path
            
        Returns:
            True if path doesn't require authentication
        """
        # Exact match
        if path in self.public_paths:
            return True
        
        # Prefix match for documentation
        if path.startswith("/docs") or path.startswith("/redoc"):
            return True
        
        return False
    
    async def _validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            # Decode and validate token
            payload = jwt.decode(
                token,
                self.settings.security.jwt_secret_key,
                algorithms=[self.settings.security.jwt_algorithm]
            )
            
            # Check expiration
            if "exp" in payload:
                exp_timestamp = payload["exp"]
                if datetime.now(timezone.utc).timestamp() > exp_timestamp:
                    logger.warning("JWT token expired")
                    return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    async def _validate_api_key(self, api_key: str) -> Optional[str]:
        """
        Validate API key.
        
        Args:
            api_key: API key
            
        Returns:
            User ID associated with API key or None if invalid
        """
        # In production, this would check against database
        # For now, use a simple check
        if api_key and len(api_key) >= 32:
            # Extract user ID from API key (simplified)
            return "api_user_" + api_key[:8]
        
        return None
    
    async def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract authentication token from request.
        
        Args:
            request: Incoming request
            
        Returns:
            Token string or None
        """
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                return parts[1]
        
        # Check cookie (for web apps)
        token_cookie = request.cookies.get("access_token")
        if token_cookie:
            return token_cookie
        
        return None
    
    async def _extract_api_key(self, request: Request) -> Optional[str]:
        """
        Extract API key from request.
        
        Args:
            request: Incoming request
            
        Returns:
            API key or None
        """
        # Check X-API-Key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key
        
        # Check query parameter (less secure, but sometimes needed)
        if hasattr(request, "query_params"):
            api_key = request.query_params.get("api_key")
            if api_key:
                return api_key
        
        return None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with authentication.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        # Check if path requires authentication
        if self._is_public_path(request.url.path):
            return await call_next(request)
        
        authenticated = False
        user_id = None
        auth_method = None
        
        # Try JWT authentication
        if self.enable_jwt:
            token = await self._extract_token(request)
            if token:
                payload = await self._validate_jwt_token(token)
                if payload:
                    user_id = payload.get("sub")
                    authenticated = True
                    auth_method = "jwt"
                    
                    # Store user info in request state
                    request.state.user_id = user_id
                    request.state.user_email = payload.get("email")
                    request.state.user_roles = payload.get("roles", [])
        
        # Try API key authentication if JWT failed
        if not authenticated and self.enable_api_key:
            api_key = await self._extract_api_key(request)
            if api_key:
                user_id = await self._validate_api_key(api_key)
                if user_id:
                    authenticated = True
                    auth_method = "api_key"
                    
                    # Store user info in request state
                    request.state.user_id = user_id
                    request.state.auth_method = auth_method
        
        # If not authenticated, return 401
        if not authenticated:
            logger.warning(
                f"Unauthenticated request to {request.url.path}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "client": request.client.host if request.client else None
                }
            )
            
            # Create problem response
            from ..schemas.errors import ProblemDetail
            problem = ProblemDetail(
                type="https://validahub.com/errors/authentication-required",
                title="Authentication Required",
                status=status.HTTP_401_UNAUTHORIZED,
                detail="Please provide valid authentication credentials.",
                instance=request.url.path
            )
            
            from ..core.utils import problem_response
            response = problem_response(problem)
            response.headers["WWW-Authenticate"] = 'Bearer realm="ValidaHub API"'
            
            return response
        
        # Log successful authentication
        logger.info(
            f"Authenticated request",
            extra={
                "user_id": user_id,
                "auth_method": auth_method,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        # Process request
        return await call_next(request)