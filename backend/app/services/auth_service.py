from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession

from app.core.security import (
    calculate_session_expiry,
    generate_session_token,
    hash_password,
    hash_session_token,
    needs_rehash,
    verify_password,
)
from app.models import AuditEvent, Session, User

# Unknown emails still perform one real Argon2 verification to reduce user-enumeration timing clues.
_DUMMY_PASSWORD_HASH = hash_password("not-a-real-user-password")


class LoginFailedError(Exception):
    """Internal signal mapped to one generic public authentication failure."""


@dataclass(frozen=True)
class LoginResult:
    """Secret-bearing service result consumed only by the cookie-issuing route."""

    raw_session_token: str
    expires_at: datetime


def _commit_login_failure(db: DatabaseSession, user: User | None) -> None:
    """Persist a sanitized failure event without recording attempted credentials."""

    db.add(
        AuditEvent(
            actor=user,
            event_type="login_failure",
            entity_type="authentication",
            entity_id=str(user.id) if user is not None else "unknown",
            event_metadata={"outcome": "failure"},
        )
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def login(
    db: DatabaseSession,
    *,
    email: str,
    password: str,
    user_agent: str | None,
    ip: str | None,
) -> LoginResult:
    """Authenticate credentials and atomically create a revocable server-side session."""

    # Email normalization occurs in the schema; the database remains the identity source of truth.
    user = db.scalar(select(User).where(User.email == email))

    # Unknown users follow the same expensive verification path as known users with wrong passwords.
    candidate_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
    password_matches = verify_password(password, candidate_hash)

    # Unknown, wrong-password, and inactive-user paths deliberately share one public failure.
    if user is None or not password_matches or not user.is_active:
        _commit_login_failure(db, user)
        raise LoginFailedError

    # One timestamp anchors creation, idle activity, absolute expiry, and the success audit.
    now = datetime.now(UTC)
    expires_at = calculate_session_expiry(now)
    raw_token = generate_session_token()

    try:
        # Upgrade valid older password hashes during authentication without storing plaintext.
        if needs_rehash(user.password_hash):
            user.password_hash = hash_password(password)

        # SQL receives only the HMAC lookup value; the raw token returns to the route for its cookie.
        session = Session(
            user=user,
            token_hash=hash_session_token(raw_token),
            created_at=now,
            last_used_at=now,
            expires_at=expires_at,
            user_agent=user_agent,
            ip=ip,
        )

        # Audit data references the generated session ID without storing cookies or credentials.
        audit_event = AuditEvent(
            actor=user,
            event_type="login_success",
            entity_type="session",
            entity_id="pending",
            event_metadata={"outcome": "success"},
            created_at=now,
        )
        db.add_all([session, audit_event])
        db.flush()

        # The generated session ID makes the audit target useful without exposing the raw token.
        audit_event.entity_id = str(session.id)

        # Password upgrade, session creation, and audit success form one all-or-nothing transaction.
        db.commit()
    except Exception:
        db.rollback()
        raise

    return LoginResult(raw_session_token=raw_token, expires_at=expires_at)


def logout(db: DatabaseSession, *, user: User, session: Session) -> None:
    """Revoke one validated session and audit the logout atomically."""

    now = datetime.now(UTC)
    try:
        # Revocation is the durable security action; deleting browser cookies is only client cleanup.
        session.revoked_at = now
        db.add(
            AuditEvent(
                actor=user,
                event_type="logout",
                entity_type="session",
                entity_id=str(session.id),
                event_metadata={"outcome": "revoked"},
                created_at=now,
            )
        )

        # Audit history and the revocation timestamp must succeed or roll back together.
        db.commit()
    except Exception:
        db.rollback()
        raise
