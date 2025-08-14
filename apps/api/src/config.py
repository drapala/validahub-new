from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    version: str = "0.1.0"
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://validahub:validahub_dev_2024@localhost:5432/validahub_db"
    )
    
    # Redis
    redis_url: str = os.getenv(
        "REDIS_URL",
        "redis://:redis_dev_2024@localhost:6379/0"
    )
    
    # S3/MinIO
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "validahub"
    s3_region: str = "us-east-1"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 3001
    cors_origins: str = "http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()