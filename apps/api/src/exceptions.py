"""
Custom exceptions for the API application.
"""


class TransientError(Exception):
    """Transient error that should be retried."""
    pass


class ValidationError(Exception):
    """Validation error that should not be retried."""
    pass


class AuthenticationError(Exception):
    """Authentication error."""
    pass