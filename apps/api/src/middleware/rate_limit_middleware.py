"""
Rate limiting middleware for API protection.
Implements token bucket algorithm with Redis backend.
"""

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional, Dict, Any
import time
import json
from datetime import datetime, timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from ..core.logging_config import get_logger
from ..core.settings import get_settings

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle rate limiting.
    
    Features:
    - Token bucket algorithm
    - Per-user and per-IP rate limiting
    - Configurable limits and windows
    - Proper rate limit headers
    """
    
    def __init__(
        self,
        app,
        rate_limit: int = 100,
        window_seconds: int = 60,
        enable_redis: bool = True,
        fail_open: bool = True
    ):
        """
        Initialize rate limit middleware.
        
        Args:
            app: FastAPI application
            rate_limit: Number of requests allowed per window
            window_seconds: Time window in seconds
            enable_redis: Whether to use Redis for distributed rate limiting
            fail_open: Whether to allow requests when Redis is unavailable (default: True)
        """
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        self.enable_redis = enable_redis and REDIS_AVAILABLE
        self.fail_open = fail_open
        self.redis_client = None
        
        if self.enable_redis:
            self._setup_redis()
        elif enable_redis and not REDIS_AVAILABLE:
            logger.warning("Redis requested but not available - using in-memory rate limiting")
    
    def _setup_redis(self):
        """Setup Redis client for distributed rate limiting."""
        if not REDIS_AVAILABLE:
            logger.error("Redis library not installed - cannot enable Redis rate limiting")
            return
            
        try:
            settings = get_settings()
            self.redis_client = redis.from_url(
                settings.redis.url,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis rate limiting enabled")
        except Exception as e:
            logger.warning(f"Redis rate limiting disabled: {e}")
            self.redis_client = None
    
    def _get_rate_limit_key(self, request: Request) -> str:
        """
        Generate rate limit key for the request.
        
        Args:
            request: Incoming request
            
        Returns:
            Rate limit key
        """
        # Use user ID if authenticated, otherwise use IP
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"rate_limit:user:{user_id}"
        
        # Use client IP
        client_ip = request.client.host if request.client else "unknown"
        return f"rate_limit:ip:{client_ip}"
    
    async def _check_rate_limit_redis(self, key: str) -> Dict[str, Any]:
        """
        Check rate limit using Redis.
        
        Args:
            key: Rate limit key
            
        Returns:
            Dict with remaining requests and reset time
        """
        if not self.redis_client:
            return {
                "allowed": True,
                "remaining": self.rate_limit,
                "reset": int(time.time()) + self.window_seconds
            }
        
        try:
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            now = int(time.time())
            window_start = now - self.window_seconds
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count requests in current window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiry
            pipe.expire(key, self.window_seconds)
            
            # Execute pipeline
            results = pipe.execute()
            request_count = results[1]
            
            # Check if limit exceeded
            if request_count >= self.rate_limit:
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset": now + self.window_seconds
                }
            
            return {
                "allowed": True,
                "remaining": self.rate_limit - request_count - 1,
                "reset": now + self.window_seconds
            }
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Handle based on fail_open configuration
            if self.fail_open:
                logger.warning("Rate limiting failed open - allowing request")
                return {
                    "allowed": True,
                    "remaining": self.rate_limit,
                    "reset": int(time.time()) + self.window_seconds
                }
            else:
                logger.warning("Rate limiting failed closed - denying request")
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset": int(time.time()) + self.window_seconds
                }
    
    async def _check_rate_limit_memory(self, key: str) -> Dict[str, Any]:
        """
        Check rate limit using in-memory storage (fallback).
        
        Args:
            key: Rate limit key
            
        Returns:
            Dict with remaining requests and reset time
        """
        # Simple in-memory implementation (not distributed)
        if not hasattr(self, "_rate_limit_store"):
            self._rate_limit_store = {}
        
        now = time.time()
        window_start = now - self.window_seconds
        
        # Get or create bucket
        if key not in self._rate_limit_store:
            self._rate_limit_store[key] = []
        
        # Remove old entries
        self._rate_limit_store[key] = [
            t for t in self._rate_limit_store[key]
            if t > window_start
        ]
        
        # Check limit
        request_count = len(self._rate_limit_store[key])
        if request_count >= self.rate_limit:
            return {
                "allowed": False,
                "remaining": 0,
                "reset": int(now + self.window_seconds)
            }
        
        # Add current request
        self._rate_limit_store[key].append(now)
        
        return {
            "allowed": True,
            "remaining": self.rate_limit - request_count - 1,
            "reset": int(now + self.window_seconds)
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response with rate limit headers
        """
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/ready", "/health/live"]:
            return await call_next(request)
        
        # Get rate limit key
        key = self._get_rate_limit_key(request)
        
        # Check rate limit
        if self.redis_client:
            limit_info = await self._check_rate_limit_redis(key)
        else:
            limit_info = await self._check_rate_limit_memory(key)
        
        # If rate limit exceeded, return 429
        if not limit_info["allowed"]:
            logger.warning(
                f"Rate limit exceeded for {key}",
                extra={
                    "key": key,
                    "limit": self.rate_limit,
                    "window": self.window_seconds
                }
            )
            
            # Create problem response
            from ..schemas.errors import RateLimitProblemDetail
            problem = RateLimitProblemDetail(
                detail="Rate limit exceeded. Please retry after some time.",
                rate_limit=self.rate_limit,
                rate_limit_remaining=0,
                rate_limit_reset=datetime.fromtimestamp(limit_info["reset"])
            )
            
            from ..core.utils import problem_response
            response = problem_response(problem)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Reset"] = str(limit_info["reset"])
            response.headers["Retry-After"] = str(self.window_seconds)
            
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(limit_info["reset"])
        
        return response