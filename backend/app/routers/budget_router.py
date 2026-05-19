from fastapi import APIRouter, Depends

from app.services.auth_service import get_current_user
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budget", tags=["Budget"])


@router.get("/estimate")
async def estimate_budget(
    destination: str,
    days: int,
    travelers: int = 1,
    current_user=Depends(get_current_user),
):
    service = BudgetService()
    return await service.estimate_budget(destination, days, travelers)
