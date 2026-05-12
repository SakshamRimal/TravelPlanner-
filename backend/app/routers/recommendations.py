from fastapi import APIRouter

from app.schemas.recommendation import RecommendationResponse
from app.services.recommendations import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{destination}", response_model=RecommendationResponse)
async def recommendations(destination: str, origin: str = "KTM", budget: float | None = None):
    service = RecommendationService()
    data = await service.get_recommendations(destination, origin=origin, budget=budget)
    return RecommendationResponse(**data)
