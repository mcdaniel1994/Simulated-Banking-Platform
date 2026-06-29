from collections.abc import Generator
from decimal import Decimal
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from app.core.security import verify_password
from app.models import Account, Transaction, TransactionType, Transfer, User, UserRole
from app.seed import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    CUSTOMER_PASSWORD,
    DEMO_USERS,
    print_demo_credentials,
    seed_database,
)
from sqlalchemy import Engine, func, select, text
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

from tests.db.conftest import DatabaseTestSettings

BACKEND_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def empty_seed_session(
    database_test_settings: DatabaseTestSettings,
    test_engine: Engine,
    test_session_factory: sessionmaker[DatabaseSession],
) -> Generator[DatabaseSession, None, None]:
    # Apply the real migration to the isolated test database before managing seed rows.
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

    session = test_session_factory()
    try:
        yield session
    finally:
        session.close()
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


def _row_counts(db: DatabaseSession) -> tuple[int, int, int, int]:
    return (
        db.scalar(select(func.count()).select_from(User)) or 0,
        db.scalar(select(func.count()).select_from(Account)) or 0,
        db.scalar(select(func.count()).select_from(Transfer)) or 0,
        db.scalar(select(func.count()).select_from(Transaction)) or 0,
    )


def test_seed_is_idempotent_and_demo_credentials_verify(
    empty_seed_session: DatabaseSession,
) -> None:
    seed_database(empty_seed_session)
    first_counts = _row_counts(empty_seed_session)
    first_hashes = {
        user.email: user.password_hash for user in empty_seed_session.scalars(select(User)).all()
    }

    seed_database(empty_seed_session)
    second_counts = _row_counts(empty_seed_session)
    second_hashes = {
        user.email: user.password_hash for user in empty_seed_session.scalars(select(User)).all()
    }

    # Rerunning preserves both row counts and already-valid randomly salted password hashes.
    assert first_counts == second_counts == (3, 4, 2, 12)
    assert first_hashes == second_hashes

    admin = empty_seed_session.scalar(select(User).where(User.email == ADMIN_EMAIL))
    assert admin is not None
    assert admin.role is UserRole.ADMIN
    assert verify_password(ADMIN_PASSWORD, admin.password_hash)

    for customer_spec in DEMO_USERS[1:]:
        customer = empty_seed_session.scalar(select(User).where(User.email == customer_spec.email))
        assert customer is not None
        assert customer.role is UserRole.CUSTOMER
        assert verify_password(CUSTOMER_PASSWORD, customer.password_hash)
        assert len(customer.accounts) == 2


def test_seeded_accounts_reconcile_and_transfers_have_two_legs(
    empty_seed_session: DatabaseSession,
) -> None:
    seed_database(empty_seed_session)

    positive_types = {TransactionType.DEPOSIT, TransactionType.TRANSFER_IN}
    for account in empty_seed_session.scalars(select(Account)).all():
        signed_total = sum(
            (
                transaction.amount
                if transaction.transaction_type in positive_types
                else -transaction.amount
            )
            for transaction in account.transactions
        )
        assert signed_total == account.balance
        assert account.balance > Decimal("0.00")

    for transfer in empty_seed_session.scalars(select(Transfer)).all():
        assert len(transfer.transactions) == 2
        assert {item.transaction_type for item in transfer.transactions} == {
            TransactionType.TRANSFER_OUT,
            TransactionType.TRANSFER_IN,
        }
        assert {item.reference_id for item in transfer.transactions} == {transfer.id}


def test_seed_command_prints_only_public_demo_credentials(
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_demo_credentials()
    output = capsys.readouterr().out

    assert ADMIN_EMAIL in output
    assert ADMIN_PASSWORD in output
    assert DEMO_USERS[1].email in output
    assert CUSTOMER_PASSWORD in output
    assert "$argon2" not in output
