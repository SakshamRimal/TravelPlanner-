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
        case_sensitive=False,
    )

    # Database - no defaults, must be set in .env
    database_url: str | None = None
    postgres_db: str | None = None
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Auth - no defaults, must be set in .env
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    access_token_expires_minutes: int = 30
    refresh_token_expires_days: int = 7

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]

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
                raise ValueError(
                    "Database URL is not configured. Set DATABASE_URL or individual POSTGRES_* environment variables."
                )
        return self

    cors_origins: str = ""

    @model_validator(mode="after")
    def _parse_allowed_origins(self):
        if self.cors_origins:
            self.allowed_origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
