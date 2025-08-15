"""Common response definitions for API v1"""

from src.schemas.errors import (
    ProblemDetail,
    FileSizeProblemDetail,
    RateLimitProblemDetail,
    ValidationProblemDetail
)

# Common error responses for all endpoints
COMMON_ERROR_RESPONSES = {
    400: {
        "model": ProblemDetail,
        "description": "Bad request"
    },
    401: {
        "model": ProblemDetail,
        "description": "Unauthorized - Missing or invalid authentication"
    },
    403: {
        "model": ProblemDetail,
        "description": "Forbidden - Insufficient permissions"
    },
    413: {
        "model": FileSizeProblemDetail,
        "description": "File too large"
    },
    415: {
        "model": ProblemDetail,
        "description": "Unsupported media type"
    },
    422: {
        "model": ValidationProblemDetail,
        "description": "Validation error"
    },
    429: {
        "model": RateLimitProblemDetail,
        "description": "Rate limit exceeded"
    },
    500: {
        "model": ProblemDetail,
        "description": "Internal server error"
    }
}

# Responses for validation endpoints
VALIDATION_RESPONSES = {
    **COMMON_ERROR_RESPONSES,
}

# Responses for correction endpoints
CORRECTION_RESPONSES = {
    **COMMON_ERROR_RESPONSES,
    200: {
        "description": "Successful correction",
        "content": {
            "text/csv": {
                "schema": {
                    "type": "string",
                    "format": "binary"
                },
                "example": "sku,price,brand\\nABC-123,29.99,Apple\\n"
            },
            "application/json": {
                "schema": {
                    "$ref": "#/components/schemas/CorrectCsvResponse"
                }
            }
        }
    }
}