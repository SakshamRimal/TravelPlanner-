from fastapi import APIRouter

from app.services.destination import DestinationService

router = APIRouter(prefix="/destinations", tags=["Destinations"])


@router.get("/search")
async def search_destinations(query: str):
    service = DestinationService()
    return await service.search(query)
