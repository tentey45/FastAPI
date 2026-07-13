import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    app_name: str = "Todo App"
    debug: bool = False
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings(
        app_name=os.getenv("APP_NAME", "Todo App"),
        debug=os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"},
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
