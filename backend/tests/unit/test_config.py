from pathlib import Path

import pytest
from app.core.config import Settings, get_settings
from pydantic import ValidationError


def test_settings_load_from_dotenv_file(tmp_path: Path) -> None:
    # Build an isolated environment file so the test never reads a developer or production secret.
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/test_bank",
                "SESSION_SECRET=test-session-secret",
                "SESSION_IDLE_MINUTES=15",
                "SESSION_ABSOLUTE_HOURS=8",
                "COOKIE_DOMAIN=",
                'CORS_ORIGINS=["http://localhost:5173"]',
                "CSRF_COOKIE_NAME=test_csrf",
                "ENV=test",
            ]
        ),
        encoding="utf-8",
    )

    # Override the configured local file to prove Pydantic can parse every supported value.
    settings = Settings(_env_file=env_file)

    assert settings.database_url.get_secret_value().endswith("/test_bank")
    assert settings.session_secret.get_secret_value() == "test-session-secret"
    assert settings.session_idle_minutes == 15
    assert settings.session_absolute_hours == 8
    assert settings.cookie_domain is None
    assert settings.cors_origins == ["http://localhost:5173"]
    assert settings.csrf_cookie_name == "test_csrf"
    assert settings.env == "test"


def test_settings_use_decided_session_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    # Supply only required values so this test isolates the defaults recorded by D1.
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost/test_bank")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret")

    settings = Settings(_env_file=None)

    assert settings.session_idle_minutes == 30
    assert settings.session_absolute_hours == 12
    assert settings.cors_origins == []
    assert settings.env == "development"


def test_settings_require_database_url_and_session_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Remove inherited values so the test proves both security-sensitive fields are mandatory.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SESSION_SECRET", raising=False)

    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None)

    missing_fields = {item["loc"][0] for item in error.value.errors()}
    assert missing_fields == {"database_url", "session_secret"}


def test_sensitive_settings_are_redacted(monkeypatch: pytest.MonkeyPatch) -> None:
    # SecretStr should prevent accidental disclosure through normal string and repr output.
    database_url = "postgresql+psycopg://user:secret-password@localhost/test_bank"
    session_secret = "secret-that-must-not-appear"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("SESSION_SECRET", session_secret)

    settings = Settings(_env_file=None)

    assert database_url not in str(settings)
    assert database_url not in repr(settings)
    assert session_secret not in str(settings)
    assert session_secret not in repr(settings)


def test_get_settings_reuses_one_cached_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    # Clear shared state so this test controls the values used to construct the cached instance.
    get_settings.cache_clear()
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost/test_bank")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret")

    try:
        first_settings = get_settings()
        second_settings = get_settings()

        # Reusing one object keeps configuration consistent throughout the process lifetime.
        assert first_settings is second_settings
    finally:
        # Prevent this test's cached environment values from leaking into later tests.
        get_settings.cache_clear()
