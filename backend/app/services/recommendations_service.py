import re
from typing import Any

import httpx

from app.core.config import get_settings
from app.services.currency_service import get_currency_service


def _normalize_iata_code(location: str) -> str:
    code = location.strip().upper()
    if len(code) == 3 and code.isalpha():
        return code
    return code[:3]


# Fallback data for common Nepal destinations
FALLBACK_DATA = {
    "pokhara": {
        "flights": [
            {
                "carrier": "Buddha Air",
                "flight_number": "U4 201",
                "departure_airport": "KTM",
                "arrival_airport": "PKR",
                "departure_time": "06:30",
                "arrival_time": "07:15",
                "duration": "45 min",
                "stops": 0,
                "price": 8500,
                "type": "Domestic",
            },
            {
                "carrier": "Yeti Airlines",
                "flight_number": "YT 501",
                "departure_airport": "KTM",
                "arrival_airport": "PKR",
                "departure_time": "08:00",
                "arrival_time": "08:45",
                "duration": "45 min",
                "stops": 0,
                "price": 9500,
                "type": "Domestic",
            },
            {
                "carrier": "Summit Air",
                "flight_number": "SMT 301",
                "departure_airport": "KTM",
                "arrival_airport": "PKR",
                "departure_time": "10:30",
                "arrival_time": "11:15",
                "duration": "45 min",
                "stops": 0,
                "price": 7800,
                "type": "Domestic",
            },
        ],
        "hotels": [
            {
                "name": "Hotel Barahi",
                "rating": 4.2,
                "reviews": 856,
                "price_per_night": 5500,
                "currency": "NRS",
                "address": "Lakeside, Pokhara",
                "amenities": ["Free WiFi", "Lake View", "Restaurant", "Spa"],
            },
            {
                "name": "Waterfront Resort",
                "rating": 4.5,
                "reviews": 1243,
                "price_per_night": 8500,
                "currency": "NRS",
                "address": "Lakeside, Phewa Lake",
                "amenities": ["Pool", "Free WiFi", "Restaurant", "Bar", "Spa"],
            },
            {
                "name": "Hotel Pokhara Grande",
                "rating": 4.0,
                "reviews": 567,
                "price_per_night": 4500,
                "currency": "NRS",
                "address": "New Road, Pokhara",
                "amenities": ["Free WiFi", "Restaurant", "Parking"],
            },
            {
                "name": "Fishtail Lodge",
                "rating": 4.3,
                "reviews": 389,
                "price_per_night": 6000,
                "currency": "NRS",
                "address": "Fewa Lake, Lakeside",
                "amenities": ["Lake View", "Restaurant", "Garden"],
            },
        ],
        "activities": [
            {
                "name": "Sarangkot Sunrise Trek",
                "rating": 4.7,
                "reviews": 2341,
                "type": "Trekking",
                "description": "Watch the sunrise over the Annapurna range from Sarangkot viewpoint. Panoramic views of Machapuchare and the entire Pokhara valley.",
                "duration": "3-4 hours",
                "estimated_cost": 1500,
                "currency": "NRS",
            },
            {
                "name": "Phewa Lake Boat Ride",
                "rating": 4.5,
                "reviews": 1876,
                "type": "Water Sports",
                "description": "Enjoy a peaceful boat ride on Phewa Lake with stunning views of the Annapurna mountains reflected in the water.",
                "duration": "1-2 hours",
                "estimated_cost": 800,
                "currency": "NRS",
            },
            {
                "name": "Paragliding in Pokhara",
                "rating": 4.8,
                "reviews": 1567,
                "type": "Adventure",
                "description": "Experience tandem paragliding over the lake and mountains. One of the best paragliding spots in the world.",
                "duration": "30 min flight",
                "estimated_cost": 5500,
                "currency": "NRS",
            },
            {
                "name": "Davis Falls Visit",
                "rating": 4.2,
                "reviews": 2109,
                "type": "Sightseeing",
                "description": "Visit the unique underground waterfall and the sacred Tal Barahi Temple on the island in Phewa Lake.",
                "duration": "2-3 hours",
                "estimated_cost": 500,
                "currency": "NRS",
            },
            {
                "name": "International Mountain Museum",
                "rating": 4.4,
                "reviews": 1234,
                "type": "Cultural",
                "description": "Learn about the history of mountaineering in the Himalayas, Nepalese culture, and mountain ecosystems.",
                "duration": "2 hours",
                "estimated_cost": 300,
                "currency": "NRS",
            },
        ],
    },
    "kathmandu": {
        "flights": [
            {
                "carrier": "Nepal Airlines",
                "flight_number": "RA 201",
                "departure_airport": "DEL",
                "arrival_airport": "KTM",
                "departure_time": "09:00",
                "arrival_time": "10:15",
                "duration": "1h 15m",
                "stops": 0,
                "price": 12500,
                "type": "International",
            },
            {
                "carrier": "IndiGo",
                "flight_number": "6E 2341",
                "departure_airport": "DEL",
                "arrival_airport": "KTM",
                "departure_time": "11:30",
                "arrival_time": "12:45",
                "duration": "1h 15m",
                "stops": 0,
                "price": 11000,
                "type": "International",
            },
            {
                "carrier": "Buddha Air",
                "flight_number": "U4 101",
                "departure_airport": "PKR",
                "arrival_airport": "KTM",
                "departure_time": "14:00",
                "arrival_time": "14:45",
                "duration": "45 min",
                "stops": 0,
                "price": 7500,
                "type": "Domestic",
            },
        ],
        "hotels": [
            {
                "name": "Hyatt Regency Kathmandu",
                "rating": 4.6,
                "reviews": 3421,
                "price_per_night": 12500,
                "currency": "NRS",
                "address": "Taragaon, Boudha",
                "amenities": ["Pool", "Spa", "Free WiFi", "Restaurant", "Gym"],
            },
            {
                "name": "Hotel Yak & Yeti",
                "rating": 4.4,
                "reviews": 2156,
                "price_per_night": 8500,
                "currency": "NRS",
                "address": "Durbar Marg",
                "amenities": ["Free WiFi", "Restaurant", "Bar", "Casino"],
            },
            {
                "name": "Shangri-La Village",
                "rating": 4.3,
                "reviews": 1879,
                "price_per_night": 6500,
                "currency": "NRS",
                "address": "Lazimpat",
                "amenities": ["Pool", "Spa", "Free WiFi", "Restaurant"],
            },
            {
                "name": "Hotel Tibet International",
                "rating": 4.1,
                "reviews": 945,
                "price_per_night": 5000,
                "currency": "NRS",
                "address": "Gangabu",
                "amenities": ["Free WiFi", "Restaurant", "Parking"],
            },
        ],
        "activities": [
            {
                "name": "Pashupatinath Temple",
                "rating": 4.7,
                "reviews": 4567,
                "type": "Religious",
                "description": "UNESCO World Heritage Site - one of the most sacred Hindu temples dedicated to Lord Shiva.",
                "duration": "2-3 hours",
                "estimated_cost": 1000,
                "currency": "NRS",
            },
            {
                "name": "Swayambhunath (Monkey Temple)",
                "rating": 4.8,
                "reviews": 5234,
                "type": "Cultural",
                "description": "Ancient Buddhist stupa with stunning views of Kathmandu valley. One of Nepal's most sacred sites.",
                "duration": "2 hours",
                "estimated_cost": 500,
                "currency": "NRS",
            },
            {
                "name": "Thamel Walking Tour",
                "rating": 4.5,
                "reviews": 1890,
                "type": "City Tour",
                "description": "Explore the vibrant streets of Thamel - known for shops, restaurants, and cultural experiences.",
                "duration": "3-4 hours",
                "estimated_cost": 800,
                "currency": "NRS",
            },
            {
                "name": "Boudhanath Stupa",
                "rating": 4.8,
                "reviews": 3876,
                "type": "Religious",
                "description": "Largest spherical stupa in Nepal - a UNESCO site and important Buddhist pilgrimage center.",
                "duration": "1-2 hours",
                "estimated_cost": 500,
                "currency": "NRS",
            },
            {
                "name": "Garden of Dreams",
                "rating": 4.3,
                "reviews": 1543,
                "type": "Sightseeing",
                "description": "Beautiful neo-classical garden in the heart of Kathmandu - perfect for relaxation.",
                "duration": "1-2 hours",
                "estimated_cost": 300,
                "currency": "NRS",
            },
        ],
    },
    "chitwan": {
        "flights": [
            {
                "carrier": "Buddha Air",
                "flight_number": "U4 401",
                "departure_airport": "KTM",
                "arrival_airport": "BIR",
                "departure_time": "07:00",
                "arrival_time": "08:00",
                "duration": "1 hour",
                "stops": 0,
                "price": 6500,
                "type": "Domestic",
            },
            {
                "carrier": "Yeti Airlines",
                "flight_number": "YT 601",
                "departure_airport": "KTM",
                "arrival_airport": "BIR",
                "departure_time": "10:30",
                "arrival_time": "11:30",
                "duration": "1 hour",
                "stops": 0,
                "price": 7000,
                "type": "Domestic",
            },
        ],
        "hotels": [
            {
                "name": "Chitwan Jungle Lodge",
                "rating": 4.5,
                "reviews": 1234,
                "price_per_night": 7500,
                "currency": "NRS",
                "address": "Sauraha, Chitwan",
                "amenities": ["Pool", "Free WiFi", "Restaurant", "Safari Tours"],
            },
            {
                "name": "Green Park Resort",
                "rating": 4.3,
                "reviews": 876,
                "price_per_night": 5500,
                "currency": "NRS",
                "address": "Meghauli",
                "amenities": ["Free WiFi", "Restaurant", "Garden", "Jeep Safari"],
            },
            {
                "name": "Tigerland Resort",
                "rating": 4.4,
                "reviews": 654,
                "price_per_night": 6500,
                "currency": "NRS",
                "address": "Sauraha",
                "amenities": ["Pool", "Restaurant", "Bar", "Cultural Show"],
            },
        ],
        "activities": [
            {
                "name": "Chitwan National Park Safari",
                "rating": 4.8,
                "reviews": 2341,
                "type": "Wildlife",
                "description": "Jeep safari through the UNESCO World Heritage site. Chance to see rhinos, tigers, and elephants.",
                "duration": "4-5 hours",
                "estimated_cost": 2500,
                "currency": "NRS",
            },
            {
                "name": "Elephant Breeding Center",
                "rating": 4.5,
                "reviews": 1876,
                "type": "Wildlife",
                "description": "Visit the elephant breeding center and learn about conservation efforts.",
                "duration": "1-2 hours",
                "estimated_cost": 500,
                "currency": "NRS",
            },
            {
                "name": "Canoeing on Rapti River",
                "rating": 4.4,
                "reviews": 1567,
                "type": "Water Sports",
                "description": "Peaceful canoe ride spotting gharials, mugger crocodiles, and various birds.",
                "duration": "2 hours",
                "estimated_cost": 800,
                "currency": "NRS",
            },
            {
                "name": "Tharu Cultural Show",
                "rating": 4.3,
                "reviews": 1234,
                "type": "Cultural",
                "description": "Experience traditional Tharu dance performance with local communities.",
                "duration": "1-2 hours",
                "estimated_cost": 600,
                "currency": "NRS",
            },
        ],
    },
    "lukla": {
        "flights": [
            {
                "carrier": "Tara Air",
                "flight_number": "TH 701",
                "departure_airport": "KTM",
                "arrival_airport": "LUA",
                "departure_time": "06:00",
                "arrival_time": "06:35",
                "duration": "35 min",
                "stops": 0,
                "price": 9500,
                "type": "Domestic",
            },
            {
                "carrier": "Sumbek Airlines",
                "flight_number": "SB 101",
                "departure_airport": "KTM",
                "arrival_airport": "LUA",
                "departure_time": "07:30",
                "arrival_time": "08:05",
                "duration": "35 min",
                "stops": 0,
                "price": 9800,
                "type": "Domestic",
            },
        ],
        "hotels": [
            {
                "name": "Khumbu Lodge",
                "rating": 4.0,
                "reviews": 345,
                "price_per_night": 3500,
                "currency": "NRS",
                "address": "Lukla",
                "amenities": ["Free WiFi", "Restaurant", "Heating"],
            },
            {
                "name": "Everest Resort",
                "rating": 4.2,
                "reviews": 234,
                "price_per_night": 4500,
                "currency": "NRS",
                "address": "Lukla",
                "amenities": ["Free WiFi", "Restaurant", "Mountain View"],
            },
        ],
        "activities": [
            {
                "name": "Everest Base Camp Trek Start",
                "rating": 4.9,
                "reviews": 3456,
                "type": "Trekking",
                "description": "Begin your journey to Everest Base Camp from the famous Lukla gateway.",
                "duration": "Multi-day",
                "estimated_cost": 50000,
                "currency": "NRS",
            },
            {
                "name": "Monjo Village Walk",
                "rating": 4.4,
                "reviews": 567,
                "type": "Walking",
                "description": "Explore the scenic village of Monjo, gateway to Sagarmatha National Park.",
                "duration": "2-3 hours",
                "estimated_cost": 500,
                "currency": "NRS",
            },
        ],
    },
}


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
            return {"organic_results": [], "local_results": {"places": []}}

        params = {"q": query, "engine": engine, "api_key": self.settings.serpapi_api_key, "num": 5}
        if extra_params:
            params.update(extra_params)

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get("https://serpapi.com/search.json", params=params)
                resp.raise_for_status()
                return resp.json()
        except Exception:
            return {"organic_results": [], "local_results": {"places": []}}

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

    def _get_fallback_data(self, destination: str) -> dict[str, Any] | None:
        normalized = destination.strip().lower()
        for key in FALLBACK_DATA:
            if key in normalized or normalized in key:
                return FALLBACK_DATA[key]
        return None

    async def _get_flights_aviationstack(self, origin: str, destination: str) -> list[dict[str, Any]]:
        origin_iata = _normalize_iata_code(origin)
        dest_iata = self._city_to_iata(destination)

        if not self.settings.aviationstack_api_key:
            fallback = self._get_fallback_data(destination)
            if fallback:
                return fallback["flights"]

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
                dep_airport = flight.get("departure", {})
                arr_airport = flight.get("arrival", {})
                airline = flight.get("airline", {})

                flights.append({
                    "carrier": airline.get("name", "Unknown"),
                    "flight_number": flight.get("flight", {}).get("iata", "N/A"),
                    "departure_airport": dep_airport.get("airport", origin_iata),
                    "arrival_airport": arr_airport.get("airport", dest_iata),
                    "departure_time": dep_airport.get("scheduled"),
                    "arrival_time": arr_airport.get("scheduled"),
                    "status": flight.get("flight_status", "Unknown"),
                })
            if flights:
                return flights
        except Exception:
            pass

        fallback = self._get_fallback_data(destination)
        if fallback:
            return fallback["flights"]

        return [{
            "carrier": "Multiple Airlines",
            "flight_number": "Check online",
            "departure_airport": origin_iata,
            "arrival_airport": dest_iata,
            "departure_time": "Varies",
            "arrival_time": "Varies",
            "duration": "Check airline",
            "stops": -1,
            "price": 0,
            "note": "Configure SERPAPI_API_KEY for real-time flight data",
        }]

    CITY_TO_IATA = {
        "kathmandu": "KTM",
        "delhi": "DEL",
        "mumbai": "BOM",
        "bangalore": "BLR",
        "kolkata": "CCU",
        "chennai": "MAA",
        "pune": "PNQ",
        "hyderabad": "HYD",
        "dubai": "DXB",
        "bangkok": "BKK",
        "singapore": "SIN",
        "kuala lumpur": "KUL",
        "london": "LHR",
        "paris": "CDG",
        "doha": "DOH",
        "pokhara": "PKR",
        "chitwan": "BIR",
        "lukla": "LUA",
    }

    def _city_to_iata(self, city: str) -> str:
        normalized = city.strip().lower()
        if normalized in self.CITY_TO_IATA:
            return self.CITY_TO_IATA[normalized]
        return _normalize_iata_code(city)

    async def _get_hotels(self, destination: str) -> list[dict[str, Any]]:
        search_destination = f"{destination} Nepal" if "nepal" not in destination.lower() else destination

        if not self.settings.serpapi_api_key:
            fallback = self._get_fallback_data(destination)
            if fallback:
                return fallback["hotels"]

        hotels: list[dict[str, Any]] = []

        try:
            data = await self._search_serpapi(
                query=f"hotels in {search_destination}",
                engine="google_hotels",
                extra_params={"hl": "en", "gl": "np"},
            )
            for prop in data.get("properties", [])[:5]:
                rate = prop.get("rate_per_night", {})
                price_raw = rate.get("lowest") or rate.get("high")
                price_nrs = await self._usd_to_nrs(price_raw) if price_raw else None
                if price_nrs:
                    hotels.append({
                        "name": prop.get("name"),
                        "rating": prop.get("overall_rating"),
                        "reviews": prop.get("reviews"),
                        "price_per_night": price_nrs,
                        "currency": "NRS",
                        "amenities": prop.get("amenities", [])[:5] if prop.get("amenities") else [],
                        "address": prop.get("address"),
                    })
        except Exception:
            pass

        if not hotels:
            fallback = self._get_fallback_data(destination)
            if fallback:
                return fallback["hotels"]

        return hotels

    async def _get_activities(self, destination: str) -> list[dict[str, Any]]:
        search_destination = f"{destination} Nepal" if "nepal" not in destination.lower() else destination

        if not self.settings.serpapi_api_key:
            fallback = self._get_fallback_data(destination)
            if fallback:
                return fallback["activities"]

        try:
            data = await self._search_serpapi(f"best things to do in {search_destination} attractions")
        except Exception:
            data = {"local_results": {"places": []}, "organic_results": []}

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
                "estimated_cost": round(price_nrs) if price_nrs else 500,
                "currency": "NRS",
            })

        if len(activities) < 5:
            for item in data.get("organic_results", [])[:5 - len(activities)]:
                activities.append({
                    "name": item.get("title"),
                    "description": item.get("snippet"),
                    "estimated_cost": 500,
                    "currency": "NRS",
                })

        if not activities:
            fallback = self._get_fallback_data(destination)
            if fallback:
                return fallback["activities"]

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
            "has_api_data": bool(self.settings.serpapi_api_key),
        }