from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings


# Weather code to condition mapping
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class WeatherService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def get_forecast(
        self, destination: str, country_code: str = "NP"
    ) -> dict[str, Any]:
        """
        Get weather forecast for a destination.

        Args:
            destination: City name to search for
            country_code: ISO 3166-1 alpha-2 country code. Defaults to "NP" (Nepal).
        """
        if not self.settings.open_meteo_base_url or not self.settings.open_meteo_geo_base_url:
            return {"detail": "Open-Meteo URLs not configured"}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                geo_resp = await client.get(
                    self.settings.open_meteo_geo_base_url,
                    params={
                        "name": destination,
                        "count": 10,  # Get more results to filter by country
                        "country_code": country_code,
                    },
                )
                geo_resp.raise_for_status()
                geo_data = geo_resp.json()
                results = geo_data.get("results") or []
                if not results:
                    return {"detail": "No geocoding results"}

                location = results[0]
                lat = location.get("latitude")
                lon = location.get("longitude")

                # Fetch both current and daily weather
                weather_resp = await client.get(
                    self.settings.open_meteo_base_url,
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                        "timezone": "auto",
                    },
                )
                weather_resp.raise_for_status()
                weather_data = weather_resp.json()
                current = weather_data.get("current", {})
                daily = weather_data.get("daily", {})
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Weather provider is unavailable",
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Weather provider error",
            ) from exc

        # Format forecast for frontend
        forecast = []
        if daily.get("time"):
            for i in range(len(daily["time"])):
                code = daily.get("weather_code", [0])[i] if i < len(daily.get("weather_code", [])) else 0
                forecast.append({
                    "date": daily["time"][i],
                    "high": daily.get("temperature_2m_max", [0])[i] if i < len(daily.get("temperature_2m_max", [])) else 0,
                    "low": daily.get("temperature_2m_min", [0])[i] if i < len(daily.get("temperature_2m_min", [])) else 0,
                    "condition": WEATHER_CODES.get(code, "Unknown"),
                })

        # Current weather
        current_code = current.get("weather_code", 0)

        return {
            "city": location.get("name"),
            "country": location.get("country"),
            "temperature": round(current.get("temperature_2m", 0)),
            "feels_like": round(current.get("apparent_temperature", 0)),
            "condition": WEATHER_CODES.get(current_code, "Unknown"),
            "humidity": current.get("relative_humidity_2m", 0),
            "wind_speed": round(current.get("wind_speed_10m", 0)),
            "visibility": 10,  # Open-Meteo doesn't provide visibility in basic plan
            "pressure": 1013,  # Open-Meteo doesn't provide pressure in basic current data
            "high": daily.get("temperature_2m_max", [0])[0] if daily.get("temperature_2m_max") else 0,
            "low": daily.get("temperature_2m_min", [0])[0] if daily.get("temperature_2m_min") else 0,
            "forecast": forecast,
        }