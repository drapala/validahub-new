import pandas as pd

from src.core.pipeline.validation_pipeline import ValidationPipeline
from src.schemas.validate import Marketplace, Category
from src.services.corrector_v2 import CSVCorrectorV2


def test_validation_pipeline_detects_errors():
    df = pd.DataFrame({
        'sku': ['SKU1', 'SKU2'],
        'title': ['Valid title', 'Invalid title that is way too long for marketplace'],
        'price': [10.0, -5.0],
        'available_quantity': [5, 5],
        'condition': ['new', 'new']
    })
    pipeline = ValidationPipeline()
    result = pipeline.validate(df, Marketplace.MERCADO_LIVRE, Category.ELETRONICOS)
    assert result.error_rows > 0
    assert any(e.column == 'price' for e in result.errors)


def test_correction_pipeline_applies_corrections():
    csv_content = (
        "sku,title,price,stock,condition\n"
        ",This is a very long title that exceeds the maximum allowed length for Mercado Livre marketplace,-10,-5,\n"
    )
    corrector = CSVCorrectorV2()
    corrected_csv, summary, result = corrector.correct_csv(
        csv_content=csv_content,
        marketplace=Marketplace.MERCADO_LIVRE,
        category=Category.ELETRONICOS,
    )
    assert summary["total_corrections"] > 0
    assert result.error_rows > 0
    assert corrected_csv != csv_content
