from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.db.base import Base, load_models
from app.models import (
    Account,
    AccountStatus,
    AccountType,
    AuditEvent,
    Session,
    Transaction,
    TransactionType,
    Transfer,
    TransferStatus,
    User,
    UserRole,
)
from sqlalchemy import CheckConstraint, DateTime, Enum, Numeric
from sqlalchemy.orm import configure_mappers


def test_metadata_registers_all_phase5_tables() -> None:
    load_models()

    # Exact table and column sets catch accidental schema drift before migration generation.
    assert set(Base.metadata.tables) == {
        "users",
        "sessions",
        "accounts",
        "transactions",
        "transfers",
        "audit_events",
    }

    expected_columns = {
        "users": {
            "id",
            "email",
            "password_hash",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        },
        "sessions": {
            "id",
            "user_id",
            "token_hash",
            "created_at",
            "last_used_at",
            "expires_at",
            "revoked_at",
            "user_agent",
            "ip",
        },
        "accounts": {
            "id",
            "user_id",
            "account_number",
            "account_type",
            "balance",
            "status",
            "created_at",
            "updated_at",
        },
        "transactions": {
            "id",
            "account_id",
            "transaction_type",
            "amount",
            "description",
            "balance_after",
            "reference_id",
            "created_at",
        },
        "transfers": {
            "id",
            "source_account_id",
            "destination_account_id",
            "amount",
            "status",
            "created_at",
        },
        "audit_events": {
            "id",
            "actor_user_id",
            "event_type",
            "entity_type",
            "entity_id",
            "metadata",
            "created_at",
        },
    }

    for table_name, column_names in expected_columns.items():
        assert set(Base.metadata.tables[table_name].c.keys()) == column_names


def test_money_and_timestamp_columns_use_required_types() -> None:
    # Precision and timezone flags are banking invariants, not incidental implementation details.
    for table_name, column_name in (
        ("accounts", "balance"),
        ("transactions", "amount"),
        ("transactions", "balance_after"),
        ("transfers", "amount"),
    ):
        column_type = Base.metadata.tables[table_name].c[column_name].type
        assert isinstance(column_type, Numeric)
        assert column_type.precision == 14
        assert column_type.scale == 2

    for table_name, column_name in (
        ("users", "created_at"),
        ("users", "updated_at"),
        ("sessions", "created_at"),
        ("sessions", "last_used_at"),
        ("sessions", "expires_at"),
        ("sessions", "revoked_at"),
        ("accounts", "created_at"),
        ("accounts", "updated_at"),
        ("transactions", "created_at"),
        ("transfers", "created_at"),
        ("audit_events", "created_at"),
    ):
        column_type = Base.metadata.tables[table_name].c[column_name].type
        assert isinstance(column_type, DateTime)
        assert column_type.timezone is True


def test_enums_have_stable_database_names_and_values() -> None:
    # Stable names matter because Alembic will create these as PostgreSQL enum types in Phase 6.
    expected_enums = {
        ("users", "role"): ("user_role", {"CUSTOMER", "ADMIN"}),
        ("accounts", "account_type"): ("account_type", {"CHECKING", "SAVINGS"}),
        ("accounts", "status"): ("account_status", {"ACTIVE", "FROZEN", "CLOSED"}),
        (
            "transactions",
            "transaction_type",
        ): ("transaction_type", {"DEPOSIT", "WITHDRAWAL", "TRANSFER_IN", "TRANSFER_OUT"}),
        ("transfers", "status"): ("transfer_status", {"COMPLETED", "FAILED"}),
    }

    for (table_name, column_name), (enum_name, values) in expected_enums.items():
        column_type = Base.metadata.tables[table_name].c[column_name].type
        assert isinstance(column_type, Enum)
        assert column_type.name == enum_name
        assert set(column_type.enums) == values


def test_required_constraints_indexes_and_foreign_keys_are_registered() -> None:
    # These metadata assertions cover the integrity and query paths named directly in the spec.
    accounts = Base.metadata.tables["accounts"]
    sessions = Base.metadata.tables["sessions"]
    transactions = Base.metadata.tables["transactions"]

    account_checks = {
        constraint.name
        for constraint in accounts.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert "ck_accounts_balance_nonnegative" in account_checks

    assert {index.name for index in sessions.indexes} == {
        "ix_sessions_token_hash",
        "ix_sessions_user_id",
    }
    assert {index.name for index in accounts.indexes} == {"ix_accounts_user_id"}
    assert {index.name for index in transactions.indexes} == {
        "ix_transactions_account_id_created_at"
    }
    assert Base.metadata.tables["users"].c.email.unique is True
    assert sessions.c.token_hash.unique is True
    assert accounts.c.account_number.unique is True

    foreign_key_targets = {
        foreign_key.target_fullname
        for table in Base.metadata.tables.values()
        for foreign_key in table.foreign_keys
    }
    assert foreign_key_targets == {
        "users.id",
        "accounts.id",
        "transfers.id",
    }


def test_models_construct_with_relationships_and_exact_decimal_values() -> None:
    # In-memory construction verifies mapper wiring without creating Phase 6 database tables early.
    configure_mappers()
    now = datetime.now(UTC)
    user = User(
        email="customer@example.test",
        password_hash="argon2id-hash",
        first_name="Test",
        last_name="Customer",
        role=UserRole.CUSTOMER,
    )
    checking = Account(
        user=user,
        account_number="1000000001",
        account_type=AccountType.CHECKING,
        balance=Decimal("125.50"),
        status=AccountStatus.ACTIVE,
    )
    savings = Account(
        user=user,
        account_number="1000000002",
        account_type=AccountType.SAVINGS,
        balance=Decimal("50.00"),
        status=AccountStatus.ACTIVE,
    )
    transfer = Transfer(
        source_account=checking,
        destination_account=savings,
        amount=Decimal("25.00"),
        status=TransferStatus.COMPLETED,
    )
    transaction = Transaction(
        account=checking,
        transfer=transfer,
        transaction_type=TransactionType.TRANSFER_OUT,
        amount=Decimal("25.00"),
        description="Transfer to savings",
        balance_after=Decimal("100.50"),
    )
    session = Session(
        user=user,
        token_hash="a" * 64,
        last_used_at=now,
        expires_at=now + timedelta(hours=12),
    )
    audit_event = AuditEvent(
        actor=user,
        event_type="customer_transfer",
        entity_type="transfer",
        entity_id="1",
        event_metadata={"result": "completed"},
    )

    assert checking.balance == Decimal("125.50")
    assert transfer in checking.outgoing_transfers
    assert transfer in savings.incoming_transfers
    assert transaction in transfer.transactions
    assert session in user.sessions
    assert audit_event in user.audit_events
