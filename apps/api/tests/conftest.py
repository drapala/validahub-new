"""
Simplified pytest fixtures for testing.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from src.core.settings import Settings
    return Settings()

# Register custom markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "flaky: Flaky tests")