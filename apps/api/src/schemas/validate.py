from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum


class Marketplace(str, Enum):
    MERCADO_LIVRE = "MERCADO_LIVRE"
    SHOPEE = "SHOPEE"
    MAGALU = "MAGALU"
    AMAZON = "AMAZON"
    AMERICANAS = "AMERICANAS"


class Category(str, Enum):
    ELETRONICOS = "ELETRONICOS"
    MODA = "MODA"
    CASA = "CASA"
    ESPORTE = "ESPORTE"
    BELEZA = "BELEZA"
    LIVROS = "LIVROS"
    BRINQUEDOS = "BRINQUEDOS"
    ALIMENTOS = "ALIMENTOS"


class ValidationError(BaseModel):
    row: int = Field(..., description="Row number where error occurred")
    column: str = Field(..., description="Column name with error")
    error: str = Field(..., description="Error description")
    value: Optional[str] = Field(None, description="Current value")
    suggestion: Optional[str] = Field(None, description="Suggested fix")
    severity: Literal["error", "warning", "info"] = Field("error", description="Error severity")


class ValidationResult(BaseModel):
    total_rows: int = Field(..., description="Total rows processed")
    valid_rows: int = Field(..., description="Number of valid rows")
    error_rows: int = Field(..., description="Number of rows with errors")
    errors: List[ValidationError] = Field(default_factory=list, description="List of validation errors")
    warnings_count: int = Field(0, description="Total warnings count")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class ValidateRequest(BaseModel):
    marketplace: Marketplace
    category: Category
    dry_run: bool = Field(True, description="If true, only validate without saving")