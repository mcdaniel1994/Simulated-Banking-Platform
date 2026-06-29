import pytest
from app.db import session as db_session
from pydantic import SecretStr, ValidationError
from sqlalchemy import Engine, make_url, text
from sqlalchemy.orm import Session, sessionmaker

from tests.db.conftest import DatabaseTestSettings


def test_database_configuration_requires_a_test_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)

    with pytest.raises(ValidationError):
        DatabaseTestSettings(
            database_url=SecretStr(
                "postgresql+psycopg://banking_user:password@localhost:5433/simulated_banking_dev"
            ),
            _env_file=None,
        )


def test_database_configuration_rejects_the_development_url_for_tests() -> None:
    shared_url = "postgresql+psycopg://banking_user:password@localhost:5433/simulated_banking_dev"

    with pytest.raises(ValidationError, match="must differ"):
        DatabaseTestSettings(
            database_url=SecretStr(shared_url),
            test_database_url=SecretStr(shared_url),
            _env_file=None,
        )


def test_database_urls_target_the_expected_isolated_databases(
    database_test_settings: DatabaseTestSettings,
) -> None:
    development_url = make_url(database_test_settings.database_url.get_secret_value())
    test_url = make_url(database_test_settings.test_database_url.get_secret_value())

    assert development_url.drivername == "postgresql+psycopg"
    assert development_url.database == "simulated_banking_dev"
    assert test_url.drivername == "postgresql+psycopg"
    assert test_url.database == "simulated_banking_test"
    assert development_url != test_url


def test_get_db_connects_to_test_database_and_closes_session(
    monkeypatch: pytest.MonkeyPatch,
    test_engine: Engine,
    test_session_factory: sessionmaker[Session],
) -> None:
    # Route the application dependency to the isolated test factory for this integration test.
    monkeypatch.setattr(db_session, "SessionLocal", test_session_factory)
    dependency = db_session.get_db()
    session = next(dependency)

    assert session.scalar(text("SELECT 1")) == 1
    assert session.scalar(text("SELECT current_database()")) == "simulated_banking_test"

    with pytest.raises(StopIteration):
        next(dependency)

    assert test_engine.pool.checkedout() == 0


def test_get_db_rolls_back_when_request_work_fails(
    monkeypatch: pytest.MonkeyPatch,
    test_engine: Engine,
    test_session_factory: sessionmaker[Session],
) -> None:
    monkeypatch.setattr(db_session, "SessionLocal", test_session_factory)

    # PostgreSQL DDL is transactional, so this table must disappear when the dependency rolls back.
    with test_engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS phase4_rollback_probe"))

    dependency = db_session.get_db()
    session = next(dependency)
    session.execute(text("CREATE TABLE phase4_rollback_probe (id integer)"))

    with pytest.raises(RuntimeError, match="forced request failure"):
        dependency.throw(RuntimeError("forced request failure"))

    with test_engine.connect() as connection:
        table_name = connection.scalar(text("SELECT to_regclass('phase4_rollback_probe')"))

    assert table_name is None
    assert test_engine.pool.checkedout() == 0
