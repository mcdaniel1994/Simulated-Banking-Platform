from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import joinedload

from app.core.config import get_settings
from app.core.security import get_session_cookie_name, hash_session_token
from app.db.session import get_db
from app.models import Session, User

UNAUTHENTICATED_ERROR = {
    "error": {
        "code": "UNAUTHENTICATED",
        "message": "Authentication required",
        "fields": {},
    }
}


class UnauthenticatedError(Exception):
    """Internal signal for every invalid server-side session state."""


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    """The user and session established together at the authentication boundary."""

    user: User
    session: Session


async def unauthenticated_exception_handler(
    _request: Request,
    _error: UnauthenticatedError,
) -> JSONResponse:
    """Render the stable public envelope later consolidated by Phase 17."""

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=UNAUTHENTICATED_ERROR,
    )


def _session_is_expired(session: Session, now: datetime, idle_minutes: int) -> bool:
    """Apply inclusive absolute and idle boundaries using timezone-aware SQL timestamps."""

    absolute_expired = session.expires_at <= now
    idle_expired = session.last_used_at + timedelta(minutes=idle_minutes) <= now
    return absolute_expired or idle_expired


def get_current_principal(
    request: Request,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> AuthenticatedPrincipal:
    """Resolve, validate, and slide one opaque server-side session."""

    settings = get_settings()
    cookie_name = get_session_cookie_name(settings.cookie_domain)
    raw_token = request.cookies.get(cookie_name)
    if raw_token is None:
        raise UnauthenticatedError

    # SQL lookup receives only the deterministic HMAC, never the raw cookie credential.
    session = db.scalar(
        select(Session)
        .options(joinedload(Session.user))
        .where(Session.token_hash == hash_session_token(raw_token))
    )
    if session is None:
        raise UnauthenticatedError

    now = datetime.now(UTC)

    # Revocation, both expiry clocks, and user deactivation independently invalidate access.
    if (
        session.revoked_at is not None
        or _session_is_expired(session, now, settings.session_idle_minutes)
        or not session.user.is_active
    ):
        raise UnauthenticatedError

    try:
        # D1 uses a sliding idle window, so every accepted request records fresh activity.
        session.last_used_at = now
        db.commit()
    except Exception:
        db.rollback()
        raise

    return AuthenticatedPrincipal(user=session.user, session=session)


def get_current_user(
    principal: Annotated[AuthenticatedPrincipal, Depends(get_current_principal)],
) -> User:
    """Expose the authenticated SQL user to routes that do not need the session row."""

    return principal.user


CurrentPrincipal = Annotated[AuthenticatedPrincipal, Depends(get_current_principal)]
CurrentUser = Annotated[User, Depends(get_current_user)]
