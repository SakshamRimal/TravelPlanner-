from typing import Any

from app.core.config import get_settings
from app.services.currency_service import get_currency_service
from app.services.recommendations_service import RecommendationService


class BudgetService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.recommendations = RecommendationService()

    async def estimate_budget(self, destination: str, days: int, travelers: int = 1, origin: str = "KTM") -> dict[str, Any]:
        try:
            data = await self.recommendations.get_recommendations(destination, origin=origin)
        except ValueError:
            return await self._fallback_budget(days, travelers, destination)

        currency_service = await get_currency_service()
        current_rate = await currency_service.get_usd_to_nrs_rate()

        flights_cost = 0
        if data.get("flights"):
            prices = [f.get("price", 0) for f in data["flights"] if f.get("price")]
            if prices:
                flights_cost = min(prices) * travelers
            else:
                # Default flight cost for domestic Nepal flights (KTM to Pokhara, etc.)
                # Domestic flights in Nepal range from NPR 5,000-15,000
                flights_cost = 8000 * travelers

        hotel_cost = 0
        if data.get("hotels"):
            prices = [h.get("price_per_night", 0) for h in data["hotels"] if h.get("price_per_night")]
            if prices:
                hotel_cost = min(prices) * days * travelers

        activity_cost = 800 * days * travelers
        food_cost = 1000 * days * travelers
        transport_cost = 500 * days * travelers

        return {
            "destination": destination,
            "days": days,
            "travelers": travelers,
            "currency": "NRS",
            "exchange_rate": current_rate,
            "total_estimate": round(flights_cost + hotel_cost + activity_cost + food_cost + transport_cost + 2000, 0),
            "breakdown": {
                "flights": flights_cost,
                "accommodation": hotel_cost,
                "activities": activity_cost,
                "food": food_cost,
                "local_transport": transport_cost,
                "miscellaneous": 2000,
            },
        }

    async def _fallback_budget(self, days: int, travelers: int, destination: str = "Nepal") -> dict[str, Any]:
        currency_service = await get_currency_service()
        current_rate = await currency_service.get_usd_to_nrs_rate()

        base_cost = 5000 * days * travelers
        return {
            "destination": destination,
            "days": days,
            "travelers": travelers,
            "currency": "NRS",
            "exchange_rate": current_rate,
            "total_estimate": round(base_cost, 0),
            "breakdown": {
                "flights": 0,
                "accommodation": round(base_cost * 0.4, 0),
                "activities": round(base_cost * 0.2, 0),
                "food": round(base_cost * 0.25, 0),
                "local_transport": round(base_cost * 0.1, 0),
                "miscellaneous": 1000,
            },
        }