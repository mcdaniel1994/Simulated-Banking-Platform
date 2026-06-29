from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Session(Base):
    """Revocable server-side authentication session linked to one user."""

    __tablename__ = "sessions"

    # Indexed ownership supports user-wide revocation when an administrator deactivates a customer.
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Only a deterministic token hash is persisted; the raw session token belongs in the cookie.
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    # These timestamps enforce D1's idle timeout, absolute expiry, and immediate revocation.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Optional request context supports future security review without becoming an auth decision.
    user_agent: Mapped[str | None] = mapped_column(Text)
    ip: Mapped[str | None] = mapped_column(String(45))

    # The relationship lets authentication load the SQL-backed principal for each valid session.
    user: Mapped[User] = relationship(back_populates="sessions")
