"""
Standardized business metrics for telemetry events.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class ValidationMetrics:
    """Metrics for validation jobs."""
    
    # Payload metrics
    payload_size_bytes: int
    file_format: str = "csv"
    
    # Record metrics
    records_total: int = 0
    records_valid: int = 0
    records_error: int = 0
    records_warning: int = 0
    
    # Field-level error tracking
    errors_by_field: Optional[Dict[str, int]] = None
    warnings_by_field: Optional[Dict[str, int]] = None
    
    # Performance metrics
    processing_time_ms: Optional[int] = None
    validation_time_ms: Optional[int] = None
    
    # Business metrics
    marketplace: str = "unknown"
    category: str = "unknown"
    region: str = "default"
    ruleset: str = "default"
    auto_fix_applied: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class ConnectorMetrics:
    """Metrics for connector sync jobs."""
    
    # Connection metrics
    connector_type: str
    connection_time_ms: int
    
    # Data transfer metrics
    records_fetched: int = 0
    records_processed: int = 0
    records_failed: int = 0
    bytes_transferred: int = 0
    
    # Performance
    fetch_time_ms: Optional[int] = None
    processing_time_ms: Optional[int] = None
    
    # Source info
    source_marketplace: str = "unknown"
    source_region: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class ReportMetrics:
    """Metrics for report generation jobs."""
    
    # Report specs
    report_type: str
    format: str  # pdf, excel, csv, json
    
    # Data metrics
    records_included: int = 0
    date_range_days: Optional[int] = None
    
    # Performance
    generation_time_ms: Optional[int] = None
    file_size_bytes: Optional[int] = None
    
    # Filters applied
    marketplaces: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    regions: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


class MetricsCollector:
    """Helper to collect and standardize metrics during job execution."""
    
    @staticmethod
    def collect_validation_metrics(
        csv_content: str,
        validation_result: Dict[str, Any],
        processing_time_ms: Optional[int] = None
    ) -> ValidationMetrics:
        """
        Collect metrics from CSV validation.
        
        Args:
            csv_content: The CSV content that was validated
            validation_result: The validation result dictionary
            processing_time_ms: Optional processing time
            
        Returns:
            ValidationMetrics object
        """
        
        # Calculate payload size
        payload_size = len(csv_content.encode('utf-8'))
        
        # Extract record counts
        total_rows = validation_result.get("total_rows", 0)
        valid_rows = validation_result.get("valid_rows", 0)
        error_rows = validation_result.get("error_rows", 0)
        warning_rows = validation_result.get("warning_rows", 0)
        
        # Extract field-level errors
        errors_by_field = {}
        warnings_by_field = {}
        
        if "errors" in validation_result:
            for error in validation_result["errors"]:
                field = error.get("field", "unknown")
                errors_by_field[field] = errors_by_field.get(field, 0) + 1
                
        if "warnings" in validation_result:
            for warning in validation_result["warnings"]:
                field = warning.get("field", "unknown")
                warnings_by_field[field] = warnings_by_field.get(field, 0) + 1
        
        return ValidationMetrics(
            payload_size_bytes=payload_size,
            records_total=total_rows,
            records_valid=valid_rows,
            records_error=error_rows,
            records_warning=warning_rows,
            errors_by_field=errors_by_field if errors_by_field else None,
            warnings_by_field=warnings_by_field if warnings_by_field else None,
            processing_time_ms=processing_time_ms
        )
    
    @staticmethod
    def calculate_error_rates(metrics: ValidationMetrics) -> Dict[str, float]:
        """
        Calculate error and warning rates.
        
        Args:
            metrics: ValidationMetrics object
            
        Returns:
            Dictionary with error_rate and warning_rate
        """
        
        if metrics.records_total == 0:
            return {"error_rate": 0.0, "warning_rate": 0.0}
        
        error_rate = metrics.records_error / metrics.records_total
        warning_rate = metrics.records_warning / metrics.records_total
        
        return {
            "error_rate": round(error_rate, 4),
            "warning_rate": round(warning_rate, 4)
        }
    
    @staticmethod
    def enrich_with_business_context(
        metrics: ValidationMetrics,
        params: Dict[str, Any]
    ) -> ValidationMetrics:
        """
        Enrich metrics with business context from job parameters.
        
        Args:
            metrics: ValidationMetrics to enrich
            params: Job parameters containing business context
            
        Returns:
            Enriched ValidationMetrics
        """
        
        metrics.marketplace = params.get("marketplace", "unknown")
        metrics.category = params.get("category", "unknown")
        metrics.region = params.get("region", "default")
        metrics.ruleset = params.get("ruleset", "default")
        metrics.auto_fix_applied = params.get("auto_fix", False)
        
        return metrics