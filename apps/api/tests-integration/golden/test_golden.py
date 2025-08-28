"""Golden tests for ValidaHub pipeline."""

import pytest
from pathlib import Path

from tests.golden.golden_runner import run_golden_case, load_spec


@pytest.mark.golden
def test_golden_auto_discovery(case_dir):
    """Test all discovered golden cases."""
    spec = load_spec(Path(case_dir) / "config.yaml")
    result = run_golden_case(case_dir, spec=spec)
    assert result.passed, result.diff_summary


@pytest.mark.golden
@pytest.mark.mercado_livre
class TestMercadoLivre:
    """Golden tests specific to Mercado Livre."""
    
    def test_eletronicos_basic(self, golden_case):
        """Test basic electronics category validation."""
        case_dir = "tests/golden/mercado_livre/eletronicos/case_001"
        result = golden_case(case_dir)
        assert result.passed, result.diff_summary


@pytest.mark.golden
@pytest.mark.shopee
class TestShopee:
    """Golden tests specific to Shopee."""
    
    def test_moda_basic(self, golden_case):
        """Test basic fashion category validation."""
        case_dir = "tests/golden/shopee/moda/case_001"
        result = golden_case(case_dir)
        assert result.passed, result.diff_summary