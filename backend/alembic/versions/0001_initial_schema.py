"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-29 16:53:22.807377
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# Revision identifiers used by Alembic to order the migration graph.
revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply this schema revision."""

    # Users are created first because accounts, sessions, and audit actors depend on them.
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("role", sa.Enum("CUSTOMER", "ADMIN", name="user_role"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # Accounts enforce exact money storage and the database-level no-overdraft backstop.
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("account_number", sa.String(length=32), nullable=False),
        sa.Column(
            "account_type", sa.Enum("CHECKING", "SAVINGS", name="account_type"), nullable=False
        ),
        sa.Column(
            "balance",
            sa.Numeric(precision=14, scale=2),
            server_default=sa.text("0.00"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "FROZEN", "CLOSED", name="account_status"),
            server_default=sa.text("'ACTIVE'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("balance >= 0", name="ck_accounts_balance_nonnegative"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_number"),
    )
    op.create_index(op.f("ix_accounts_user_id"), "accounts", ["user_id"], unique=False)

    # Audit actors may become NULL, preserving immutable event history if a user is removed.
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=255), nullable=False),
        sa.Column("metadata", sa.JSON(), server_default=sa.text("'{}'::json"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Server-side sessions index both token lookup and user-wide revocation paths.
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("ip", sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sessions_token_hash"), "sessions", ["token_hash"], unique=True)
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)

    # Transfers are parents of their two transaction legs and reference both affected accounts.
    op.create_table(
        "transfers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_account_id", sa.Integer(), nullable=False),
        sa.Column("destination_account_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("status", sa.Enum("COMPLETED", "FAILED", name="transfer_status"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["destination_account_id"],
            ["accounts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_account_id"],
            ["accounts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Append-only transaction rows retain balance snapshots and optional transfer linkage.
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column(
            "transaction_type",
            sa.Enum(
                "DEPOSIT", "WITHDRAWAL", "TRANSFER_IN", "TRANSFER_OUT", name="transaction_type"
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("balance_after", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["reference_id"],
            ["transfers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_transactions_account_id_created_at",
        "transactions",
        ["account_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Reverse this schema revision."""

    # Remove dependent tables and indexes before the parent rows they reference.
    op.drop_index("ix_transactions_account_id_created_at", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("transfers")
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_token_hash"), table_name="sessions")
    op.drop_table("sessions")
    op.drop_table("audit_events")
    op.drop_index(op.f("ix_accounts_user_id"), table_name="accounts")
    op.drop_table("accounts")
    op.drop_table("users")

    # PostgreSQL enum types are schema objects and must be removed for a clean re-upgrade.
    sa.Enum(
        "DEPOSIT",
        "WITHDRAWAL",
        "TRANSFER_IN",
        "TRANSFER_OUT",
        name="transaction_type",
    ).drop(op.get_bind(), checkfirst=True)
    sa.Enum("COMPLETED", "FAILED", name="transfer_status").drop(
        op.get_bind(),
        checkfirst=True,
    )
    sa.Enum("ACTIVE", "FROZEN", "CLOSED", name="account_status").drop(
        op.get_bind(),
        checkfirst=True,
    )
    sa.Enum("CHECKING", "SAVINGS", name="account_type").drop(
        op.get_bind(),
        checkfirst=True,
    )
    sa.Enum("CUSTOMER", "ADMIN", name="user_role").drop(
        op.get_bind(),
        checkfirst=True,
    )
