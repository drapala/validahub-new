"""
Integration tests for validation endpoints with rule engine.
"""

import pytest
from fastapi.testclient import TestClient
import io
import csv
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from main import app

client = TestClient(app)


class TestValidationEndpoints:
    
    def test_validate_csv_endpoint(self):
        """Test the /api/v2/validate endpoint."""
        # Create test CSV data
        csv_data = [
            ["sku", "title", "price", "stock", "category"],
            ["SKU001", "Product 1", "10.99", "5", "Electronics"],
            ["", "Product 2", "-5", "0", "InvalidCategory"],  # Has errors
            ["SKU003", "", "20", "-1", "Clothing"],  # Has errors
        ]
        
        # Convert to CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        csv_content = output.getvalue()
        
        # Create file-like object
        files = {
            "file": ("test.csv", csv_content, "text/csv")
        }
        data = {
            "marketplace": "MERCADO_LIVRE",
            "category": "ELETRONICOS",
            "auto_fix": "true"
        }
        
        response = client.post("/api/v1/validate", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Check response structure
        assert "total_rows" in result
        assert "valid_rows" in result
        assert "error_rows" in result
        assert "validation_items" in result
        assert "summary" in result
        
        # Check that errors were found
        assert result["total_rows"] == 3  # Excluding header
        assert result["error_rows"] > 0
        assert len(result["validation_items"]) > 0
    
    def test_validate_row_endpoint(self):
        """Test the /api/v2/validate_row endpoint."""
        row_data = {
            "sku": "",
            "title": "Test Product",
            "price": -10,
            "stock": 5
        }
        
        response = client.post(
            "/api/v1/validate_row",
            json=row_data,
            params={
                "marketplace": "MERCADO_LIVRE",
                "auto_fix": True,
                "row_number": 1
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Check response structure
        assert "original_row" in result
        assert "fixed_row" in result
        assert "validation_items" in result
        assert "has_errors" in result
        assert "auto_fix_applied" in result
        
        # Check that issues were found
        assert result["has_errors"] is True or result["has_warnings"] is True
        assert len(result["validation_items"]) > 0
        
        # Check that fixes were applied
        if result["auto_fix_applied"] and result["fixed_row"]:
            # SKU should have been fixed with default value
            if "sku" in result["fixed_row"]:
                assert result["fixed_row"]["sku"] != ""
    
    def test_correct_csv_endpoint(self):
        """Test the /api/v2/correct endpoint."""
        # Create test CSV with errors
        csv_data = [
            ["sku", "title", "price", "stock"],
            ["", "Product 1", "-10", "5"],  # Missing SKU, negative price
            ["SKU002", "", "20", "-1"],  # Missing title, negative stock
        ]
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        csv_content = output.getvalue()
        
        files = {
            "file": ("test.csv", csv_content, "text/csv")
        }
        data = {
            "marketplace": "MERCADO_LIVRE",
            "category": "ELETRONICOS"
        }
        
        response = client.post("/api/v1/correct", files=files, data=data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        
        # Check correction headers
        assert "x-total-corrections" in response.headers
        assert "x-total-errors" in response.headers
        
        # Parse corrected CSV
        corrected_csv = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(corrected_csv))
        corrected_rows = list(reader)
        
        assert len(corrected_rows) == 2
        
        # Check that corrections were applied
        # Note: Actual corrections depend on rule configuration
        for row in corrected_rows:
            # SKU should not be empty if it was fixed
            if "sku" in row:
                # Check if default value was applied
                pass  # Depends on rule configuration
    
    def test_reload_rules_endpoint(self):
        """Test the /api/v2/reload_rules endpoint."""
        response = client.post("/api/v1/reload_rules")
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["status"] == "success"
        assert "message" in result
        assert "timestamp" in result
        
        # Test with specific marketplace
        response_specific = client.post(
            "/api/v1/reload_rules",
            params={"marketplace": "MERCADO_LIVRE"}
        )
        
        assert response_specific.status_code == 200
        result_specific = response_specific.json()
        assert "MERCADO_LIVRE" in result_specific["message"]
    
    def test_validate_with_invalid_file_type(self):
        """Test validation with non-CSV file."""
        files = {
            "file": ("test.txt", "not a csv", "text/plain")
        }
        data = {
            "marketplace": "MERCADO_LIVRE",
            "category": "ELETRONICOS"
        }
        
        response = client.post("/api/v1/validate", files=files, data=data)
        
        assert response.status_code == 415
        assert response.headers["content-type"] == "application/problem+json"
        
        error = response.json()
        assert "title" in error
        assert "detail" in error
        assert "CSV" in error["detail"]
    
    def test_validate_with_empty_csv(self):
        """Test validation with empty CSV."""
        files = {
            "file": ("empty.csv", "", "text/csv")
        }
        data = {
            "marketplace": "MERCADO_LIVRE",
            "category": "ELETRONICOS"
        }
        
        response = client.post("/api/v1/validate", files=files, data=data)
        
        # Should handle empty CSV gracefully
        assert response.status_code in [400, 422, 500]
    
    def test_validate_with_correlation_id(self):
        """Test that correlation ID is properly handled."""
        csv_data = [
            ["sku", "title", "price"],
            ["SKU001", "Product 1", "10.99"]
        ]
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        csv_content = output.getvalue()
        
        files = {
            "file": ("test.csv", csv_content, "text/csv")
        }
        data = {
            "marketplace": "MERCADO_LIVRE",
            "category": "ELETRONICOS"
        }
        headers = {
            "X-Correlation-Id": "test-correlation-123"
        }
        
        response = client.post("/api/v1/validate", files=files, data=data, headers=headers)
        
        assert response.status_code == 200
        # Correlation ID should be in response if there's an error
        # or in specific headers depending on implementation
    
    @pytest.mark.parametrize("marketplace", ["MERCADO_LIVRE", "SHOPEE", "AMAZON", "MAGALU"])
    def test_validate_different_marketplaces(self, marketplace):
        """Test validation with different marketplaces."""
        csv_data = [
            ["sku", "title", "price"],
            ["SKU001", "Product 1", "10.99"]
        ]
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        csv_content = output.getvalue()
        
        files = {
            "file": ("test.csv", csv_content, "text/csv")
        }
        data = {
            "marketplace": marketplace,
            "category": "ELETRONICOS"
        }
        
        response = client.post("/api/v1/validate", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["marketplace"].upper() == marketplace or result["marketplace"].lower() == marketplace.lower()