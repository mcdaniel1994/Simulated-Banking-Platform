from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import UserRole


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


class CurrentUserResponse(BaseModel):
    """Safe authenticated-user fields returned from the SQL-backed session principal."""

    model_config = ConfigDict(from_attributes=True)

    # Password hashes, sessions, and audit relationships never cross the response boundary.
    id: int
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
