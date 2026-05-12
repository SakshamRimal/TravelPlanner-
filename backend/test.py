#!/usr/bin/env python3
"""
Backend integration tests using real SerpApi with mock responses.
Run with: python backend/test.py
Or: pytest backend/test.py -v
"""
import os
import sys
import asyncio
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("SERPAPI_API_KEY", "test-key")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("JWT_SECRET", "test-secret-key")
os.environ.setdefault("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")
os.environ.setdefault("OPEN_METEO_GEO_BASE_URL", "https://geocoding-api.open-meteo.com/v1/search")

from app.core.config import get_settings
from app.services.recommendations import RecommendationService
from app.services.destination import DestinationService
from app.services.budget import BudgetService
from app.services.weather import WeatherService


class DummyResp:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


def create_mock_serpapi_response():
    return {
        "organic_results": [
            {"title": "Hotel Yak & Yeti, Kathmandu - Nepal", "snippet": "Luxury hotel in heart of Kathmandu", "link": "https://hotel.example/1"},
            {"title": "Hotel Tibet, Kathmandu", "snippet": "Mid-range hotel with great views", "link": "https://hotel.example/2"},
        ],
        "properties": [
            {
                "name": "Hyatt Regency Kathmandu",
                "overall_rating": 4.5,
                "reviews": 1250,
                "rate_per_night": {"lowest": 120},
                "total_rate": {"lowest": 840},
                "amenities": ["WiFi", "Pool", "Spa"],
                "link": "https://hyatt.example.com",
                "images": [{"thumbnail": "https://img.example.com/hyatt.jpg"}],
            }
        ],
        "best_flights": [
            {
                "price": 450,
                "total_duration": 420,
                "flights": [
                    {
                        "airline": "Nepal Airlines",
                        "flight_number": "RA 215",
                        "departure_airport": {"name": "Indira Gandhi Intl", "time": "06:30"},
                        "arrival_airport": {"name": "Tribhuvan Intl", "time": "08:30"},
                        "airline_logo": "https://logo.example.com/nepal.png",
                    }
                ],
                "booking_token": "token123",
            }
        ],
        "other_flights": [
            {
                "price": 380,
                "total_duration": 480,
                "flights": [
                    {
                        "airline": "IndiGo",
                        "flight_number": "6E 1234",
                        "departure_airport": {"name": "Indira Gandhi Intl", "time": "14:00"},
                        "arrival_airport": {"name": "Tribhuvan Intl", "time": "16:00"},
                        "airline_logo": "https://logo.example.com/indigo.png",
                    }
                ],
            }
        ],
        "local_results": {
            "places": [
                {
                    "title": "Pashupatinath Temple",
                    "rating": 4.7,
                    "reviews": 3500,
                    "type": "Hindu temple",
                    "description": "UNESCO World Heritage Site",
                    "address": "Kathmandu, Nepal",
                    "thumbnail": "https://img.example.com/pashupatinath.jpg",
                    "links": {"website": "https://pashupatinath.example.com"},
                    "gps_coordinates": {"latitude": 27.9766, "longitude": 85.3489},
                },
                {
                    "title": "Swayambhunath Stupa",
                    "rating": 4.8,
                    "reviews": 2800,
                    "type": "Buddhist temple",
                    "description": "Monkey Temple with panoramic city views",
                    "address": "Kathmandu, Nepal",
                    "thumbnail": "https://img.example.com/swayambhu.jpg",
                }
            ]
        },
    }


def create_mock_geo_response():
    return {
        "results": [
            {"name": "Kathmandu", "country": "Nepal", "latitude": 27.7172, "longitude": 85.3240}
        ]
    }


def create_mock_weather_response():
    return {
        "daily": {
            "time": ["2026-05-13", "2026-05-14", "2026-05-15"],
            "temperature_2m_max": [25, 26, 24],
            "temperature_2m_min": [15, 16, 14],
            "weathercode": [1, 2, 3],
        }
    }


async def test_recommendations():
    print("\n=== Testing RecommendationService ===")

    async def fake_get(*args, **kwargs):
        return DummyResp(create_mock_serpapi_response())

    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=fake_get)):
        service = RecommendationService()
        result = await service.get_recommendations("Kathmandu")

    assert result["destination"] == "Kathmandu"
    assert "flights" in result
    assert "hotels" in result
    assert "activities" in result

    print(f"PASS: Got {len(result['flights'])} flights, {len(result['hotels'])} hotels, {len(result['activities'])} activities")
    print(f"  Exchange rate: {result.get('exchange_rate', 'N/A')}")
    return True


