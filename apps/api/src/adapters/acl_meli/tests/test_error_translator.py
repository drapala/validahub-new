"""
Unit tests for MELI error translator.
"""

import pytest

from ..models.meli_models import MeliApiError
from ..errors.meli_error_translator import (
    MeliErrorTranslator,
    CanonicalErrorCode,
    CanonicalError
)


class TestMeliErrorTranslator:
    """Test cases for the MELI error translator."""
    
    @pytest.fixture
    def translator(self):
        """Create error translator instance."""
        return MeliErrorTranslator()
    
    def test_translate_auth_error(self, translator):
        """Test translation of authentication error."""
        meli_error = MeliApiError(
            message="Invalid access token",
            error="invalid_token",
            status=401
        )
        
        canonical_error = translator.translate_api_error(meli_error)
        
        assert canonical_error.code == CanonicalErrorCode.AUTH_FAILED
        assert canonical_error.message == "Invalid access token"
        assert canonical_error.recoverable is True
        assert canonical_error.details["status_code"] == 401
    
    def test_translate_validation_error(self, translator):
        """Test translation of validation error."""
        meli_error = MeliApiError(
            message="Required parameter missing",
            error="required_parameter",
            status=400,
            cause=[{"field": "title", "code": "required"}]
        )
        
        canonical_error = translator.translate_api_error(meli_error)
        
        assert canonical_error.code == CanonicalErrorCode.REQUIRED_FIELD_MISSING
        assert canonical_error.field == "title"
        assert canonical_error.recoverable is False
    
    def test_translate_rate_limit_error(self, translator):
        """Test translation of rate limit error."""
        meli_error = MeliApiError(
            message="Too many requests",
            error="too_many_requests",
            status=429
        )
        
        canonical_error = translator.translate_api_error(meli_error)
        
        assert canonical_error.code == CanonicalErrorCode.RATE_LIMIT_EXCEEDED
        assert canonical_error.recoverable is True
        assert canonical_error.retry_after == 60
    
    def test_translate_unknown_error(self, translator):
        """Test translation of unknown error."""
        meli_error = MeliApiError(
            message="Something went wrong",
            error="unknown_error_code",
            status=500
        )
        
        canonical_error = translator.translate_api_error(meli_error)
        
        assert canonical_error.code == CanonicalErrorCode.UNKNOWN_ERROR
        assert canonical_error.message == "Something went wrong"
    
    def test_translate_http_errors(self, translator):
        """Test translation of HTTP status codes."""
        # 400 Bad Request
        error = translator.translate_http_error(400, "Invalid request")
        assert error.code == CanonicalErrorCode.VALIDATION_ERROR
        assert error.message == "Invalid request"
        
        # 401 Unauthorized
        error = translator.translate_http_error(401)
        assert error.code == CanonicalErrorCode.AUTH_FAILED
        assert error.message == "Authentication failed"
        
        # 403 Forbidden
        error = translator.translate_http_error(403)
        assert error.code == CanonicalErrorCode.INSUFFICIENT_PERMISSIONS
        
        # 404 Not Found
        error = translator.translate_http_error(404)
        assert error.code == CanonicalErrorCode.ITEM_NOT_FOUND
        
        # 429 Too Many Requests
        error = translator.translate_http_error(429)
        assert error.code == CanonicalErrorCode.RATE_LIMIT_EXCEEDED
        assert error.retry_after == 60
        
        # 500 Internal Server Error
        error = translator.translate_http_error(500)
        assert error.code == CanonicalErrorCode.INTERNAL_ERROR
        
        # 503 Service Unavailable
        error = translator.translate_http_error(503)
        assert error.code == CanonicalErrorCode.SERVICE_UNAVAILABLE
        assert error.recoverable is True
    
    def test_translate_validation_error_list(self, translator):
        """Test translation of validation error list."""
        validation_errors = [
            {
                "type": "required",
                "field": "title",
                "message": "Title is required"
            },
            {
                "type": "format",
                "field": "price",
                "message": "Invalid price format"
            },
            {
                "type": "range",
                "field": "quantity",
                "message": "Quantity out of range"
            }
        ]
        
        canonical_errors = translator.translate_validation_errors(validation_errors)
        
        assert len(canonical_errors) == 3
        
        # Check first error
        assert canonical_errors[0].code == CanonicalErrorCode.REQUIRED_FIELD_MISSING
        assert canonical_errors[0].field == "title"
        
        # Check second error
        assert canonical_errors[1].code == CanonicalErrorCode.INVALID_FORMAT
        assert canonical_errors[1].field == "price"
        
        # Check third error
        assert canonical_errors[2].code == CanonicalErrorCode.VALUE_OUT_OF_RANGE
        assert canonical_errors[2].field == "quantity"
    
    def test_error_summary(self, translator):
        """Test error summary creation."""
        errors = [
            CanonicalError(
                code=CanonicalErrorCode.REQUIRED_FIELD_MISSING,
                message="Title is required",
                field="title"
            ),
            CanonicalError(
                code=CanonicalErrorCode.REQUIRED_FIELD_MISSING,
                message="Price is required",
                field="price"
            ),
            CanonicalError(
                code=CanonicalErrorCode.INVALID_FORMAT,
                message="Invalid date format",
                field="date",
                recoverable=True
            )
        ]
        
        summary = translator.create_error_summary(errors)
        
        assert summary["total_errors"] == 3
        assert summary["recoverable_errors"] == 1
        assert summary["errors_by_code"]["REQUIRED_FIELD_MISSING"] == 2
        assert summary["errors_by_code"]["INVALID_FORMAT"] == 1
        assert "title" in summary["errors_by_field"]
        assert "price" in summary["errors_by_field"]
        assert len(summary["errors"]) == 3
    
    def test_canonical_error_to_dict(self, translator):
        """Test canonical error dictionary conversion."""
        error = CanonicalError(
            code=CanonicalErrorCode.RATE_LIMIT_EXCEEDED,
            message="Too many requests",
            details={"requests_made": 100},
            field="api_call",
            severity="WARNING",
            recoverable=True,
            retry_after=60
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["code"] == "RATE_LIMIT_EXCEEDED"
        assert error_dict["message"] == "Too many requests"
        assert error_dict["field"] == "api_call"
        assert error_dict["severity"] == "WARNING"
        assert error_dict["recoverable"] is True
        assert error_dict["retry_after"] == 60
        assert error_dict["details"]["requests_made"] == 100
