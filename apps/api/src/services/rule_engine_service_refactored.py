"""
Refactored RuleEngineService using separate components.
This version delegates responsibilities to specialized classes.
"""

import copy
from core.logging_config import get_logger
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from infrastructure.factories.rule_engine_factory import (
    RuleEngineFactory,
    RuleEngineFactoryConfig
)
from infrastructure.loaders.rule_loader import RuleLoader, RuleLoaderConfig
from infrastructure.mappers.result_mapper import ResultMapper
from schemas.validate import ValidationItem

logger = get_logger(__name__)


@dataclass
class RuleEngineServiceConfig:
    """Configuration for the refactored rule engine service."""
    rule_loader_config: Optional[RuleLoaderConfig] = None
    engine_factory_config: Optional[RuleEngineFactoryConfig] = None


class RuleEngineServiceRefactored:
    """
    Refactored service for rule engine operations.
    
    This version delegates specific responsibilities to:
    - RuleLoader: Loading ruleset files
    - RuleEngineFactory: Creating and managing engine instances
    - ResultMapper: Converting between result formats
    
    The service now focuses only on orchestrating these components.
    """
    
    def __init__(
        self,
        config: Optional[RuleEngineServiceConfig] = None,
        rule_loader: Optional[RuleLoader] = None,
        engine_factory: Optional[RuleEngineFactory] = None,
        result_mapper: Optional[ResultMapper] = None
    ):
        """
        Initialize service with optional components.
        
        Args:
            config: Service configuration
            rule_loader: Optional rule loader instance
            engine_factory: Optional engine factory instance
            result_mapper: Optional result mapper instance
        """
        self.config = config or RuleEngineServiceConfig()
        
        # Initialize components
        self.rule_loader = rule_loader or RuleLoader(self.config.rule_loader_config)
        self.engine_factory = engine_factory or RuleEngineFactory(
            self.config.engine_factory_config,
            self.rule_loader
        )
        self.result_mapper = result_mapper or ResultMapper()
    
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
        # Get engine for marketplace
        engine = self.engine_factory.get_engine(marketplace)
        
        # Execute validation
        results = engine.execute(row, auto_fix=False)
        
        # Map results to validation items
        validation_items = self.result_mapper.map_multiple(
            results, row_number, row
        )
        
        return validation_items
    
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
        # Create a deep copy to preserve original row
        fixed_row = copy.deepcopy(row)
        
        # Get engine for marketplace
        engine = self.engine_factory.get_engine(marketplace)
        
        # Run validation with auto-fix on the copy
        results = engine.execute(fixed_row, auto_fix=auto_fix)
        
        # Map results to validation items
        validation_items = self.result_mapper.map_multiple(
            results, row_number, row  # Use original row for comparison
        )
        
        return fixed_row, validation_items
    
    def clear_cache(self):
        """Clear all caches in the service."""
        self.engine_factory.clear_cache()
        logger.info("Rule engine service cache cleared")
    
    def reload_marketplace_rules(self, marketplace: str):
        """
        Reload rules for a specific marketplace.
        
        Args:
            marketplace: The marketplace to reload
        """
        self.engine_factory.reload_engine(marketplace)
        logger.info(f"Reloaded rules for marketplace: {marketplace}")
    
    def get_service_stats(self) -> dict:
        """
        Get statistics about the service.
        
        Returns:
            Dictionary with service statistics
        """
        return {
            "engine_stats": self.engine_factory.get_engine_stats(),
            "available_marketplaces": self.rule_loader.list_available_marketplaces()
        }