"""
Mapper for converting between rule engine results and API validation items.
This separates result transformation logic from business logic.
"""

from src.core.logging_config import get_logger
from typing import Optional, Dict, Any, List

from src.libs.rule_engine.engine import RuleResult

from src.schemas.validate import (
    ValidationItem,
    ValidationStatus,
    ErrorDetail,
    CorrectionDetail
)
from src.core.enums import Severity

logger = get_logger(__name__)


class ResultMapper:
    """
    Maps between RuleEngine results and API ValidationItems.
    
    This class handles:
    - Converting RuleResult to ValidationItem
    - Extracting field information from results
    - Mapping status and severity levels
    - Building error and correction details
    """
    
    def map_to_validation_item(
        self,
        result: RuleResult,
        row_number: int,
        original_row: Dict[str, Any]
    ) -> Optional[ValidationItem]:
        """
        Convert a RuleResult to a ValidationItem.
        
        Args:
            result: The rule engine result
            row_number: The row number being validated
            original_row: The original row data before any fixes
            
        Returns:
            ValidationItem if the result needs to be reported, None otherwise
        """
        # Skip PASS and SKIP results - they don't need to be reported
        if result.status in ["PASS", "SKIP"]:
            return None
        
        # Map status
        status = self._map_status(result.status)
        
        # Extract field information
        field = self._extract_field(result)
        
        # Build error detail if needed
        error_detail = self._build_error_detail(
            result, field, original_row
        )
        
        # Build correction detail if needed
        correction_detail = self._build_correction_detail(
            result, field, original_row
        )
        
        return ValidationItem(
            row_number=row_number,
            status=status,
            errors=[error_detail] if error_detail else [],
            corrections=[correction_detail] if correction_detail else [],
            metadata={
                "rule_id": result.rule_id,
                **(result.metadata or {})
            }
        )
    
    def map_multiple(
        self,
        results: List[RuleResult],
        row_number: int,
        original_row: Dict[str, Any]
    ) -> List[ValidationItem]:
        """
        Convert multiple RuleResults to ValidationItems.
        
        Args:
            results: List of rule engine results
            row_number: The row number being validated
            original_row: The original row data before any fixes
            
        Returns:
            List of ValidationItems (excluding PASS/SKIP results)
        """
        items = []
        for result in results:
            item = self.map_to_validation_item(result, row_number, original_row)
            if item:
                items.append(item)
        return items
    
    def _map_status(self, rule_status: str) -> ValidationStatus:
        """
        Map RuleEngine status to ValidationStatus.
        
        Args:
            rule_status: Status from RuleResult
            
        Returns:
            Corresponding ValidationStatus
        """
        status_mapping = {
            "FAIL": ValidationStatus.ERROR,
            "FIXED": ValidationStatus.WARNING,
            "ERROR": ValidationStatus.ERROR,
        }
        
        return status_mapping.get(rule_status, ValidationStatus.INFO)
    
    def _extract_field(self, result: RuleResult) -> Optional[str]:
        """
        Extract field name from result.
        
        Args:
            result: The rule engine result
            
        Returns:
            Field name if found, None otherwise
        """
        # First try metadata
        if result.metadata and "field" in result.metadata:
            return result.metadata["field"]
        
        # Try to extract from rule_id
        if "_" in result.rule_id:
            # Common pattern: "field_validation_type" -> "field"
            # e.g., "sku_required" -> "sku"
            parts = result.rule_id.rsplit("_", 1)
            if len(parts) == 2:
                return parts[0]
        
        return None
    
    def _map_severity(self, result: RuleResult) -> Severity:
        """
        Map rule result to severity level.
        
        Args:
            result: The rule engine result
            
        Returns:
            Severity level
        """
        # Check metadata for severity hint
        if result.metadata and "severity" in result.metadata:
            severity_str = str(result.metadata["severity"]).upper()
            
            severity_mapping = {
                "CRITICAL": Severity.ERROR,
                "ERROR": Severity.ERROR,
                "WARNING": Severity.WARNING,
                "INFO": Severity.INFO
            }
            
            return severity_mapping.get(severity_str, Severity.INFO)
        
        # Default based on status
        if result.status == "ERROR":
            return Severity.ERROR
        elif result.status == "FAIL":
            return Severity.WARNING
        else:
            return Severity.INFO
    
    def _build_error_detail(
        self,
        result: RuleResult,
        field: Optional[str],
        original_row: Dict[str, Any]
    ) -> Optional[ErrorDetail]:
        """
        Build error detail from result.
        
        Args:
            result: The rule engine result
            field: Extracted field name
            original_row: Original row data
            
        Returns:
            ErrorDetail if this is an error, None otherwise
        """
        if result.status not in ["FAIL", "ERROR"]:
            return None
        
        return ErrorDetail(
            code=result.rule_id,
            message=result.message or f"Validation failed for rule {result.rule_id}",
            severity=self._map_severity(result),
            field=field,
            value=original_row.get(field) if field else None,
            expected=result.metadata.get("expected") if result.metadata else None
        )
    
    def _build_correction_detail(
        self,
        result: RuleResult,
        field: Optional[str],
        original_row: Dict[str, Any]
    ) -> Optional[CorrectionDetail]:
        """
        Build correction detail from result.
        
        Args:
            result: The rule engine result
            field: Extracted field name
            original_row: Original row data
            
        Returns:
            CorrectionDetail if this is a correction, None otherwise
        """
        if result.status != "FIXED":
            return None
        
        if not result.metadata:
            return None
        
        fixed_value = result.metadata.get("fixed_value")
        if fixed_value is None:
            return None
        
        return CorrectionDetail(
            field=field or "",
            original_value=original_row.get(field) if field else None,
            corrected_value=fixed_value,
            correction_type=result.metadata.get("fix_type", "auto_fix"),
            confidence=float(result.metadata.get("confidence", 1.0))
        )
    
    def extract_fixes_from_results(
        self,
        results: List[RuleResult],
        original_row: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract all fixes from results to build the fixed row.
        
        Args:
            results: List of rule engine results
            original_row: Original row data
            
        Returns:
            Dictionary of field -> fixed value mappings
        """
        fixes = {}
        
        for result in results:
            if result.status == "FIXED" and result.metadata:
                field = self._extract_field(result)
                fixed_value = result.metadata.get("fixed_value")
                
                if field and fixed_value is not None:
                    fixes[field] = fixed_value
        
        return fixes