"""
Use case for single row validation.
Handles validation of individual data rows.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base import UseCase
from ..pipeline.validation_pipeline import ValidationPipeline
from ...schemas.validate import (
    ValidationItem,
    ValidationStatus,
    ValidationSummary,
    Marketplace,
    Category
)

logger = logging.getLogger(__name__)


@dataclass
class ValidateRowInput:
    """Input data for row validation use case."""
    row_data: Dict[str, Any]
    row_number: int
    marketplace: Marketplace
    category: Category
    auto_fix: bool = False
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}


@dataclass
class ValidateRowOutput:
    """Output data for row validation use case."""
    row_number: int
    validation_items: List[ValidationItem]
    has_errors: bool
    has_warnings: bool
    corrected_data: Optional[Dict[str, Any]] = None
    summary: Optional[ValidationSummary] = None


class ValidateRowUseCase(UseCase[ValidateRowInput, ValidateRowOutput]):
    """
    Use case for validating a single row of data.
    
    This class handles the validation of individual rows
    without any infrastructure dependencies.
    """
    
    def __init__(self, validation_pipeline: ValidationPipeline = None):
        self.validation_pipeline = validation_pipeline or ValidationPipeline()
    
    async def execute(self, input_data: ValidateRowInput) -> ValidateRowOutput:
        """
        Execute row validation logic.
        
        Args:
            input_data: Input containing row data and validation parameters
            
        Returns:
            ValidateRowOutput with validation results
        """
        try:
            # Perform validation using the pipeline
            validation_items = self.validation_pipeline.validate_row(
                row=input_data.row_data,
                row_number=input_data.row_number,
                marketplace=input_data.marketplace,
                category=input_data.category
            )
            
            # Determine if there are errors or warnings (using enum comparison)
            has_errors = any(item.status == ValidationStatus.ERROR for item in validation_items)
            has_warnings = any(item.status == ValidationStatus.WARNING for item in validation_items)
            
            # Apply corrections if requested and there are errors
            corrected_data = None
            if input_data.auto_fix and has_errors:
                corrected_data = self._apply_corrections(
                    input_data.row_data,
                    validation_items
                )
            
            # Create summary
            summary = self._create_summary(validation_items)
            
            return ValidateRowOutput(
                row_number=input_data.row_number,
                validation_items=validation_items,
                has_errors=has_errors,
                has_warnings=has_warnings,
                corrected_data=corrected_data,
                summary=summary
            )
            
        except Exception as e:
            logger.exception(f"Error validating row {input_data.row_number}: {e}")
            raise
    
    def _apply_corrections(
        self,
        row_data: Dict[str, Any],
        validation_items: List[ValidationItem]
    ) -> Dict[str, Any]:
        """Apply corrections to row data based on validation items."""
        corrected = row_data.copy()
        
        for item in validation_items:
            if item.status == ValidationStatus.ERROR and item.corrected_value is not None:
                corrected[item.field] = item.corrected_value
        
        return corrected
    
    def _create_summary(self, validation_items: List[ValidationItem]) -> ValidationSummary:
        """Create validation summary from validation items."""
        error_count = sum(1 for item in validation_items if item.status == ValidationStatus.ERROR)
        warning_count = sum(1 for item in validation_items if item.status == ValidationStatus.WARNING)
        
        errors_by_field = {}
        warnings_by_field = {}
        
        for item in validation_items:
            if item.status == ValidationStatus.ERROR:
                if item.field not in errors_by_field:
                    errors_by_field[item.field] = []
                errors_by_field[item.field].append(item.message)
            elif item.status == ValidationStatus.WARNING:
                if item.field not in warnings_by_field:
                    warnings_by_field[item.field] = []
                warnings_by_field[item.field].append(item.message)
        
        return ValidationSummary(
            total_errors=error_count,
            total_warnings=warning_count,
            errors_by_field=errors_by_field,
            warnings_by_field=warnings_by_field,
            processing_time_ms=0  # Will be set by the endpoint
        )