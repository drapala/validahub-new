# Golden Tests Documentation

## Overview

Golden tests are regression tests that compare actual pipeline outputs against known-good "golden" outputs. They ensure that changes to the validation and correction pipelines don't introduce unexpected behavior changes.

## Purpose

1. **Non-regression guarantee**: Ensure refactoring doesn't break existing functionality
2. **Documentation by example**: Each test case documents expected behavior
3. **Fast feedback**: Quickly identify what changed when tests fail
4. **Marketplace-specific validation**: Test each marketplace's unique rules

## Architecture

```
tests/golden/
├── config_schema.py       # Pydantic schema for test configuration
├── normalizers.py         # Data normalization utilities
├── comparators.py         # CSV and JSON comparison logic
├── golden_runner.py       # Main test runner
├── conftest.py           # Pytest fixtures and configuration
├── test_golden.py        # Test definitions
│
├── mercado_livre/
│   └── eletronicos/
│       └── case_001/
│           ├── config.yaml           # Test configuration
│           ├── input.csv            # Input data
│           ├── expected_output.csv  # Expected corrected output
│           └── expected_report.json # Expected validation report
│
├── shopee/
│   └── moda/
│       └── case_001/
│           └── ...
│
└── amazon/
    └── default/
        └── case_001/
            └── ...
```

## Running Tests

### Run all golden tests
```bash
make test-golden
```

### Run tests for specific marketplace
```bash
make test-golden-ml      # Mercado Livre only
make test-golden-shopee  # Shopee only
make test-golden-amazon  # Amazon only
```

### Run with pytest directly
```bash
# All golden tests
pytest -m golden

# Specific marketplace
pytest -m "golden and mercado_livre"

# Specific test case
pytest tests/golden/test_golden.py::test_golden_auto_discovery[case_001]
```

## Creating New Test Cases

### 1. Create directory structure
```bash
mkdir -p tests/golden/{marketplace}/{category}/case_xxx
```

### 2. Add configuration file
Create `config.yaml`:
```yaml
separator: ","
decimal: "."
encoding: "utf-8"

key_columns: ["sku"]  # Columns that identify unique rows
sort_by: ["sku"]      # Sort output for deterministic comparison

float_tolerance: 0.000001
trim_whitespace: true
casefold_text: false
normalize_floats: true

ignore_columns_in_diff: []  # Columns to ignore in comparison
report_ignore_keys: ["run_id", "timestamp", "duration_ms"]

chunk_size: null  # null = process entire file, or specify number for streaming
```

### 3. Add input data
Create `input.csv` with test data that triggers specific validation rules:
```csv
sku,title,price,description
PROD001,Very long title that exceeds the marketplace limit...,-99.99,Description
```

### 4. Generate expected outputs
Run the pipeline manually first time to generate expected outputs:
```python
from tests.golden.golden_runner import run_pipeline
import pandas as pd

# Load input
df = pd.read_csv("tests/golden/mercado_livre/eletronicos/case_001/input.csv")

# Run pipeline
output_df, report = run_pipeline(df, "mercado_livre", "eletronicos")

# Save expected outputs
output_df.to_csv("expected_output.csv", index=False)
import json
with open("expected_report.json", "w") as f:
    json.dump(report, f, indent=2)
```

### 5. Verify test passes
```bash
pytest tests/golden/mercado_livre/eletronicos/case_001
```

## Configuration Options

### Normalization Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `trim_whitespace` | bool | true | Remove leading/trailing spaces |
| `casefold_text` | bool | false | Convert text to lowercase for comparison |
| `normalize_floats` | bool | true | Round floats to specified precision |
| `float_tolerance` | float | 1e-6 | Maximum difference for float equality |

### Comparison Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `key_columns` | list | [] | Columns that identify unique rows |
| `sort_by` | list | [] | Columns to sort by before comparison |
| `ignore_columns_in_diff` | list | [] | Columns to exclude from comparison |
| `report_ignore_keys` | list | ["run_id", "timestamp"] | JSON keys to ignore |

### Localization Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `separator` | str | "," | CSV field separator |
| `decimal` | str | "." | Decimal separator (e.g., "," for Brazilian format) |
| `encoding` | str | "utf-8" | File encoding |

## Debugging Failed Tests

### 1. Check artifacts
When tests fail, artifacts are saved in the case directory:
```
tests/golden/{marketplace}/{category}/case_xxx/artifacts/
├── actual_output.csv    # What the pipeline produced
├── diff.html           # Visual diff report
└── actual_report.json  # Actual validation report
```

### 2. View HTML diff
Open `artifacts/diff.html` in a browser to see a visual comparison:
- Red cells: Values that don't match
- Blue cells: Missing values
- Green cells: Extra values

### 3. Update golden files (if change is intentional)
If the pipeline behavior changed intentionally:
```bash
# Copy actual to expected
cp artifacts/actual_output.csv ../expected_output.csv
cp artifacts/actual_report.json ../expected_report.json

# Verify test now passes
pytest tests/golden/{marketplace}/{category}/case_xxx
```

## CI Integration

Golden tests run automatically on:
- Push to main, develop, or feature branches
- Pull requests

Failed tests upload artifacts as GitHub Actions artifacts, downloadable for 7 days.

## Best Practices

### 1. Test Case Design
- Each case should test specific scenarios (e.g., "title too long", "negative price")
- Keep input files small but comprehensive
- Name cases descriptively: `case_001_title_truncation`, not just `case_001`

### 2. Maintenance
- Review golden outputs when validation rules change
- Update expected outputs only after verifying changes are correct
- Document why each test case exists in a README in the case directory

### 3. Performance
- Use `chunk_size` for large files (>10k rows)
- Keep most test files under 100 rows
- Create separate cases for performance testing

## Troubleshooting

### Tests fail with "module not found"
Ensure the API dependencies are installed:
```bash
pip install -r apps/api/requirements.txt
```

### Float comparison issues
Adjust `float_tolerance` in config.yaml:
```yaml
float_tolerance: 0.001  # Less strict
```

### Locale/encoding issues
For Brazilian Portuguese data:
```yaml
separator: ";"
decimal: ","
encoding: "latin-1"
```

### Determinism issues
Ensure data is sorted consistently:
```yaml
sort_by: ["sku", "created_at"]  # Multiple columns for stability
```

## Advanced Usage

### Streaming large files
For files too large for memory:
```yaml
chunk_size: 1000  # Process 1000 rows at a time
```

### Custom normalizers
Add to `normalizers.py`:
```python
def normalize_brazilian_cpf(cpf: str) -> str:
    """Normalize CPF to XXX.XXX.XXX-XX format."""
    digits = re.sub(r'\D', '', cpf)
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
```

### Parameterized tests
Use pytest parametrization for variants:
```python
@pytest.mark.parametrize("locale", ["en_US", "pt_BR"])
def test_with_locale(golden_case, locale):
    result = golden_case(f"case_{locale}")
    assert result.passed
```