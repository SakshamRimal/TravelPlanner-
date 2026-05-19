import pytest
import logging
from unittest.mock import patch, AsyncMock

from backend.app.services.currency_service import CurrencyService


@pytest.mark.asyncio
async def test_currency_service_uses_fallback_on_api_failure():
    service = CurrencyService()
    service.settings.exchangerate_api_key = "fake_key"

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        rate = await service.get_usd_to_nrs_rate()
        assert rate == service.settings.usd_to_nrs_rate


@pytest.mark.asyncio
async def test_currency_service_uses_cache():
    service = CurrencyService()
    service._rate_cache = 140.0
    service._cache_time = 9999999999

    rate = await service.get_usd_to_nrs_rate()
    assert rate == 140.0


def test_usd_to_nrs_conversion():
    service = CurrencyService()
    service._rate_cache = 135.0

    result = service.usd_to_nrs(100)
    assert result == 13500.0


def test_nrs_to_usd_conversion():
    service = CurrencyService()
    service._rate_cache = 135.0

    result = service.nrs_to_usd(13500)
    assert result == 100.0