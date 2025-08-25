"""Tests for product ID validator."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.validators.product_id_validator import validate_product_id


class TestValidateProductId:
    """Test product ID validation."""

    def test_valid_product_id(self):
        assert validate_product_id("ML123456") is True
        assert validate_product_id("ML999999") is True

    def test_invalid_prefix(self):
        assert validate_product_id("AB123456") is False
        assert validate_product_id("123456") is False

    def test_too_short(self):
        assert validate_product_id("ML123") is False
        assert validate_product_id("ML") is False

    def test_empty_product_id(self):
        assert validate_product_id("") is False

