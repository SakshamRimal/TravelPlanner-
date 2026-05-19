from pydantic import BaseModel, Field


class ItineraryDay(BaseModel):
    date: str
    title: str
    morning: str = Field(description="Morning activity with time, location and details")
    late_morning: str = Field(description="Late morning activity with time, location and details")
    afternoon: str = Field(description="Afternoon activity with time, location and details")
    late_afternoon: str = Field(description="Late afternoon activity with time, location and details")
    evening: str = Field(description="Evening activity with time, location and details")


class ItineraryGenerationRequest(BaseModel):
    origin: str
    destination: str
    budget: float | None = None
    travelers: int = 1
    start_date: str
    end_date: str
    interests: list[str] = Field(default_factory=list)
    transport: str | None = None
    accommodation: str | None = None
    additional_notes: str | None = None


class ItineraryGenerationResponse(BaseModel):
    summary: str
    days: list[ItineraryDay]
    tips: list[str]
    estimated_total: float | None = None
