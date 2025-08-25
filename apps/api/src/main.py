from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager

from src.config import settings
from src.infrastructure.logging_config import setup_logging
from src.core.logging_config import get_logger
# from src.db.base import engine, Base  # Commented for testing
from src.api.v1 import health, validation, jobs
from src.middleware.correlation import (
    CorrelationMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware
)

# Setup centralized logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up ValidaHub API...")
    yield
    logger.info("Shutting down ValidaHub API...")


app = FastAPI(
    title="ValidaHub API",
    version=settings.version,
    description="Professional CSV validation and correction API for e-commerce marketplaces",
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url="/redoc" if settings.app_env == "development" else None,
    lifespan=lifespan,
    servers=[
        {"url": "http://localhost:3001", "description": "Local development"},
        {"url": "https://api.validahub.com", "description": "Production"},
        {"url": "https://staging-api.validahub.com", "description": "Staging"},
    ],
)

# Add custom middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, rate_limit=100, window_seconds=60)
app.add_middleware(CorrelationMiddleware)

# Add telemetry middleware if enabled
# TODO: Fix settings adapter to include telemetry attribute
# if settings.telemetry.enabled:
#     from src.middleware.telemetry_middleware import TelemetryMiddleware, PerformanceTrackingMiddleware
#     app.add_middleware(TelemetryMiddleware)
#     if settings.telemetry.metrics_enabled:
#         app.add_middleware(PerformanceTrackingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "*",
        "X-Correlation-Id",
        "Idempotency-Key",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset"
    ],
    expose_headers=[
        "X-Correlation-Id",
        "X-Process-Time-Ms",
        "X-Corrections-Applied",
        "X-Success-Rate",
        "X-Job-Id",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset"
    ],
)

# Include routers
app.include_router(health.router)  # Health endpoints (no prefix)
app.include_router(validation.router)  # Validation endpoints with YAML rule engine
app.include_router(jobs.router)  # Job queue endpoints


@app.get("/status")
async def get_status(response: Response):
    """Legacy health check endpoint - use /health instead."""
    # Add deprecation headers
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2025-03-01"  # Set sunset date 3 months from now
    response.headers["Link"] = '</health>; rel="successor-version"'
    
    return {
        "ok": True,
        "version": settings.version,
        "environment": settings.app_env,
        "services": {
            "api": "up",
            "database": "up",
            "redis": "up",
            "s3": "up"
        },
        "deprecation_notice": "This endpoint is deprecated. Please use /health instead."
    }


def custom_openapi():
    """Customize OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ValidaHub API",
        version=settings.version,
        description="Professional CSV validation and correction API for e-commerce marketplaces",
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT authentication token"
        },
        "apiKey": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key authentication"
        }
    }
    
    # Add global parameters
    if "parameters" not in openapi_schema["components"]:
        openapi_schema["components"]["parameters"] = {}
    
    openapi_schema["components"]["parameters"].update({
        "correlationId": {
            "name": "X-Correlation-Id",
            "in": "header",
            "description": "Correlation ID for request tracking",
            "required": False,
            "schema": {"type": "string", "format": "uuid"}
        },
        "idempotencyKey": {
            "name": "Idempotency-Key",
            "in": "header",
            "description": "Idempotency key for safe retries",
            "required": False,
            "schema": {"type": "string"}
        }
    })
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)