from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_env_file_path() -> Path:
    backend_dir = Path(__file__).parent.parent.parent
    project_root = backend_dir.parent

    if (project_root / ".env").exists():
        return project_root / ".env"
    if (Path.cwd() / ".env").exists():
        return Path.cwd() / ".env"
    return project_root / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_get_env_file_path()),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str | None = None
    postgres_db: str | None = "travelplanner"
    postgres_user: str | None = "travelplanner"
    postgres_password: str | None = "travelplanner"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    jwt_secret: str = "dev-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expires_minutes: int = 30
    refresh_token_expires_days: int = 7

    llm_provider: str = "gemini"
    gemini_api_key: str | None = None
    ai_temperature: float = 0.3

    open_meteo_base_url: str | None = None
    open_meteo_geo_base_url: str | None = None

    serpapi_api_key: str | None = None
    aviationstack_api_key: str | None = None
    exchangerate_api_key: str | None = None

    currency: str = "NRS"
    usd_to_nrs_rate: float = 135.0

    @model_validator(mode="after")
    def _build_database_url(self):
        if not self.database_url:
            if self.postgres_user and self.postgres_password and self.postgres_db:
                self.database_url = (
                    f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:"
                    f"{self.postgres_port}/{self.postgres_db}"
                )
            else:
                self.database_url = ""
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
