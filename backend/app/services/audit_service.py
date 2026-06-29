import logging
from typing import Any

from sqlalchemy.orm import Session as DatabaseSession

from app.models import AuditEvent, User

logger = logging.getLogger(__name__)


def record_permission_denied(
    db: DatabaseSession,
    *,
    actor: User,
    entity_type: str,
    entity_id: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Persist and safely log an authorization denial without sensitive request data."""

    try:
        db.add(
            AuditEvent(
                actor=actor,
                event_type="permission_denied",
                entity_type=entity_type,
                entity_id=entity_id,
                event_metadata=metadata or {},
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    logger.warning(
        "permission_denied actor_user_id=%s entity_type=%s entity_id=%s",
        actor.id,
        entity_type,
        entity_id,
    )
