from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.transfer import Transfer


class TransactionType(StrEnum):
    """Signed business events used later for balance reconciliation."""

    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"


class Transaction(Base):
    __tablename__ = "transactions"

    # Account-plus-time ordering supports the primary transaction-history query.
    __table_args__ = (Index("ix_transactions_account_id_created_at", "account_id", "created_at"),)

    # Every immutable history row belongs to exactly one account.
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="transaction_type"),
    )

    # balance_after records the post-operation snapshot needed for audits and reconciliation.
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    description: Mapped[str] = mapped_column(String(255))
    balance_after: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    # Transfer rows link their debit and credit legs through one shared parent identifier.
    reference_id: Mapped[int | None] = mapped_column(ForeignKey("transfers.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # No delete cascade is configured because history must survive independently of ORM operations.
    account: Mapped[Account] = relationship(back_populates="transactions")
    transfer: Mapped[Transfer | None] = relationship(back_populates="transactions")
