"""Pytest configuration for golden tests."""

import pytest
from pathlib import Path
from typing import List
import tempfile
import shutil

from tests.golden.golden_runner import run_golden_case, discover_cases, load_spec


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "golden: mark test as golden test")
    config.addinivalue_line("markers", "mercado_livre: mark test for Mercado Livre")
    config.addinivalue_line("markers", "shopee: mark test for Shopee")
    config.addinivalue_line("markers", "amazon: mark test for Amazon")


@pytest.fixture
def golden_case():
    """Fixture for running a golden test case."""
    def _run_case(case_dir: str, **kwargs):
        return run_golden_case(case_dir, **kwargs)
    return _run_case


@pytest.fixture
def pipeline_ctx():
    """Fixture providing pipeline context."""
    return {
        'marketplace': None,
        'category': None,
        'config': {},
    }


@pytest.fixture
def tmp_outdir():
    """Fixture providing temporary output directory."""
    tmpdir = tempfile.mkdtemp(prefix="golden_test_")
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


def pytest_collection_modifyitems(items):
    """Auto-mark tests based on their path."""
    for item in items:
        # Get the test file path
        test_path = str(item.fspath)
        
        # Auto-add golden marker if in golden directory
        if 'tests/golden' in test_path:
            item.add_marker(pytest.mark.golden)
        
        # Auto-add marketplace markers based on path
        if 'mercado_livre' in test_path:
            item.add_marker(pytest.mark.mercado_livre)
        elif 'shopee' in test_path:
            item.add_marker(pytest.mark.shopee)
        elif 'amazon' in test_path:
            item.add_marker(pytest.mark.amazon)


def pytest_generate_tests(metafunc):
    """Parametrize tests with discovered golden cases."""
    if "case_dir" in metafunc.fixturenames:
        # Check if specific marketplace filter is requested
        markers = [m.name for m in metafunc.definition.iter_markers()]
        
        # Discover all cases
        all_cases = discover_cases()
        
        # Filter by marketplace if marker present
        filtered_cases = []
        for case in all_cases:
            if 'mercado_livre' in markers and 'mercado_livre' not in case:
                continue
            if 'shopee' in markers and 'shopee' not in case:
                continue
            if 'amazon' in markers and 'amazon' not in case:
                continue
            filtered_cases.append(case)
        
        if filtered_cases:
            # Use case name as test ID
            ids = [Path(case).name for case in filtered_cases]
            metafunc.parametrize("case_dir", filtered_cases, ids=ids)