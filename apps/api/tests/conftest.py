"""
Global pytest fixtures and configuration for all tests.
Enhanced with deterministic data, proper isolation, and anti-flakiness measures.
"""

import pytest
import asyncio
import os
from datetime import datetime
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
import tempfile
import freezegun
from faker import Faker

# Add src to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.main import app
from src.core.settings import Settings, get_settings


# ============== Deterministic Configuration ==============

# Fixed seeds for reproducible tests
FAKER_SEED = 12345
RANDOM_SEED = 42
FIXED_TIME = "2024-08-24 12:00:00"

@pytest.fixture(scope="session", autouse=True)
def configure_determinism():
    """Configure deterministic behavior for all tests."""
    # Set random seeds
    import random
    random.seed(RANDOM_SEED)
    
    # Configure faker
    fake = Faker()
    fake.seed_instance(FAKER_SEED)
    
    # Set environment for tests
    os.environ["TESTING"] = "true"
    os.environ["PYTHONHASHSEED"] = str(RANDOM_SEED)


# ============== Time and Data Fixtures ==============

@pytest.fixture
def fixed_time():
    """Freeze time for deterministic tests."""
    with freezegun.freeze_time(FIXED_TIME):
        yield datetime.fromisoformat(FIXED_TIME)


@pytest.fixture
def seeded_faker():
    """Faker instance with fixed seed."""
    fake = Faker('pt_BR')  # Brazilian locale for realistic data
    fake.seed_instance(FAKER_SEED)
    return fake


# ============== Configuration Fixtures ==============

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Override settings for testing."""
    return Settings(
        environment="testing",
        debug=True,
        database={
            "url": "postgresql://test:test@localhost:5432/test_db",
            "echo": False
        },
        redis={
            "url": "redis://localhost:6379/1"
        },
        telemetry={
            "enabled": False  # Disable telemetry in tests
        },
        security={
            "secret_key": "test-secret-key-do-not-use-in-production"
        }
    )


@pytest.fixture
def mock_settings(test_settings, monkeypatch):
    """Mock get_settings to return test settings."""
    monkeypatch.setattr("src.core.settings.get_settings", lambda: test_settings)
    return test_settings


# ============== API Client Fixtures ==============

@pytest.fixture
def client(mock_settings) -> TestClient:
    """Create FastAPI test client with isolation."""
    return TestClient(app)


@pytest.fixture
async def async_client(mock_settings):
    """Create async FastAPI test client."""
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============== Database Fixtures ==============

@pytest.fixture
async def isolated_db():
    """Create isolated database session with rollback."""
    # In a real implementation, this would use:
    # - Testcontainers for database isolation
    # - Transaction rollback for cleanup
    # - Separate test database
    
    # Mock implementation for now
    db = Mock()
    
    # Setup
    transaction = Mock()
    db.begin = Mock(return_value=transaction)
    
    yield db
    
    # Cleanup - rollback transaction
    transaction.rollback()


@pytest.fixture
def mock_db_session():
    """Mock database session for unit tests."""
    session = Mock()
    session.commit = Mock()
    session.rollback = Mock() 
    session.close = Mock()
    session.query = Mock()
    session.add = Mock()
    session.delete = Mock()
    return session


# ============== File and Storage Fixtures ==============

@pytest.fixture
def temp_csv_file(tmp_path, seeded_faker):
    """Create temporary CSV file with deterministic content."""
    csv_content = "product_id,title,price,stock,category,brand\n"
    
    # Generate deterministic test data
    for i in range(10):
        csv_content += f"ML{i:06d},{seeded_faker.sentence(nb_words=3)},{seeded_faker.pyfloat(min_value=10, max_value=1000, right_digits=2)},{seeded_faker.random_int(min=0, max=100)},Electronics,{seeded_faker.company()}\n"
    
    file_path = tmp_path / "test.csv"
    file_path.write_text(csv_content, encoding='utf-8')
    return str(file_path)


@pytest.fixture  
def large_csv_file(tmp_path, seeded_faker):
    """Create large CSV file for performance testing."""
    csv_lines = ["product_id,title,price,stock,category,brand"]
    
    # Generate deterministic large dataset
    for i in range(10000):
        title = f"Product {i:05d}"  # Predictable titles
        price = round(i * 0.99 + 10, 2)  # Deterministic prices
        stock = i % 100  # Predictable stock
        csv_lines.append(f"ML{i:06d},{title},{price},{stock},Category{i%10},Brand{i%5}")
    
    file_path = tmp_path / "large_test.csv"
    file_path.write_text("\n".join(csv_lines), encoding='utf-8')
    return str(file_path)


@pytest.fixture
def invalid_csv_file(tmp_path):
    """Create CSV with known validation errors."""
    csv_content = """product_id,title,price,stock,category,brand
