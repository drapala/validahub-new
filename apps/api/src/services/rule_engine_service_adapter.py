"""
Adapter that provides backward compatibility for RuleEngineService.
This allows gradual migration to the refactored version.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from .rule_engine_service_refactored import (
    RuleEngineServiceRefactored,
    RuleEngineServiceConfig
)
from ..infrastructure.loaders.rule_loader import RuleLoaderConfig
from ..infrastructure.factories.rule_engine_factory import RuleEngineFactoryConfig
from ..schemas.validate import ValidationItem

logger = logging.getLogger(__name__)


@dataclass
class RuleEngineConfig:
    """Legacy configuration for backward compatibility."""
    rulesets_path: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent.parent / "rulesets")
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds (not used in refactored version)


class RuleEngineService:
    """
    Adapter class that maintains the old RuleEngineService interface
    while using the refactored implementation internally.
    
    This allows existing code to continue working while we gradually
    migrate to the new component-based architecture.
    """
    
    def __init__(self, config: Optional[RuleEngineConfig] = None):
        """
        Initialize with legacy configuration.
        
        Args:
            config: Legacy RuleEngineConfig
        """
        self.config = config or RuleEngineConfig()
        
        # Convert legacy config to new format
        rule_loader_config = RuleLoaderConfig(
            rulesets_path=self.config.rulesets_path,
            fallback_to_default=True
        )
        
        engine_factory_config = RuleEngineFactoryConfig(
            cache_engines=self.config.cache_enabled,
            rule_loader_config=rule_loader_config
        )
        
        service_config = RuleEngineServiceConfig(
            rule_loader_config=rule_loader_config,
            engine_factory_config=engine_factory_config
        )
        
        # Create refactored service
        self._service = RuleEngineServiceRefactored(config=service_config)
        
        # Legacy compatibility attributes
        self._engines_cache = {}  # Not used, kept for compatibility
        self._rulesets_cache = {}  # Not used, kept for compatibility
    
    def get_engine_for_marketplace(self, marketplace: str):
        """
        Legacy method for getting engine (for compatibility).
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            RuleEngine instance
        """
        return self._service.engine_factory.get_engine(marketplace)
    
    def _get_ruleset_file(self, marketplace: str) -> Path:
        """
        Legacy method for getting ruleset file path.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Path to ruleset file
        """
        # Delegate to rule loader
        return self._service.rule_loader._find_ruleset_file(marketplace)
    
    def _load_marketplace_ruleset(self, marketplace: str) -> dict:
        """
        Legacy method for loading ruleset.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Loaded ruleset dictionary
        """
        return self._service.rule_loader.load_ruleset(marketplace)
    
    def validate_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0
    ) -> List[ValidationItem]:
        """
        Validate a single row using the rule engine.
        
        Args:
            row: Row data to validate
            marketplace: Target marketplace
            row_number: Row number for reporting
            
        Returns:
            List of validation items
        """
        return self._service.validate_row(row, marketplace, row_number)
    
    def validate_and_fix_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        auto_fix: bool = True
    ) -> Tuple[Dict[str, Any], List[ValidationItem]]:
        """
        Validate and optionally fix a row.
        
        Args:
            row: Row data to validate
            marketplace: Target marketplace  
            row_number: Row number for reporting
            auto_fix: Whether to apply fixes
            
        Returns:
            Tuple of (fixed_row, validation_items)
        """
        return self._service.validate_and_fix_row(
            row, marketplace, row_number, auto_fix
        )
    
    def _convert_result_to_validation_item(self, result, row_number, original_row):
        """
        Legacy method kept for compatibility.
        Delegates to ResultMapper.
        """
        return self._service.result_mapper.map_to_validation_item(
            result, row_number, original_row
        )
    
    def _map_severity(self, result):
        """
        Legacy method kept for compatibility.
        Delegates to ResultMapper.
        """
        return self._service.result_mapper._map_severity(result)
    
    def clear_cache(self):
        """Clear all cached engines and rulesets."""
        self._service.clear_cache()
    
    def reload_marketplace_rules(self, marketplace: str):
        """
        Reload rules for a specific marketplace.
        
        Args:
            marketplace: The marketplace to reload
        """
        self._service.reload_marketplace_rules(marketplace)