from fastapi import APIRouter, Depends

from app.schemas.ai_schema import ItineraryGenerationRequest, ItineraryGenerationResponse
from app.services.auth_service import get_current_user
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/itinerary", response_model=ItineraryGenerationResponse)
async def generate_itinerary(
    payload: ItineraryGenerationRequest,
    current_user=Depends(get_current_user),
):
    service = AIService()
    response = await service.generate_itinerary(payload.model_dump())
    return response
