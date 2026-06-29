from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.transaction import Transaction


class TransferStatus(StrEnum):
    """Recorded outcomes for the parent of a two-legged internal transfer."""

    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Transfer(Base):
    __tablename__ = "transfers"

    # Both account references are required and will be locked in deterministic ID order by services.
    id: Mapped[int] = mapped_column(primary_key=True)
    source_account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    destination_account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))

    # The parent amount must exactly match both transaction legs created in the same DB transaction.
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    status: Mapped[TransferStatus] = mapped_column(
        Enum(TransferStatus, name="transfer_status"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # Explicit foreign keys preserve source/destination meaning across the two account relationships.
    source_account: Mapped[Account] = relationship(
        foreign_keys=[source_account_id],
        back_populates="outgoing_transfers",
    )
    destination_account: Mapped[Account] = relationship(
        foreign_keys=[destination_account_id],
        back_populates="incoming_transfers",
    )

    # The collection holds the TRANSFER_OUT and TRANSFER_IN rows sharing this transfer ID.
    transactions: Mapped[list[Transaction]] = relationship(back_populates="transfer")
