"""
Validator V2 - Using Plugin Architecture
Adapter to integrate new architecture with existing code
"""
import pandas as pd
import io
from typing import List, Dict, Any
from fastapi import UploadFile
import time

from src.schemas.validate import (
    ValidationError as SchemaValidationError,
    ValidationResult,
    Marketplace,
    Category,
)
from src.core.engines.rule_engine import RuleEngine
from src.core.interfaces import ValidationError as CoreValidationError


class CSVValidator:
    """
    New validator using plugin architecture
    Maintains compatibility with existing interface
    """
    
    def __init__(self):
        self.engine = RuleEngine()
    
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
        start_time = time.time()
        
        # Read CSV content
        content = await file.read()
        csv_string = content.decode('utf-8')
        
        # Parse CSV into DataFrame
        try:
            df = pd.read_csv(io.StringIO(csv_string))
        except Exception as e:
            # Return error if CSV is malformed
            return ValidationResult(
                total_rows=0,
                valid_rows=0,
                error_rows=0,
                errors=[],
                warnings_count=0,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Clear any existing rules
        self.engine.clear_rules()
        self.engine.clear_providers()
        
        # Load marketplace-specific rules
        if marketplace == Marketplace.MERCADO_LIVRE:
            from src.rules.marketplaces.mercado_livre import MercadoLivreRuleProvider
            provider = MercadoLivreRuleProvider()
            self.engine.add_provider(provider)
        elif marketplace == Marketplace.SHOPEE:
            from src.rules.marketplaces.shopee import ShopeeRuleProvider
            provider = ShopeeRuleProvider()
            self.engine.add_provider(provider)
        elif marketplace == Marketplace.AMAZON:
            from src.rules.marketplaces.amazon import AmazonRuleProvider
            provider = AmazonRuleProvider()
            self.engine.add_provider(provider)
        else:
            # For marketplaces not yet implemented, use Mercado Livre as default
            from src.rules.marketplaces.mercado_livre import MercadoLivreRuleProvider
            provider = MercadoLivreRuleProvider()
            self.engine.add_provider(provider)
        
        # Create context for validation
        context = {
            'marketplace': marketplace.value,
            'category': category.value
        }
        
        # Run validation
        core_errors = self.engine.validate(df, context)
        
        # Convert core errors to schema errors
        schema_errors = self._convert_errors(core_errors)
        
        # Calculate statistics
        total_rows = len(df)
        error_rows = len(set(e.row - 1 for e in schema_errors))  # Unique rows with errors
        valid_rows = total_rows - error_rows
        warnings_count = sum(1 for e in schema_errors if e.severity == "warning")
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return ValidationResult(
            total_rows=total_rows,
            valid_rows=valid_rows,
            error_rows=error_rows,
            errors=schema_errors,
            warnings_count=warnings_count,
            processing_time_ms=processing_time_ms
        )
    
    def _convert_errors(self, core_errors: List[CoreValidationError]) -> List[SchemaValidationError]:
        """Convert core ValidationError to schema ValidationError"""
        schema_errors = []
        
        for error in core_errors:
            schema_error = SchemaValidationError(
                row=error.row,
                column=error.column,
                error=error.error,
                value=str(error.value) if error.value is not None else None,
                suggestion=error.suggestion,
                severity=error.severity.value  # Convert enum to string
            )
            schema_errors.append(schema_error)
        
        return schema_errors


# Create singleton instance for backward compatibility
csv_validator = CSVValidator()