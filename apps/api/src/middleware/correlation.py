from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Deque
import uuid
import time
from collections import defaultdict, deque
import asyncio
from core.logging_config import get_logger

logger = get_logger(__name__)


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle correlation IDs and request tracking."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-Id")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Store in request state for access in endpoints
        request.state.correlation_id = correlation_id
        
        # Track request timing
        start_time = time.monotonic()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = (time.monotonic() - start_time) * 1000  # Convert to ms
        
        # Add response headers
        response.headers["X-Correlation-Id"] = correlation_id
        response.headers["X-Process-Time-Ms"] = str(int(process_time))
        
        # Log request details
        logger.info(
            f"Request processed",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": int(process_time)
            }
        )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limiting."""
    
    def __init__(self, app, rate_limit: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        # Store request timestamps per client using sliding window
        self.request_windows: Dict[str, Deque[float]] = defaultdict(deque)
        self.lock = asyncio.Lock()
        
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier from request."""
        # Try to get real IP from headers (for proxied requests)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        # Fall back to direct client
        return request.client.host if request.client else "unknown"
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)
            
        client_id = self._get_client_id(request)
        current_time = time.monotonic()
        window_start = current_time - self.window_seconds
        
        async with self.lock:
            # Get or create window for this client
            client_window = self.request_windows[client_id]
            
            # Remove expired timestamps
            while client_window and client_window[0] < window_start:
                client_window.popleft()
            
            # Check if rate limit exceeded
            if len(client_window) >= self.rate_limit:
                # Calculate when the oldest request will expire
                reset_time = client_window[0] + self.window_seconds
                retry_after = int(reset_time - current_time) + 1
                
                logger.warning(f"Rate limit exceeded for client {client_id}")
                
                # Return 429 response with proper headers
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={
                        "X-RateLimit-Limit": str(self.rate_limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                        "Retry-After": str(retry_after)
                    }
                )
            
            # Add current request to window
            client_window.append(current_time)
            remaining = self.rate_limit - len(client_window)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.window_seconds))
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response