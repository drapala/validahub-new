import pandas as pd
import pytest

from src.core.pipeline.validation_pipeline import ValidationPipeline
from src.schemas.validate import Marketplace, Category
# CSVCorrectorV2 has been replaced by the rule engine system
# from src.services.corrector_v2 import CSVCorrectorV2


def test_validation_pipeline_detects_errors():
    df = pd.DataFrame({
        'sku': ['SKU1', 'SKU2'],
        'title': ['Valid title', 'Invalid title that is way too long for marketplace'],
        'price': [10.0, -5.0],
        'available_quantity': [5, 5],
        'condition': ['new', 'new']
    })
    pipeline = ValidationPipeline(auto_fix=False)  # Disable auto-fix to detect errors
    result = pipeline.validate(df, Marketplace.MERCADO_LIVRE, Category.ELETRONICOS, auto_fix=False)
    
    # Check if we have validation items with errors
    error_items = [item for item in result.validation_items if item.status == 'ERROR']
    assert len(error_items) > 0, f"Expected errors but got: {result.validation_items}"
    
    # Check for price error specifically
    price_errors = []
    for item in result.validation_items:
        if hasattr(item, 'errors'):
            for error in item.errors:
                if hasattr(error, 'field') and error.field == 'price':
                    price_errors.append(error)
    
    assert result.error_rows > 0 or len(price_errors) > 0, "Expected price validation errors"


@pytest.mark.skip(reason="CSVCorrectorV2 has been replaced by the rule engine system")
def test_correction_pipeline_applies_corrections():
    csv_content = (
        "sku,title,price,stock,condition\n"
        ",This is a very long title that exceeds the maximum allowed length for Mercado Livre marketplace,-10,-5,\n"
    )
    # corrector = CSVCorrectorV2()
    # corrected_csv, summary, result = corrector.correct_csv(
    #     csv_content=csv_content,
    #     marketplace=Marketplace.MERCADO_LIVRE,
    #     category=Category.ELETRONICOS,
    # )
    # assert summary["total_corrections"] > 0
    # assert result.error_rows > 0
    # assert corrected_csv != csv_content
    pass
