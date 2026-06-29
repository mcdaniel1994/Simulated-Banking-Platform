from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.models import AccountStatus, AccountType


class AccountResponse(BaseModel):
    """Public customer account fields with money represented as an exact JSON string."""

    model_config = ConfigDict(from_attributes=True)

    # Ownership identifiers and ORM relationships remain inside the backend security boundary.
    id: int
    account_number: str
    account_type: AccountType
    balance: str
    status: AccountStatus
    created_at: datetime
    updated_at: datetime

    @field_validator("balance", mode="before")
    @classmethod
    def serialize_balance(cls, value: Decimal | str) -> str:
        """Preserve cents exactly without passing through binary floating point."""

        decimal_value = value if isinstance(value, Decimal) else Decimal(value)
        return format(decimal_value, ".2f")
