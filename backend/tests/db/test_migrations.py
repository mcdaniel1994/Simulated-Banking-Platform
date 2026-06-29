from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect, text
from sqlalchemy.exc import IntegrityError

from tests.conftest import DatabaseTestSettings

BACKEND_ROOT = Path(__file__).resolve().parents[2]
APPLICATION_TABLES = {
    "accounts",
    "audit_events",
    "sessions",
    "transactions",
    "transfers",
    "users",
}


def build_test_alembic_config(database_test_settings: DatabaseTestSettings) -> Config:
    """Point Alembic at the isolated test URL without exposing it through runtime settings."""

    config = Config(BACKEND_ROOT / "alembic.ini")
    config.attributes["database_url"] = database_test_settings.test_database_url.get_secret_value()
    return config


def test_initial_migration_round_trip_and_balance_constraint(
    database_test_settings: DatabaseTestSettings,
    test_engine: Engine,
) -> None:
    alembic_config = build_test_alembic_config(database_test_settings)

    # Start from a known empty schema, then prove the migration creates every application table.
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
    inspector = inspect(test_engine)
    assert APPLICATION_TABLES <= set(inspector.get_table_names())
    assert {constraint["name"] for constraint in inspector.get_check_constraints("accounts")} == {
        "ck_accounts_balance_nonnegative"
    }

    # Inspect the live PostgreSQL schema, not just model metadata, for uniqueness and query indexes.
    assert {tuple(item["column_names"]) for item in inspector.get_unique_constraints("users")} == {
        ("email",)
    }
    assert {
        tuple(item["column_names"]) for item in inspector.get_unique_constraints("accounts")
    } == {("account_number",)}
    assert {
        (tuple(item["column_names"]), item["unique"]) for item in inspector.get_indexes("sessions")
    } == {
        (("token_hash",), True),
        (("user_id",), False),
    }
    assert {tuple(item["column_names"]) for item in inspector.get_indexes("transactions")} == {
        ("account_id", "created_at")
    }

    # A valid owner row isolates the balance check from unrelated foreign-key failures.
    with test_engine.begin() as connection:
        user_id = connection.scalar(
            text(
                """
                INSERT INTO users (
                    email, password_hash, first_name, last_name, role
                )
                VALUES (
                    'migration-test@example.test', 'hash', 'Migration', 'Test', 'CUSTOMER'
                )
                RETURNING id
                """
            )
        )

    with pytest.raises(IntegrityError):
        with test_engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO accounts (
                        user_id, account_number, account_type, balance, status
                    )
                    VALUES (
                        :user_id, 'migration-negative', 'CHECKING', -0.01, 'ACTIVE'
                    )
                    """
                ),
                {"user_id": user_id},
            )

    # Downgrade must remove the schema cleanly; upgrade restores it for the final verified state.
    command.downgrade(alembic_config, "base")
    assert APPLICATION_TABLES.isdisjoint(inspect(test_engine).get_table_names())
    command.upgrade(alembic_config, "head")
    assert APPLICATION_TABLES <= set(inspect(test_engine).get_table_names())
