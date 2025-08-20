"""
Optimized decoupled validation pipeline with parallel processing.
"""

import time
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

from ..interfaces.validation import IValidator
from ...schemas.validate import (
    ValidationResult, 
    ValidationItem,
    ValidationStatus,
    Marketplace, 
    Category,
    ValidationSummary,
    ErrorDetail,
    CorrectionDetail
)

logger = logging.getLogger(__name__)


class ValidationPipelineDecoupledOptimized:
    """
    Optimized validation pipeline with parallel row processing.
    """
    
    def __init__(
        self, 
        validator: IValidator,
        auto_fix: bool = True,
        batch_size: int = 100
    ):
        """
        Initialize pipeline with a validator.
        
        Args:
            validator: Any implementation of IValidator interface
            auto_fix: Default auto-fix setting
            batch_size: Number of rows to process in parallel
        """
        self.validator = validator
        self.auto_fix = auto_fix
        self.batch_size = batch_size
    
    async def validate(
        self, 
        df: pd.DataFrame, 
        marketplace: Marketplace, 
        category: Category,
        auto_fix: Optional[bool] = None,
        job_id: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate a DataFrame using parallel processing.
        """
        start_time = time.time()
        
        if auto_fix is None:
            auto_fix = self.auto_fix
        
        # Convert marketplace enum to string
        marketplace_str = marketplace.value if hasattr(marketplace, 'value') else str(marketplace)
        
        # Prepare data for parallel processing
        corrected_data = df.copy() if auto_fix else None
        context = {'category': category}
        
        # Process rows in batches for better performance
        all_results = []
        total_rows = len(df)
        
        for batch_start in range(0, total_rows, self.batch_size):
            batch_end = min(batch_start + self.batch_size, total_rows)
            
            # Create tasks for this batch
            tasks = []
            for row_tuple in df.iloc[batch_start:batch_end].itertuples(index=True, name=None):
                idx = row_tuple[0]
                row_values = row_tuple[1:]
                row_dict = dict(zip(df.columns, row_values))
                row_number = idx + 1
                
                # Create async task for row validation
                task = self._validate_row_async(
                    row_dict, marketplace_str, row_number, auto_fix, context, idx
                )
                tasks.append(task)
            
            # Execute batch in parallel
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            all_results.extend(batch_results)
        
        # Process results
        validation_items = []
        if corrected_data is not None and auto_fix:
            for result in all_results:
                if isinstance(result, Exception):
                    # Handle exceptions
                    logger.error(f"Error in batch processing: {str(result)}")
                    continue
                
                idx, fixed_row, items, error = result
                if error:
                    validation_items.append(error)
                else:
                    validation_items.extend(items)
                    if fixed_row and corrected_data is not None:
                        # Update corrected data
                        for key, value in fixed_row.items():
                            if key in corrected_data.columns:
                                corrected_data.at[idx, key] = value
        else:
            # Just collect validation items
            for result in all_results:
                if isinstance(result, Exception):
                    continue
                _, _, items, error = result
                if error:
                    validation_items.append(error)
                else:
                    validation_items.extend(items)
        
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
    
    async def _validate_row_async(
        self,
        row_dict: Dict[str, Any],
        marketplace_str: str,
        row_number: int,
        auto_fix: bool,
        context: Dict[str, Any],
        idx: int
    ) -> Tuple[int, Optional[Dict[str, Any]], List[ValidationItem], Optional[ValidationItem]]:
        """
        Validate a single row asynchronously.
        
        Returns:
            Tuple of (index, fixed_row, validation_items, error_item)
        """
        try:
            if auto_fix:
                fixed_row, items = await self.validator.validate_and_fix_row(
                    row=row_dict,
                    marketplace=marketplace_str,
                    row_number=row_number,
                    auto_fix=True,
                    context=context
                )
                return (idx, fixed_row, items, None)
            else:
                items = await self.validator.validate_row(
                    row=row_dict,
                    marketplace=marketplace_str,
                    row_number=row_number,
                    context=context
                )
                return (idx, None, items, None)
                
        except Exception as e:
            logger.error(f"Error validating row {row_number}: {str(e)}")
            error_item = ValidationItem(
                row_number=row_number,
                status=ValidationStatus.ERROR,
                errors=[ErrorDetail(
                    field="__row__",
                    message=f"Validation error: {str(e)}",
                    error_type="VALIDATION_ERROR"
                )]
            )
            return (idx, None, [], error_item)
    
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