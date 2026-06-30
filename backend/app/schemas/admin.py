from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import AccountStatus
from app.schemas.account import AccountResponse
from app.schemas.transaction import TransactionResponse


class AdminCustomerResponse(BaseModel):
    """Safe customer identity and lifecycle fields for administrator reads."""

    model_config = ConfigDict(from_attributes=True)

    # Credential hashes, sessions, role internals, and audit relationships are intentionally absent.
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime


class AdminCustomerCreateRequest(BaseModel):
    """Administrator-provided identity fields for one new customer."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("first_name", "last_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        # Whitespace-only names must not survive validation into customer records.
        normalized = value.strip()
        if not normalized:
            raise ValueError("name must not be blank")
        return normalized

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        # Login uses this same lowercase representation when resolving SQL identities.
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("email must contain @")
        return normalized


class AdminCustomerDetailResponse(BaseModel):
    """One customer with owned accounts and a paginated transaction slice."""

    # Existing public schemas keep money and history serialization identical across roles.
    customer: AdminCustomerResponse
    accounts: list[AccountResponse]
    transactions: list[TransactionResponse]
    transaction_limit: int
    transaction_offset: int


class AdminDashboardResponse(BaseModel):
    """Aggregate platform statistics safe for the administrator dashboard."""

    # The explicit window makes "recent" measurable rather than an ambiguous UI label.
    customer_count: int
    account_count: int
    total_simulated_balance: str
    recent_transaction_count: int
    recent_window_days: int

    @field_validator("total_simulated_balance", mode="before")
    @classmethod
    def serialize_balance(cls, value: Decimal | str) -> str:
        # Convert Decimal directly so the aggregate never crosses a binary-float boundary.
        decimal_value = value if isinstance(value, Decimal) else Decimal(value)
        return format(decimal_value, ".2f")


class UserStatusRequest(BaseModel):
    """Administrator-selected customer activation state."""

    # The server, not the frontend, translates this state into session-revocation behavior.
    is_active: bool


class AccountStatusRequest(BaseModel):
    """Freeze or unfreeze an account without reopening a CLOSED account."""

    status: AccountStatus

    @field_validator("status")
    @classmethod
    def allow_only_active_or_frozen(cls, value: AccountStatus) -> AccountStatus:
        # CLOSED requires a separate lifecycle workflow and cannot be reopened accidentally here.
        if value not in {AccountStatus.ACTIVE, AccountStatus.FROZEN}:
            raise ValueError("status must be ACTIVE or FROZEN")
        return value
