from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve the repository root so local commands load the same .env file from any directory.
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Typed configuration loaded from environment variables or the local root .env file."""

    # Ignore unrelated environment values while keeping variable names case-insensitive.
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database and session secrets are required because safe defaults do not exist.
    database_url: SecretStr = Field(min_length=1)
    session_secret: SecretStr = Field(min_length=1)

    # These defaults record the session-lifetime decision made in D1.
    session_idle_minutes: int = Field(default=30, gt=0)
    session_absolute_hours: int = Field(default=12, gt=0)

    # Cookie, browser, CSRF, and environment settings support later authentication phases.
    cookie_domain: str | None = None
    cors_origins: list[str] = Field(default_factory=list)
    csrf_cookie_name: str = Field(default="csrf_token", min_length=1)
    env: Literal["development", "test", "production"] = "development"

    @field_validator("cookie_domain", mode="before")
    @classmethod
    def normalize_empty_cookie_domain(cls, value: object) -> object:
        """Treat a blank local cookie domain as an omitted Domain attribute."""

        return None if value == "" else value


@lru_cache
def get_settings() -> Settings:
    """Build settings once per process so every dependency sees the same configuration."""

    return Settings()
