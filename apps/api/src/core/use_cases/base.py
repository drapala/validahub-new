"""
Base use case classes following Clean Architecture principles.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class UseCase(ABC, Generic[TInput, TOutput]):
    """Base class for all use cases."""
    
    @abstractmethod
    async def execute(self, input_data: TInput) -> TOutput:
        """Execute the use case with given input."""
        pass