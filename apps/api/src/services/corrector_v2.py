"""CSV correction service using the centralized pipeline."""
import csv
import io
from typing import Dict, List, Any, Optional
import pandas as pd
from src.schemas.validate import ValidationResult, ValidationError, Marketplace, Category
from src.core.interfaces.corrector import ICorrection, ICorrectionProvider
from src.core.corrections.base import (
    TruncateCorrection,
    DefaultValueCorrection,
    MinValueCorrection,
    NumericCleanCorrection,
)
from src.core.corrections.base import AutoGenerateCorrection
from src.core.pipeline.correction_pipeline import CorrectionPipeline


class MarketplaceCorrectionProvider(ICorrectionProvider):
    """Provides corrections based on marketplace"""
    
    def __init__(self, marketplace: Marketplace):
        self.marketplace = marketplace
        self.corrections = self._load_corrections()
    
    def _load_corrections(self) -> Dict[str, List[ICorrection]]:
        """Load marketplace-specific corrections"""
        corrections = {}
        
        if self.marketplace == Marketplace.MERCADO_LIVRE:
            corrections = {
                'title': [
                    TruncateCorrection(60),
                    DefaultValueCorrection("Produto sem título")
                ],
                'price': [
                    MinValueCorrection(0.01),
                ],
                'stock': [
                    MinValueCorrection(0),
                    NumericCleanCorrection(0)
                ],
                'sku': [
                    AutoGenerateCorrection(prefix="ML", field_type="sku"),
                    DefaultValueCorrection("SKU-DEFAULT")
                ],
                'condition': [
                    DefaultValueCorrection("new")
                ]
            }
            
        elif self.marketplace == Marketplace.SHOPEE:
            corrections = {
                'title': [
                    TruncateCorrection(100),
                    DefaultValueCorrection("Product Title")
                ],
                'price': [
                    MinValueCorrection(0.01),
                ],
                'quantity': [
                    MinValueCorrection(0),
                    NumericCleanCorrection(0)
                ],
                'sku': [
                    AutoGenerateCorrection(prefix="SH", field_type="sku"),
                ],
                'weight': [
                    MinValueCorrection(1),
                    DefaultValueCorrection(100)
                ]
            }
            
        elif self.marketplace == Marketplace.AMAZON:
            corrections = {
                'title': [
                    TruncateCorrection(200),
                    DefaultValueCorrection("Product")
                ],
                'price': [
                    MinValueCorrection(0.01),
                ],
                'quantity': [
                    MinValueCorrection(0),
                    NumericCleanCorrection(0)
                ],
                'sku': [
                    AutoGenerateCorrection(prefix="AMZ", field_type="sku"),
                ],
                'brand': [
                    DefaultValueCorrection("Generic")
                ],
                'manufacturer': [
                    DefaultValueCorrection("Unknown")
                ]
            }
        
        # Add common corrections for all marketplaces
        for column in ['description', 'desc']:
            if column not in corrections:
                corrections[column] = []
            corrections[column].append(DefaultValueCorrection("N/A"))
        
        return corrections
    
    def get_corrections(self) -> List[ICorrection]:
        """Get all corrections"""
        all_corrections = []
        for column_corrections in self.corrections.values():
            all_corrections.extend(column_corrections)
        return all_corrections
    
    def get_correction_for_error(self, error: ValidationError) -> Optional[ICorrection]:
        """Get the best correction for a specific error"""
        column = error.column.lower()
        
        # Check if we have corrections for this column
        column_corrections = self.corrections.get(column, [])
        
        # Find the first correction that can handle this error
        for correction in sorted(column_corrections, key=lambda c: c.get_priority()):
            if correction.can_correct(error):
                return correction
        
        # Try generic corrections
        if "required" in error.error.lower() and "empty" in error.error.lower():
            return DefaultValueCorrection("N/A")
        
        return None


