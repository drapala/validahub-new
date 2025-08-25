"""
Decoupled validation pipeline that uses IValidator interface.
This version removes direct dependency on RuleEngineService.
"""

import time
from core.logging_config import get_logger
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

from core.interfaces.validation import IValidator
from schemas.validate import (
    ValidationResult, 
    ValidationItem,
    ValidationStatus,
    Marketplace, 
    Category,
    ValidationSummary,
    ErrorDetail,
    CorrectionDetail
)

logger = get_logger(__name__)


class ValidationPipelineDecoupled:
    """
    Validation pipeline that uses IValidator interface.
    Completely decoupled from RuleEngineService implementation.
    """
    
    def __init__(
        self, 
        validator: IValidator,
        auto_fix: bool = True
    ):
        """
        Initialize pipeline with a validator.
        
        Args:
            validator: Any implementation of IValidator interface
            auto_fix: Default auto-fix setting
        """
        self.validator = validator
        self.auto_fix = auto_fix
    
    async def validate(
        self, 
        df: pd.DataFrame, 
        marketplace: Marketplace, 
        category: Category,
        auto_fix: Optional[bool] = None,
        job_id: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate a DataFrame using the injected validator.
        
        Args:
            df: DataFrame to validate
            marketplace: Target marketplace
            category: Product category
            auto_fix: Whether to apply fixes
            job_id: Optional job ID for tracking
            
        Returns:
            ValidationResult with all validation details
        """
        start_time = time.time()
        
        if auto_fix is None:
            auto_fix = self.auto_fix
        
        # Convert marketplace enum to string
        marketplace_str = marketplace.value if hasattr(marketplace, 'value') else str(marketplace)
        
        validation_items = []
        corrected_data = df.copy() if auto_fix else None
        
        # Validate each row (using itertuples for better performance)
        for row_tuple in df.itertuples(index=True, name=None):
            idx = row_tuple[0]
            row_values = row_tuple[1:]
            row_dict = dict(zip(df.columns, row_values))
            row_number = idx + 1
            
            try:
                if auto_fix:
                    # Validate and fix the row
                    fixed_row, items = await self.validator.validate_and_fix_row(
                        row=row_dict,
                        marketplace=marketplace_str,
                        row_number=row_number,
                        auto_fix=True,
                        context={'category': category}
                    )
                    
                    # Update corrected data
                    if corrected_data is not None:
                        for key, value in fixed_row.items():
                            if key in corrected_data.columns:
                                corrected_data.at[idx, key] = value
                else:
                    # Just validate without fixing
                    items = await self.validator.validate_row(
                        row=row_dict,
                        marketplace=marketplace_str,
                        row_number=row_number,
                        context={'category': category}
                    )
                
                validation_items.extend(items)
                
            except Exception as e:
                logger.error(f"Error validating row {row_number}: {str(e)}")
                # Create error item for this row
                error_item = ValidationItem(
                    row_number=row_number,
                    status=ValidationStatus.ERROR,
                    errors=[ErrorDetail(
                        field="__row__",
                        message=f"Validation error: {str(e)}",
                        error_type="VALIDATION_ERROR"
                    )]
                )
                validation_items.append(error_item)
        
        # Calculate summary
        processing_time = time.time() - start_time
        summary = self._calculate_summary(
            validation_items, 
            len(df), 
            processing_time
        )
        
        return ValidationResult(
            validation_items=validation_items,
            summary=summary,
            corrected_data=corrected_data,
            job_id=job_id,
            marketplace=marketplace_str,
            category=category.value if hasattr(category, 'value') else str(category),
            auto_fix_applied=auto_fix,
            total_rows=len(df),
            valid_rows=summary.valid_rows,
            invalid_rows=summary.invalid_rows
        )
    
    async def validate_single_row(
        self,
        row: Dict[str, Any],
        marketplace: Marketplace,
        category: Optional[Category] = None,
        row_number: int = 1,
        auto_fix: bool = False
    ) -> Tuple[Dict[str, Any], List[ValidationItem]]:
        """
        Validate a single row of data.
        
        Args:
            row: Row data as dictionary
            marketplace: Target marketplace
            category: Product category
            row_number: Row number for reporting
            auto_fix: Whether to apply fixes
            
        Returns:
            Tuple of (fixed_row, validation_items)
        """
        marketplace_str = marketplace.value if hasattr(marketplace, 'value') else str(marketplace)
        context = {'category': category} if category else {}
        
        if auto_fix:
            return await self.validator.validate_and_fix_row(
                row=row,
                marketplace=marketplace_str,
                row_number=row_number,
                auto_fix=True,
                context=context
            )
        else:
            items = await self.validator.validate_row(
                row=row,
                marketplace=marketplace_str,
                row_number=row_number,
                context=context
            )
            return row, items
    
    def _calculate_summary(
        self, 
        validation_items: List[ValidationItem],
        total_rows: int,
        processing_time: float
    ) -> ValidationSummary:
        """
        Calculate validation summary from items.
        
        Args:
            validation_items: List of validation items
            total_rows: Total number of rows
            processing_time: Time taken to process
            
        Returns:
            ValidationSummary with statistics
        """
        total_errors = sum(
            len(item.errors) if item.errors else 0 
            for item in validation_items
        )
        
        total_warnings = sum(
            len(item.warnings) if item.warnings else 0 
            for item in validation_items
        )
        
        total_corrections = sum(
            len(item.corrections) if item.corrections else 0 
            for item in validation_items
        )
        
        # Count unique rows with issues
        rows_with_errors = len(set(
            item.row_number for item in validation_items 
            if item.errors
        ))
        
        rows_with_warnings = len(set(
            item.row_number for item in validation_items 
            if item.warnings
        ))
        
        valid_rows = total_rows - rows_with_errors
        
        return ValidationSummary(
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=rows_with_errors,
            total_errors=total_errors,
            total_warnings=total_warnings,
            total_corrections=total_corrections,
            rows_with_errors=rows_with_errors,
            rows_with_warnings=rows_with_warnings,
            processing_time_seconds=processing_time
        )