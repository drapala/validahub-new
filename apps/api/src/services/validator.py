import pandas as pd
import io
from typing import Dict, List, Any
from fastapi import UploadFile
import time

from src.schemas.validate import (
    ValidationError,
    ValidationResult,
    Marketplace,
    Category,
)


class CSVValidator:
    """Service for validating CSV files based on marketplace and category rules"""
    
    # Define required columns per marketplace
    MARKETPLACE_RULES: Dict[Marketplace, Dict[str, Any]] = {
        Marketplace.MERCADO_LIVRE: {
            "required_columns": ["sku", "title", "price", "available_quantity", "condition"],
            "max_title_length": 60,
            "max_description_length": 5000,
        },
        Marketplace.SHOPEE: {
            "required_columns": ["sku", "name", "price", "stock", "category_id"],
            "max_title_length": 100,
            "max_description_length": 3000,
        },
        Marketplace.AMAZON: {
            "required_columns": ["sku", "product_name", "standard_price", "quantity", "product_id_type"],
            "max_title_length": 200,
            "max_description_length": 2000,
        },
        Marketplace.MAGALU: {
            "required_columns": ["sku", "titulo", "preco", "estoque", "categoria"],
            "max_title_length": 150,
            "max_description_length": 4000,
        },
        Marketplace.AMERICANAS: {
            "required_columns": ["sku", "nome", "preco_de", "preco_por", "estoque"],
            "max_title_length": 100,
            "max_description_length": 3000,
        },
    }
    
    # Category-specific validation rules
    CATEGORY_RULES: Dict[Category, Dict[str, Any]] = {
        Category.ELETRONICOS: {
            "required_fields": ["brand", "model", "warranty"],
            "validate_ean": True,
        },
        Category.MODA: {
            "required_fields": ["size", "color", "material"],
            "validate_ean": False,
        },
        Category.CASA: {
            "required_fields": ["dimensions", "material", "color"],
            "validate_ean": True,
        },
        Category.ESPORTE: {
            "required_fields": ["size", "brand", "sport_type"],
            "validate_ean": True,
        },
        Category.BELEZA: {
            "required_fields": ["brand", "volume", "ingredients"],
            "validate_ean": True,
        },
        Category.LIVROS: {
            "required_fields": ["isbn", "author", "publisher", "pages"],
            "validate_ean": False,
        },
        Category.BRINQUEDOS: {
            "required_fields": ["age_range", "brand", "safety_warning"],
            "validate_ean": True,
        },
        Category.ALIMENTOS: {
            "required_fields": ["expiry_date", "ingredients", "nutritional_info"],
            "validate_ean": True,
        },
    }
    
    async def validate_csv(
        self,
        file: UploadFile,
        marketplace: Marketplace,
        category: Category,
    ) -> ValidationResult:
        """
        Validate CSV file based on marketplace and category rules
        """
        start_time = time.time()
        errors: List[ValidationError] = []
        
        # Read CSV file
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        total_rows = len(df)
        
        # Get rules for marketplace and category
        marketplace_rules = self.MARKETPLACE_RULES.get(marketplace, {})
        category_rules = self.CATEGORY_RULES.get(category, {})
        
        # Check required columns for marketplace
        required_cols = marketplace_rules.get("required_columns", [])
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            for col in missing_cols:
                errors.append(
                    ValidationError(
                        row=0,
                        column=col,
                        error=f"Missing required column: {col}",
                        value=None,
                        suggestion=f"Add column '{col}' to your CSV",
                        severity="error",
                    )
                )
        
        # Validate each row
        for idx, row in df.iterrows():
            row_errors = self._validate_row(
                row,
                idx + 1,  # Row number (1-indexed)
                marketplace_rules,
                category_rules,
            )
            errors.extend(row_errors)
        
        # Calculate metrics
        error_rows = len(set(e.row for e in errors if e.severity == "error"))
        warning_count = len([e for e in errors if e.severity == "warning"])
        valid_rows = total_rows - error_rows
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return ValidationResult(
            total_rows=total_rows,
            valid_rows=valid_rows,
            error_rows=error_rows,
            errors=errors[:100],  # Limit to first 100 errors
            warnings_count=warning_count,
            processing_time_ms=processing_time,
        )
    
    def _validate_row(
        self,
        row: pd.Series,
        row_num: int,
        marketplace_rules: Dict[str, Any],
        category_rules: Dict[str, Any],
    ) -> List[ValidationError]:
        """Validate a single row"""
        errors = []
        
        # Validate title length
        title_fields = ["title", "name", "product_name", "titulo", "nome"]
        max_title_length = marketplace_rules.get("max_title_length", 200)
        
        for field in title_fields:
            if field in row and pd.notna(row[field]):
                if len(str(row[field])) > max_title_length:
                    errors.append(
                        ValidationError(
                            row=row_num,
                            column=field,
                            error=f"Title too long (max {max_title_length} chars)",
                            value=str(row[field])[:50] + "...",
                            suggestion=f"Shorten to {max_title_length} characters",
                            severity="error",
                        )
                    )
        
        # Validate price
        price_fields = ["price", "standard_price", "preco", "preco_de", "preco_por"]
        for field in price_fields:
            if field in row and pd.notna(row[field]):
                try:
                    price = float(row[field])
                    if price <= 0:
                        errors.append(
                            ValidationError(
                                row=row_num,
                                column=field,
                                error="Price must be greater than 0",
                                value=str(row[field]),
                                suggestion="Set a positive price value",
                                severity="error",
                            )
                        )
                    elif price > 999999:
                        errors.append(
                            ValidationError(
                                row=row_num,
                                column=field,
                                error="Price seems too high",
                                value=str(row[field]),
                                suggestion="Verify the price value",
                                severity="warning",
                            )
                        )
                except (ValueError, TypeError):
                    errors.append(
                        ValidationError(
                            row=row_num,
                            column=field,
                            error="Invalid price format",
                            value=str(row[field]),
                            suggestion="Use numeric value for price",
                            severity="error",
                        )
                    )
        
        # Validate stock/quantity
        stock_fields = ["available_quantity", "stock", "quantity", "estoque"]
        for field in stock_fields:
            if field in row and pd.notna(row[field]):
                try:
                    stock = int(row[field])
                    if stock < 0:
                        errors.append(
                            ValidationError(
                                row=row_num,
                                column=field,
                                error="Stock cannot be negative",
                                value=str(row[field]),
                                suggestion="Set stock to 0 or positive value",
                                severity="error",
                            )
                        )
                except (ValueError, TypeError):
                    errors.append(
                        ValidationError(
                            row=row_num,
                            column=field,
                            error="Invalid stock format",
                            value=str(row[field]),
                            suggestion="Use integer value for stock",
                            severity="error",
                        )
                    )
        
        # Check for empty required fields
        for field in marketplace_rules.get("required_columns", []):
            if field in row and (pd.isna(row[field]) or str(row[field]).strip() == ""):
                errors.append(
                    ValidationError(
                        row=row_num,
                        column=field,
                        error="Required field is empty",
                        value=None,
                        suggestion=f"Provide value for {field}",
                        severity="error",
                    )
                )
        
        return errors


# Singleton instance
csv_validator = CSVValidator()