import os

from app.config import get_settings


def test_get_settings_reads_environment_variables(monkeypatch) -> None:
    monkeypatch.setenv("APP_NAME", "My Todo App")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.app_name == "My Todo App"
    assert settings.debug is True
    assert settings.log_level == "DEBUG"

    get_settings.cache_clear()
    os.environ.pop("APP_NAME", None)
    os.environ.pop("DEBUG", None)
    os.environ.pop("LOG_LEVEL", None)
