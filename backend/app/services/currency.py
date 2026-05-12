import httpx

from app.core.config import get_settings


class CurrencyService:
    _rate_cache: float | None = None
    _cache_time: float = 0
    _cache_duration: int = 3600

    def __init__(self) -> None:
        self.settings = get_settings()

    async def get_usd_to_nrs_rate(self) -> float:
        import time
        current_time = time.time()

        if self._rate_cache is not None and (current_time - self._cache_time) < self._cache_duration:
            return self._rate_cache

        if self.settings.exchangerate_api_key:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(
                        f"https://v6.exchangerate-api.com/v6/{self.settings.exchangerate_api_key}/latest/USD"
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    rate = data.get("conversion_rates", {}).get("NPR", 135.0)
                    self._rate_cache = rate
                    self._cache_time = current_time
                    return rate
            except Exception:
                pass

        return self.settings.usd_to_nrs_rate

    def usd_to_nrs(self, amount_usd: float) -> float:
        if self._rate_cache:
            return round(amount_usd * self._rate_cache, 2)
        return round(amount_usd * self.settings.usd_to_nrs_rate, 2)

    def nrs_to_usd(self, amount_nrs: float) -> float:
        if self._rate_cache:
            return round(amount_nrs / self._rate_cache, 2)
        return round(amount_nrs / self.settings.usd_to_nrs_rate, 2)


_currency_service: CurrencyService | None = None


async def get_currency_service() -> CurrencyService:
    global _currency_service
    if _currency_service is None:
        _currency_service = CurrencyService()
        await _currency_service.get_usd_to_nrs_rate()
    return _currency_service