"""Application configuration loaded from environment variables.

Uses pydantic-settings to read values from a .env file at the project root.
"""

from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """Central configuration for the Gujarati Phonetics server."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Gemini ---
    GEMINI_API_KEY: str = ""

    # --- Server ---
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # --- Dictionary API ---
    DICTIONARY_API_BASE: str = "https://api.dictionaryapi.dev/api/v2/entries/en"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()
