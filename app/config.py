from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

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
        app_name="Todo App",
        debug=True,
        log_level="INFO",
    )
