from fastapi import APIRouter, Response, Header
from typing import Optional, Dict
import time
from datetime import datetime, timezone
import asyncio
from sqlalchemy import text

from src.schemas.validate import HealthStatus
from src.config import settings
from src.db.session import get_db_session
from src.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["health"])

startup_time = time.monotonic()


async def check_database_health() -> str:
    """Check database connectivity and health."""
    try:
        async with get_db_session() as session:
            # Execute a simple query with timeout
            result = await asyncio.wait_for(
                session.execute(text("SELECT 1")),
                timeout=5.0
            )
            return "healthy" if result else "unhealthy"
    except asyncio.TimeoutError:
        logger.warning("Database health check timed out")
        return "degraded"
    except Exception as e:
        logger.error(f"Database health check failed: {type(e).__name__}")
        return "unhealthy"


async def check_redis_health() -> str:
    """Check Redis connectivity and health."""
    try:
        import aioredis
        from src.config import settings
        
        # Create Redis connection with timeout
        redis = await asyncio.wait_for(
            aioredis.from_url(
                str(settings.redis.url),
                decode_responses=True
            ),
            timeout=2.0
        )
        
        # Ping Redis
        pong = await asyncio.wait_for(redis.ping(), timeout=2.0)
        await redis.close()
        
        return "healthy" if pong else "unhealthy"
    except asyncio.TimeoutError:
        logger.warning("Redis health check timed out")
        return "degraded"
    except Exception as e:
        logger.error(f"Redis health check failed: {type(e).__name__}")
        return "unhealthy"


async def check_s3_health() -> str:
    """Check S3/storage connectivity and health."""
    try:
        from src.services.storage_service import get_storage_service
        
        storage = get_storage_service()
        if storage.s3_client:
            # Try to list buckets with timeout
            result = await asyncio.wait_for(
                asyncio.to_thread(storage.s3_client.list_buckets),
                timeout=3.0
            )
            return "healthy" if result else "degraded"
        else:
            # No S3 configured, check local storage
            import os
            return "healthy" if os.path.exists(storage.temp_dir) else "degraded"
    except asyncio.TimeoutError:
        logger.warning("S3 health check timed out")
        return "degraded"
    except Exception as e:
        logger.error(f"S3 health check failed: {type(e).__name__}")
        return "unhealthy"


@router.get("/health", response_model=HealthStatus)
async def health_check(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id")
) -> HealthStatus:
    """
    Health check endpoint - no authentication required.
    Returns basic health status and service availability.
    """
    
    uptime = int(time.monotonic() - startup_time)
    
    # Run health checks concurrently for better performance
    db_check, redis_check, s3_check = await asyncio.gather(
        check_database_health(),
        check_redis_health(),
        check_s3_health(),
        return_exceptions=True
    )
    
    # Handle any exceptions from health checks
    services = {
        "api": "healthy",
        "database": db_check if isinstance(db_check, str) else "unhealthy",
        "redis": redis_check if isinstance(redis_check, str) else "unhealthy",
        "s3": s3_check if isinstance(s3_check, str) else "unhealthy"
    }
    
    # Determine overall status
    if all(status == "healthy" for status in services.values()):
        overall_status = "healthy"
    elif any(status == "unhealthy" for status in services.values()):
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"
    
    return HealthStatus(
        status=overall_status,
        version=settings.version,
        environment=settings.app_env,
        services=services,
        uptime_seconds=uptime
    )


@router.get("/health/ready")
async def readiness_check() -> dict:
    """
    Kubernetes readiness probe endpoint.
    Returns 200 if service is ready to accept traffic.
    """
    # Check if critical services are available
    db_status = await check_database_health()
    redis_status = await check_redis_health()
    
    # Service is ready if database and redis are at least degraded
    ready = db_status != "unhealthy" and redis_status != "unhealthy"
    
    return {
        "ready": ready,
        "database": db_status,
        "redis": redis_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/live")
async def liveness_check() -> dict:
    """
    Kubernetes liveness probe endpoint.
    Returns 200 if service is alive.
    """
    return {"alive": True, "timestamp": datetime.now(timezone.utc).isoformat()}