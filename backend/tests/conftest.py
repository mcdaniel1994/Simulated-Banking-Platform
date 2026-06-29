from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from app.core.config import PROJECT_ROOT
from app.db.session import get_db
from app.main import app
from app.seed import seed_database
from fastapi.testclient import TestClient
from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

BACKEND_ROOT = Path(__file__).resolve().parents[1]


class DatabaseTestSettings(BaseSettings):
    """Test-only database configuration that cannot fall back to the development database."""

    # Shared API, service, and DB tests all load the same ignored root environment file.
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
        # Equality is a hard failure because mutation tests truncate and rebuild their target.
        if self.test_database_url.get_secret_value() == self.database_url.get_secret_value():
            raise ValueError("TEST_DATABASE_URL must differ from DATABASE_URL")
        return self


@pytest.fixture(scope="session")
def database_test_settings() -> DatabaseTestSettings:
    # Missing or unsafe test configuration is an error, never a reason to skip database tests.
    return DatabaseTestSettings()


@pytest.fixture(scope="session")
def test_engine(database_test_settings: DatabaseTestSettings) -> Generator[Engine, None, None]:
    # One shared pool keeps integration tests fast while every test controls its own data lifecycle.
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
    """Create isolated ORM sessions bound only to the validated test engine."""

    return sessionmaker(
        bind=test_engine,
        class_=Session,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest.fixture
def login_test_context(
    database_test_settings: DatabaseTestSettings,
    test_engine: Engine,
    test_session_factory: sessionmaker[Session],
) -> Generator[tuple[TestClient, sessionmaker[Session]], None, None]:
    """Provide the migrated, seeded SQL boundary used by authentication and role API tests."""

    # Recreate only test data while applying the same migration and seed used by development.
    alembic_config = Config(BACKEND_ROOT / "alembic.ini")
    alembic_config.attributes["database_url"] = (
        database_test_settings.test_database_url.get_secret_value()
    )
    command.upgrade(alembic_config, "head")
    with test_engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    transactions, transfers, sessions, audit_events, accounts, users
                RESTART IDENTITY CASCADE
                """
            )
        )

    seed_session = test_session_factory()
    try:
        # Production seed logic supplies real Argon2 users instead of authentication mocks.
        seed_database(seed_session)
    finally:
        seed_session.close()

    def override_get_db() -> Generator[Session, None, None]:
        # FastAPI receives request-scoped sessions bound only to simulated_banking_test.
        db = test_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app, base_url="https://testserver") as client:
            yield client, test_session_factory
    finally:
        # Restore global FastAPI state and remove every row created by the current test.
        app.dependency_overrides.clear()
        with test_engine.begin() as connection:
            connection.execute(
                text(
                    """
                    TRUNCATE TABLE
                        transactions, transfers, sessions, audit_events, accounts, users
                    RESTART IDENTITY CASCADE
                    """
                )
            )
