import time
from typing import List
import pandas as pd

from src.core.engines.rule_engine import RuleEngine
from src.core.interfaces import ValidationError as CoreValidationError
from src.schemas.validate import ValidationResult, ValidationError as SchemaValidationError, Marketplace, Category
from src.rules.registry import MARKETPLACE_PROVIDERS


class ValidationPipeline:
    """Pipeline that coordinates the rule engine validation process."""

    def __init__(self, engine: RuleEngine | None = None):
        self.engine = engine or RuleEngine()

    def _convert_errors(self, core_errors: List[CoreValidationError]) -> List[SchemaValidationError]:
        errors: List[SchemaValidationError] = []
        for error in core_errors:
            errors.append(
                SchemaValidationError(
                    row=error.row,
                    column=error.column,
                    error=error.error,
                    value=str(error.value) if error.value is not None else None,
                    suggestion=error.suggestion,
                    severity=error.severity.value,
                )
            )
        return errors

    def validate(self, df: pd.DataFrame, marketplace: Marketplace, category: Category) -> ValidationResult:
        start_time = time.time()

        # Clear existing rules and providers
        self.engine.clear_rules()
        self.engine.clear_providers()

        # Load marketplace specific provider using registry
        provider_cls = MARKETPLACE_PROVIDERS.get(marketplace)
        if not provider_cls:
            raise ValueError(f"Marketplace '{marketplace.value}' is not registered")
        
        provider = provider_cls()

        self.engine.add_provider(provider)

        context = {
            "marketplace": marketplace.value,
            "category": category.value,
        }

        core_errors = self.engine.validate(df, context)
        schema_errors = self._convert_errors(core_errors)

        total_rows = len(df)
        error_rows = len({e.row - 1 for e in schema_errors})
        valid_rows = total_rows - error_rows
        warnings_count = sum(1 for e in schema_errors if e.severity == "warning")
        processing_time_ms = int((time.time() - start_time) * 1000)

        return ValidationResult(
            total_rows=total_rows,
            valid_rows=valid_rows,
            error_rows=error_rows,
            errors=schema_errors,
            warnings_count=warnings_count,
            processing_time_ms=processing_time_ms,
        )
