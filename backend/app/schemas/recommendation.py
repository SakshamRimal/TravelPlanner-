from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    flights: list[dict]
    hotels: list[dict]
    activities: list[dict]
