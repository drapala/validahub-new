"""
Service layer for integrating the YAML-based rule engine with the API.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import sys

# Add libs to path for import
libs_path = Path(__file__).parent.parent.parent.parent.parent / "libs"
if str(libs_path) not in sys.path:
    sys.path.insert(0, str(libs_path))
# The 'rule_engine' package must be installed in the environment (e.g., via pip install -e libs)
from rule_engine import RuleEngine, RuleResult, load_ruleset

from ..schemas.validate import ValidationItem, ErrorDetail, CorrectionDetail
from ..core.enums import ValidationStatus, Severity, MarketplaceType

logger = logging.getLogger(__name__)


@dataclass
class RuleEngineConfig:
    """Configuration for the rule engine service."""
    rulesets_path: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent.parent / "rulesets")
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    

class RuleEngineService:
    """Service for managing rule engine operations."""
    
    def __init__(self, config: Optional[RuleEngineConfig] = None):
        self.config = config or RuleEngineConfig()
        self._engines_cache: Dict[str, RuleEngine] = {}
        self._rulesets_cache: Dict[str, dict] = {}
        
    def get_engine_for_marketplace(self, marketplace: str) -> RuleEngine:
        """Get or create a rule engine for a specific marketplace."""
        cache_key = marketplace.lower()
        
        if self.config.cache_enabled and cache_key in self._engines_cache:
            return self._engines_cache[cache_key]
        
        # Create engine
        engine = RuleEngine()
        
        # Load ruleset for marketplace
        ruleset_file = self._get_ruleset_file(marketplace)
        if ruleset_file.exists():
            # Load rules and mappings from the YAML file
            engine.load_ruleset(str(ruleset_file))
        
        if self.config.cache_enabled:
            self._engines_cache[cache_key] = engine
            
        return engine
    
    def _get_ruleset_file(self, marketplace: str) -> Path:
        """Get the path to the ruleset file for a marketplace."""
        # Try marketplace-specific ruleset
        ruleset_file = self.config.rulesets_path / f"{marketplace.lower()}.yaml"
        
        # Fallback to default if not found
        if not ruleset_file.exists():
            logger.warning(f"Ruleset not found for {marketplace}, using default")
            ruleset_file = self.config.rulesets_path / "default.yaml"
        
        return ruleset_file
    
    def _load_marketplace_ruleset(self, marketplace: str) -> dict:
        """Load ruleset YAML file for a marketplace."""
        cache_key = marketplace.lower()
        
        if self.config.cache_enabled and cache_key in self._rulesets_cache:
            return self._rulesets_cache[cache_key]
        
        # Try to find marketplace-specific ruleset
        ruleset_file = self.config.rulesets_path / f"{marketplace.lower()}.yaml"
        
        # Fallback to default ruleset if marketplace-specific not found
        if not ruleset_file.exists():
            logger.warning(f"Ruleset not found for {marketplace}, using default")
            ruleset_file = self.config.rulesets_path / "default.yaml"
            
        if not ruleset_file.exists():
            # Return minimal ruleset if no files found
            logger.error(f"No ruleset files found in {self.config.rulesets_path}")
            return {
                "version": "1.0",
                "name": f"{marketplace} Rules",
                "rules": [],
                "mappings": {}
            }
        
        try:
            ruleset = load_ruleset(str(ruleset_file))
            
            if self.config.cache_enabled:
                self._rulesets_cache[cache_key] = ruleset
                
            return ruleset
            
        except Exception as e:
            logger.error(f"Error loading ruleset for {marketplace}: {e}")
            return {
                "version": "1.0",
                "name": f"{marketplace} Rules",
                "rules": [],
                "mappings": {}
            }
    
    def validate_row(
        self, 
        row: Dict[str, Any], 
        marketplace: str,
        row_number: int = 0
    ) -> List[ValidationItem]:
        """Validate a single row using the rule engine."""
        engine = self.get_engine_for_marketplace(marketplace)
        results = engine.execute(row, auto_fix=False)
        
        validation_items = []
        
        for result in results:
            validation_item = self._convert_result_to_validation_item(
                result, 
                row_number,
                row
            )
            if validation_item:
                validation_items.append(validation_item)
                
        return validation_items
    
    def validate_and_fix_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        auto_fix: bool = True
    ) -> tuple[Dict[str, Any], List[ValidationItem]]:
        """Validate and optionally fix a row."""
        import copy
        engine = self.get_engine_for_marketplace(marketplace)
        
        # Create a deep copy to preserve original row
        fixed_row = copy.deepcopy(row)
        
        # Run validation with auto-fix on the copy
        results = engine.execute(fixed_row, auto_fix=auto_fix)
        
        validation_items = []
        
        for result in results:
            # The fixes are already applied to fixed_row by engine.execute()
            validation_item = self._convert_result_to_validation_item(
                result,
                row_number,
                row  # Pass original row for comparison
            )
            if validation_item:
                validation_items.append(validation_item)
        
        return fixed_row, validation_items
    
    def _convert_result_to_validation_item(
        self,
        result: RuleResult,
        row_number: int,
        original_row: Dict[str, Any]
    ) -> Optional[ValidationItem]:
        """Convert RuleResult to ValidationItem for API response."""
        
        # Skip PASS and SKIP results - they don't need to be reported
        if result.status in ["PASS", "SKIP"]:
            return None
        
        # Map RuleStatus to ValidationStatus
        if result.status == "FAIL":
            status = ValidationStatus.ERROR
        elif result.status == "FIXED":
            status = ValidationStatus.WARNING
        elif result.status == "ERROR":
            status = ValidationStatus.ERROR
        else:
            status = ValidationStatus.INFO
        
        # Extract field from metadata or rule_id
        field = result.metadata.get("field") if result.metadata else None
        if not field and "_" in result.rule_id:
            # Try to extract field from rule_id (e.g., "sku_required" -> "sku")
            field = result.rule_id.rsplit("_", 1)[0]
        
        # Build error detail
        error_detail = None
        if result.status in ["FAIL", "ERROR"]:
            error_detail = ErrorDetail(
                code=result.rule_id,
                message=result.message or f"Validation failed for rule {result.rule_id}",
                severity=self._map_severity(result),
                field=field,
                value=original_row.get(field) if field else None,
                expected=result.metadata.get("expected") if result.metadata else None
            )
        
        # Build correction detail
        correction_detail = None
        if result.status == "FIXED":
            fixed_value = result.metadata.get("fixed_value") if result.metadata else None
            if fixed_value is not None:
                correction_detail = CorrectionDetail(
                    field=field or "",
                    original_value=original_row.get(field) if field else None,
                    corrected_value=fixed_value,
                    correction_type=result.metadata.get("fix_type", "auto_fix") if result.metadata else "auto_fix",
                    confidence=result.metadata.get("confidence", 1.0) if result.metadata else 1.0
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
    
    def _map_severity(self, result: RuleResult) -> Severity:
        """Map rule result to severity level."""
        # Check metadata for severity hint
        if result.metadata and "severity" in result.metadata:
            severity_str = result.metadata["severity"].upper()
            if severity_str in ["CRITICAL", "ERROR"]:
                return Severity.ERROR
            elif severity_str == "WARNING":
                return Severity.WARNING
            else:
                return Severity.INFO
        
        # Default based on status
        if result.status == "ERROR":
            return Severity.ERROR
        elif result.status == "FAIL":
            return Severity.WARNING
        else:
            return Severity.INFO
    
    def clear_cache(self):
        """Clear all cached engines and rulesets."""
        self._engines_cache.clear()
        self._rulesets_cache.clear()
        logger.info("Rule engine cache cleared")
    
    def reload_marketplace_rules(self, marketplace: str):
        """Reload rules for a specific marketplace."""
        cache_key = marketplace.lower()
        
        # Remove from cache
        self._engines_cache.pop(cache_key, None)
        self._rulesets_cache.pop(cache_key, None)
        
        # Reload
        self.get_engine_for_marketplace(marketplace)
        logger.info(f"Reloaded rules for marketplace: {marketplace}")