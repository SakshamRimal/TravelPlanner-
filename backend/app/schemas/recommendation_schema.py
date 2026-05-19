from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    destination: str | None = None
    origin: str | None = None
    budget: float | None = None
    budget_nrs: float | None = None
    currency: str = "NRS"
    exchange_rate: float
    flights: list[dict]
    hotels: list[dict]
    activities: list[dict]
