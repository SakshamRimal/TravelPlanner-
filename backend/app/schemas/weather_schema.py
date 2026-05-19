from pydantic import BaseModel


class WeatherResponse(BaseModel):
    location: dict
    forecast: dict
