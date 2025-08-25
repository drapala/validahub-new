"""
Error translator for MELI API errors.
Maps MELI-specific errors to canonical error format.
"""

from typing import Dict, Any, List, Optional
from enum import Enum

from core.logging_config import get_logger
from ..models.meli_models import MeliApiError

logger = get_logger(__name__)


class CanonicalErrorCode(str, Enum):
    """Canonical error codes for marketplace errors."""
    
    # Authentication and Authorization
    AUTH_FAILED = "AUTH_FAILED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Validation Errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_VALUE = "INVALID_VALUE"
    VALUE_OUT_OF_RANGE = "VALUE_OUT_OF_RANGE"
    
    # Business Logic Errors
    CATEGORY_NOT_FOUND = "CATEGORY_NOT_FOUND"
    INVALID_CATEGORY = "INVALID_CATEGORY"
    ITEM_NOT_FOUND = "ITEM_NOT_FOUND"
    DUPLICATE_ITEM = "DUPLICATE_ITEM"
    
    # Rate Limiting and Quotas
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    
    # System Errors
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    
    # Unknown
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class CanonicalError:
    """Canonical error representation."""
    
    def __init__(
        self,
        code: CanonicalErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None,
        severity: str = "ERROR",
        recoverable: bool = False,
        retry_after: Optional[int] = None
    ):
        """
        Initialize canonical error.
        
        Args:
            code: Canonical error code
            message: Human-readable error message
            details: Additional error details
            field: Field that caused the error (for validation errors)
            severity: Error severity (ERROR, WARNING, INFO)
            recoverable: Whether the error is recoverable
            retry_after: Seconds to wait before retry (for rate limiting)
        """
        self.code = code
        self.message = message
        self.details = details or {}
        self.field = field
        self.severity = severity
        self.recoverable = recoverable
        self.retry_after = retry_after
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "code": self.code.value if isinstance(self.code, CanonicalErrorCode) else self.code,
            "message": self.message,
            "severity": self.severity,
            "recoverable": self.recoverable
        }
        
        if self.field:
            result["field"] = self.field
        if self.details:
            result["details"] = self.details
        if self.retry_after:
            result["retry_after"] = self.retry_after
        
        return result


