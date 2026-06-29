from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class AuditEvent(Base):
    """Minimal immutable security and business-event record selected by D2."""

    __tablename__ = "audit_events"

    # Actor is optional for anonymous failures and becomes NULL rather than deleting audit history.
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
    )

    # String target fields let one audit table identify users, accounts, transfers, or auth events.
    event_type: Mapped[str] = mapped_column(String(100))
    entity_type: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[str] = mapped_column(String(255))

    # "metadata" is reserved by DeclarativeBase, so only the Python attribute uses another name.
    event_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        server_default=text("'{}'::json"),
    )

    # Server time makes audit ordering independent of the caller's clock.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # This is navigation only; authorization must still use the authenticated SQL principal.
    actor: Mapped[User | None] = relationship(back_populates="audit_events")
