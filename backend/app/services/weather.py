from typing import Any

import httpx

from app.core.config import get_settings


class WeatherService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def get_forecast(self, destination: str) -> dict[str, Any]:
        if not self.settings.open_meteo_base_url or not self.settings.open_meteo_geo_base_url:
            return {"detail": "Open-Meteo URLs not configured"}

        async with httpx.AsyncClient(timeout=10) as client:
            geo_resp = await client.get(
                self.settings.open_meteo_geo_base_url,
                params={"name": destination, "count": 1},
            )
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()
            results = geo_data.get("results") or []
            if not results:
                return {"detail": "No geocoding results"}

            location = results[0]
            lat = location.get("latitude")
            lon = location.get("longitude")

            weather_resp = await client.get(
                self.settings.open_meteo_base_url,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                    "timezone": "auto",
                },
            )
            weather_resp.raise_for_status()
            return {
                "location": {
                    "name": location.get("name"),
                    "country": location.get("country"),
                    "latitude": lat,
                    "longitude": lon,
                },
                "forecast": weather_resp.json().get("daily", {}),
            }
