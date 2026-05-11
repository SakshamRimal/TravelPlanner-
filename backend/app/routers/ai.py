from fastapi import APIRouter

from app.schemas.ai import ItineraryGenerationRequest, ItineraryGenerationResponse
from app.services.ai import AIService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/itinerary", response_model=ItineraryGenerationResponse)
async def generate_itinerary(payload: ItineraryGenerationRequest):
    service = AIService()
    response = await service.generate_itinerary(payload.model_dump())
    return response
