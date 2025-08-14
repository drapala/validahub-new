"""Comparison utilities for golden tests."""

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple, Dict, Any
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ComparisonResult:
    """Result of a comparison operation."""
    passed: bool
    diff_summary: str
    diff_details: Optional[Dict[str, Any]] = None
    
    def to_html(self) -> str:
        """Generate HTML diff report."""
        html = f"""
        <html>
        <head>
            <title>Golden Test Diff</title>
            <style>
                body {{ font-family: monospace; margin: 20px; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .diff {{ background: #ffffcc; padding: 10px; }}
                table {{ border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background: #f2f2f2; }}
                .mismatch {{ background: #ffcccc; }}
                .missing {{ background: #ccccff; }}
                .extra {{ background: #ccffcc; }}
            </style>
        </head>
        <body>
            <h1 class="{'passed' if self.passed else 'failed'}">
                {'✓ PASSED' if self.passed else '✗ FAILED'}
            </h1>
            <div class="diff">
                <h2>Summary</h2>
                <pre>{self.diff_summary}</pre>
            </div>
        """
        
        if self.diff_details and 'cell_differences' in self.diff_details:
            html += """
            <h2>Cell Differences</h2>
            <table>
                <tr>
                    <th>Row</th>
                    <th>Column</th>
                    <th>Expected</th>
                    <th>Actual</th>
                </tr>
            """
            for diff in self.diff_details['cell_differences'][:100]:  # Limit to 100
                html += f"""
                <tr class="mismatch">
                    <td>{diff['row']}</td>
                    <td>{diff['column']}</td>
                    <td>{diff['expected']}</td>
                    <td>{diff['actual']}</td>
                </tr>
                """
            html += "</table>"
            
            if len(self.diff_details['cell_differences']) > 100:
                html += f"<p>... and {len(self.diff_details['cell_differences']) - 100} more differences</p>"
        
        html += "</body></html>"
        return html


def compare_csv(
    actual_df: pd.DataFrame,
    expected_df: pd.DataFrame,
    float_tolerance: float = 1e-6,
    ignore_columns: Optional[List[str]] = None,
) -> ComparisonResult:
    """
    Compare two DataFrames with tolerance for floats.
    
    Args:
        actual_df: Actual output DataFrame
        expected_df: Expected output DataFrame
        float_tolerance: Tolerance for float comparison
        ignore_columns: Columns to ignore in comparison
    
    Returns:
        ComparisonResult with detailed differences
    """
    ignore_columns = ignore_columns or []
    
    # Remove ignored columns
    if ignore_columns:
        actual_df = actual_df.drop(columns=ignore_columns, errors='ignore')
        expected_df = expected_df.drop(columns=ignore_columns, errors='ignore')
    
    # Check shape
    if actual_df.shape != expected_df.shape:
        return ComparisonResult(
            passed=False,
            diff_summary=f"Shape mismatch: actual {actual_df.shape} vs expected {expected_df.shape}",
            diff_details={
                'actual_shape': actual_df.shape,
                'expected_shape': expected_df.shape,
                'actual_columns': list(actual_df.columns),
                'expected_columns': list(expected_df.columns),
            }
        )
    
    # Check columns
    if not actual_df.columns.equals(expected_df.columns):
        missing = set(expected_df.columns) - set(actual_df.columns)
        extra = set(actual_df.columns) - set(expected_df.columns)
        return ComparisonResult(
            passed=False,
            diff_summary=f"Column mismatch. Missing: {missing}, Extra: {extra}",
            diff_details={
                'missing_columns': list(missing),
                'extra_columns': list(extra),
            }
        )
    
    # Compare values
    differences = []
    for col in actual_df.columns:
        for idx in actual_df.index:
            actual_val = actual_df.loc[idx, col]
            expected_val = expected_df.loc[idx, col]
            
            # Handle NaN comparison
            if pd.isna(actual_val) and pd.isna(expected_val):
                continue
            elif pd.isna(actual_val) or pd.isna(expected_val):
                differences.append({
                    'row': idx,
                    'column': col,
                    'expected': expected_val,
                    'actual': actual_val,
                })
                continue
            
            # Float comparison with tolerance
            if isinstance(actual_val, (float, np.floating)) and isinstance(expected_val, (float, np.floating)):
                if not np.isclose(actual_val, expected_val, atol=float_tolerance):
                    differences.append({
                        'row': idx,
                        'column': col,
                        'expected': expected_val,
                        'actual': actual_val,
                        'diff': abs(actual_val - expected_val),
                    })
            # Exact comparison for other types
            elif actual_val != expected_val:
                differences.append({
                    'row': idx,
                    'column': col,
                    'expected': expected_val,
                    'actual': actual_val,
                })
    
    if differences:
        summary = f"Found {len(differences)} cell differences"
        if len(differences) <= 5:
            for d in differences:
                summary += f"\n  [{d['row']}, {d['column']}]: {d['expected']} != {d['actual']}"
        else:
            summary += f"\n  First 5 differences:"
            for d in differences[:5]:
                summary += f"\n  [{d['row']}, {d['column']}]: {d['expected']} != {d['actual']}"
            summary += f"\n  ... and {len(differences) - 5} more"
        
        return ComparisonResult(
            passed=False,
            diff_summary=summary,
            diff_details={'cell_differences': differences}
        )
    
    return ComparisonResult(
        passed=True,
        diff_summary="All values match within tolerance"
    )


