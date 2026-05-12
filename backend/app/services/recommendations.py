import re
from typing import Any

import httpx

from app.core.config import get_settings
from app.services.currency import get_currency_service


class RecommendationService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def _usd_to_nrs(self, amount_usd: float | None) -> float | None:
        if amount_usd is None:
            return None
        currency_service = await get_currency_service()
        return currency_service.usd_to_nrs(amount_usd)

    async def _search_serpapi(self, query: str, engine: str = "google", extra_params: dict | None = None) -> dict[str, Any]:
        if not self.settings.serpapi_api_key:
            raise ValueError("SERPAPI_API_KEY is not configured.")

        params = {"q": query, "engine": engine, "api_key": self.settings.serpapi_api_key, "num": 5}
        if extra_params:
            params.update(extra_params)

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get("https://serpapi.com/search.json", params=params)
            resp.raise_for_status()
            return resp.json()

    def _extract_price_nrs(self, text: str) -> float | None:
        patterns = [
            r'Rs\.?\s*[\d,]+',
            r'रू\s*[\d,]+',
            r'NRs\.?\s*[\d,]+',
            r'NPR\s*[\d,]+',
            r'\$[\d,]+',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group()
                numbers = re.findall(r'[\d,]+', price_str)
                if numbers:
                    try:
                        value = float(numbers[0].replace(',', ''))
                        if '$' in price_str:
                            return None
                        return value
                    except ValueError:
                        pass
        return None

    async def _get_flights_aviationstack(self, origin: str, destination: str) -> list[dict[str, Any]]:
        if not self.settings.aviationstack_api_key:
            return await self._get_flights_fallback(origin, destination)

        iata_map = {
            "kathmandu": "KTM", "pokhara": "PKR", "lukla": "LUA",
            "chitwan": "RVR", "bhairahawa": "BIR", "nepalgunj": "KEP",
            "delhi": "DEL", "dubai": "DXB", "singapore": "SIN",
            "bangkok": "BKK", "kolkata": "CCU", "mumbai": "BOM",
        }

        origin_iata = iata_map.get(origin.lower(), origin.upper()[:3])
        dest_iata = iata_map.get(destination.lower(), destination.upper()[:3])

        url = "http://api.aviationstack.com/v1/flights"
        params = {
            "access_key": self.settings.aviationstack_api_key,
            "dep_iata": origin_iata,
            "arr_iata": dest_iata,
            "limit": 10,
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()

            flights = []
            for flight in data.get("data", [])[:5]:
                price_nrs = await self._get_nepal_flight_price(origin_iata, dest_iata)
                dep_airport = flight.get("departure", {})
                arr_airport = flight.get("arrival", {})

                flights.append({
                    "carrier": flight.get("airline", {}).get("name", "Unknown"),
                    "flight_number": flight.get("flight", {}).get("iata", "N/A"),
                    "departure_airport": dep_airport.get("airport", "Unknown"),
                    "arrival_airport": arr_airport.get("airport", "Unknown"),
                    "departure_time": dep_airport.get("scheduled"),
                    "arrival_time": arr_airport.get("scheduled"),
                    "status": flight.get("flight_status", "Unknown"),
                    "price": price_nrs,
                    "currency": "NRS",
                    "origin": origin_iata,
                    "destination": dest_iata,
                })
            return flights
        except Exception:
            return await self._get_flights_fallback(origin, destination)

    async def _get_flights_fallback(self, origin: str, destination: str) -> list[dict[str, Any]]:
        iata_map = {
            "kathmandu": "KTM", "pokhara": "PKR", "lukla": "LUA",
            "chitwan": "RVR", "bhairahawa": "BIR", "nepalgunj": "KEP",
            "delhi": "DEL", "dubai": "DXB", "singapore": "SIN",
            "bangkok": "BKK", "kolkata": "CCU", "mumbai": "BOM",
        }

        origin_iata = iata_map.get(origin.lower(), origin.upper()[:3])
        dest_iata = iata_map.get(destination.lower(), destination.upper()[:3])

        try:
            data = await self._search_serpapi(
                query=f"flights {origin_iata} to {dest_iata} Nepal price",
                engine="google",
                extra_params={"num": 5},
            )

            flights = []
            for item in data.get("organic_results", [])[:5]:
                price_nrs = self._extract_price_nrs(item.get("title", "") + item.get("snippet", ""))
                if price_nrs and price_nrs < 500:
                    price_nrs = price_nrs * 100
                if not price_nrs or price_nrs < 100:
                    price_nrs = await self._get_nepal_flight_price(origin_iata, dest_iata)
                if price_nrs:
                    flights.append({
                        "carrier": "Multiple Airlines",
                        "source": item.get("title"),
                        "description": item.get("snippet", "")[:200] if item.get("snippet") else None,
                        "price": round(price_nrs),
                        "currency": "NRS",
                        "origin": origin_iata,
                        "destination": dest_iata,
                        "url": item.get("link"),
                    })
            return flights
        except Exception:
            return []

    async def _get_nepal_flight_price(self, origin: str, destination: str) -> int:
        routes = {
            ("KTM", "DEL"): 8500, ("DEL", "KTM"): 8500,
            ("KTM", "DXB"): 28000, ("DXB", "KTM"): 28000,
            ("KTM", "SIN"): 35000, ("SIN", "KTM"): 35000,
            ("KTM", "BKK"): 25000, ("BKK", "KTM"): 25000,
            ("KTM", "CCU"): 6500, ("CCU", "KTM"): 6500,
            ("KTM", "BOM"): 12000, ("BOM", "KTM"): 12000,
            ("KTM", "PKR"): 3500, ("PKR", "KTM"): 3500,
            ("KTM", "LUA"): 15000, ("LUA", "KTM"): 15000,
            ("KTM", "BIR"): 5000, ("BIR", "KTM"): 5000,
            ("KTM", "KEP"): 5500, ("KEP", "KTM"): 5500,
        }
        return routes.get((origin, destination), 15000)

    async def _get_hotels(self, destination: str) -> list[dict[str, Any]]:
        try:
            data = await self._search_serpapi(
                query=f"hotels in {destination} Nepal price per night",
                engine="google_hotels",
                extra_params={"hl": "en", "gl": "np"},
            )
        except Exception:
            data = {}

        hotels: list[dict[str, Any]] = []

        for prop in data.get("properties", [])[:5]:
            rate = prop.get("rate_per_night", {})
            price_raw = rate.get("lowest") or rate.get("high")
            price_nrs = await self._usd_to_nrs(price_raw) if price_raw else None

            if not price_nrs or price_nrs < 1000:
                price_nrs = await self._get_nepal_hotel_price(prop.get("rating"))

            hotels.append({
                "name": prop.get("name"),
                "rating": prop.get("overall_rating"),
                "reviews": prop.get("reviews"),
                "price_per_night": price_nrs,
                "currency": "NRS",
                "amenities": prop.get("amenities", [])[:5] if prop.get("amenities") else [],
                "address": prop.get("address"),
                "url": prop.get("link"),
                "thumbnail": (prop.get("images", [{}])[0].get("thumbnail") if prop.get("images") else None),
            })

        if not hotels:
            fallback = await self._search_serpapi(f"best hotels in {destination} Nepal price")
            for item in fallback.get("organic_results", [])[:5]:
                price_nrs = self._extract_price_nrs(item.get("snippet", ""))
                if not price_nrs or price_nrs < 1000:
                    price_nrs = await self._get_nepal_hotel_price(None)
                hotels.append({
                    "name": item.get("title"),
                    "info": item.get("snippet"),
                    "price_per_night": round(price_nrs),
                    "currency": "NRS",
                    "url": item.get("link"),
                })

        return hotels

    async def _get_nepal_hotel_price(self, rating: float | None) -> int:
        if rating and rating >= 4.5:
            return 8000
        elif rating and rating >= 4.0:
            return 5000
        elif rating and rating >= 3.0:
            return 3000
        return 2500

    async def _get_activities(self, destination: str) -> list[dict[str, Any]]:
        try:
            data = await self._search_serpapi(f"best things to do in {destination} Nepal attractions")
        except Exception:
            return []

        activities: list[dict[str, Any]] = []

        for place in data.get("local_results", {}).get("places", [])[:5]:
            price_text = place.get("price", "")
            price_nrs = self._extract_price_nrs(price_text) or self._extract_price_nrs(place.get("description", ""))

            activities.append({
                "name": place.get("title"),
                "rating": place.get("rating"),
                "reviews": place.get("reviews"),
                "type": place.get("type"),
                "description": place.get("description"),
                "address": place.get("address"),
                "thumbnail": place.get("thumbnail"),
                "url": place.get("links", {}).get("website"),
                "gps": place.get("gps_coordinates"),
                "estimated_cost": round(price_nrs) if price_nrs else 500,
                "currency": "NRS",
            })

        if len(activities) < 5:
            for item in data.get("organic_results", [])[:5 - len(activities)]:
                activities.append({
                    "name": item.get("title"),
                    "description": item.get("snippet"),
                    "url": item.get("link"),
                    "estimated_cost": 500,
                    "currency": "NRS",
                })

        return activities

    async def get_recommendations(self, destination: str, origin: str = "KTM", budget: float | None = None) -> dict[str, Any]:
        currency_service = await get_currency_service()
        current_rate = await currency_service.get_usd_to_nrs_rate()

        flights = await self._get_flights_aviationstack(origin, destination)
        hotels = await self._get_hotels(destination)
        activities = await self._get_activities(destination)

        return {
            "destination": destination,
            "origin": origin,
            "currency": "NRS",
            "exchange_rate": current_rate,
            "rate_source": "exchangerate-api.com" if self.settings.exchangerate_api_key else "default",
            "flights": flights,
            "hotels": hotels,
            "activities": activities,
        }