,Missing ID Product,99.99,10,Electronics,Apple
ML123456,"Product with ""quotes""",invalid_price,abc,Electronics,Samsung  
ML789012,Valid Product,-50.00,5,,
"""
    file_path = tmp_path / "invalid.csv"
    file_path.write_text(csv_content, encoding='utf-8')
    return str(file_path)


# ============== Mock Service Fixtures ==============

@pytest.fixture
def mock_validation_service(seeded_faker):
    """Mock validation service with predictable responses."""
    service = Mock()
    
    # Default successful validation
    service.validate_csv = AsyncMock(return_value={
        "status": "completed",
        "total_rows": 100,
        "valid_rows": 95,
        "invalid_rows": 5,
        "processing_time_ms": 1500,  # Deterministic processing time
        "errors": [
            {
                "row": 3,
                "field": "price", 
                "message": "Price must be positive",
                "severity": "ERROR",
                "value": -50.00
            }
        ]
    })
    
    service.validate_row = Mock(return_value={
        "is_valid": True,
        "errors": []
    })
    
    return service


@pytest.fixture
def mock_s3_client():
    """Mock S3 client for storage tests."""
    client = Mock()
    client.upload_file = Mock(return_value="s3://test-bucket/file.csv")
    client.download_file = Mock()
    client.delete_file = Mock(return_value=True)
    client.generate_presigned_url = Mock(return_value="https://test-signed-url.com")
    client.list_objects = Mock(return_value=[])
    return client


@pytest.fixture
def mock_redis_client():
    """Mock Redis client with predictable behavior."""
    client = Mock()
    client.get = Mock(return_value=None)
    client.set = Mock(return_value=True)
    client.delete = Mock(return_value=1)
    client.expire = Mock(return_value=True)
    client.exists = Mock(return_value=False)
    client.ttl = Mock(return_value=-1)
    return client


@pytest.fixture
def mock_celery_app():
    """Mock Celery app for task testing."""
    app = Mock()
    task_result = Mock()
    task_result.id = "test-task-12345"
    task_result.state = "PENDING"
    task_result.result = None
    
    app.send_task = Mock(return_value=task_result)
    app.control.inspect = Mock(return_value=Mock(
        active=Mock(return_value={}),
        scheduled=Mock(return_value={}),
        reserved=Mock(return_value={})
    ))
    return app


# ============== Authentication and User Fixtures ==============

@pytest.fixture
def auth_headers():
    """Authentication headers for protected endpoints."""
    return {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test-token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def admin_user(seeded_faker):
    """Admin user with predictable data."""
    return {
        "id": "admin-12345",
        "email": "admin@validahub.com", 
        "name": "Test Admin",
        "role": "admin",
        "is_active": True,
        "created_at": FIXED_TIME,
        "permissions": ["read", "write", "admin"]
    }


@pytest.fixture
def regular_user(seeded_faker):
    """Regular user with predictable data."""
    return {
        "id": "user-67890",
        "email": "user@example.com",
        "name": "Test User",
        "role": "user", 
        "is_active": True,
        "created_at": FIXED_TIME,
        "permissions": ["read"]
    }


# ============== Sample Data Fixtures ==============

@pytest.fixture
def valid_marketplace_data():
    """Valid marketplace validation data."""
    return {
        "marketplace": "mercado_livre",
        "category": "electronics",
        "rows": [
            {
                "product_id": "ML123456",
                "title": "iPhone 15 Pro Max 256GB",
                "price": 7999.99,
                "stock": 10,
                "category": "Celulares e Telefones",
                "brand": "Apple",
                "condition": "new",
                "shipping": "free"
            },
            {
                "product_id": "ML789012",
                "title": "Samsung Galaxy S24 Ultra 512GB", 
                "price": 5999.99,
                "stock": 25,
                "category": "Celulares e Telefones",
                "brand": "Samsung",
                "condition": "new",
                "shipping": "standard"
            }
        ]
    }


@pytest.fixture
def invalid_marketplace_data():
    """Invalid marketplace validation data."""
    return {
        "marketplace": "mercado_livre",
        "category": "electronics",
        "rows": [
            {
                "product_id": "",  # Missing required field
                "title": "Product without ID",
                "price": -100.00,  # Negative price
                "stock": "invalid",  # Invalid stock format
                "category": "",  # Missing category
                "brand": "A" * 51,  # Too long brand name
                "condition": "invalid_condition",  # Invalid condition
                "shipping": None  # Null shipping
            }
        ]
    }


# ============== Performance and Logging Fixtures ==============

@pytest.fixture
def capture_logs():
    """Capture log messages during tests."""
    import logging
    from io import StringIO
    
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    
    # Formatter to match production logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    
    yield log_capture
    
    logger.removeHandler(handler)


@pytest.fixture
def performance_monitor():
    """Monitor test performance and resource usage."""
    import time
    import psutil
    
    start_time = time.time()
    process = psutil.Process()
    start_memory = process.memory_info().rss
    
    yield {
        "start_time": start_time,
        "start_memory": start_memory
    }
    
    end_time = time.time()
    end_memory = process.memory_info().rss
    execution_time = end_time - start_time
    memory_delta = end_memory - start_memory
    
    # Log performance metrics
    print(f"\n📊 Test Performance:")
    print(f"   ⏱️  Execution time: {execution_time:.3f}s")
    print(f"   🧠 Memory delta: {memory_delta / 1024 / 1024:.2f} MB")
    
    # Warn on slow tests
    if execution_time > 1.0:
        print(f"⚠️  Slow test detected: {execution_time:.3f}s > 1.0s")


# ============== Cleanup and Utilities ==============

@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Automatically cleanup temporary files after each test."""
    yield
    
    # Cleanup temp files
    temp_dir = tempfile.gettempdir()
    for file in os.listdir(temp_dir):
        if file.startswith("test_validahub_"):
            try:
                os.remove(os.path.join(temp_dir, file))
            except:
                pass  # Ignore cleanup errors


