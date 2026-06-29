from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from app.models import AccountStatus
from app.schemas.account import AccountResponse
from app.schemas.transaction import TransactionResponse


class AdminCustomerResponse(BaseModel):
    """Safe customer identity and lifecycle fields for administrator reads."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime


class AdminCustomerDetailResponse(BaseModel):
    """One customer with owned accounts and a paginated transaction slice."""

    customer: AdminCustomerResponse
    accounts: list[AccountResponse]
    transactions: list[TransactionResponse]
    transaction_limit: int
    transaction_offset: int


class AdminDashboardResponse(BaseModel):
    """Aggregate platform statistics safe for the administrator dashboard."""

    customer_count: int
    account_count: int
    total_simulated_balance: str
    recent_transaction_count: int
    recent_window_days: int

    @field_validator("total_simulated_balance", mode="before")
    @classmethod
    def serialize_balance(cls, value: Decimal | str) -> str:
        decimal_value = value if isinstance(value, Decimal) else Decimal(value)
        return format(decimal_value, ".2f")


class UserStatusRequest(BaseModel):
    """Administrator-selected customer activation state."""

    is_active: bool


class AccountStatusRequest(BaseModel):
    """Freeze or unfreeze an account without reopening a CLOSED account."""

    status: AccountStatus

    @field_validator("status")
    @classmethod
    def allow_only_active_or_frozen(cls, value: AccountStatus) -> AccountStatus:
        if value not in {AccountStatus.ACTIVE, AccountStatus.FROZEN}:
            raise ValueError("status must be ACTIVE or FROZEN")
        return value
