from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="EKA_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Enterprise Knowledge and Analytics Agent"
    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    debug: bool = False
    request_timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_request_bytes: int = Field(default=1_048_576, ge=1_024)


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings instance for the current process."""

    return Settings()
