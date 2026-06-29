from typing import Literal

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    """Credentials accepted by the public login endpoint."""

    # Length bounds reject empty or unreasonably large input before password hashing or SQL lookup.
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=1024)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Match the normalized lowercase addresses stored by the application."""

        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("email must contain @")
        return normalized


class LoginResponse(BaseModel):
    """Small success body; raw authentication material remains cookie-only."""

    # User details intentionally wait for the authenticated /auth/me endpoint in Phase 11.
    status: Literal["authenticated"] = "authenticated"
