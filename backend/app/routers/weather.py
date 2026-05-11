from fastapi import APIRouter

from app.services.weather import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("")
async def weather(destination: str):
    service = WeatherService()
    return await service.get_forecast(destination)
