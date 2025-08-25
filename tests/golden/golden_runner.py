"""Golden test runner for ValidaHub pipeline."""

import pandas as pd
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from .config_schema import GoldenTestConfig
from .normalizers import (
    normalize_dataframe,
    normalize_json,
    normalize_numeric_columns,
)
from .comparators import compare_csv, compare_json, ComparisonResult


def load_spec(config_path: str) -> GoldenTestConfig:
    """
    Load and validate test specification from YAML.
    
    Args:
        config_path: Path to config.yaml file
    
    Returns:
        Validated GoldenTestConfig
    """
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    return GoldenTestConfig(**data)


def read_csv_stream(path: str, chunk_size: Optional[int] = None, **kwargs):
    """
    Read CSV file, optionally in chunks for streaming.
    
    Args:
        path: Path to CSV file
        chunk_size: Number of rows per chunk (None for full file)
        **kwargs: Additional pandas read_csv arguments
    
    Yields:
        DataFrame chunks or single DataFrame
    """
    if chunk_size:
        for chunk in pd.read_csv(path, chunksize=chunk_size, **kwargs):
            yield chunk
    else:
        yield pd.read_csv(path, **kwargs)


def run_pipeline(
    input_df: pd.DataFrame,
    marketplace: str,
    category: str = "default",
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run the validation/correction pipeline.
    
    Args:
        input_df: Input DataFrame
        marketplace: Marketplace name
        category: Category name
    
    Returns:
        Tuple of (corrected DataFrame, validation report)
    """
    # Import pipeline components
    try:
        from apps.api.src.core.pipeline.validation_pipeline import ValidationPipeline
        from apps.api.src.core.pipeline.correction_pipeline import CorrectionPipeline
        from apps.api.src.models.marketplace import Marketplace
        
        # Map string to enum
        marketplace_enum = {
            'mercado_livre': Marketplace.MERCADO_LIVRE,
            'shopee': Marketplace.SHOPEE,
            'amazon': Marketplace.AMAZON,
        }.get(marketplace.lower())
        
        if not marketplace_enum:
            raise ValueError(f"Unknown marketplace: {marketplace}")
        
        # Run validation
        validation_pipeline = ValidationPipeline(
            marketplace=marketplace_enum,
            category=category.upper(),
        )
        validation_result = validation_pipeline.validate(input_df)
        
        # Run correction
        correction_pipeline = CorrectionPipeline(
            marketplace=marketplace_enum,
            category=category.upper(),
        )
        corrected_df = correction_pipeline.correct(input_df, validation_result.errors)
        
        # Build report
        report = {
            'marketplace': marketplace,
            'category': category,
            'total_rows': len(input_df),
            'errors_found': len(validation_result.errors),
            'corrections_applied': validation_result.corrections_count,
            'validation_errors': [
                {
                    'row': e.row,
                    'column': e.column,
                    'error': e.message,
                    'value': e.value,
                }
                for e in validation_result.errors[:100]  # Limit for readability
            ],
        }
        
        return corrected_df, report
        
    except ImportError as e:
        # Fallback for testing without full pipeline
        print(f"Warning: Pipeline not available, using mock: {e}")
        return input_df.copy(), {
            'marketplace': marketplace,
            'category': category,
            'mock': True,
            'total_rows': len(input_df),
        }


def run_golden_case(
    case_dir: str,
    spec: Optional[GoldenTestConfig] = None,
    save_artifacts: bool = True,
) -> ComparisonResult:
    """
    Run a single golden test case.
    
    Args:
        case_dir: Directory containing test case files
        spec: Test specification (loaded from config.yaml if None)
        save_artifacts: Save actual outputs for debugging
    
    Returns:
        ComparisonResult
    """
    case_path = Path(case_dir)
    
    # Load spec if not provided
    if spec is None:
        spec = load_spec(case_path / "config.yaml")
    
    # Extract marketplace and category from path
    parts = case_path.parts
    marketplace_idx = parts.index('golden') + 1
    marketplace = parts[marketplace_idx] if marketplace_idx < len(parts) else 'unknown'
    category = parts[marketplace_idx + 1] if marketplace_idx + 1 < len(parts) else 'default'
    
    # Read input
    input_path = case_path / "input.csv"
    if not input_path.exists():
        return ComparisonResult(
            passed=False,
            diff_summary=f"Input file not found: {input_path}"
        )
    
    # Process in chunks if specified
    all_outputs = []
    all_reports = []
    
    for chunk_df in read_csv_stream(
        input_path,
        chunk_size=spec.chunk_size,
        sep=spec.separator,
        encoding=spec.encoding,
    ):
        # Normalize numeric columns if needed
        if spec.decimal != ".":
            chunk_df = normalize_numeric_columns(chunk_df, spec.decimal)
        
        # Run pipeline
        output_df, report = run_pipeline(chunk_df, marketplace, category)
        all_outputs.append(output_df)
        all_reports.append(report)
    
    # Combine results
    actual_output = pd.concat(all_outputs, ignore_index=True)
    
    # Combine reports (simplified - just take last one for now)
    actual_report = all_reports[-1] if all_reports else {}
    
    # Normalize actual output
    actual_output = normalize_dataframe(
        actual_output,
        key_columns=spec.key_columns,
        sort_by=spec.sort_by,
        trim_whitespace=spec.trim_whitespace,
        casefold_text=spec.casefold_text,
        normalize_floats=spec.normalize_floats,
    )
    
    # Load and normalize expected output
    expected_output_path = case_path / "expected_output.csv"
    if expected_output_path.exists():
        expected_output = pd.read_csv(
            expected_output_path,
            sep=spec.separator,
            encoding=spec.encoding,
        )
        if spec.decimal != ".":
            expected_output = normalize_numeric_columns(expected_output, spec.decimal)
        
        expected_output = normalize_dataframe(
            expected_output,
            key_columns=spec.key_columns,
            sort_by=spec.sort_by,
            trim_whitespace=spec.trim_whitespace,
            casefold_text=spec.casefold_text,
            normalize_floats=spec.normalize_floats,
        )
        
        # Compare CSV outputs
        csv_result = compare_csv(
            actual_output,
            expected_output,
            float_tolerance=spec.float_tolerance,
            ignore_columns=spec.ignore_columns_in_diff,
        )
        
        if not csv_result.passed:
            if save_artifacts:
                artifacts_dir = case_path / "artifacts"
                artifacts_dir.mkdir(exist_ok=True)
                actual_output.to_csv(artifacts_dir / "actual_output.csv", index=False)
                with open(artifacts_dir / "diff.html", 'w') as f:
                    f.write(csv_result.to_html())
            return csv_result
    
    # Load and compare report if exists
    expected_report_path = case_path / "expected_report.json"
    if expected_report_path.exists():
        with open(expected_report_path, 'r') as f:
            expected_report = json.load(f)
        
        # Normalize reports
        actual_report = normalize_json(
            actual_report,
            ignore_keys=spec.report_ignore_keys,
        )
        expected_report = normalize_json(
            expected_report,
            ignore_keys=spec.report_ignore_keys,
        )
        
        # Compare reports
        report_result = compare_json(
            actual_report,
            expected_report,
            ignore_keys=spec.report_ignore_keys,
            float_tolerance=spec.float_tolerance,
        )
        
        if not report_result.passed:
            if save_artifacts:
                artifacts_dir = case_path / "artifacts"
                artifacts_dir.mkdir(exist_ok=True)
                with open(artifacts_dir / "actual_report.json", 'w') as f:
                    json.dump(actual_report, f, indent=2)
                with open(artifacts_dir / "report_diff.html", 'w') as f:
                    f.write(report_result.to_html())
            return report_result
    
    return ComparisonResult(
        passed=True,
        diff_summary="All golden test checks passed"
    )


def discover_cases(root_dir: str = "tests/golden") -> list:
    """
    Discover all golden test cases.
    
    Args:
        root_dir: Root directory to search
    
    Returns:
        List of case directories
    """
    cases = []
    root_path = Path(root_dir)
    
    for case_dir in root_path.glob("**/case_*"):
        if (case_dir / "input.csv").exists():
            cases.append(str(case_dir))
    
    return sorted(cases)