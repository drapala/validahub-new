from fastapi import APIRouter, Response, Header
from typing import Optional
import time
from datetime import datetime

from src.schemas.validate import HealthStatus
from src.config import settings

router = APIRouter(tags=["health"])

startup_time = time.time()


@router.get("/health", response_model=HealthStatus)
async def health_check(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-Id")
) -> HealthStatus:
    """
    Health check endpoint - no authentication required.
    Returns basic health status and service availability.
    """
    
    uptime = int(time.time() - startup_time)
    
    # Check service health (simplified for now)
    services = {
        "api": "healthy",
        "database": "healthy",  # TODO: Add actual DB health check
        "redis": "healthy",     # TODO: Add actual Redis health check
        "s3": "healthy"         # TODO: Add actual S3 health check
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
    # TODO: Add actual readiness checks
    return {"ready": True, "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/live")
async def liveness_check() -> dict:
    """
    Kubernetes liveness probe endpoint.
    Returns 200 if service is alive.
    """
    return {"alive": True, "timestamp": datetime.utcnow().isoformat()}