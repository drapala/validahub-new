"""Clock port for time abstractions."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional


class ClockPort(ABC):
    """
    Port for time-related operations.
    Allows testing time-sensitive code and ensures UTC consistency.
    """
    
    @abstractmethod
    def now(self) -> datetime:
        """Get current time in UTC."""
        pass
    
    @abstractmethod
    def monotonic(self) -> float:
        """Get monotonic time for measuring intervals (not affected by clock adjustments)."""
        pass
    
    @abstractmethod
    def timestamp(self) -> float:
        """Get current Unix timestamp."""
        pass
    
    @abstractmethod
    def parse_iso(self, iso_string: str) -> datetime:
        """Parse ISO 8601 datetime string to UTC datetime."""
        pass
    
    @abstractmethod
    def format_iso(self, dt: datetime) -> str:
        """Format datetime to ISO 8601 string."""
        pass
    
    @abstractmethod
    def add_seconds(self, dt: datetime, seconds: float) -> datetime:
        """Add seconds to a datetime."""
        pass
    
    @abstractmethod
    def is_expired(self, expiry_time: datetime, buffer_seconds: float = 0) -> bool:
        """Check if a datetime has expired (with optional buffer)."""
        pass