"""
Enhanced validation pipeline using the YAML-based rule engine.
"""

import time
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

from ...services.rule_engine_service import RuleEngineService, RuleEngineConfig
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


class ValidationPipeline:
    """Enhanced pipeline using YAML-based rule engine."""
    
    def __init__(
        self, 
        rule_engine_service: Optional[RuleEngineService] = None,
        auto_fix: bool = True
    ):
        self.rule_engine_service = rule_engine_service or RuleEngineService()
        self.auto_fix = auto_fix
    
    def validate(
        self, 
        df: pd.DataFrame, 
        marketplace: Marketplace, 
        category: Category,
        auto_fix: bool = None
    ) -> ValidationResult:
        """Validate a DataFrame using the rule engine."""
        start_time = time.time()
        
        if auto_fix is None:
            auto_fix = self.auto_fix
        
        # Convert marketplace enum to string
        marketplace_str = marketplace.value
        
        # Process each row
        validation_items: List[ValidationItem] = []
        fixed_rows: List[Dict[str, Any]] = []
        
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            row_number = idx + 1  # 1-indexed for user display
            
            if auto_fix:
                fixed_row, items = self.rule_engine_service.validate_and_fix_row(
                    row_dict,
                    marketplace_str,
                    row_number
                )
                fixed_rows.append(fixed_row)
            else:
                items = self.rule_engine_service.validate_row(
                    row_dict,
                    marketplace_str,
                    row_number
                )
                fixed_rows.append(row_dict)
            
            validation_items.extend(items)
        
        # Calculate summary statistics
        total_rows = len(df)
        error_items = [item for item in validation_items if item.status == ValidationStatus.ERROR]
        warning_items = [item for item in validation_items if item.status == ValidationStatus.WARNING]
        
        # Count unique rows with errors
        error_rows = len(set(item.row_number for item in error_items))
        valid_rows = total_rows - error_rows
        
        # Count corrections
        total_corrections = sum(len(item.corrections) for item in validation_items)
        
        # Group errors by type
        error_types: Dict[str, int] = {}
        for item in error_items:
            for error in item.errors:
                error_types[error.code] = error_types.get(error.code, 0) + 1
        
        processing_time = time.time() - start_time
        
        # Create corrected DataFrame if auto_fix was enabled
        corrected_df = pd.DataFrame(fixed_rows) if auto_fix and fixed_rows else None
        
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
    
    def validate_single_row(
        self,
        row: Dict[str, Any],
        marketplace: Marketplace,
        category: Optional[Category] = None,
        row_number: int = 1,
        auto_fix: bool = None
    ) -> tuple[Dict[str, Any], List[ValidationItem]]:
        """Validate a single row."""
        if auto_fix is None:
            auto_fix = self.auto_fix
            
        marketplace_str = marketplace.value
        
        if auto_fix:
            return self.rule_engine_service.validate_and_fix_row(
                row,
                marketplace_str,
                row_number
            )
        else:
            items = self.rule_engine_service.validate_row(
                row,
                marketplace_str,
                row_number
            )
            return row, items
    
    def reload_rules(self, marketplace: Optional[Marketplace] = None):
        """Reload validation rules for a marketplace or all marketplaces."""
        if marketplace:
            self.rule_engine_service.reload_marketplace_rules(marketplace.value)
            logger.info(f"Reloaded rules for {marketplace.value}")
        else:
            self.rule_engine_service.clear_cache()
            logger.info("Cleared all rule caches")