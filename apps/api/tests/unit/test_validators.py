"""
Tests for validators module - used for mutation testing demo.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.validators import (
    validate_positive_number,
    validate_email,
    validate_product_id,
    calculate_discount
)


class TestValidatePositiveNumber:
    """Test positive number validation."""
    
    def test_positive_number(self):
        assert validate_positive_number(1.0) is True
        assert validate_positive_number(100.5) is True
        assert validate_positive_number(0.001) is True
    
    def test_negative_number(self):
        assert validate_positive_number(-1.0) is False
        assert validate_positive_number(-100.5) is False
    
    def test_zero(self):
        assert validate_positive_number(0.0) is False


class TestValidateEmail:
    """Test email validation."""
    
    def test_valid_email(self):
        assert validate_email("user@example.com") is True
        assert validate_email("test.user@domain.co.uk") is True
    
    def test_invalid_email_no_at(self):
        assert validate_email("userexample.com") is False
    
    def test_invalid_email_no_dot(self):
        assert validate_email("user@example") is False
    
    def test_empty_email(self):
        assert validate_email("") is False
        assert validate_email(" ") is False


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