"""
Dependency injection for TabularDataPort.
Provides the concrete implementation to be injected into use cases.
"""

from functools import lru_cache

from core.ports.tabular_data_port import TabularDataPort
from infrastructure.adapters.pandas_adapter import PandasAdapter


@lru_cache()
def get_tabular_adapter() -> TabularDataPort:
    """
    Get the tabular data adapter instance.
    
    This function provides the concrete implementation of TabularDataPort
    to be injected into use cases and other components.
    
    Returns:
        TabularDataPort: The concrete pandas adapter
    """
    return PandasAdapter()


def get_validate_csv_use_case():
    """
    Factory function for ValidateCsvUseCase with proper dependency injection.
    """
    from core.use_cases.validate_csv import ValidateCsvUseCase
    from .validation_pipeline import get_validation_pipeline
    
    return ValidateCsvUseCase(
        validation_pipeline=get_validation_pipeline(),
        tabular_adapter=get_tabular_adapter()
    )


def get_correct_csv_use_case():
    """
    Factory function for CorrectCsvUseCase with proper dependency injection.
    """
    from core.use_cases.correct_csv import CorrectCsvUseCase
    from .validation_pipeline import get_validation_pipeline
    
    return CorrectCsvUseCase(
        validation_pipeline=get_validation_pipeline(),
        tabular_adapter=get_tabular_adapter()
    )