from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple

from schemas.validate import ValidationItem


class IRuleEngineService(ABC):
    """Interface for rule engine services"""

    @abstractmethod
    def validate_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
    ) -> List[ValidationItem]:
        """Validate a single row."""
        raise NotImplementedError

    @abstractmethod
    def validate_and_fix_row(
        self,
        row: Dict[str, Any],
        marketplace: str,
        row_number: int = 0,
        auto_fix: bool = True,
    ) -> Tuple[Dict[str, Any], List[ValidationItem]]:
        """Validate and optionally fix a row."""
        raise NotImplementedError

    @abstractmethod
    def clear_cache(self) -> None:
        """Clear internal caches."""
        raise NotImplementedError

    @abstractmethod
    def reload_marketplace_rules(self, marketplace: str) -> None:
        """Reload rules for a marketplace."""
        raise NotImplementedError
