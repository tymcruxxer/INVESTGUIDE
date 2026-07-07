"""Application configuration."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"

class Settings(BaseSettings):
    """Environment-driven backend settings."""

    app_name: str = "InvestGuide Backend"
    app_version: str = "0.1.0-alpha"
    environment: str = Field(default="development", validation_alias=AliasChoices("APP_ENV", "ENVIRONMENT"))
    debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg://investguide_user:investguide_password@localhost:5432/investguide",
        validation_alias="DATABASE_URL",
    )

    cors_origins: Annotated[list[str], NoDecode] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
        validation_alias="CORS_ORIGINS",
    )

    log_level: str = "INFO"
    ingestion_mode: Literal["DRY_RUN", "WRITE"] = Field(
        default="DRY_RUN",
        validation_alias="INGESTION_MODE",
    )
    jwt_secret_key: str = Field(
        default="investguide-development-secret-change-me",
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
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
                return json.loads(value)
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("ingestion_mode", mode="before")
    @classmethod
    def normalize_ingestion_mode(cls, value: Any) -> Any:
        """Allow operators to provide ingestion mode case-insensitively."""
        if isinstance(value, str):
            return value.strip().upper()
        return value



def get_masked_database_url(database_url: str) -> str:
    """Return a database URL with credentials masked for diagnostics."""
    if "://" not in database_url or "@" not in database_url:
        return database_url
    scheme, rest = database_url.split("://", 1)
    _, host_part = rest.rsplit("@", 1)
    return f"{scheme}://***:***@{host_part}"
@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()

