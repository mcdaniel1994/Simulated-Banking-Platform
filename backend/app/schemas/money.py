from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

MAX_MONEY_AMOUNT = Decimal("999999999999.99")


class MoneyAmountRequest(BaseModel):
    """Validate exact two-decimal money submitted as a JSON string."""

    # These bounds mirror PostgreSQL NUMERIC(14,2) before a request reaches a transaction service.
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)

    @field_validator("amount", mode="before")
    @classmethod
    def require_decimal_string(cls, value: object) -> object:
        """Keep binary floating-point values out of every money mutation."""

        # Pydantic can coerce JSON numbers to Decimal, so reject them explicitly at the API edge.
        if not isinstance(value, str):
            raise ValueError("amount must be a decimal string")
        return value
