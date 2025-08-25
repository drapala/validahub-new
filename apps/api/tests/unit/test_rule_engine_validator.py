import pytest
from unittest.mock import AsyncMock

from src.core.interfaces import IRuleEngineService
from src.infrastructure.validators.rule_engine_validator import RuleEngineValidator


@pytest.mark.asyncio
async def test_validate_row_uses_service():
    service = AsyncMock(spec=IRuleEngineService)
    service.validate_row.return_value = ["item"]
    validator = RuleEngineValidator(service)

    result = await validator.validate_row({}, "ml")

    assert result == ["item"]
    service.validate_row.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_and_fix_row_uses_service():
    service = AsyncMock(spec=IRuleEngineService)
    service.validate_and_fix_row.return_value = ({}, ["item"])
    validator = RuleEngineValidator(service)

    fixed_row, items = await validator.validate_and_fix_row({}, "ml")

    assert fixed_row == {}
    assert items == ["item"]
    service.validate_and_fix_row.assert_awaited_once()
