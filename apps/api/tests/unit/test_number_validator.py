"""Tests for number validator."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.validators.number_validator import validate_positive_number


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

