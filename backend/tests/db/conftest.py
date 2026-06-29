from collections.abc import Generator

import pytest
from app.core.config import PROJECT_ROOT
from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


class DatabaseTestSettings(BaseSettings):
    """Test-only database configuration that cannot fall back to the development database."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: SecretStr
    test_database_url: SecretStr

    @model_validator(mode="after")
    def require_isolated_test_database(self) -> "DatabaseTestSettings":
        if self.test_database_url.get_secret_value() == self.database_url.get_secret_value():
            raise ValueError("TEST_DATABASE_URL must differ from DATABASE_URL")
        return self


@pytest.fixture(scope="session")
def database_test_settings() -> DatabaseTestSettings:
    # Missing or unsafe test configuration is an error, never a reason to skip database tests.
    return DatabaseTestSettings()


@pytest.fixture(scope="session")
def test_engine(database_test_settings: DatabaseTestSettings) -> Generator[Engine, None, None]:
    engine = create_engine(
        database_test_settings.test_database_url.get_secret_value(),
        pool_pre_ping=True,
    )
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def test_session_factory(test_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=test_engine,
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )
