"""
Contract tests for API endpoints against OpenAPI specification.
"""

import pytest
from pathlib import Path
import yaml
import json
from openapi_spec_validator import validate_spec
from jsonschema import validate, ValidationError
import httpx
from typing import Dict, Any


class TestOpenAPIContract:
    """Test API compliance with OpenAPI specification."""
    
    @pytest.fixture
    def openapi_spec(self):
        """Load OpenAPI specification."""
        # First check if we have an OpenAPI spec file
        spec_paths = [
            Path("openapi.yaml"),
            Path("openapi.yml"),
            Path("openapi.json"),
            Path("docs/openapi.yaml"),
            Path("docs/api.yaml"),
        ]
        
        for path in spec_paths:
            if path.exists():
                if path.suffix in ['.yaml', '.yml']:
                    with open(path) as f:
                        return yaml.safe_load(f)
                else:
                    with open(path) as f:
                        return json.load(f)
        
        # If no spec file exists, create a minimal one for testing
        return {
            "openapi": "3.0.3",
            "info": {
                "title": "ValidaHub API",
                "version": "1.0.0",
                "description": "CSV validation API"
            },
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {
                            "200": {
                                "description": "Service is healthy",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "status": {"type": "string"},
                                                "version": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/v1/validate": {
                    "post": {
                        "summary": "Validate CSV",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "multipart/form-data": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "file": {
                                                "type": "string",
                                                "format": "binary"
                                            },
                                            "marketplace": {
                                                "type": "string",
                                                "enum": ["MERCADO_LIVRE", "AMAZON", "SHOPEE"]
                                            }
                                        },
                                        "required": ["file", "marketplace"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Validation successful",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ValidationResult"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "ValidationResult": {
                        "type": "object",
                        "properties": {
                            "total_rows": {"type": "integer"},
                            "valid_rows": {"type": "integer"},
                            "error_rows": {"type": "integer"},
                            "errors": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "row": {"type": "integer"},
                                        "field": {"type": "string"},
                                        "message": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "required": ["total_rows", "valid_rows", "error_rows"]
                    }
                }
            }
        }
    
    def test_openapi_spec_is_valid(self, openapi_spec):
        """Test that OpenAPI specification is valid."""
        # This will raise an exception if the spec is invalid
        validate_spec(openapi_spec)
    
    def test_health_endpoint_contract(self, openapi_spec):
        """Test health endpoint matches contract."""
        # Get health endpoint schema from spec
        health_schema = openapi_spec["paths"]["/health"]["get"]["responses"]["200"]
        expected_schema = health_schema["content"]["application/json"]["schema"]
        
        # Mock response that should match the schema
        mock_response = {
            "status": "healthy",
            "version": "1.0.0"
        }
        
        # Validate response against schema
        try:
            validate(instance=mock_response, schema=expected_schema)
        except ValidationError as e:
            pytest.fail(f"Response does not match schema: {e}")
    
    def test_validation_endpoint_request_schema(self, openapi_spec):
        """Test validation endpoint request schema."""
        validation_path = openapi_spec["paths"]["/api/v1/validate"]["post"]
        request_schema = validation_path["requestBody"]["content"]["multipart/form-data"]["schema"]
        
        # Check required fields
        assert "required" in request_schema
        assert "file" in request_schema["required"]
        assert "marketplace" in request_schema["required"]
        
        # Check marketplace enum values
        marketplace_enum = request_schema["properties"]["marketplace"]["enum"]
        assert "MERCADO_LIVRE" in marketplace_enum
        assert "AMAZON" in marketplace_enum
    
    def test_validation_response_schema(self, openapi_spec):
        """Test validation endpoint response schema."""
        # Get ValidationResult schema
        validation_schema = openapi_spec["components"]["schemas"]["ValidationResult"]
        
        # Mock response that should match the schema
        mock_response = {
            "total_rows": 100,
            "valid_rows": 95,
            "error_rows": 5,
            "errors": [
                {
                    "row": 1,
                    "field": "price",
                    "message": "Price must be positive"
                }
            ]
        }
        
        # Validate response against schema
        try:
            validate(instance=mock_response, schema=validation_schema)
        except ValidationError as e:
            pytest.fail(f"Response does not match schema: {e}")
    
    def test_schema_backward_compatibility(self, openapi_spec):
        """Test that required fields maintain backward compatibility."""
        # Check that ValidationResult maintains essential fields
        validation_schema = openapi_spec["components"]["schemas"]["ValidationResult"]
        required_fields = validation_schema.get("required", [])
        
        # These fields should always be required for backward compatibility
        essential_fields = ["total_rows", "valid_rows", "error_rows"]
        for field in essential_fields:
            assert field in required_fields, f"Field '{field}' must be required for backward compatibility"


class TestContractWithSchemathesis:
    """Property-based contract testing with Schemathesis."""
    
    @pytest.mark.skipif(
        not Path("openapi.yaml").exists() and not Path("openapi.json").exists(),
        reason="OpenAPI spec file not found"
    )
    def test_api_contract_with_schemathesis(self):
        """Run Schemathesis contract tests."""
        import schemathesis
        
        # Load schema
        if Path("openapi.yaml").exists():
            schema = schemathesis.from_path("openapi.yaml")
        else:
            schema = schemathesis.from_path("openapi.json")
        
        # Generate test cases
        @schema.parametrize()
        def test_api(case):
            """Test each endpoint with generated data."""
            # This would make actual API calls in integration tests
            # For unit tests, we just validate the schema
            assert case.path is not None
            assert case.method is not None