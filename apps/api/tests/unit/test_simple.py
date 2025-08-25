"""
Simple test to verify testing setup works.
"""

import pytest


def test_basic_math():
    """Test that basic math works."""
    assert 2 + 2 == 4


def test_string_operations():
    """Test basic string operations."""
    text = "ValidaHub"
    assert text.lower() == "validahub"
    assert text.upper() == "VALIDAHUB"


@pytest.mark.unit
class TestSimpleClass:
    """Simple test class."""
    
    def test_list_operations(self):
        """Test list operations."""
        items = [1, 2, 3]
        items.append(4)
        assert len(items) == 4
        assert items[-1] == 4
    
    def test_dict_operations(self):
        """Test dictionary operations."""
        data = {"key": "value"}
        data["new_key"] = "new_value"
        assert "new_key" in data
        assert data.get("missing", "default") == "default"