class MeliErrorTranslator:
    """
    Translates MELI-specific errors to canonical error format.
    
    This translator handles:
    - Error code mapping
    - Message extraction
    - Field identification
    - Severity determination
    - Recovery hints
    """
    
    # Map MELI error codes to canonical codes
    ERROR_CODE_MAPPING = {
        # Authentication errors
        "invalid_token": CanonicalErrorCode.AUTH_FAILED,
        "expired_token": CanonicalErrorCode.TOKEN_EXPIRED,
        "forbidden": CanonicalErrorCode.INSUFFICIENT_PERMISSIONS,
        "unauthorized": CanonicalErrorCode.AUTH_FAILED,
        
        # Validation errors
        "validation_error": CanonicalErrorCode.VALIDATION_ERROR,
        "required_parameter": CanonicalErrorCode.REQUIRED_FIELD_MISSING,
        "invalid_parameter": CanonicalErrorCode.INVALID_VALUE,
        "invalid_format": CanonicalErrorCode.INVALID_FORMAT,
        "out_of_range": CanonicalErrorCode.VALUE_OUT_OF_RANGE,
        
        # Business logic errors
        "category_not_found": CanonicalErrorCode.CATEGORY_NOT_FOUND,
        "invalid_category": CanonicalErrorCode.INVALID_CATEGORY,
        "item_not_found": CanonicalErrorCode.ITEM_NOT_FOUND,
        "duplicated_item": CanonicalErrorCode.DUPLICATE_ITEM,
        
        # Rate limiting
        "too_many_requests": CanonicalErrorCode.RATE_LIMIT_EXCEEDED,
        "quota_exceeded": CanonicalErrorCode.QUOTA_EXCEEDED,
        
        # System errors
        "service_unavailable": CanonicalErrorCode.SERVICE_UNAVAILABLE,
        "internal_server_error": CanonicalErrorCode.INTERNAL_ERROR,
        "timeout": CanonicalErrorCode.TIMEOUT,
        "connection_error": CanonicalErrorCode.NETWORK_ERROR
    }
    
    # Recoverable error codes
    RECOVERABLE_ERRORS = {
        CanonicalErrorCode.RATE_LIMIT_EXCEEDED,
        CanonicalErrorCode.SERVICE_UNAVAILABLE,
        CanonicalErrorCode.TIMEOUT,
        CanonicalErrorCode.NETWORK_ERROR,
        CanonicalErrorCode.TOKEN_EXPIRED
    }
    
    def translate_api_error(self, meli_error: MeliApiError, headers: Optional[Dict[str, str]] = None) -> CanonicalError:
        """
        Translate a MELI API error to canonical format.
        
        Args:
            meli_error: MELI API error
            
        Returns:
            Canonical error
        """
        # Map error code (handle missing or None error field)
        error_code = meli_error.error if meli_error.error else "unknown"
        canonical_code = self.ERROR_CODE_MAPPING.get(
            error_code.lower(),
            CanonicalErrorCode.UNKNOWN_ERROR
        )
        
        # Determine if recoverable
        recoverable = canonical_code in self.RECOVERABLE_ERRORS
        
        # Extract field information from cause
        field = None
        if meli_error.cause:
            field = self._extract_field_from_cause(meli_error.cause)
        
        # Determine retry_after for rate limiting
        retry_after = None
        if canonical_code == CanonicalErrorCode.RATE_LIMIT_EXCEEDED:
            retry_after = self._parse_retry_after(headers) if headers else 60
        
        # Create details dictionary
        details = {
            "original_error": error_code,
            "status_code": meli_error.status
        }
        if meli_error.cause:
            details["cause"] = meli_error.cause
        
        return CanonicalError(
            code=canonical_code,
            message=meli_error.message,
            details=details,
            field=field,
            severity="ERROR",
            recoverable=recoverable,
            retry_after=retry_after
        )
    
    def translate_validation_errors(self, validation_errors: List[Dict[str, Any]]) -> List[CanonicalError]:
        """
        Translate a list of validation errors.
        
        Args:
            validation_errors: List of validation error dictionaries
            
        Returns:
            List of canonical errors
        """
        canonical_errors = []
        
        for error in validation_errors:
            canonical_error = self._translate_validation_error(error)
            canonical_errors.append(canonical_error)
        
        return canonical_errors
    
    def translate_http_error(self, status_code: int, message: Optional[str] = None, headers: Optional[Dict[str, str]] = None) -> CanonicalError:
        """
        Translate HTTP status code to canonical error.
        
        Args:
            status_code: HTTP status code
            message: Optional error message
            
        Returns:
            Canonical error
        """
        if status_code == 400:
            code = CanonicalErrorCode.VALIDATION_ERROR
            default_message = "Bad request"
        elif status_code == 401:
            code = CanonicalErrorCode.AUTH_FAILED
            default_message = "Authentication failed"
        elif status_code == 403:
            code = CanonicalErrorCode.INSUFFICIENT_PERMISSIONS
            default_message = "Insufficient permissions"
        elif status_code == 404:
            code = CanonicalErrorCode.ITEM_NOT_FOUND
            default_message = "Resource not found"
        elif status_code == 429:
            code = CanonicalErrorCode.RATE_LIMIT_EXCEEDED
            default_message = "Rate limit exceeded"
        elif status_code == 500:
            code = CanonicalErrorCode.INTERNAL_ERROR
            default_message = "Internal server error"
        elif status_code == 502:
            code = CanonicalErrorCode.SERVICE_UNAVAILABLE
            default_message = "Bad gateway"
        elif status_code == 503:
            code = CanonicalErrorCode.SERVICE_UNAVAILABLE
            default_message = "Service unavailable"
        elif status_code == 504:
            code = CanonicalErrorCode.SERVICE_UNAVAILABLE
            default_message = "Gateway timeout"
        else:
            code = CanonicalErrorCode.UNKNOWN_ERROR
            default_message = f"HTTP error {status_code}"
        
        # Parse Retry-After header if available
        retry_after = None
        if code == CanonicalErrorCode.RATE_LIMIT_EXCEEDED or code == CanonicalErrorCode.SERVICE_UNAVAILABLE:
            retry_after = self._parse_retry_after(headers) if headers else 60
        
        return CanonicalError(
            code=code,
            message=message or default_message,
            details={"status_code": status_code},
            recoverable=code in self.RECOVERABLE_ERRORS,
            retry_after=retry_after
        )
    
    def _translate_validation_error(self, error: Dict[str, Any]) -> CanonicalError:
        """
        Translate a single validation error.
        
        Args:
            error: Validation error dictionary
            
        Returns:
            Canonical error
        """
        # Extract error type
        error_type = error.get("type", "validation_error")
        field = error.get("field", error.get("attribute"))
        message = error.get("message", "Validation failed")
        
        # Map to canonical code
        if error_type == "required":
            code = CanonicalErrorCode.REQUIRED_FIELD_MISSING
        elif error_type in ["format", "pattern"]:
            code = CanonicalErrorCode.INVALID_FORMAT
        elif error_type in ["min", "max", "range"]:
            code = CanonicalErrorCode.VALUE_OUT_OF_RANGE
        elif error_type == "invalid":
            code = CanonicalErrorCode.INVALID_VALUE
        else:
            code = CanonicalErrorCode.VALIDATION_ERROR
        
        return CanonicalError(
            code=code,
            message=message,
            field=field,
            details=error,
            severity="ERROR",
            recoverable=False
        )
    
    def _extract_field_from_cause(self, cause: List[Dict[str, Any]]) -> Optional[str]:
        """
        Extract field name from error cause.
        
        Args:
            cause: List of cause dictionaries
            
        Returns:
            Field name or None
        """
        if not cause:
            return None
        
        for item in cause:
            if "field" in item:
                return item["field"]
            if "attribute" in item:
                return item["attribute"]
            if "parameter" in item:
                return item["parameter"]
        
        return None
    
    def create_error_summary(self, errors: List[CanonicalError]) -> Dict[str, Any]:
        """
        Create a summary of errors.
        
        Args:
            errors: List of canonical errors
            
        Returns:
            Error summary dictionary
        """
        summary = {
            "total_errors": len(errors),
            "recoverable_errors": sum(1 for e in errors if e.recoverable),
            "errors_by_code": {},
            "errors_by_field": {},
            "errors": [e.to_dict() for e in errors]
        }
        
        # Group by error code
        for error in errors:
            code = error.code.value if isinstance(error.code, CanonicalErrorCode) else error.code
            if code not in summary["errors_by_code"]:
                summary["errors_by_code"][code] = 0
            summary["errors_by_code"][code] += 1
        
        # Group by field
        for error in errors:
            if error.field:
                if error.field not in summary["errors_by_field"]:
                    summary["errors_by_field"][error.field] = []
                summary["errors_by_field"][error.field].append(error.message)
        
        return summary
    
    def _parse_retry_after(self, headers: Dict[str, str]) -> int:
        """
        Parse Retry-After header from API response.
        
        Args:
            headers: Response headers
            
        Returns:
            Number of seconds to wait, default 60 if not found
        """
        retry_after = headers.get("retry-after") or headers.get("Retry-After")
        if retry_after:
            try:
                # Could be seconds (integer) or HTTP date
                return int(retry_after)
            except ValueError:
                # If it's a date, calculate seconds from now
                from datetime import datetime
                try:
                    retry_date = datetime.strptime(retry_after, "%a, %d %b %Y %H:%M:%S GMT")
                    seconds = (retry_date - datetime.utcnow()).total_seconds()
                    return max(int(seconds), 1)
                except ValueError:
                    pass
        return 60  # Default fallback
