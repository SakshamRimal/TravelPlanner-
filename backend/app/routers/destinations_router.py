from fastapi import APIRouter, Depends

from app.services.auth_service import get_current_user
from app.services.destination_service_service import DestinationService

router = APIRouter(prefix="/destinations", tags=["Destinations"])


@router.get("/search")
async def search_destinations(
    query: str,
    current_user=Depends(get_current_user),
):
    service = DestinationService()
    return await service.search(query)
