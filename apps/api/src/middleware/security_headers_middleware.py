"""
Security headers middleware for API protection.
Adds various security headers to all responses.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional, Dict

from ..core.logging_config import get_logger
from ..core.settings import get_settings

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.
    
    Features:
    - Content Security Policy
    - X-Frame-Options
    - X-Content-Type-Options
    - Strict-Transport-Security
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    """
    
    def __init__(
        self,
        app,
        enable_hsts: bool = True,
        enable_csp: bool = False,
        custom_headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize security headers middleware.
        
        Args:
            app: FastAPI application
            enable_hsts: Whether to enable HSTS header
            enable_csp: Whether to enable Content Security Policy
            custom_headers: Additional custom security headers
        """
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.enable_csp = enable_csp
        self.custom_headers = custom_headers or {}
        self.settings = get_settings()
    
    def _get_csp_header(self) -> str:
        """
        Generate Content Security Policy header.
        
        Returns:
            CSP header value
        """
        # Basic CSP for API
        csp_directives = [
            "default-src 'none'",
            "script-src 'none'",
            "style-src 'none'",
            "img-src 'none'",
            "font-src 'none'",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'none'",
            "form-action 'none'"
        ]
        
        return "; ".join(csp_directives)
    
    def _should_add_security_headers(self, request: Request) -> bool:
        """
        Check if security headers should be added for this request.
        
        Args:
            request: Incoming request
            
        Returns:
            True if headers should be added
        """
        # Skip for health checks
        if request.url.path in ["/health", "/health/ready", "/health/live"]:
            return False
        
        # Skip for internal endpoints if configured
        if request.url.path.startswith("/internal/"):
            return False
        
        return True
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers to response.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response with security headers
        """
        # Process request
        response = await call_next(request)
        
        # Check if headers should be added
        if not self._should_add_security_headers(request):
            return response
        
        # Add standard security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add Permissions Policy (formerly Feature Policy)
        permissions = [
            "accelerometer=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=()",
            "usb=()"
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)
        
        # Add HSTS header for production
        if self.enable_hsts and self.settings.environment.value == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Add CSP if enabled
        if self.enable_csp:
            response.headers["Content-Security-Policy"] = self._get_csp_header()
        
        # Add custom headers
        for header, value in self.custom_headers.items():
            response.headers[header] = value
        
        # Add API version header
        response.headers["X-API-Version"] = self.settings.app_version
        
        # Log security headers application
        logger.debug(
            "Security headers applied",
            extra={
                "path": request.url.path,
                "method": request.method,
                "headers_count": len(response.headers)
            }
        )
        
        return response