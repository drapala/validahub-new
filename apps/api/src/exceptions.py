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


class MissingParameterError(ValueError):
    """Required parameter is missing."""
    def __init__(self, message: str, parameter_name: str = None):
        super().__init__(message)
        self.parameter_name = parameter_name