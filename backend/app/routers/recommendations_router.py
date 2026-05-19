from fastapi import APIRouter, Depends

from app.schemas.recommendation_schema import RecommendationResponse
from app.services.auth_service import get_current_user
from app.services.recommendations_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{destination}", response_model=RecommendationResponse)
async def recommendations(
    destination: str,
    origin: str = "KTM",
    budget: float | None = None,
    current_user=Depends(get_current_user),
):
    service = RecommendationService()
    data = await service.get_recommendations(destination, origin=origin, budget=budget)
    return RecommendationResponse(**data)
