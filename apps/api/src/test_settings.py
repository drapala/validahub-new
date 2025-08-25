"""
Test-specific settings and configurations.
This file contains settings that should only be used during testing.
"""

import os
from typing import Any, Dict

# Test database configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://validahub:validahub@localhost:5432/validahub_test"
)

# Test Redis configuration  
TEST_REDIS_URL = os.getenv(
    "TEST_REDIS_URL",
    "redis://localhost:6379/1"  # Use different DB number for tests
)

# SQLAlchemy test configuration
SQLALCHEMY_TEST_CONFIG = {
    "pool_size": 1,
    "max_overflow": 0,
    "pool_pre_ping": True,
    "echo": False,  # Set to True for SQL debugging in tests
}

# Base model configuration for tests
# Enable extend_existing to allow model redefinition in tests
BASE_MODEL_CONFIG = {
    "__table_args__": {"extend_existing": True}
}

def get_test_db_config() -> Dict[str, Any]:
    """Get database configuration for tests."""
    return {
        "url": TEST_DATABASE_URL,
        **SQLALCHEMY_TEST_CONFIG
    }

def get_test_redis_config() -> Dict[str, Any]:
    """Get Redis configuration for tests."""
    return {
        "url": TEST_REDIS_URL,
        "decode_responses": True,
        "socket_keepalive": True,
        "socket_connect_timeout": 5,
    }

def is_test_environment() -> bool:
    """Check if we're running in a test environment."""
    return any([
        os.getenv("PYTEST_CURRENT_TEST"),
        os.getenv("APP_ENV") == "test",
        os.getenv("ENV") == "test",
        "pytest" in os.getenv("_", ""),
    ])

# Test-specific feature flags
TEST_FEATURE_FLAGS = {
    "enable_mock_auth": True,
    "enable_debug_endpoints": True,
    "disable_rate_limiting": True,
    "use_in_memory_cache": True,
    "skip_external_api_calls": True,
}

# Test user for authentication
TEST_USER = {
    "id": "00000000-0000-0000-0000-000000000001",
    "email": "test@validahub.com",
    "name": "Test User",
    "is_admin": True,
}

# Fixtures path
FIXTURES_PATH = os.path.join(os.path.dirname(__file__), "tests", "fixtures")