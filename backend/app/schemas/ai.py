from pydantic import BaseModel


class ItineraryGenerationRequest(BaseModel):
    destination: str
    budget: float | None = None
    travelers: int = 1
    start_date: str
    end_date: str
    interests: list[str] = []
    transport: str | None = None
    accommodation: str | None = None
    additional_notes: str | None = None


class ItineraryGenerationResponse(BaseModel):
    summary: str
    days: list[dict]
    tips: list[str]
    estimated_total: float | None = None
