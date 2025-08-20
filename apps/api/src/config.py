"""Legacy configuration adapter.
Migrating to core.settings module."""

from typing import List
from .core.settings import get_settings as get_new_settings


class Settings:
    """Adapter class for legacy configuration.
    Provides backward compatibility while migrating to new settings.
    """
    
    def __init__(self):
        self._settings = get_new_settings()
    
    @property
    def app_env(self) -> str:
        return self._settings.environment.value
    
    @property
    def secret_key(self) -> str:
        return self._settings.security.secret_key
    
    @property
    def algorithm(self) -> str:
        return self._settings.security.algorithm
    
    @property
    def access_token_expire_minutes(self) -> int:
        return self._settings.security.access_token_expire_minutes
    
    @property
    def version(self) -> str:
        return self._settings.app_version
    
    @property
    def database_url(self) -> str:
        return str(self._settings.database.url)
    
    @property
    def redis_url(self) -> str:
        return str(self._settings.redis.url)
    
    @property
    def s3_endpoint(self) -> str:
        return self._settings.storage.s3_endpoint_url or "http://localhost:9000"
    
    @property
    def s3_access_key(self) -> str:
        return self._settings.storage.s3_access_key_id or "minioadmin"
    
    @property
    def s3_secret_key(self) -> str:
        return self._settings.storage.s3_secret_access_key or "minioadmin"
    
    @property
    def s3_bucket(self) -> str:
        return self._settings.storage.s3_bucket or "validahub"
    
    @property
    def s3_region(self) -> str:
        return self._settings.storage.s3_region
    
    @property
    def api_host(self) -> str:
        return "0.0.0.0"
    
    @property
    def api_port(self) -> int:
        return 3001
    
    @property
    def cors_origins(self) -> str:
        return ",".join(self._settings.security.cors_origins)
    
    @property
    def cors_origins_list(self) -> List[str]:
        return self._settings.security.cors_origins


# Global settings instance for backward compatibility
settings = Settings()