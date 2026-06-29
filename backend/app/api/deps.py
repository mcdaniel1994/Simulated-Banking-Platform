from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hmac import compare_digest
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import joinedload

from app.core.config import get_settings
from app.core.security import get_session_cookie_name, hash_session_token
from app.db.session import get_db
from app.errors import CsrfInvalidError, ForbiddenError, NotFoundError, UnauthenticatedError
from app.models import Account, Session, User, UserRole
from app.services.audit_service import record_permission_denied

SAFE_HTTP_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    """The user and session established together at the authentication boundary."""

    user: User
    session: Session


def verify_csrf_token(request: Request) -> None:
    """Require the readable CSRF cookie to be echoed on unsafe requests."""

    # Safe methods only read state, so they do not need a double-submit credential.
    if request.method.upper() in SAFE_HTTP_METHODS:
        return

    settings = get_settings()
    cookie_token = request.cookies.get(settings.csrf_cookie_name)
    header_token = request.headers.get("X-CSRF-Token")

    # Constant-time comparison avoids making token equality observable through timing.
    if (
        cookie_token is None
        or header_token is None
        or not compare_digest(cookie_token, header_token)
    ):
        raise CsrfInvalidError


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


def require_role(required_role: UserRole) -> Callable[..., User]:
    """Build a reusable guard that trusts only the authenticated SQL user."""

    def role_dependency(
        user: Annotated[User, Depends(get_current_user)],
        db: Annotated[DatabaseSession, Depends(get_db)],
    ) -> User:
        # The role arrived through the database-backed session lookup, never request input.
        if user.role is not required_role:
            record_permission_denied(
                db,
                actor=user,
                entity_type="role",
                entity_id=required_role.value,
                metadata={"actual_role": user.role.value},
            )
            raise ForbiddenError
        return user

    return role_dependency


CurrentPrincipal = Annotated[AuthenticatedPrincipal, Depends(get_current_principal)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CsrfProtected = Annotated[None, Depends(verify_csrf_token)]

# Named aliases keep route signatures explicit while sharing the same role-checking factory.
AdminUser = Annotated[User, Depends(require_role(UserRole.ADMIN))]
CustomerUser = Annotated[User, Depends(require_role(UserRole.CUSTOMER))]


def get_owned_account(
    account_id: int,
    customer: CustomerUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> Account:
    """Load one account only when its SQL owner is the authenticated customer."""

    # Filtering by resource and owner together prevents existence disclosure and IDOR access.
    account = db.scalar(
        select(Account).where(
            Account.id == account_id,
            Account.user_id == customer.id,
        )
    )
    if account is None:
        record_permission_denied(
            db,
            actor=customer,
            entity_type="account",
            entity_id=str(account_id),
            metadata={"reason": "missing_or_not_owned"},
        )
        raise NotFoundError
    return account


# Every future account-scoped customer route should enter through this ownership boundary.
OwnedAccount = Annotated[Account, Depends(get_owned_account)]
