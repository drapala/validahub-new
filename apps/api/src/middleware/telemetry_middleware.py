"""
Telemetry middleware for tracking API requests and responses.
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import asyncio

from core.logging_config import get_logger
from telemetry.telemetry_service import get_telemetry_service
from telemetry.events import EventType

logger = get_logger(__name__)


class TelemetryMiddleware(BaseHTTPMiddleware):
    """
    Middleware for emitting telemetry events for API requests.
    
    Features:
    - Tracks request/response timing
    - Emits structured telemetry events
    - Captures client information
    - Monitors slow requests
    """
    
    def __init__(
        self,
        app: ASGIApp,
        service: str = "validahub-api",
        slow_request_threshold_ms: int = 1000
    ):
        """
        Initialize telemetry middleware.
        
        Args:
            app: FastAPI application
            service: Service name for telemetry
            slow_request_threshold_ms: Threshold for slow request warnings
        """
        super().__init__(app)
        self.service = service
        self.slow_request_threshold_ms = slow_request_threshold_ms
        self.telemetry = get_telemetry_service()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and emit telemetry events.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response from the application
        """
        # Skip telemetry for health checks
        if request.url.path in ["/health", "/health/ready", "/health/live"]:
            return await call_next(request)
        
        # Get correlation ID from headers or context
        correlation_id = request.headers.get("X-Correlation-Id")
        if correlation_id:
            self.telemetry.set_context(correlation_id=correlation_id)
        
        # Get user info if available
        user_id = None
        if hasattr(request.state, "user_id"):
            user_id = request.state.user_id
            self.telemetry.set_context(user_id=user_id)
        
        # Track request start
        start_time = time.monotonic()
        
        # Emit request event
        await self.telemetry.emit_api_request(
            method=request.method,
            path=str(request.url.path),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent")
        )
        
        # Process request
        response = None
        error = None
        
        try:
            response = await call_next(request)
        except Exception as e:
            error = e
            logger.error(f"Request failed: {e}")
            
            # Emit error event
            await self.telemetry.emit_system_error(
                component="api",
                message=f"Request failed: {str(e)}",
                error_type=type(e).__name__
            )
            
            # Re-raise the error
            raise
        finally:
            # Calculate response time
            response_time_ms = int((time.monotonic() - start_time) * 1000)
            
            # Emit response event
            if response:
                await self.telemetry.emit_api_response(
                    method=request.method,
                    path=str(request.url.path),
                    status_code=response.status_code,
                    response_time_ms=response_time_ms
                )
                
                # Check for slow requests
                if response_time_ms > self.slow_request_threshold_ms:
                    await self.telemetry.emit_performance_metric(
                        metric_name="slow_request",
                        metric_value=response_time_ms,
                        metric_unit="ms",
                        threshold_value=self.slow_request_threshold_ms,
                        operation=f"{request.method} {request.url.path}"
                    )
                
                # Add response time header
                response.headers["X-Response-Time-Ms"] = str(response_time_ms)
            
            # Clear context
            self.telemetry.clear_context()
        
        return response


class PerformanceTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking performance metrics.
    
    Features:
    - Memory usage tracking
    - CPU usage tracking
    - Request rate monitoring
    - Concurrent request tracking
    """
    
    def __init__(
        self,
        app: ASGIApp,
        emit_interval: int = 60  # seconds
    ):
        """
        Initialize performance tracking middleware.
        
        Args:
            app: FastAPI application
            emit_interval: Interval for emitting metrics
        """
        super().__init__(app)
        self.emit_interval = emit_interval
        self.telemetry = get_telemetry_service()
        self.request_count = 0
        self.concurrent_requests = 0
        self.total_response_time = 0
        self._start_metrics_task()
    
    def _start_metrics_task(self):
        """Start background task for emitting metrics."""
        asyncio.create_task(self._emit_metrics_periodically())
    
    async def _emit_metrics_periodically(self):
        """Periodically emit performance metrics."""
        while True:
            await asyncio.sleep(self.emit_interval)
            
            try:
                # Get system metrics
                import psutil
                
                # CPU usage - use non-blocking approach
                cpu_percent = await asyncio.to_thread(psutil.cpu_percent, interval=0.1)
                await self.telemetry.emit_performance_metric(
                    metric_name="cpu_usage",
                    metric_value=cpu_percent,
                    metric_unit="percentage",
                    threshold_value=80.0
                )
                
                # Memory usage
                memory = psutil.virtual_memory()
                await self.telemetry.emit_performance_metric(
                    metric_name="memory_usage",
                    metric_value=memory.percent,
                    metric_unit="percentage",
                    threshold_value=90.0
                )
                
                # Request rate
                if self.request_count > 0:
                    avg_response_time = self.total_response_time / self.request_count
                    await self.telemetry.emit_performance_metric(
                        metric_name="avg_response_time",
                        metric_value=avg_response_time,
                        metric_unit="ms"
                    )
                    
                    await self.telemetry.emit_performance_metric(
                        metric_name="request_rate",
                        metric_value=self.request_count / self.emit_interval,
                        metric_unit="requests_per_second"
                    )
                    
                    # Reset counters
                    self.request_count = 0
                    self.total_response_time = 0
                
                # Concurrent requests
                await self.telemetry.emit_performance_metric(
                    metric_name="concurrent_requests",
                    metric_value=self.concurrent_requests,
                    metric_unit="count"
                )
                
            except Exception as e:
                logger.error(f"Failed to emit performance metrics: {e}")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track performance.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response from the application
        """
        # Track concurrent requests
        self.concurrent_requests += 1
        
        # Track timing
        start_time = time.monotonic()
        
        try:
            response = await call_next(request)
            
            # Update metrics
            response_time_ms = (time.monotonic() - start_time) * 1000
            self.request_count += 1
            self.total_response_time += response_time_ms
            
            return response
        finally:
            self.concurrent_requests -= 1