"""
Refactored validation pipeline with dependency injection.
Decoupled from specific validator implementations.
"""

import time
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd

from ..interfaces.validation import (
    IValidator,
    IDataAdapter,
    IValidationPipeline
)
from ...schemas.validate import (
    ValidationResult,
    ValidationItem,
    ValidationStatus,
    Marketplace,
    Category,
    ValidationSummary
)

logger = logging.getLogger(__name__)


class PandasDataAdapter(IDataAdapter):
    """
    Data adapter for pandas DataFrame operations.
    """
    
    def dataframe_to_rows(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DataFrame to list of row dictionaries."""
        return df.to_dict('records')
    
    def rows_to_dataframe(self, rows: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert list of rows to DataFrame."""
        return pd.DataFrame(rows)
    
    def normalize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a row for validation.
        Handles NaN, None, and type conversions.
        """
        normalized = {}
        for key, value in row.items():
            # Handle pandas NaN
            if pd.isna(value):
                normalized[key] = None
            else:
                normalized[key] = value
        return normalized


class ValidationPipelineV2(IValidationPipeline):
    """
    Refactored validation pipeline with dependency injection.
    No direct coupling to specific validators or services.
    """
    
    def __init__(
        self,
        validator: IValidator,
        data_adapter: Optional[IDataAdapter] = None,
        parallel_processing: bool = False,
        batch_size: int = 100
    ):
        """
        Initialize pipeline with injected dependencies.
        
        Args:
            validator: The validator to use
            data_adapter: Data adapter for conversions
            parallel_processing: Enable parallel row processing
            batch_size: Batch size for parallel processing
        """
        self.validator = validator
        self.data_adapter = data_adapter or PandasDataAdapter()
        self.parallel_processing = parallel_processing
        self.batch_size = batch_size
    
    async def validate(
        self,
        df: pd.DataFrame,
        marketplace: Marketplace,
        category: Category,
        auto_fix: bool = False
    ) -> ValidationResult:
        """
        Validate a DataFrame.
        
        Args:
            df: DataFrame to validate
            marketplace: Target marketplace
            category: Product category
            auto_fix: Whether to apply fixes
            
        Returns:
            Complete validation result
        """
        start_time = time.time()
        marketplace_str = marketplace.value
        
        # Convert DataFrame to rows
        rows = self.data_adapter.dataframe_to_rows(df)
        
        # Process rows
        if self.parallel_processing:
            validation_items, fixed_rows = await self._process_rows_parallel(
                rows, marketplace_str, auto_fix
            )
        else:
            validation_items, fixed_rows = await self._process_rows_sequential(
                rows, marketplace_str, auto_fix
            )
        
        # Calculate statistics
        total_rows = len(rows)
        error_items = [
            item for item in validation_items 
            if item.status == ValidationStatus.ERROR
        ]
        warning_items = [
            item for item in validation_items 
            if item.status == ValidationStatus.WARNING
        ]
        
        # Count unique rows with errors
        error_rows = len(set(item.row_number for item in error_items))
        valid_rows = total_rows - error_rows
        
        # Count corrections
        total_corrections = sum(
            len(item.corrections) for item in validation_items
        )
        
        # Group errors by type
        error_types: Dict[str, int] = {}
        for item in error_items:
            for error in item.errors:
                error_types[error.code] = error_types.get(error.code, 0) + 1
        
        processing_time = time.time() - start_time
        
        # Create corrected DataFrame if auto_fix was enabled
        corrected_df = None
        if auto_fix and fixed_rows:
            corrected_df = self.data_adapter.rows_to_dataframe(fixed_rows)
        
        # Build summary
        summary = ValidationSummary(
            total_errors=len(error_items),
            total_warnings=len(warning_items),
            total_corrections=total_corrections,
            error_types=error_types,
            processing_time_seconds=processing_time
        )
        
        return ValidationResult(
            total_rows=total_rows,
            valid_rows=valid_rows,
            error_rows=error_rows,
            validation_items=validation_items,
            summary=summary,
            corrected_data=corrected_df,
            marketplace=marketplace_str,
            category=category.value if category else None,
            auto_fix_applied=auto_fix
        )
    
    async def _process_rows_sequential(
        self,
        rows: List[Dict[str, Any]],
        marketplace: str,
        auto_fix: bool
    ) -> Tuple[List[ValidationItem], List[Dict[str, Any]]]:
        """
        Process rows sequentially.
        
        Args:
            rows: Rows to process
            marketplace: Target marketplace
            auto_fix: Whether to apply fixes
            
        Returns:
            Tuple of (validation_items, fixed_rows)
        """
        validation_items = []
        fixed_rows = []
        
        for idx, row in enumerate(rows):
            row_number = idx + 1
            normalized_row = self.data_adapter.normalize_row(row)
            
            if auto_fix:
                fixed_row, items = await self.validator.validate_and_fix_row(
                    normalized_row, marketplace, row_number, auto_fix
                )
                fixed_rows.append(fixed_row)
            else:
                items = await self.validator.validate_row(
                    normalized_row, marketplace, row_number
                )
                fixed_rows.append(normalized_row)
            
            validation_items.extend(items)
        
        return validation_items, fixed_rows
    
    async def _process_rows_parallel(
        self,
        rows: List[Dict[str, Any]],
        marketplace: str,
        auto_fix: bool
    ) -> Tuple[List[ValidationItem], List[Dict[str, Any]]]:
        """
        Process rows in parallel batches.
        
        Args:
            rows: Rows to process
            marketplace: Target marketplace
            auto_fix: Whether to apply fixes
            
        Returns:
            Tuple of (validation_items, fixed_rows)
        """
        all_validation_items = []
        all_fixed_rows = []
        
        # Process in batches
        for batch_start in range(0, len(rows), self.batch_size):
            batch_end = min(batch_start + self.batch_size, len(rows))
            batch = rows[batch_start:batch_end]
            
            # Create tasks for batch
            tasks = []
            for idx, row in enumerate(batch):
                row_number = batch_start + idx + 1
                normalized_row = self.data_adapter.normalize_row(row)
                
                if auto_fix:
                    task = self.validator.validate_and_fix_row(
                        normalized_row, marketplace, row_number, auto_fix
                    )
                else:
                    task = self.validator.validate_row(
                        normalized_row, marketplace, row_number
                    )
                
                tasks.append(task)
            
            # Execute batch in parallel
            results = await asyncio.gather(*tasks)
            
            # Process results
            for idx, result in enumerate(results):
                if auto_fix:
                    fixed_row, items = result
                    all_fixed_rows.append(fixed_row)
                    all_validation_items.extend(items)
                else:
                    items = result
                    all_fixed_rows.append(batch[idx])
                    all_validation_items.extend(items)
        
        return all_validation_items, all_fixed_rows
    
    async def validate_single_row(
        self,
        row: Dict[str, Any],
        marketplace: Marketplace,
        category: Optional[Category] = None,
        row_number: int = 1,
        auto_fix: bool = False
    ) -> Tuple[Dict[str, Any], List[ValidationItem]]:
        """
        Validate a single row.
        
        Args:
            row: Row to validate
            marketplace: Target marketplace
            category: Product category (unused currently)
            row_number: Row number
            auto_fix: Whether to apply fixes
            
        Returns:
            Tuple of (fixed_row, validation_items)
        """
        marketplace_str = marketplace.value
        normalized_row = self.data_adapter.normalize_row(row)
        
        if auto_fix:
            return await self.validator.validate_and_fix_row(
                normalized_row, marketplace_str, row_number, auto_fix
            )
        else:
            items = await self.validator.validate_row(
                normalized_row, marketplace_str, row_number
            )
            return normalized_row, items
    
    async def reload_rules(self, marketplace: Optional[Marketplace] = None):
        """
        Reload validation rules.
        
        Args:
            marketplace: Specific marketplace or None for all
        """
        # This is validator-specific
        # Could be extended to notify validator of reload request
        logger.info(f"Reload request for {marketplace.value if marketplace else 'all'}")
        
        # If validator supports reloading
        if hasattr(self.validator, 'reload'):
            await self.validator.reload(marketplace.value if marketplace else None)