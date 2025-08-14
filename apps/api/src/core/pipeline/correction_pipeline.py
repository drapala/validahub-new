import io
from typing import Any, Dict, Tuple
import pandas as pd

from src.schemas.validate import Marketplace, Category, ValidationResult
from .validation_pipeline import ValidationPipeline


class CorrectionPipeline:
    """Pipeline that runs validation and then applies CSV corrections."""

    def __init__(self, corrector: Any, validator: ValidationPipeline | None = None):
        self.corrector = corrector
        self.validator = validator or ValidationPipeline()

    def run(
        self,
        csv_content: str,
        marketplace: Marketplace,
        category: Category,
    ) -> Tuple[str, Dict[str, Any], ValidationResult]:
        """Validate CSV content and apply automatic corrections."""
        try:
            df = pd.read_csv(io.StringIO(csv_content))
        except (pd.errors.ParserError, ValueError) as e:
            # Handle malformed CSV content similarly to the validator service
            from src.schemas.validate import ValidationError as SchemaValidationError
            validation_result = ValidationResult(
                total_rows=0,
                valid_rows=0,
                error_rows=0,
                errors=[SchemaValidationError(
                    row=0,
                    column="CSV",
                    error=f"Malformed CSV: {str(e)}",
                    value=None,
                    suggestion="Please check CSV format",
                    severity="error"
                )],
                warnings_count=0,
                processing_time_ms=0
            )
            return csv_content, {}, validation_result
        validation_result = self.validator.validate(df, marketplace, category)
        corrected_csv, summary = self.corrector.apply_corrections(
            csv_content=csv_content,
            validation_result=validation_result,
            marketplace=marketplace,
            category=category,
        )
        return corrected_csv, summary, validation_result
