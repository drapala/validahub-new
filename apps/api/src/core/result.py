"""
Result pattern for error handling without exceptions.
Inspired by Rust's Result type and functional programming.
"""

from typing import TypeVar, Generic, Optional, Union, Callable, NoReturn
from dataclasses import dataclass
from enum import Enum

T = TypeVar('T')  # Success type
E = TypeVar('E')  # Error type


class JobError(str, Enum):
    """Standard job-related errors."""
    NOT_FOUND = "job_not_found"
    UNAUTHORIZED = "unauthorized"
    INVALID_STATUS = "invalid_status"
    ALREADY_EXISTS = "already_exists"
    QUEUE_ERROR = "queue_error"
    VALIDATION_ERROR = "validation_error"
    DATABASE_ERROR = "database_error"


@dataclass(frozen=True)
class Ok(Generic[T, E]):
    """Represents a successful result."""
    value: T
    
    def is_ok(self) -> bool:
        return True
    
    def is_err(self) -> bool:
        return False
    
    def unwrap(self) -> T:
        """Get the value. Safe because we know it's Ok."""
        return self.value
    
    def unwrap_err(self) -> NoReturn:
        """Raises because this is not an error."""
        raise ValueError("Called unwrap_err on Ok value")
    
    def map(self, f: Callable[[T], T]) -> 'Result[T, E]':
        """Transform the value if Ok."""
        return Ok(f(self.value))
    
    def map_err(self, f: Callable[[E], E]) -> 'Result[T, E]':
        """No-op for Ok values."""
        return self


@dataclass(frozen=True)
class Err(Generic[T, E]):
    """Represents an error result."""
    error: E
    
    def is_ok(self) -> bool:
        return False
    
    def is_err(self) -> bool:
        return True
    
    def unwrap(self) -> NoReturn:
        """Raises because this is an error."""
        raise ValueError(f"Called unwrap on Err value: {self.error}")
    
    def unwrap_err(self) -> E:
        """Get the error. Safe because we know it's Err."""
        return self.error
    
    def map(self, f: Callable[[T], T]) -> 'Result[T, E]':
        """No-op for Err values."""
        return self
    
    def map_err(self, f: Callable[[E], E]) -> 'Result[T, E]':
        """Transform the error if Err."""
        return Err(f(self.error))


# Type alias for Result
Result = Union[Ok[T, E], Err[T, E]]


def result_ok(value: T) -> Result[T, E]:
    """Helper to create Ok result."""
    return Ok(value)


def result_err(error: E) -> Result[T, E]:
    """Helper to create Err result."""
    return Err(error)