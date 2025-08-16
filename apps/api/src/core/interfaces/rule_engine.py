"""
Interfaces for rule engine abstractions.
Following Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path


class IRulesetRepository(ABC):
    """
    Abstract interface for ruleset storage.
    Allows switching between filesystem, S3, database, etc.
    """
    
    @abstractmethod
    async def get_ruleset(self, marketplace: str) -> Dict[str, Any]:
        """
        Retrieve ruleset configuration for a marketplace.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            Dict containing ruleset configuration
        """
        pass
    
    @abstractmethod
    async def save_ruleset(self, marketplace: str, ruleset: Dict[str, Any]) -> None:
        """
        Save ruleset configuration for a marketplace.
        
        Args:
            marketplace: The marketplace identifier
            ruleset: The ruleset configuration to save
        """
        pass
    
    @abstractmethod
    async def list_marketplaces(self) -> List[str]:
        """
        List all available marketplaces with rulesets.
        
        Returns:
            List of marketplace identifiers
        """
        pass
    
    @abstractmethod
    async def exists(self, marketplace: str) -> bool:
        """
        Check if a ruleset exists for a marketplace.
        
        Args:
            marketplace: The marketplace identifier
            
        Returns:
            True if ruleset exists, False otherwise
        """
        pass


class IRuleEngine(ABC):
    """
    Abstract interface for rule engine operations.
    Decouples domain logic from specific rule engine implementations.
    """
    
    @abstractmethod
    def load_ruleset(self, ruleset: Dict[str, Any]) -> None:
        """
        Load a ruleset configuration into the engine.
        
        Args:
            ruleset: The ruleset configuration dictionary
        """
        pass
    
    @abstractmethod
    def execute(self, data: Dict[str, Any], auto_fix: bool = False) -> List[Any]:
        """
        Execute rules against data.
        
        Args:
            data: The data to validate
            auto_fix: Whether to apply automatic fixes
            
        Returns:
            List of rule execution results
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear loaded rules and reset engine state."""
        pass


class IRuleEngineFactory(ABC):
    """
    Factory interface for creating rule engines.
    Supports different engine types and configurations.
    """
    
    @abstractmethod
    def create_engine(self, engine_type: str = "default") -> IRuleEngine:
        """
        Create a rule engine instance.
        
        Args:
            engine_type: Type of engine to create
            
        Returns:
            IRuleEngine instance
        """
        pass


class IRuleEngineService(ABC):
    """
    High-level service interface for rule engine operations.
    Orchestrates repository and engine interactions.
    """
    
    @abstractmethod
    async def validate_row(
        self, 
        row: Dict[str, Any], 
        marketplace: str,
        row_number: int = 0
    ) -> List[Any]:
        """
        Validate a single row using rules for the marketplace.
        
        Args:
            row: Data row to validate
            marketplace: Target marketplace
            row_number: Row number for error reporting
            
        Returns:
            List of validation results
        """
        pass
    
    @abstractmethod
    async def validate_and_fix_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        auto_fix: bool = True
    ) -> tuple[Dict[str, Any], List[Any]]:
        """
        Validate and optionally fix a row.
        
        Args:
            row: Data row to validate and fix
            marketplace: Target marketplace
            row_number: Row number for error reporting
            auto_fix: Whether to apply automatic fixes
            
        Returns:
            Tuple of (fixed_row, validation_results)
        """
        pass
    
    @abstractmethod
    async def reload_marketplace_rules(self, marketplace: str) -> None:
        """
        Reload rules for a specific marketplace.
        
        Args:
            marketplace: The marketplace to reload rules for
        """
        pass
    
    @abstractmethod
    async def clear_cache(self) -> None:
        """Clear all cached rules and engines."""
        pass