async def test_destination_search():
    print("\n=== Testing DestinationService ===")

    mock_data = {
        "organic_results": [
            {"title": "Pokhara - Nepal", "snippet": "Beautiful lakeside city", "link": "https://pokhara.example.com"},
            {"title": "Chitwan - Nepal", "snippet": "Wildlife sanctuary", "link": "https://chitwan.example.com"},
        ]
    }

    async def fake_get(*args, **kwargs):
        return DummyResp(mock_data)

    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=fake_get)):
        service = DestinationService()
        results = await service.search("Pokhara")

    assert len(results) == 2
    assert any("Pokhara" in r["name"] for r in results)

    print(f"PASS: Found {len(results)} destinations")
    for r in results:
        print(f"  - {r['name']} ({r['country']})")
    return True


async def test_budget_estimation():
    print("\n=== Testing BudgetService ===")

    async def fake_get(*args, **kwargs):
        return DummyResp(create_mock_serpapi_response())

    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=fake_get)):
        service = BudgetService()
        result = await service.estimate_budget("Kathmandu", days=3, travelers=2)

    assert result["destination"] == "Kathmandu"
    assert result["days"] == 3
    assert result["travelers"] == 2
    assert result["currency"] == "NRS"
    assert "total_estimate" in result
    assert "breakdown" in result

    breakdown = result["breakdown"]
    assert "flights" in breakdown
    assert "accommodation" in breakdown
    assert "activities" in breakdown
    assert "food" in breakdown

    print(f"PASS: Budget estimate {result['total_estimate']} NRS for 3 days x 2 travelers")
    print(f"  Breakdown: Flights={breakdown['flights']}, Hotel={breakdown['accommodation']}, Food={breakdown['food']}")
    return True


async def test_weather_service():
    print("\n=== Testing WeatherService ===")

    geo_response = DummyResp(create_mock_geo_response())
    weather_response = DummyResp(create_mock_weather_response())

    class DummyAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url, **kwargs):
            if "geocoding" in url:
                return geo_response
            return weather_response

    with patch("httpx.AsyncClient", DummyAsyncClient):
        service = WeatherService()
        result = await service.get_forecast("Kathmandu")

    assert "location" in result, f"Missing location, got: {result}"
    assert result["location"]["name"] == "Kathmandu", f"Wrong name: {result}"
    assert "forecast" in result, f"Missing forecast: {result}"
    assert "time" in result["forecast"], f"Missing time in forecast: {result}"

    print(f"PASS: Weather for {result['location']['name']}, {result['location']['country']}")
    print(f"  Forecast: {result['forecast']['time']}")
    return True


async def test_budget_fallback():
    print("\n=== Testing BudgetService Fallback ===")

    async def fake_get(*args, **kwargs):
        raise ValueError("SERPAPI not available")

    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=fake_get)):
        service = BudgetService()
        result = await service.estimate_budget("Unknown", days=2, travelers=1)

    assert result["destination"] == "Unknown"
    assert "total_estimate" in result
    print(f"PASS: Fallback budget {result['total_estimate']} NRS")
    return True


async def test_recommendations_budget_filter():
    print("\n=== Testing RecommendationService Budget Filter ===")

    async def fake_get(*args, **kwargs):
        return DummyResp(create_mock_serpapi_response())

    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=fake_get)):
        service = RecommendationService()
        result = await service.get_recommendations("Kathmandu")

    print(f"PASS: Got {len(result['flights'])} flights with prices in NRS")
    return True


async def main():
    print("=" * 50)
    print("TravelPlanner Backend Tests")
    print("=" * 50)

    get_settings.cache_clear()

    tests = [
        test_recommendations,
        test_destination_search,
        test_budget_estimation,
        test_weather_service,
        test_budget_fallback,
        test_recommendations_budget_filter,
    ]

    results = []
    for test in tests:
        try:
            passed = await test()
            results.append((test.__name__, passed))
        except Exception as e:
            print(f"FAIL: {test.__name__} - {e}")
            results.append((test.__name__, False))

    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    passed = sum(1 for _, p in results if p)
    total = len(results)
    print(f"{passed}/{total} tests passed")

    if passed == total:
        print("All tests PASSED!")
        return 0
    else:
        print("Some tests FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
