"""
Interfaces for validation pipeline abstractions.
Decouples pipeline from specific validator implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

from ...schemas.validate import (
    ValidationResult,
    ValidationItem,
    Marketplace,
    Category
)


class IValidator(ABC):
    """
    Abstract interface for validators.
    Allows different validation strategies (rules, ML, custom).
    """
    
    @abstractmethod
    async def validate_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationItem]:
        """
        Validate a single row of data.
        
        Args:
            row: Row data to validate
            marketplace: Target marketplace
            row_number: Row number for reporting
            context: Additional validation context
            
        Returns:
            List of validation items
        """
        pass
    
    @abstractmethod
    async def validate_and_fix_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        auto_fix: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], List[ValidationItem]]:
        """
        Validate and optionally fix a row.
        
        Args:
            row: Row data to validate and fix
            marketplace: Target marketplace
            row_number: Row number for reporting
            auto_fix: Whether to apply fixes
            context: Additional validation context
            
        Returns:
            Tuple of (fixed_row, validation_items)
        """
        pass


class IDataAdapter(ABC):
    """
    Abstract interface for data adapters.
    Handles conversion between different data formats.
    """
    
    @abstractmethod
    def dataframe_to_rows(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Convert DataFrame to list of row dictionaries.
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            List of row dictionaries
        """
        pass
    
    @abstractmethod
    def rows_to_dataframe(self, rows: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert list of rows to DataFrame.
        
        Args:
            rows: List of row dictionaries
            
        Returns:
            Pandas DataFrame
        """
        pass
    
    @abstractmethod
    def normalize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a row for validation.
        
        Args:
            row: Raw row data
            
        Returns:
            Normalized row data
        """
        pass


class IValidationOrchestrator(ABC):
    """
    Abstract interface for validation orchestration.
    Coordinates validation workflow without implementation details.
    """
    
    @abstractmethod
    async def orchestrate_validation(
        self,
        data: pd.DataFrame,
        marketplace: Marketplace,
        category: Optional[Category] = None,
        auto_fix: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Orchestrate the validation process.
        
        Args:
            data: Data to validate
            marketplace: Target marketplace
            category: Product category
            auto_fix: Whether to apply fixes
            options: Additional options
            
        Returns:
            Complete validation result
        """
        pass
    
    @abstractmethod
    async def orchestrate_row_validation(
        self,
        row: Dict[str, Any],
        marketplace: Marketplace,
        category: Optional[Category] = None,
        row_number: int = 1,
        auto_fix: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], List[ValidationItem]]:
        """
        Orchestrate single row validation.
        
        Args:
            row: Row to validate
            marketplace: Target marketplace
            category: Product category
            row_number: Row number
            auto_fix: Whether to apply fixes
            options: Additional options
            
        Returns:
            Tuple of (fixed_row, validation_items)
        """
        pass


class IValidationPipeline(ABC):
    """
    High-level interface for validation pipeline.
    Provides clean API for validation operations.
    """
    
    @abstractmethod
    async def validate(
        self,
        df: pd.DataFrame,
        marketplace: Marketplace,
        category: Category,
        auto_fix: bool = False
    ) -> ValidationResult:
        """
        Validate a DataFrame.
        
        Args:
            df: DataFrame to validate
            marketplace: Target marketplace
            category: Product category
            auto_fix: Whether to apply fixes
            
        Returns:
            Validation result
        """
        pass
    
    @abstractmethod
    async def validate_single_row(
        self,
        row: Dict[str, Any],
        marketplace: Marketplace,
        category: Optional[Category] = None,
        row_number: int = 1,
        auto_fix: bool = False
    ) -> Tuple[Dict[str, Any], List[ValidationItem]]:
        """
        Validate a single row.
        
        Args:
            row: Row to validate
            marketplace: Target marketplace
            category: Product category
            row_number: Row number
            auto_fix: Whether to apply fixes
            
        Returns:
            Tuple of (fixed_row, validation_items)
        """
        pass
    
    @abstractmethod
    async def reload_rules(self, marketplace: Optional[Marketplace] = None):
        """
        Reload validation rules.
        
        Args:
            marketplace: Specific marketplace or None for all
        """
        pass


class IValidationStrategy(ABC):
    """
    Strategy pattern for validation approaches.
    Allows switching between different validation methods.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name."""
        pass
    
    @abstractmethod
    async def validate(
        self,
        data: Any,
        config: Dict[str, Any]
    ) -> List[ValidationItem]:
        """
        Execute validation strategy.
        
        Args:
            data: Data to validate
            config: Strategy configuration
            
        Returns:
            List of validation items
        """
        pass
    
    @abstractmethod
    def supports_auto_fix(self) -> bool:
        """Check if strategy supports auto-fixing."""
        pass