def compare_json(
    actual: dict,
    expected: dict,
    ignore_keys: Optional[List[str]] = None,
    float_tolerance: float = 1e-6,
    path: str = "",
) -> ComparisonResult:
    """
    Compare two JSON objects with tolerance for floats.
    
    Args:
        actual: Actual JSON data
        expected: Expected JSON data
        ignore_keys: Keys to ignore in comparison
        float_tolerance: Tolerance for float comparison
        path: Current path in nested structure (for error reporting)
    
    Returns:
        ComparisonResult with differences
    """
    ignore_keys = ignore_keys or []
    differences = []
    
    def _compare(actual_val, expected_val, current_path):
        if isinstance(actual_val, dict) and isinstance(expected_val, dict):
            # Compare dictionaries
            actual_keys = set(actual_val.keys()) - set(ignore_keys)
            expected_keys = set(expected_val.keys()) - set(ignore_keys)
            
            missing = expected_keys - actual_keys
            extra = actual_keys - expected_keys
            
            if missing:
                differences.append({
                    'path': current_path,
                    'type': 'missing_keys',
                    'keys': list(missing),
                })
            if extra:
                differences.append({
                    'path': current_path,
                    'type': 'extra_keys',
                    'keys': list(extra),
                })
            
            for key in actual_keys & expected_keys:
                _compare(actual_val[key], expected_val[key], f"{current_path}.{key}")
                
        elif isinstance(actual_val, list) and isinstance(expected_val, list):
            # Compare lists
            if len(actual_val) != len(expected_val):
                differences.append({
                    'path': current_path,
                    'type': 'list_length',
                    'expected': len(expected_val),
                    'actual': len(actual_val),
                })
            else:
                for i, (a, e) in enumerate(zip(actual_val, expected_val)):
                    _compare(a, e, f"{current_path}[{i}]")
                    
        elif isinstance(actual_val, float) and isinstance(expected_val, float):
            # Float comparison with tolerance
            if not np.isclose(actual_val, expected_val, atol=float_tolerance):
                differences.append({
                    'path': current_path,
                    'type': 'value',
                    'expected': expected_val,
                    'actual': actual_val,
                })
        else:
            # Exact comparison
            if actual_val != expected_val:
                differences.append({
                    'path': current_path,
                    'type': 'value',
                    'expected': expected_val,
                    'actual': actual_val,
                })
    
    _compare(actual, expected, path or "root")
    
    if differences:
        summary = f"Found {len(differences)} differences in JSON"
        for d in differences[:5]:
            if d['type'] == 'value':
                summary += f"\n  {d['path']}: {d['expected']} != {d['actual']}"
            elif d['type'] == 'missing_keys':
                summary += f"\n  {d['path']}: missing keys {d['keys']}"
            elif d['type'] == 'extra_keys':
                summary += f"\n  {d['path']}: extra keys {d['keys']}"
            elif d['type'] == 'list_length':
                summary += f"\n  {d['path']}: length {d['expected']} != {d['actual']}"
        
        if len(differences) > 5:
            summary += f"\n  ... and {len(differences) - 5} more"
        
        return ComparisonResult(
            passed=False,
            diff_summary=summary,
            diff_details={'json_differences': differences}
        )
    
    return ComparisonResult(
        passed=True,
        diff_summary="JSON objects match"
    )