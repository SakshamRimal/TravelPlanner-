from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expires_minutes: int = 30
    refresh_token_expires_days: int = 7

    llm_provider: str = "gemini"
    gemini_api_key: str | None = None
    ai_temperature: float = 0.3

    google_maps_api_key: str | None = None
    open_meteo_base_url: str | None = None
    open_meteo_geo_base_url: str | None = None
    liteapi_hotel_base_url: str | None = None
    liteapi_api_key: str | None = None
    liteapi_country_code: str = "NP"


@lru_cache
def get_settings() -> Settings:
    return Settings()