@pytest.fixture
def mock_external_apis():
    """Mock external API calls for isolation."""
    with patch('httpx.AsyncClient.post') as mock_post, \
         patch('httpx.AsyncClient.get') as mock_get:
        
        # Default successful responses
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={"status": "success"}),
            text="OK"
        )
        mock_get.return_value = Mock(
            status_code=200, 
            json=Mock(return_value={"data": "test"}),
            text="OK"
        )
        
        yield {
            "post": mock_post,
            "get": mock_get
        }


# ============== Test Markers and Configuration ==============

def pytest_configure(config):
    """Register custom markers and configure pytest."""
    
    # Register markers
    markers = [
        "unit: Unit tests (fast, isolated)",
        "integration: Integration tests (database, external services)",
        "e2e: End-to-end tests (full system)",
        "contract: Contract tests (API schemas, Pact)",
        "slow: Slow running tests (>1s)",
        "flaky: Flaky tests (quarantined)",
        "security: Security-related tests",
        "performance: Performance tests",
        "mutation: Mutation testing",
        "smoke: Smoke tests for CI/CD"
    ]
    
    for marker in markers:
        config.addinivalue_line("markers", marker)


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on location and naming."""
    
    for item in items:
        # Mark by directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        elif "contract" in str(item.fspath):
            item.add_marker(pytest.mark.contract)
            
        # Mark slow tests
        if "slow" in item.name or "large" in item.name:
            item.add_marker(pytest.mark.slow)
            
        # Mark flaky tests (if explicitly marked in test name or docstring)
        if "flaky" in item.name or (item.function.__doc__ and "flaky" in item.function.__doc__.lower()):
            item.add_marker(pytest.mark.flaky)