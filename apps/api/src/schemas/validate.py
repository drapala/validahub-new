from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal, Dict, Any
from enum import Enum
from datetime import datetime


class Marketplace(str, Enum):
    MERCADO_LIVRE = "MERCADO_LIVRE"
    SHOPEE = "SHOPEE"
    MAGALU = "MAGALU"
    AMAZON = "AMAZON"
    AMAZON_BR = "AMAZON_BR"
    AMERICANAS = "AMERICANAS"


class Category(str, Enum):
    ELETRONICOS = "ELETRONICOS"
    CELL_PHONE = "CELL_PHONE"
    MODA = "MODA"
    CASA = "CASA"
    ESPORTE = "ESPORTE"
    BELEZA = "BELEZA"
    LIVROS = "LIVROS"
    BRINQUEDOS = "BRINQUEDOS"
    ALIMENTOS = "ALIMENTOS"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ValidationStatus(str, Enum):
    """Status of a validation check"""
    PASS = "PASS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    INFO = "INFO"


class ErrorDetail(BaseModel):
    """Detailed error information"""
    code: str = Field(..., description="Error code/rule ID")
    message: str = Field(..., description="Human-readable error message")
    severity: Severity = Field(..., description="Error severity")
    field: Optional[str] = Field(None, description="Field/column name")
    value: Optional[Any] = Field(None, description="Current value")
    expected: Optional[Any] = Field(None, description="Expected value or format")


class CorrectionDetail(BaseModel):
    """Detailed correction information"""
    field: str = Field(..., description="Field/column name")
    original_value: Optional[Any] = Field(None, description="Original value")
    corrected_value: Any = Field(..., description="Corrected value")
    correction_type: str = Field(..., description="Type of correction applied")
    confidence: float = Field(1.0, description="Confidence score (0-1)", ge=0, le=1)


class ValidationItem(BaseModel):
    """Individual validation result for a row"""
    row_number: int = Field(..., description="Row number (1-indexed)")
    status: ValidationStatus = Field(..., description="Validation status")
    errors: List[ErrorDetail] = Field(default_factory=list, description="List of errors")
    corrections: List[CorrectionDetail] = Field(default_factory=list, description="List of corrections")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ValidationError(BaseModel):
    """Legacy validation error model - use ValidationItem instead"""
    rule_id: str = Field(..., description="Rule identifier")
    row: Optional[int] = Field(None, description="Row number where error occurred")
    field: Optional[str] = Field(None, description="Field/column name with error")
    severity: Severity = Field(..., description="Error severity")
    message: str = Field(..., description="Human-readable error message")
    before: Optional[Any] = Field(None, description="Original value")
    after: Optional[Any] = Field(None, description="Corrected value")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional rule metadata")


class ValidationSummary(BaseModel):
    """Summary statistics for validation results"""
    total_errors: int = Field(0, description="Total error count")
    total_warnings: int = Field(0, description="Total warning count")
    total_corrections: int = Field(0, description="Total corrections applied")
    error_types: Dict[str, int] = Field(default_factory=dict, description="Count by error type")
    processing_time_seconds: float = Field(..., description="Processing time in seconds")


class ValidationTotals(BaseModel):
    total_rows: int = Field(..., description="Total rows processed")
    valid_rows: int = Field(..., description="Number of valid rows")
    error_rows: int = Field(..., description="Number of rows with errors")
    errors_count: int = Field(0, description="Total errors count")
    warnings_count: int = Field(0, description="Total warnings count")
    info_count: int = Field(0, description="Total info messages count")


class ValidationResult(BaseModel):
    """Complete validation result with enhanced structure"""
    total_rows: int = Field(..., description="Total rows processed")
    valid_rows: int = Field(..., description="Number of valid rows")
    error_rows: int = Field(..., description="Number of rows with errors")
    validation_items: List[ValidationItem] = Field(default_factory=list, description="Detailed validation results")
    summary: ValidationSummary = Field(..., description="Summary statistics")
    corrected_data: Optional[Any] = Field(None, description="Corrected DataFrame if auto_fix was applied")
    marketplace: str = Field(..., description="Marketplace used for validation")
    category: Optional[str] = Field(None, description="Category used for validation")
    auto_fix_applied: bool = Field(False, description="Whether auto-fix was applied")
    job_id: Optional[str] = Field(None, description="Job ID for tracking")


class ValidateCsvRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    marketplace: Marketplace = Field(..., description="Target marketplace")
    category: Category = Field(..., description="Product category")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional validation options")


class CorrectCsvRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    marketplace: Marketplace = Field(..., description="Target marketplace")
    category: Category = Field(..., description="Product category")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional correction options")


class CorrectionPreviewRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    marketplace: Marketplace = Field(..., description="Target marketplace")
    category: Category = Field(..., description="Product category")
    sample_strategy: Literal["head", "random"] = Field("head", description="Sampling strategy")
    sample_size: int = Field(100, description="Number of rows to preview", ge=1, le=1000)
    show_only_changed: bool = Field(False, description="Show only changed fields")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional preview options")


class CorrectionSummary(BaseModel):
    total_corrections: int = Field(..., description="Total number of corrections applied")
    success_rate: float = Field(..., description="Percentage of successful corrections")
    corrections_by_rule: Dict[str, int] = Field(..., description="Breakdown by rule")
    affected_rows: List[int] = Field(..., description="List of affected row numbers")


class CorrectionPreviewResponse(BaseModel):
    summary: CorrectionSummary = Field(..., description="Summary of corrections")
    preview_data: List[Dict[str, Any]] = Field(..., description="Sample of corrected data")
    changes: List[ValidationItem] = Field(..., description="List of changes that would be applied")
    job_id: Optional[str] = Field(None, description="Job ID for tracking")


class HealthStatus(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"] = Field(..., description="Overall health status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Deployment environment")
    services: Dict[str, str] = Field(..., description="Status of dependent services")
    uptime_seconds: Optional[int] = Field(None, description="Service uptime in seconds")


class CorrectCsvResponse(BaseModel):
    """Response for JSON content-type correction requests"""
    job_id: str = Field(..., description="Job ID for tracking")
    files: Dict[str, str] = Field(..., description="URLs to generated files")
    summary: CorrectionSummary = Field(..., description="Correction summary")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class AsyncJobResponse(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    status: Literal["accepted", "processing", "completed", "failed"] = Field(..., description="Job status")
    message: str = Field(..., description="Status message")
    location: Optional[str] = Field(None, description="URL to check job status")
    progress: Optional[int] = Field(None, description="Progress percentage (0-100)", ge=0, le=100)
    result: Optional[Dict[str, Any]] = Field(None, description="Result data when completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: Optional[datetime] = Field(None, description="Job creation time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")