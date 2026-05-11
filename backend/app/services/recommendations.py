from typing import Any

import httpx

from app.core.config import get_settings


class RecommendationService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def _fetch_liteapi_hotels(self, destination: str) -> list[dict[str, Any]] | None:
        if not self.settings.liteapi_hotel_base_url or not self.settings.liteapi_api_key:
            return None

        headers = {"X-API-Key": self.settings.liteapi_api_key}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                self.settings.liteapi_hotel_base_url,
                params={
                    "countryCode": self.settings.liteapi_country_code,
                    "cityName": destination,
                },
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                return data.get("data", data.get("hotels", []))
            return data

    async def get_recommendations(self, destination: str):
        hotels = await self._fetch_liteapi_hotels(destination)

        return {
            "flights": [
                {
                    "carrier": "AirVista",
                    "flight_number": "AV203",
                    "price": 220.0,
                    "origin": "DEL",
                    "destination": destination,
                }
            ],
            "hotels": hotels
            if hotels
            else [
                {"name": "Lakeside Retreat", "nightly_price": 65.0, "rating": 4.4}
            ],
            "activities": [
                {"name": "Sunrise hike", "cost": 18.0, "category": "Adventure"}
            ],
        }
