"""
Refactored Rule Engine Service using dependency injection.
Decoupled from filesystem through repository pattern.
"""

import logging
import copy
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..core.interfaces.rule_engine import (
    IRuleEngine,
    IRuleEngineFactory,
    IRuleEngineService,
    IRulesetRepository
)
from ..schemas.validate import ValidationItem, ErrorDetail, CorrectionDetail
from ..core.enums import ValidationStatus

logger = logging.getLogger(__name__)


@dataclass
class RuleEngineServiceConfig:
    """Configuration for the refactored rule engine service."""
    cache_engines: bool = True
    max_cached_engines: int = 10


class RuleEngineAdapter(IRuleEngine):
    """
    Adapter for the existing rule engine to match IRuleEngine interface.
    This allows us to use the current rule engine without modification.
    """
    
    def __init__(self, engine):
        """Wrap existing engine instance."""
        self._engine = engine
    
    def load_ruleset(self, ruleset: Dict[str, Any]) -> None:
        """Load ruleset from dictionary instead of file."""
        # Convert dict ruleset to engine format
        # The existing engine expects a file path, so we need to adapt
        # TODO: Modify rule_engine library to accept dict directly
        import tempfile
        import yaml
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(ruleset, f)
            temp_path = f.name
        
        try:
            self._engine.load_ruleset(temp_path)
        finally:
            import os
            os.unlink(temp_path)
    
    def execute(self, data: Dict[str, Any], auto_fix: bool = False) -> List[Any]:
        """Execute rules against data."""
        return self._engine.execute(data, auto_fix=auto_fix)
    
    def clear(self) -> None:
        """Clear loaded rules."""
        # Reset engine state
        self._engine = self._engine.__class__()


class RuleEngineFactory(IRuleEngineFactory):
    """Factory for creating rule engine instances."""
    
    def create_engine(self, engine_type: str = "default") -> IRuleEngine:
        """
        Create a rule engine instance.
        
        Args:
            engine_type: Type of engine to create
            
        Returns:
            IRuleEngine instance
        """
        if engine_type == "default":
            # Import the existing engine
            import sys
            from pathlib import Path
            
            libs_path = Path(__file__).parent.parent.parent.parent.parent / "libs"
            if str(libs_path) not in sys.path:
                sys.path.insert(0, str(libs_path))
            
            from rule_engine import RuleEngine
            
            # Wrap in adapter
            return RuleEngineAdapter(RuleEngine())
        else:
            raise ValueError(f"Unknown engine type: {engine_type}")


