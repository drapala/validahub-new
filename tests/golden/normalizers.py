"""Data normalization utilities for golden tests."""

import pandas as pd
import numpy as np
from typing import List, Optional
import locale
import re


def normalize_dataframe(
    df: pd.DataFrame,
    key_columns: Optional[List[str]] = None,
    sort_by: Optional[List[str]] = None,
    trim_whitespace: bool = True,
    casefold_text: bool = False,
    normalize_floats: bool = True,
    float_precision: int = 6,
) -> pd.DataFrame:
    """
    Normalize a DataFrame for deterministic comparison.
    
    Args:
        df: Input DataFrame
        key_columns: Columns to use as keys (for deduplication)
        sort_by: Columns to sort by
        trim_whitespace: Strip leading/trailing whitespace
        casefold_text: Convert text to lowercase
        normalize_floats: Round floats to specified precision
        float_precision: Number of decimal places for float rounding
    
    Returns:
        Normalized DataFrame
    """
    df = df.copy()
    
    # Normalize text columns
    for col in df.select_dtypes(include=['object']).columns:
        if trim_whitespace:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        if casefold_text:
            df[col] = df[col].apply(lambda x: x.lower() if isinstance(x, str) else x)
    
    # Normalize floats
    if normalize_floats:
        for col in df.select_dtypes(include=[np.float32, np.float64]).columns:
            df[col] = df[col].round(float_precision)
    
    # Remove duplicates if key columns specified
    if key_columns:
        df = df.drop_duplicates(subset=key_columns, keep='first')
    
    # Sort for deterministic order
    if sort_by:
        df = df.sort_values(by=sort_by).reset_index(drop=True)
    elif key_columns:
        df = df.sort_values(by=key_columns).reset_index(drop=True)
    else:
        # Sort by all columns for full determinism
        df = df.sort_values(by=list(df.columns)).reset_index(drop=True)
    
    return df


def normalize_json(
    data: dict,
    ignore_keys: Optional[List[str]] = None,
    sort_lists: bool = True,
    normalize_floats: bool = True,
    float_precision: int = 6,
) -> dict:
    """
    Normalize JSON data for comparison.
    
    Args:
        data: Input dictionary/JSON
        ignore_keys: Keys to remove before comparison
        sort_lists: Sort lists for deterministic comparison
        normalize_floats: Round floats to specified precision
        float_precision: Number of decimal places
    
    Returns:
        Normalized dictionary
    """
    ignore_keys = ignore_keys or []
    
    def _normalize_value(value):
        if isinstance(value, float):
            if normalize_floats:
                return round(value, float_precision)
            return value
        elif isinstance(value, list):
            normalized = [_normalize_value(v) for v in value]
            if sort_lists and all(isinstance(v, (str, int, float)) for v in normalized):
                return sorted(normalized)
            return normalized
        elif isinstance(value, dict):
            return _normalize_dict(value)
        else:
            return value
    
    def _normalize_dict(d):
        result = {}
        for k, v in sorted(d.items()):  # Sort keys
            if k not in ignore_keys:
                result[k] = _normalize_value(v)
        return result
    
    return _normalize_dict(data)


def parse_locale_number(value: str, decimal_sep: str = ".") -> float:
    """
    Parse a number string with specific decimal separator.
    
    Args:
        value: String representation of number
        decimal_sep: Decimal separator character
    
    Returns:
        Float value
    """
    if not isinstance(value, str):
        return float(value)
    
    # Remove thousand separators (opposite of decimal)
    thousand_sep = "," if decimal_sep == "." else "."
    value = value.replace(thousand_sep, "")
    
    # Replace decimal separator with standard dot
    if decimal_sep != ".":
        value = value.replace(decimal_sep, ".")
    
    return float(value)


def normalize_numeric_columns(
    df: pd.DataFrame,
    decimal_sep: str = ".",
    numeric_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Convert string numeric columns to proper numeric type.
    
    Args:
        df: Input DataFrame
        decimal_sep: Decimal separator used in the CSV
        numeric_columns: Specific columns to convert (auto-detect if None)
    
    Returns:
        DataFrame with normalized numeric columns
    """
    df = df.copy()
    
    if numeric_columns is None:
        # Auto-detect numeric columns by trying to parse first non-null value
        numeric_columns = []
        for col in df.columns:
            first_val = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
            if first_val is not None and isinstance(first_val, str):
                try:
                    parse_locale_number(first_val, decimal_sep)
                    numeric_columns.append(col)
                except (ValueError, AttributeError):
                    pass
    
    for col in numeric_columns:
        df[col] = df[col].apply(lambda x: parse_locale_number(x, decimal_sep) if pd.notna(x) else np.nan)
    
    return df