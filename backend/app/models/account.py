from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.transfer import Transfer
    from app.models.user import User


class AccountType(StrEnum):
    """Supported simulated product types for the submission scope."""

    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"


class AccountStatus(StrEnum):
    """Operational states used by money services to allow or block movement."""

    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class Account(Base):
    __tablename__ = "accounts"

    # The database check is the final integrity backstop if service validation ever fails.
    __table_args__ = (CheckConstraint("balance >= 0", name="ck_accounts_balance_nonnegative"),)

    # Ownership must be included in customer queries to prevent cross-user account access.
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    account_number: Mapped[str] = mapped_column(String(32), unique=True)
    account_type: Mapped[AccountType] = mapped_column(
        Enum(AccountType, name="account_type"),
    )

    # NUMERIC and Decimal preserve cents exactly; ACTIVE is the initial operational state.
    balance: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        server_default=text("0.00"),
    )
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status"),
        default=AccountStatus.ACTIVE,
        server_default=text("'ACTIVE'"),
    )

    # Updated timestamps make status and balance changes observable without storing local time.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Transaction history is append-only, so these relationships intentionally omit delete cascades.
    user: Mapped[User] = relationship(back_populates="accounts")
    transactions: Mapped[list[Transaction]] = relationship(back_populates="account")

    # Explicit foreign keys disambiguate the two account roles attached to every transfer.
    outgoing_transfers: Mapped[list[Transfer]] = relationship(
        foreign_keys="Transfer.source_account_id",
        back_populates="source_account",
    )
    incoming_transfers: Mapped[list[Transfer]] = relationship(
        foreign_keys="Transfer.destination_account_id",
        back_populates="destination_account",
    )
