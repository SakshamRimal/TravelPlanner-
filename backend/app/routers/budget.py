from fastapi import APIRouter

from app.services.budget import BudgetService

router = APIRouter(prefix="/budget", tags=["Budget"])


@router.get("/estimate")
async def estimate_budget(destination: str, days: int, travelers: int = 1):
    service = BudgetService()
    return await service.estimate_budget(destination, days, travelers)
