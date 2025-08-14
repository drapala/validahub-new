"""CSV validation service using the centralized pipeline."""
import io
from typing import List, Dict, Any
from fastapi import UploadFile
import pandas as pd

from src.schemas.validate import ValidationResult, Marketplace, Category
from src.core.pipeline.validation_pipeline import ValidationPipeline


class CSVValidator:
    """
    New validator using plugin architecture
    Maintains compatibility with existing interface
    """
    
    def __init__(self):
        self.pipeline = ValidationPipeline()
    
    async def validate_csv(
        self,
        file: UploadFile,
        marketplace: Marketplace,
        category: Category,
    ) -> ValidationResult:
        """
        Validate CSV file using plugin architecture
        
        Args:
            file: The uploaded CSV file
            marketplace: Target marketplace
            category: Product category
            
        Returns:
            ValidationResult with all errors found
        """
        # Read CSV content
        content = await file.read()
        csv_string = content.decode("utf-8")

        # Parse CSV into DataFrame
        try:
            df = pd.read_csv(io.StringIO(csv_string))
        except Exception:
            return ValidationResult(
                total_rows=0,
                valid_rows=0,
                error_rows=0,
                errors=[],
                warnings_count=0,
                processing_time_ms=0,
            )

        # Delegate validation to the pipeline
        return self.pipeline.validate(df, marketplace, category)


# Create singleton instance for backward compatibility
csv_validator = CSVValidator()