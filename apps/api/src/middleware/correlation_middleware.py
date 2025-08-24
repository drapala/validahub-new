"""
Correlation ID middleware for request tracking.
Handles correlation ID generation, propagation, and timing.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time

from ..core.logging_config import get_logger
from ..core.utils import set_correlation_id, clear_correlation_id

logger = get_logger(__name__)


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle correlation IDs and request tracking.
    
    Features:
    - Generates correlation ID if not provided
    - Propagates correlation ID through the request
    - Tracks request processing time
    - Logs request details with correlation
    """
    
    def __init__(self, app, service_name: str = "validahub-api"):
        """
        Initialize correlation middleware.
        
        Args:
            app: FastAPI application
            service_name: Name of the service for logging
        """
        super().__init__(app)
        self.service_name = service_name
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with correlation tracking.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response with correlation headers
        """
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-Id")
        if not correlation_id:
            import uuid
            correlation_id = str(uuid.uuid4())
        
        # Store in request state for access in endpoints
        request.state.correlation_id = correlation_id
        
        # Set correlation ID in context for logging and telemetry
        set_correlation_id(correlation_id)
        
        # Track request timing
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time_ms = (time.time() - start_time) * 1000
            
            # Add response headers
            response.headers["X-Correlation-Id"] = correlation_id
            response.headers["X-Process-Time-Ms"] = str(int(process_time_ms))
            response.headers["X-Service-Name"] = self.service_name
            
            # Log request details
            logger.info(
                "Request processed",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time_ms": int(process_time_ms),
                    "service": self.service_name
                }
            )
            
            return response
            
        except Exception as e:
            # Log error with correlation
            process_time_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time_ms": int(process_time_ms),
                    "service": self.service_name
                }
            )
            raise
            
        finally:
            # Clear correlation ID from context
            clear_correlation_id()