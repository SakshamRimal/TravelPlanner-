from fastapi import APIRouter, Depends

from app.services.auth_service import get_current_user
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("")
async def weather(
    destination: str,
    current_user=Depends(get_current_user),
):
    service = WeatherService()
    return await service.get_forecast(destination)
