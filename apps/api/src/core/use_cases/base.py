"""
Base use case definition following Clean Architecture principles.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class UseCase(ABC, Generic[TInput, TOutput]):
    """
    Abstract base class for use cases.
    
    Use cases encapsulate business logic and are independent of
    external frameworks, databases, or UI concerns.
    """
    
    @abstractmethod
    async def execute(self, input_data: TInput) -> TOutput:
        """
        Execute the use case business logic.
        
        Args:
            input_data: The input data for the use case
            
        Returns:
            The output data from the use case
        """
        pass