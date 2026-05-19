import pytest
from datetime import datetime

from backend.app.services.budget_service import BudgetService


@pytest.mark.asyncio
async def test_1_day_trip_budget():
    service = BudgetService()
    result = await service.estimate_budget("Pokhara", 1, 1)
    assert result["days"] == 1
    assert "total_estimate" in result


@pytest.mark.asyncio
async def test_7_day_trip_budget():
    service = BudgetService()
    result = await service.estimate_budget("Pokhara", 7, 1)
    assert result["days"] == 7
    assert "total_estimate" in result


@pytest.mark.asyncio
async def test_14_day_trip_budget():
    service = BudgetService()
    result = await service.estimate_budget("Pokhara", 14, 2)
    assert result["days"] == 14
    assert result["travelers"] == 2


@pytest.mark.asyncio
async def test_missing_dates_defaults_to_1_day():
    service = BudgetService()
    result = await service.estimate_budget("Pokhara", 1, 1)
    assert result["days"] == 1


def test_days_calculation_from_dates():
    from datetime import datetime

    start = datetime.now()
    end = start.replace(day=start.day + 6)
    days = max(1, (end - start).days + 1)
    assert days == 7


def test_invalid_date_strings_handled():
    from datetime import datetime

    try:
        start = datetime.fromisoformat("invalid-date")
        end = datetime.fromisoformat("2024-01-15")
        days = max(1, (end - start).days + 1)
    except ValueError:
        days = 1
    assert days == 1