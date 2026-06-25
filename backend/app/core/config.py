"""Application configuration."""

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven backend settings."""

    app_name: str = "InvestGuide Backend"
    app_version: str = "0.1.0-alpha"
    environment: str = "development"
    debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/investguide",
        validation_alias="DATABASE_URL",
    )

    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        validation_alias="CORS_ORIGINS",
    )

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Any:
        """Allow CORS origins as a JSON list or comma-separated string."""
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            if value.startswith("["):
                return value
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()

