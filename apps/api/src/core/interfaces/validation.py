"""
Validation interfaces for decoupling the pipeline from concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

from schemas.validate import ValidationItem


class IValidator(ABC):
    """
    Interface for validators that can validate and fix rows.
    This interface allows the ValidationPipeline to work with any validator implementation.
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
        Validate a single row.
        
        Args:
            row: Row data to validate
            marketplace: Target marketplace
            row_number: Row number for reporting
            context: Additional validation context
            
        Returns:
            List of validation items with errors and warnings
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
            auto_fix: Whether to apply automatic fixes
            context: Additional validation context
            
        Returns:
            Tuple of (fixed_row, validation_items)
        """
        pass