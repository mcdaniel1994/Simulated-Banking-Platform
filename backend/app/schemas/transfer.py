from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import TransferStatus
from app.schemas.money import MoneyAmountRequest


class TransferRequest(MoneyAmountRequest):
    """Two owned account IDs plus one exact decimal-string amount."""

    # Positive IDs are structural validation; ownership and same-account rules require SQL context.
    source_account_id: int = Field(gt=0)
    destination_account_id: int = Field(gt=0)


class TransferResponse(BaseModel):
    """Public transfer parent; individual debit/credit legs remain in transaction history."""

    model_config = ConfigDict(from_attributes=True)

    # The parent exposes linkage/status while transaction history carries balance_after values.
    id: int
    source_account_id: int
    destination_account_id: int
    amount: str
    status: TransferStatus
    created_at: datetime

    @field_validator("amount", mode="before")
    @classmethod
    def serialize_amount(cls, value: Decimal | str) -> str:
        # Match every other public money field with an exact two-decimal string.
        decimal_value = value if isinstance(value, Decimal) else Decimal(value)
        return format(decimal_value, ".2f")
