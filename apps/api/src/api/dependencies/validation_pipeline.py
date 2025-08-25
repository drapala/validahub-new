"""
Dependency providers for validation pipeline and related services.

This module constructs the ValidationPipeline and its required services
so they can be injected into API endpoints via FastAPI's Depends system.
Providing dependencies through functions allows tests to supply mocks or
alternative implementations.
"""

from functools import lru_cache

from fastapi import Depends

from ...core.pipeline.validation_pipeline import ValidationPipeline
from ...services.rule_engine_service import RuleEngineService


@lru_cache
def get_rule_engine_service() -> RuleEngineService:
    """Create a cached RuleEngineService instance."""
    return RuleEngineService()


def get_validation_pipeline(
    rule_engine_service: RuleEngineService = Depends(get_rule_engine_service),
) -> ValidationPipeline:
    """Provide a ValidationPipeline with injected RuleEngineService."""
    return ValidationPipeline(rule_engine_service=rule_engine_service)


__all__ = ["get_rule_engine_service", "get_validation_pipeline"]
