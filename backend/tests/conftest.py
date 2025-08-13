import io
import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture
def small_csv_bytes():
    data = "sku,title,brand,model_number,ean\nSKU-1,Title,Samsung,SM-G991B,7891234567895\n"
    return io.BytesIO(data.encode("utf-8"))