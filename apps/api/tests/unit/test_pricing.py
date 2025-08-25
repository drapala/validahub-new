"""Tests for pricing utilities."""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.validators.pricing import calculate_discount


class TestCalculateDiscount:
    """Test discount calculation."""

    def test_valid_discount(self):
        assert calculate_discount(100.0, 10.0) == 90.0
        assert calculate_discount(50.0, 50.0) == 25.0
        assert calculate_discount(100.0, 0.0) == 100.0
        assert calculate_discount(100.0, 100.0) == 0.0

    def test_invalid_price(self):
        with pytest.raises(ValueError, match="Price must be positive"):
            calculate_discount(0.0, 10.0)
        with pytest.raises(ValueError, match="Price must be positive"):
            calculate_discount(-10.0, 10.0)

    def test_invalid_discount(self):
        with pytest.raises(ValueError, match="Discount must be between"):
            calculate_discount(100.0, -10.0)
        with pytest.raises(ValueError, match="Discount must be between"):
            calculate_discount(100.0, 110.0)