class RuleEngineServiceV2(IRuleEngineService):
    """
    Refactored rule engine service with dependency injection.
    No direct filesystem dependencies.
    """
    
    def __init__(
        self,
        repository: IRulesetRepository,
        factory: Optional[IRuleEngineFactory] = None,
        config: Optional[RuleEngineServiceConfig] = None
    ):
        """
        Initialize service with injected dependencies.
        
        Args:
            repository: Repository for loading rulesets
            factory: Factory for creating engines
            config: Service configuration
        """
        self.repository = repository
        self.factory = factory or RuleEngineFactory()
        self.config = config or RuleEngineServiceConfig()
        
        # Cache for engines
        self._engines_cache: Dict[str, IRuleEngine] = {}
    
    async def get_engine_for_marketplace(self, marketplace: str) -> IRuleEngine:
        """
        Get or create engine for marketplace.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Configured rule engine
        """
        cache_key = marketplace.lower()
        
        # Check cache
        if self.config.cache_engines and cache_key in self._engines_cache:
            return self._engines_cache[cache_key]
        
        # Create new engine
        engine = self.factory.create_engine()
        
        # Load ruleset from repository
        ruleset = await self.repository.get_ruleset(marketplace)
        engine.load_ruleset(ruleset)
        
        # Cache if enabled
        if self.config.cache_engines:
            # Implement LRU-style caching
            if len(self._engines_cache) >= self.config.max_cached_engines:
                # Remove oldest entry
                oldest = next(iter(self._engines_cache))
                del self._engines_cache[oldest]
            
            self._engines_cache[cache_key] = engine
        
        return engine
    
    async def validate_row(
        self, 
        row: Dict[str, Any], 
        marketplace: str,
        row_number: int = 0
    ) -> List[ValidationItem]:
        """
        Validate a single row.
        
        Args:
            row: Data row to validate
            marketplace: Target marketplace
            row_number: Row number for error reporting
            
        Returns:
            List of validation items
        """
        engine = await self.get_engine_for_marketplace(marketplace)
        results = engine.execute(row, auto_fix=False)
        
        validation_items = []
        for result in results:
            item = self._convert_result_to_validation_item(
                result, row_number, row
            )
            if item:
                validation_items.append(item)
        
        return validation_items
    
    async def validate_and_fix_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        auto_fix: bool = True
    ) -> tuple[Dict[str, Any], List[ValidationItem]]:
        """
        Validate and optionally fix a row.
        
        Args:
            row: Data row to validate and fix
            marketplace: Target marketplace
            row_number: Row number for error reporting
            auto_fix: Whether to apply automatic fixes
            
        Returns:
            Tuple of (fixed_row, validation_items)
        """
        engine = await self.get_engine_for_marketplace(marketplace)
        
        # Deep copy to preserve original
        fixed_row = copy.deepcopy(row)
        
        # Execute with auto-fix
        results = engine.execute(fixed_row, auto_fix=auto_fix)
        
        validation_items = []
        for result in results:
            item = self._convert_result_to_validation_item(
                result, row_number, row
            )
            if item:
                validation_items.append(item)
        
        return fixed_row, validation_items
    
    async def reload_marketplace_rules(self, marketplace: str) -> None:
        """
        Reload rules for a marketplace.
        
        Args:
            marketplace: The marketplace to reload
        """
        cache_key = marketplace.lower()
        
        # Remove from cache
        if cache_key in self._engines_cache:
            self._engines_cache[cache_key].clear()
            del self._engines_cache[cache_key]
        
        logger.info(f"Reloaded rules for {marketplace}")
    
    async def clear_cache(self) -> None:
        """Clear all cached engines."""
        for engine in self._engines_cache.values():
            engine.clear()
        self._engines_cache.clear()
        logger.info("All rule engine caches cleared")
    
    def _convert_result_to_validation_item(
        self,
        result: Any,
        row_number: int,
        original_row: Dict[str, Any]
    ) -> Optional[ValidationItem]:
        """
        Convert rule result to validation item.
        
        Args:
            result: Rule execution result
            row_number: Row number
            original_row: Original row data
            
        Returns:
            ValidationItem or None
        """
        # Skip PASS and SKIP results
        if hasattr(result, 'status') and result.status in ["PASS", "SKIP"]:
            return None
        
        # Map status
        status = ValidationStatus.ERROR
        if hasattr(result, 'status'):
            if result.status == "FAIL":
                status = ValidationStatus.ERROR
            elif result.status == "FIXED":
                status = ValidationStatus.WARNING
            elif result.status == "ERROR":
                status = ValidationStatus.ERROR
            else:
                status = ValidationStatus.INFO
        
        # Extract field
        field = None
        if hasattr(result, 'metadata') and result.metadata:
            field = result.metadata.get("field")
        if not field and hasattr(result, 'rule_id') and "_" in result.rule_id:
            field = result.rule_id.rsplit("_", 1)[0]
        
        # Build error detail
        errors = []
        if hasattr(result, 'status') and result.status in ["FAIL", "ERROR"]:
            error = ErrorDetail(
                field=field or "unknown",
                message=getattr(result, 'message', "Validation failed"),
                code=getattr(result, 'rule_id', "UNKNOWN"),
                severity=getattr(result, 'severity', "ERROR"),
                value=original_row.get(field) if field else None
            )
            errors.append(error)
        
        # Build correction detail
        corrections = []
        if hasattr(result, 'status') and result.status == "FIXED":
            if hasattr(result, 'fixes') and result.fixes:
                for fix in result.fixes:
                    correction = CorrectionDetail(
                        field=fix.get("field", field),
                        original_value=fix.get("original"),
                        corrected_value=fix.get("fixed"),
                        correction_type=fix.get("type", "AUTO_FIX"),
                        reason=fix.get("reason", result.message if hasattr(result, 'message') else "")
                    )
                    corrections.append(correction)
        
        return ValidationItem(
            row_number=row_number,
            status=status,
            errors=errors,
            corrections=corrections
        )