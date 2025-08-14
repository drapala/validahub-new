"""
Validator Interface Definitions
Defines the contracts for validators and validation pipeline
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd
from .rule import ValidationError


class IValidator(ABC):
    """Base interface for validators"""
    
    @abstractmethod
    def validate(self, data: pd.DataFrame, context: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate a dataframe
        
        Args:
            data: DataFrame to validate
            context: Additional context (marketplace, category, etc)
            
        Returns:
            List of validation errors
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get validator name"""
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """
        Get validator priority (lower runs first)
        
        Returns:
            Priority value (default 100)
        """
        return 100


class IValidationPipeline(ABC):
    """Interface for validation pipeline"""
    
    @abstractmethod
    def add_validator(self, validator: IValidator) -> None:
        """Add a validator to the pipeline"""
        pass
    
    @abstractmethod
    def remove_validator(self, name: str) -> None:
        """Remove a validator by name"""
        pass
    
    @abstractmethod
    def validate(self, data: pd.DataFrame, context: Dict[str, Any]) -> List[ValidationError]:
        """Run all validators in pipeline"""
        pass
    
    @abstractmethod
    def get_validators(self) -> List[IValidator]:
        """Get list of validators in order"""
        pass