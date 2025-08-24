"""
Middleware package for ValidaHub API.
Each middleware handles a specific concern following single responsibility principle.
"""

from .correlation_middleware import CorrelationMiddleware
from .rate_limit_middleware import RateLimitMiddleware
from .security_headers_middleware import SecurityHeadersMiddleware
from .authentication_middleware import AuthenticationMiddleware
from .telemetry_middleware import TelemetryMiddleware, PerformanceTrackingMiddleware

# For backward compatibility, import from correlation.py if new files not found
try:
    from .correlation import (
        CorrelationMiddleware as CorrelationMiddleware_Old,
        RateLimitMiddleware as RateLimitMiddleware_Old,
        SecurityHeadersMiddleware as SecurityHeadersMiddleware_Old
    )
except ImportError:
    CorrelationMiddleware_Old = CorrelationMiddleware
    RateLimitMiddleware_Old = RateLimitMiddleware
    SecurityHeadersMiddleware_Old = SecurityHeadersMiddleware

__all__ = [
    "CorrelationMiddleware",
    "RateLimitMiddleware", 
    "SecurityHeadersMiddleware",
    "AuthenticationMiddleware",
    "TelemetryMiddleware",
    "PerformanceTrackingMiddleware"
]