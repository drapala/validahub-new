"""
Pure domain service for CSV validation logic.
Decoupled from infrastructure concerns (queues, storage).
"""

import logging
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import io

from ..services.rule_engine_service import RuleEngineService
from ..core.pipeline.validation_pipeline import ValidationPipeline

logger = logging.getLogger(__name__)


class CSVValidationService:
    """
    Pure domain service for CSV validation.
    No infrastructure dependencies - only business logic.
    """
    
    def __init__(self, rule_engine_service: Optional[RuleEngineService] = None):
        """Initialize with optional rule engine service."""
        self.rule_engine = rule_engine_service or RuleEngineService()
        self.pipeline = ValidationPipeline(rule_engine_service=self.rule_engine)
    
    def validate_csv_content(
        self,
        csv_content: str,
        marketplace: str = "mercado_livre",
        category: str = "general",
        ruleset: str = "default",
        auto_fix: bool = False
    ) -> Dict[str, Any]:
        """
        Validate CSV content and return results.
        
        Args:
            csv_content: Raw CSV content as string
            marketplace: Target marketplace
            category: Product category
            ruleset: Ruleset to apply
            auto_fix: Whether to apply auto-corrections
            
        Returns:
            Dictionary with validation results and optional corrections
        """
        
        # Parse CSV
        df = pd.read_csv(io.StringIO(csv_content))
        total_rows = len(df)
        
        logger.info(f"Validating CSV with {total_rows} rows for {marketplace}/{category}")
        
        # Perform validation
        result = self.pipeline.validate(
            data=df,
            marketplace=marketplace,
            category=category,
            auto_fix=auto_fix
        )
        
        # Build response
        validation_result = {
            "total_rows": result.total_rows,
            "valid_rows": result.valid_rows,
            "error_rows": result.error_rows,
            "warning_rows": result.warning_rows,
            "errors": [
                {
                    "row": err.row,
                    "field": err.field,
                    "value": err.value,
                    "rule": err.rule,
                    "message": err.message,
                    "severity": err.severity
                }
                for err in result.errors
            ],
            "warnings": [
                {
                    "row": warn.row,
                    "field": warn.field,
                    "value": warn.value,
                    "rule": warn.rule,
                    "message": warn.message
                }
                for warn in result.warnings
            ]
        }
        
        # Add corrected data if auto_fix was enabled
        corrected_csv = None
        if auto_fix and result.corrected_data is not None:
            corrected_csv = result.corrected_data.to_csv(index=False)
            validation_result["has_corrections"] = True
        else:
            validation_result["has_corrections"] = False
            
        return validation_result, corrected_csv
    
    def calculate_metrics(
        self,
        csv_content: str,
        validation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate business metrics from validation.
        
        Args:
            csv_content: Raw CSV content
            validation_result: Results from validation
            
        Returns:
            Dictionary of business metrics
        """
        
        metrics = {
            "payload_size_bytes": len(csv_content.encode('utf-8')),
            "total_rows": validation_result.get("total_rows", 0),
            "valid_rows": validation_result.get("valid_rows", 0),
            "error_rows": validation_result.get("error_rows", 0),
            "warning_rows": validation_result.get("warning_rows", 0),
            "error_rate": 0.0,
            "warning_rate": 0.0
        }
        
        # Calculate rates
        if metrics["total_rows"] > 0:
            metrics["error_rate"] = metrics["error_rows"] / metrics["total_rows"]
            metrics["warning_rate"] = metrics["warning_rows"] / metrics["total_rows"]
        
        # Field-level error distribution
        error_by_field = {}
        for error in validation_result.get("errors", []):
            field = error.get("field", "unknown")
            error_by_field[field] = error_by_field.get(field, 0) + 1
        
        metrics["errors_by_field"] = error_by_field
        
        return metrics