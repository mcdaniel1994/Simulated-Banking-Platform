from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.models import TransactionType


class TransactionResponse(BaseModel):
    """Public append-only history with exact string-serialized money values."""

    model_config = ConfigDict(from_attributes=True)

    # account_id identifies the owned account in a combined feed; owner relationships stay hidden.
    id: int
    account_id: int
    transaction_type: TransactionType
    amount: str
    description: str
    balance_after: str
    reference_id: int | None
    created_at: datetime

    @field_validator("amount", "balance_after", mode="before")
    @classmethod
    def serialize_money(cls, value: Decimal | str) -> str:
        """Preserve cents exactly without introducing binary floating point."""

        # Movement and resulting snapshot use the same stable two-decimal public contract.
        decimal_value = value if isinstance(value, Decimal) else Decimal(value)
        return format(decimal_value, ".2f")
