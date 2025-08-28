"""Interfaces for rule engine service."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

from src.schemas.validate import ValidationItem


class IRuleEngineService(ABC):
    """Abstract interface for rule engine service."""

    @abstractmethod
    async def validate_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
    ) -> List[ValidationItem]:
        """Validate a single row of data."""

    @abstractmethod
    async def validate_and_fix_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        auto_fix: bool = True,
    ) -> Tuple[Dict[str, Any], List[ValidationItem]]:
        """Validate and optionally fix a row."""
