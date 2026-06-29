from decimal import Decimal

from pydantic import BaseModel, field_validator


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
