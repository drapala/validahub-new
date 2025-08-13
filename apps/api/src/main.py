from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.config import settings
from src.db.base import engine, Base
from src.api import validate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up ValidaHub API...")
    yield
    logger.info("Shutting down ValidaHub API...")


app = FastAPI(
    title="ValidaHub API",
    version=settings.version,
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url="/redoc" if settings.app_env == "development" else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(validate.router)


@app.get("/status")
async def get_status():
    """Health check endpoint."""
    return {
        "ok": True,
        "version": settings.version,
        "environment": settings.app_env,
        "services": {
            "api": "up",
            "database": "up",
            "redis": "up",
            "s3": "up"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)