class CSVCorrectorV2:
    """New CSV Corrector using plugin architecture and pipeline."""

    def __init__(self):
        # Initialize pipeline with this corrector instance
        self.pipeline = CorrectionPipeline(corrector=self)

    def correct_csv(
        self,
        csv_content: str,
        marketplace: Marketplace,
        category: Category,
    ) -> Tuple[str, Dict[str, Any], ValidationResult]:
        """Run full correction pipeline: validate and apply corrections."""
        return self.pipeline.run(csv_content, marketplace, category)
    
    def apply_corrections(
        self, 
        csv_content: str, 
        validation_result: ValidationResult,
        marketplace: Marketplace,
        category: Category
    ) -> tuple[str, Dict[str, Any]]:
        """
        Apply automatic corrections to CSV based on validation errors
        
        Returns:
            tuple: (corrected_csv_content, correction_summary)
        """
        # Parse CSV into dataframe
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Create correction provider
        provider = MarketplaceCorrectionProvider(marketplace)
        
        corrections_applied = []
        rows_corrected = set()
        
        # Apply corrections for each error
        for error in validation_result.errors:
            # error.row is 1-based counting from first data row (after header)
            row_idx = error.row - 1  # Convert to 0-based index
            
            if row_idx >= 0 and row_idx < len(df):
                correction = self._apply_single_correction(
                    df, row_idx, error, provider, category
                )
                if correction:
                    corrections_applied.append(correction)
                    rows_corrected.add(row_idx)
        
        # Convert back to CSV
        output = io.StringIO()
        df.to_csv(output, index=False)
        corrected_csv = output.getvalue()
        
        # Create summary
        summary = {
            "total_corrections": len(corrections_applied),
            "rows_corrected": len(rows_corrected),
            "corrections": corrections_applied[:100],  # Limit to first 100
            "success_rate": (
                len(corrections_applied) / len(validation_result.errors) * 100
                if validation_result.errors else 0
            )
        }
        
        return corrected_csv, summary
    
    def _apply_single_correction(
        self, 
        df: pd.DataFrame, 
        row_idx: int, 
        error: ValidationError,
        provider: ICorrectionProvider,
        category: Category
    ) -> Optional[Dict[str, Any]]:
        """Apply a single correction to the dataframe"""
        
        try:
            # Check if column exists in dataframe
            if error.column not in df.columns:
                return None
            
            old_value = df.at[row_idx, error.column]
            
            # Get correction from provider
            correction = provider.get_correction_for_error(error)
            
            if correction:
                # Create context for correction
                context = {
                    'row': row_idx + 1,
                    'column': error.column,
                    'category': category.value
                }
                
                # Apply correction
                new_value = correction.apply(old_value, error, context)
                
                if new_value != old_value:
                    df.at[row_idx, error.column] = new_value
                    return {
                        "row": error.row,
                        "column": error.column,
                        "old_value": str(old_value) if old_value is not None else None,
                        "new_value": str(new_value),
                        "reason": error.error
                    }
            
        except Exception as e:
            print(f"Error applying correction: {e}")
        
        return None
    
    def generate_correction_report(
        self,
        original_csv: str,
        corrected_csv: str,
        summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a detailed correction report"""
        
        # Parse both CSVs
        original_df = pd.read_csv(io.StringIO(original_csv))
        corrected_df = pd.read_csv(io.StringIO(corrected_csv))
        
        # Calculate statistics
        report = {
            "summary": summary,
            "statistics": {
                "total_rows": len(original_df),
                "rows_modified": summary["rows_corrected"],
                "success_rate": summary["success_rate"],
                "corrections_by_column": {}
            },
            "sample_corrections": summary["corrections"][:10]
        }
        
        # Count corrections by column
        for correction in summary["corrections"]:
            col = correction["column"]
            if col not in report["statistics"]["corrections_by_column"]:
                report["statistics"]["corrections_by_column"][col] = 0
            report["statistics"]["corrections_by_column"][col] += 1
        
        return report