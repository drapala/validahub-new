from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details for HTTP APIs"""
    
    type: str = Field(
        default="about:blank",
        description="URI reference that identifies the problem type"
    )
    title: str = Field(
        ...,
        description="Short, human-readable summary of the problem type"
    )
    status: int = Field(
        ...,
        description="HTTP status code",
        ge=100,
        le=599
    )
    detail: Optional[str] = Field(
        None,
        description="Human-readable explanation specific to this occurrence"
    )
    instance: Optional[str] = Field(
        None,
        description="URI reference that identifies the specific occurrence"
    )
    extensions: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional problem-specific information"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the error occurred"
    )
    correlation_id: Optional[str] = Field(
        None,
        description="Correlation ID for tracing"
    )


class ValidationProblemDetail(ProblemDetail):
    """Extended problem detail for validation errors"""
    
    type: str = Field(default="/errors/validation-failed")
    title: str = Field(default="Validation Failed")
    status: int = Field(default=422)
    
    validation_errors: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed validation errors by field"
    )


class FileSizeProblemDetail(ProblemDetail):
    """Problem detail for file size errors"""
    
    type: str = Field(default="/errors/file-too-large")
    title: str = Field(default="File Too Large")
    status: int = Field(default=413)
    
    max_size_bytes: Optional[int] = Field(None)
    actual_size_bytes: Optional[int] = Field(None)


class RateLimitProblemDetail(ProblemDetail):
    """Problem detail for rate limit errors"""
    
    type: str = Field(default="/errors/rate-limit-exceeded")
    title: str = Field(default="Rate Limit Exceeded")
    status: int = Field(default=429)
    
    retry_after_seconds: Optional[int] = Field(None)
    rate_limit_remaining: Optional[int] = Field(None)
    rate_limit_reset: Optional[datetime] = Field(None)