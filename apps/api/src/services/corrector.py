"""
CSV Correction Service
Applies automatic fixes based on validation suggestions
"""
import csv
import io
from typing import Dict, List, Any, Optional
import pandas as pd
from src.schemas.validate import ValidationResult, ValidationError, Marketplace, Category
from src.services.validator import CSVValidator


class CSVCorrector:
    """Service to apply automatic corrections to CSV files"""
    
    def __init__(self):
        self.validator = CSVValidator()
    
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
        
        corrections_applied = []
        rows_corrected = set()
        
        # Get marketplace rules
        rules = CSVValidator.MARKETPLACE_RULES.get(marketplace, {})
        
        # Apply corrections for each error
        for error in validation_result.errors:
            # Apply all corrections, not just those with suggestions
            # error.row is 1-based counting from first data row (after header)
            # So error.row=2 means the 2nd data row, which is index 1 in dataframe
            row_idx = error.row - 1  # Convert to 0-based index
            if row_idx >= 0 and row_idx < len(df):
                correction = self._apply_correction(
                    df, row_idx, error, rules
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
    
    def _apply_correction(
        self, 
        df: pd.DataFrame, 
        row_idx: int, 
        error: ValidationError,
        rules: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Apply a single correction to the dataframe"""
        
        try:
            # Check if column exists in dataframe
            if error.column not in df.columns:
                print(f"Warning: Column {error.column} not found in dataframe")
                return None
                
            old_value = df.at[row_idx, error.column]
            new_value = None
            
            # Apply correction based on error type
            if "too long" in error.error.lower():
                max_length = rules.get("max_title_length", 60)
                new_value = str(old_value)[:max_length] if pd.notna(old_value) else ""
                
            elif "must be greater than 0" in error.error.lower():
                # Set minimum valid price
                new_value = 0.01
                
            elif "cannot be negative" in error.error.lower():
                # Set to 0 for negative stock
                new_value = 0
                
            elif "required field is empty" in error.error.lower():
                # Generate placeholder for required fields
                if error.column == "sku":
                    new_value = f"SKU-AUTO-{row_idx+1:04d}"
                elif error.column == "condition":
                    new_value = "new"
                else:
                    new_value = "N/A"
            
            elif "invalid" in error.error.lower() and "format" in error.error.lower():
                # Fix format issues
                if "stock" in error.column.lower() or "quantity" in error.column.lower():
                    # Try to extract number from string
                    try:
                        # If it's already a string representation of a number
                        if pd.isna(old_value):
                            new_value = 0
                        else:
                            # Try to convert to int, if it fails, extract digits
                            try:
                                new_value = int(float(str(old_value)))
                            except:
                                digits = ''.join(filter(str.isdigit, str(old_value)))
                                new_value = int(digits) if digits else 0
                    except:
                        new_value = 0
            
            if new_value is not None:
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