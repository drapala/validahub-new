"""Tests for email validator."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.validators.email_validator import validate_email


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

