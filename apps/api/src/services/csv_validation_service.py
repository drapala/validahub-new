"""
Pure domain service for CSV validation logic.
Decoupled from infrastructure concerns (queues, storage).
"""

from core.logging_config import get_logger
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import io

from .rule_engine_service import RuleEngineService
from core.pipeline.validation_pipeline import ValidationPipeline

logger = get_logger(__name__)


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
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Validate CSV content and return results.
        
        Args:
            csv_content: Raw CSV content as string
            marketplace: Target marketplace
            category: Product category
            ruleset: Ruleset to apply
            auto_fix: Whether to apply auto-corrections
            
        Returns:
            Tuple of (validation_result dict, corrected_csv string or None)
        """
        
        if not csv_content:
            return {"total_rows": 0, "valid_rows": 0, "error_rows": 0, "errors": [], "warnings": []}, None
        
        try:
            # Parse CSV
            df = pd.read_csv(io.StringIO(csv_content))
            
            if df.empty:
                return {
                    "total_rows": 0,
                    "valid_rows": 0,
                    "error_rows": 0,
                    "errors": [],
                    "warnings": []
                }, None
            
            logger.info(f"Validating CSV with {len(df)} rows for {marketplace}/{category}")
            
            # Convert string to enum if needed
            from schemas.validate import Marketplace, Category
            try:
                marketplace_enum = Marketplace[marketplace.upper()] if isinstance(marketplace, str) else marketplace
            except (KeyError, AttributeError):
                marketplace_enum = Marketplace.MERCADO_LIVRE  # Default
            
            try:
                category_enum = Category[category.upper()] if isinstance(category, str) else category
            except (KeyError, AttributeError):
                category_enum = None
            
            # Perform validation
            result = self.pipeline.validate(
                df=df,
                marketplace=marketplace_enum,
                category=category_enum,
                auto_fix=auto_fix
            )
            
            # Extract errors and warnings from validation items
            errors = []
            warnings = []
            
            for item in result.validation_items:
                for error in item.errors:
                    if error.severity == "ERROR":
                        errors.append({
                            "row": item.row_number,
                            "field": error.field,
                            "value": error.value,
                            "rule": error.code,
                            "message": error.message,
                            "severity": error.severity
                        })
                    elif error.severity == "WARNING":
                        warnings.append({
                            "row": item.row_number,
                            "field": error.field,
                            "value": error.value,
                            "rule": error.code,
                            "message": error.message
                        })
            
            # Build response
            validation_result = {
                "total_rows": result.total_rows,
                "valid_rows": result.valid_rows,
                "error_rows": result.error_rows,
                "warning_rows": len(set(w["row"] for w in warnings)),
                "errors": errors,
                "warnings": warnings,
                "has_corrections": result.auto_fix_applied and result.corrected_data is not None
            }
            
            # Add corrected data if auto_fix was enabled
            corrected_csv = None
            if result.auto_fix_applied and result.corrected_data is not None:
                corrected_csv = result.corrected_data.to_csv(index=False)
            
            return validation_result, corrected_csv
            
        except Exception as e:
            logger.error(f"Error validating CSV: {e}")
            return {
                "total_rows": 0,
                "valid_rows": 0,
                "error_rows": 0,
                "errors": [{"message": str(e), "severity": "ERROR"}],
                "warnings": []
            }, None
    
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