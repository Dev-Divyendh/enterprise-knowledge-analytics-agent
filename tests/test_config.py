from pathlib import Path

import pytest
from pydantic import ValidationError

from enterprise_knowledge_analytics_agent.config import Settings, get_settings


def test_settings_use_safe_defaults(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("EKA_ENVIRONMENT", raising=False)
    monkeypatch.delenv("EKA_DEBUG", raising=False)
    monkeypatch.delenv("EKA_REQUEST_TIMEOUT_SECONDS", raising=False)

    settings = Settings()

    assert settings.environment == "development"
    assert settings.debug is False
    assert settings.request_timeout_seconds == 30
    assert settings.max_request_bytes == 1_048_576


def test_settings_parse_environment_variables(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("EKA_ENVIRONMENT", "test")
    monkeypatch.setenv("EKA_DEBUG", "true")
    monkeypatch.setenv("EKA_REQUEST_TIMEOUT_SECONDS", "45")

    settings = Settings()

    assert settings.environment == "test"
    assert settings.debug is True
    assert settings.request_timeout_seconds == 45
    assert isinstance(settings.request_timeout_seconds, int)


def test_settings_reject_invalid_timeout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("EKA_REQUEST_TIMEOUT_SECONDS", "0")

    with pytest.raises(ValidationError):
        Settings()


def test_get_settings_returns_cached_instance(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert first is second

    get_settings.cache_clear()
