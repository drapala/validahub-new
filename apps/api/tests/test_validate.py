import io
import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_validate_csv_success():
    """Test successful CSV validation"""
    # Create a valid CSV
    csv_content = """sku,title,price,available_quantity,condition
SKU001,Product 1,99.99,10,new
SKU002,Product 2,49.99,5,used
SKU003,Product 3,199.99,0,new"""
    
    csv_file = io.BytesIO(csv_content.encode())
    
    response = client.post(
        "/api/v1/validate_csv",
        params={
            "marketplace": "MERCADO_LIVRE",
            "category": "ELETRONICOS",
            "dry_run": True
        },
        files={"file": ("test.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 3
    assert data["valid_rows"] > 0
    assert "errors" in data
    assert "processing_time_ms" in data


def test_validate_csv_with_errors():
    """Test CSV validation with errors"""
    # Create a CSV with errors
    csv_content = """sku,title,price,available_quantity,condition
SKU001,This is a very long title that exceeds the maximum allowed length for Mercado Livre marketplace,-10,10,new
SKU002,Product 2,0,-5,used
,Product 3,abc,0,new"""
    
    csv_file = io.BytesIO(csv_content.encode())
    
    response = client.post(
        "/api/v1/validate_csv",
        params={
            "marketplace": "MERCADO_LIVRE",
            "category": "ELETRONICOS",
        },
        files={"file": ("test.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 3
    assert data["error_rows"] > 0
    assert len(data["errors"]) > 0
    
    # Check for specific errors
    errors = data["errors"]
    error_types = [e["error"] for e in errors]
    assert any("Title too long" in e for e in error_types)
    assert any("Price must be greater than 0" in e for e in error_types)
    assert any("Stock cannot be negative" in e for e in error_types)


def test_validate_csv_missing_columns():
    """Test CSV validation with missing required columns"""
    # CSV missing required columns
    csv_content = """sku,name,cost
SKU001,Product 1,99.99
SKU002,Product 2,49.99"""
    
    csv_file = io.BytesIO(csv_content.encode())
    
    response = client.post(
        "/api/v1/validate_csv",
        params={
            "marketplace": "MERCADO_LIVRE",
            "category": "MODA",
        },
        files={"file": ("test.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["errors"]) > 0
    
    # Check for missing column errors
    errors = data["errors"]
    error_messages = [e["error"] for e in errors]
    assert any("Missing required column" in msg for msg in error_messages)


def test_validate_invalid_file_type():
    """Test validation with invalid file type"""
    response = client.post(
        "/api/v1/validate_csv",
        params={
            "marketplace": "SHOPEE",
            "category": "CASA",
        },
        files={"file": ("test.txt", b"invalid content", "text/plain")}
    )
    
    assert response.status_code == 400
    assert "CSV file" in response.json()["detail"]


def test_validate_different_marketplaces():
    """Test validation for different marketplaces"""
    marketplaces = ["SHOPEE", "AMAZON", "MAGALU", "AMERICANAS"]
    
    for marketplace in marketplaces:
        # Create CSV with generic columns
        csv_content = """sku,name,price,stock
SKU001,Product 1,99.99,10
SKU002,Product 2,49.99,5"""
        
        csv_file = io.BytesIO(csv_content.encode())
        
        response = client.post(
            "/api/v1/validate_csv",
            params={
                "marketplace": marketplace,
                "category": "ELETRONICOS",
            },
            files={"file": ("test.csv", csv_file, "text/csv")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_rows" in data
        assert "errors" in data