"""
Centralized configuration using Pydantic Settings.
Provides type safety, validation, and environment variable loading.
"""

from typing import Set, Dict, Optional, List
from enum import Enum
from pydantic import Field, field_validator, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings
from functools import lru_cache


class Environment(str, Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class JobPlan(str, Enum):
    """Job subscription plans."""
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    url: PostgresDsn = Field(
        default="postgresql://validahub:validahub_dev_2024@localhost:5432/validahub_db",
        env="DATABASE_URL"
    )
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")
    echo: bool = Field(default=False, env="DB_ECHO")
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration."""
    url: RedisDsn = Field(
        default="redis://:redis_dev_2024@localhost:6379/0",
        env="REDIS_URL"
    )
    max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")
    socket_timeout: int = Field(default=5, env="REDIS_SOCKET_TIMEOUT")
    socket_connect_timeout: int = Field(default=5, env="REDIS_SOCKET_CONNECT_TIMEOUT")
    socket_keepalive: bool = Field(default=True, env="REDIS_SOCKET_KEEPALIVE")
    socket_keepalive_options: Optional[Dict] = Field(default=None, env="REDIS_SOCKET_KEEPALIVE_OPTIONS")
    
    class Config:
        env_prefix = "REDIS_"


class CelerySettings(BaseSettings):
    """Celery configuration."""
    broker_url: str = Field(
        default="redis://:redis_dev_2024@localhost:6379/1",
        env="CELERY_BROKER_URL"
    )
    result_backend: str = Field(
        default="redis://:redis_dev_2024@localhost:6379/2",
        env="CELERY_RESULT_BACKEND"
    )
    task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    accept_content: List[str] = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    timezone: str = Field(default="UTC", env="CELERY_TIMEZONE")
    enable_utc: bool = Field(default=True, env="CELERY_ENABLE_UTC")
    task_track_started: bool = Field(default=True, env="CELERY_TASK_TRACK_STARTED")
    task_time_limit: int = Field(default=300, env="CELERY_TASK_TIME_LIMIT")
    task_soft_time_limit: int = Field(default=270, env="CELERY_TASK_SOFT_TIME_LIMIT")
    worker_prefetch_multiplier: int = Field(default=1, env="CELERY_WORKER_PREFETCH_MULTIPLIER")
    worker_max_tasks_per_child: int = Field(default=1000, env="CELERY_WORKER_MAX_TASKS_PER_CHILD")
    
    class Config:
        env_prefix = "CELERY_"


class ValidationSettings(BaseSettings):
    """Validation configuration."""
    allowed_rulesets: Set[str] = Field(
        default={"default", "strict", "lenient", "minimal", "comprehensive"},
        env="ALLOWED_RULESETS"
    )
    max_csv_file_size: int = Field(
        default=1073741824,  # 1GB
        env="MAX_CSV_FILE_SIZE"
    )
    streaming_threshold: int = Field(
        default=104857600,  # 100MB
        env="STREAMING_THRESHOLD"
    )
    max_rows_per_batch: int = Field(default=1000, env="MAX_ROWS_PER_BATCH")
    max_validation_errors: int = Field(default=100, env="MAX_VALIDATION_ERRORS")
    
    @field_validator("allowed_rulesets", mode="before")
    @classmethod
    def parse_rulesets(cls, v):
        if isinstance(v, str):
            return set(r.strip() for r in v.split(","))
        return v
    
    class Config:
        env_prefix = "VALIDATION_"


class QueueSettings(BaseSettings):
    """Queue configuration."""
    valid_tasks: Set[str] = Field(
        default={
            "validate_csv_job",
            "correct_csv_job",
            "analyze_data_job",
            "export_results_job",
            "sync_connector_job",
            "generate_report_job"
        },
        env="VALID_TASKS"
    )
    task_mappings: Dict[str, str] = Field(
        default={
            "validate_csv_job": "src.workers.tasks.validate_csv_job",
            "correct_csv_job": "src.workers.tasks.correct_csv_job",
            "sync_connector_job": "src.workers.tasks.sync_connector_job",
            "generate_report_job": "src.workers.tasks.generate_report_job"
        },
        env="TASK_MAPPINGS"
    )
    queue_by_plan: Dict[JobPlan, str] = Field(
        default={
            JobPlan.FREE: "queue:free",
            JobPlan.PRO: "queue:pro",
            JobPlan.BUSINESS: "queue:business",
            JobPlan.ENTERPRISE: "queue:enterprise"
        }
    )
    validate_csv_time_limit: int = Field(default=300, env="VALIDATE_CSV_JOB_TIME_LIMIT")
    validate_csv_soft_limit: int = Field(default=270, env="VALIDATE_CSV_JOB_SOFT_TIME_LIMIT")
    correct_csv_time_limit: int = Field(default=600, env="CORRECT_CSV_JOB_TIME_LIMIT")
    correct_csv_soft_limit: int = Field(default=570, env="CORRECT_CSV_JOB_SOFT_TIME_LIMIT")
    default_time_limit: int = Field(default=300, env="DEFAULT_JOB_TIME_LIMIT")
    default_soft_limit: int = Field(default=270, env="DEFAULT_JOB_SOFT_TIME_LIMIT")
    
    @field_validator("valid_tasks", mode="before")
    @classmethod
    def parse_tasks(cls, v):
        if isinstance(v, str):
            return set(t.strip() for t in v.split(","))
        return v
    
    @field_validator("task_mappings", mode="before")
    @classmethod
    def parse_mappings(cls, v):
        if isinstance(v, str):
            mappings = {}
            for mapping in v.split(","):
                if ":" in mapping:
                    task, path = mapping.strip().split(":", 1)
                    mappings[task] = path
            return mappings
        return v
    
    class Config:
        env_prefix = "QUEUE_"


class SecuritySettings(BaseSettings):
    """Security configuration."""
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_prefix = "SECURITY_"


class StorageSettings(BaseSettings):
    """Storage configuration."""
    local_base_path: str = Field(default="/tmp/validahub", env="STORAGE_LOCAL_PATH")
    s3_bucket: Optional[str] = Field(default=None, env="S3_BUCKET")
    s3_region: str = Field(default="us-east-1", env="S3_REGION")
    s3_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    s3_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    s3_endpoint_url: Optional[str] = Field(default=None, env="S3_ENDPOINT_URL")
    max_upload_size: int = Field(default=5368709120, env="MAX_UPLOAD_SIZE")  # 5GB
    allowed_extensions: Set[str] = Field(
        default={".csv", ".xlsx", ".xls", ".json", ".xml"},
        env="ALLOWED_EXTENSIONS"
    )
    
    @field_validator("allowed_extensions", mode="before")
    @classmethod
    def parse_extensions(cls, v):
        if isinstance(v, str):
            return set(ext.strip() for ext in v.split(","))
        return v
    
    class Config:
        env_prefix = "STORAGE_"


class KafkaSettings(BaseSettings):
    """Kafka configuration for event streaming."""
    bootstrap_servers: List[str] = Field(
        default=["localhost:9092"],
        env="KAFKA_BOOTSTRAP_SERVERS"
    )
    telemetry_topic: str = Field(
        default="telemetry-events",
        env="KAFKA_TELEMETRY_TOPIC"
    )
    validation_events_topic: str = Field(
        default="validation-events",
        env="KAFKA_VALIDATION_TOPIC"
    )
    consumer_group: str = Field(
        default="validahub-consumer",
        env="KAFKA_CONSUMER_GROUP"
    )
    compression_type: str = Field(default="snappy", env="KAFKA_COMPRESSION_TYPE")
    batch_size: int = Field(default=16384, env="KAFKA_BATCH_SIZE")
    linger_ms: int = Field(default=100, env="KAFKA_LINGER_MS")
    
    @field_validator("bootstrap_servers", mode="before")
    @classmethod
    def parse_bootstrap_servers(cls, v):
        if isinstance(v, str):
            return [server.strip() for server in v.split(",")]
        return v
    
    class Config:
        env_prefix = "KAFKA_"


class TelemetrySettings(BaseSettings):
    """Telemetry and monitoring configuration."""
    enabled: bool = Field(default=True, env="TELEMETRY_ENABLED")
    service_name: str = Field(default="validahub-api", env="TELEMETRY_SERVICE_NAME")
    otel_exporter_endpoint: Optional[str] = Field(default=None, env="OTEL_EXPORTER_ENDPOINT")
    otel_exporter_headers: Optional[Dict[str, str]] = Field(default=None, env="OTEL_EXPORTER_HEADERS")
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    traces_enabled: bool = Field(default=True, env="TRACES_ENABLED")
    logs_enabled: bool = Field(default=True, env="LOGS_ENABLED")
    sampling_rate: float = Field(default=1.0, env="TELEMETRY_SAMPLING_RATE")
    
    # Event emission configuration
    enable_console_output: bool = Field(default=True, env="TELEMETRY_CONSOLE_OUTPUT")
    enable_file_output: bool = Field(default=False, env="TELEMETRY_FILE_OUTPUT")
    output_file: str = Field(default="/tmp/validahub_telemetry.jsonl", env="TELEMETRY_OUTPUT_FILE")
    enable_kafka: bool = Field(default=False, env="TELEMETRY_KAFKA_ENABLED")
    
    # Batching configuration
    batch_size: int = Field(default=100, env="TELEMETRY_BATCH_SIZE")
    flush_interval: int = Field(default=5, env="TELEMETRY_FLUSH_INTERVAL")
    
    @field_validator("sampling_rate")
    @classmethod
    def validate_sampling_rate(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Sampling rate must be between 0 and 1")
        return v
    
    @field_validator("batch_size")
    @classmethod
    def validate_batch_size(cls, v):
        if v < 1 or v > 10000:
            raise ValueError("Batch size must be between 1 and 10000")
        return v
    
    class Config:
        env_prefix = "TELEMETRY_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Application
    app_name: str = Field(default="ValidaHub API", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    
    # API
    api_prefix: str = Field(default="/api", env="API_PREFIX")
    docs_url: Optional[str] = Field(default="/docs", env="DOCS_URL")
    redoc_url: Optional[str] = Field(default="/redoc", env="REDOC_URL")
    openapi_url: Optional[str] = Field(default="/openapi.json", env="OPENAPI_URL")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")
    
    # Sub-configurations
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    celery: CelerySettings = CelerySettings()
    validation: ValidationSettings = ValidationSettings()
    queue: QueueSettings = QueueSettings()
    security: SecuritySettings = SecuritySettings()
    storage: StorageSettings = StorageSettings()
    kafka: KafkaSettings = KafkaSettings()
    telemetry: TelemetrySettings = TelemetrySettings()
    
    @field_validator("environment", mode="before")
    @classmethod
    def parse_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @field_validator("log_level", mode="before")
    @classmethod
    def parse_log_level(cls, v):
        if isinstance(v, str):
            return LogLevel(v.upper())
        return v
    
    @field_validator("docs_url", "redoc_url", "openapi_url")
    @classmethod
    def disable_docs_in_production(cls, v, info):
        if info.data.get("environment") == Environment.PRODUCTION and v:
            return None
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow extra fields for backward compatibility


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Convenience function for getting specific settings
def get_database_url() -> str:
    """Get database URL."""
    return get_settings().database.url


def get_redis_url() -> str:
    """Get Redis URL."""
    return get_settings().redis.url


def get_celery_broker_url() -> str:
    """Get Celery broker URL."""
    return get_settings().celery.broker_url


def is_production() -> bool:
    """Check if running in production."""
    return get_settings().environment == Environment.PRODUCTION


def is_development() -> bool:
    """Check if running in development."""
    return get_settings().environment == Environment.DEVELOPMENT


def is_testing() -> bool:
    """Check if running in testing."""
    return get_settings().environment == Environment.TESTING