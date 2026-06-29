from datetime import UTC, datetime, timedelta

import pytest
from app.api.deps import _session_is_expired
from app.core.security import HOST_SESSION_COOKIE_NAME, hash_session_token
from app.errors import UNAUTHENTICATED_ERROR
from app.models import AuditEvent, Session, User
from app.seed import ADMIN_EMAIL, ADMIN_PASSWORD
from argon2 import PasswordHasher, Type
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

# Tests assert the complete public contract so future refactors cannot reintroduce enumeration.
GENERIC_LOGIN_ERROR = {
    "error": {
        "code": "UNAUTHENTICATED",
        "message": "Invalid email or password",
        "fields": {},
    }
}


def test_successful_login_creates_hashed_session_audit_and_secure_cookies(
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, session_factory = login_test_context
    response = client.post(
        "/api/auth/login",
        json={"email": f"  {ADMIN_EMAIL.upper()}  ", "password": ADMIN_PASSWORD},
        headers={"user-agent": "phase10-test-client"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": "authenticated"}

    # Cookie values must be independent, and neither secret may appear in the response body.
    raw_token = response.cookies.get(HOST_SESSION_COOKIE_NAME)
    csrf_token = response.cookies.get("csrf_token")
    assert raw_token is not None
    assert csrf_token is not None
    assert raw_token != csrf_token
    assert raw_token not in response.text

    cookie_headers = response.headers.get_list("set-cookie")
    session_cookie = next(
        header for header in cookie_headers if header.startswith(f"{HOST_SESSION_COOKIE_NAME}=")
    )
    csrf_cookie = next(header for header in cookie_headers if header.startswith("csrf_token="))
    for attribute in ("HttpOnly", "Secure", "SameSite=strict", "Path=/", "Max-Age=43200"):
        assert attribute.lower() in session_cookie.lower()
    assert "domain=" not in session_cookie.lower()
    assert "httponly" not in csrf_cookie.lower()
    for attribute in ("Secure", "SameSite=strict", "Path=/", "Max-Age=43200"):
        assert attribute.lower() in csrf_cookie.lower()

    # Database assertions prove the route persisted only the HMAC and preserved D1 timestamps.
    with session_factory() as db:
        session_record = db.scalar(select(Session))
        assert session_record is not None
        assert session_record.token_hash == hash_session_token(raw_token)
        assert session_record.token_hash != raw_token
        assert session_record.last_used_at == session_record.created_at
        assert int((session_record.expires_at - session_record.created_at).total_seconds()) == 43200
        assert session_record.user_agent == "phase10-test-client"

        audit_event = db.scalar(select(AuditEvent).where(AuditEvent.event_type == "login_success"))
        assert audit_event is not None
        assert audit_event.actor_user_id == session_record.user_id
        assert audit_event.entity_id == str(session_record.id)


def test_unknown_and_wrong_password_fail_with_identical_generic_response(
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, session_factory = login_test_context
    unknown_response = client.post(
        "/api/auth/login",
        json={"email": "unknown@demo.bank.test", "password": "wrong-password"},
    )
    wrong_response = client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": "wrong-password"},
    )

    assert unknown_response.status_code == 401
    assert wrong_response.status_code == 401

    # Matching bodies and absent cookies prevent the response contract from revealing user existence.
    assert unknown_response.json() == wrong_response.json() == GENERIC_LOGIN_ERROR
    assert not unknown_response.headers.get_list("set-cookie")
    assert not wrong_response.headers.get_list("set-cookie")

    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(Session)) == 0
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "login_failure")
            )
            == 2
        )


def test_inactive_user_is_blocked_with_the_same_generic_failure(
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, session_factory = login_test_context

    # Administrative deactivation changes SQL state; the frontend cannot override this decision.
    with session_factory() as db:
        admin = db.scalar(select(User).where(User.email == ADMIN_EMAIL))
        assert admin is not None
        admin.is_active = False
        db.commit()

    response = client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )

    assert response.status_code == 401
    assert response.json() == GENERIC_LOGIN_ERROR
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(Session)) == 0
        failure = db.scalar(select(AuditEvent).where(AuditEvent.event_type == "login_failure"))
        assert failure is not None
        assert failure.actor_user_id is not None


def test_successful_login_rehashes_outdated_password_parameters(
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, session_factory = login_test_context

    # A deliberately weak but valid hash simulates credentials created under older parameters.
    weaker_hasher = PasswordHasher(
        time_cost=1,
        memory_cost=8 * 1024,
        parallelism=1,
        hash_len=32,
        salt_len=16,
        type=Type.ID,
    )
    weak_hash = weaker_hasher.hash(ADMIN_PASSWORD)

    with session_factory() as db:
        admin = db.scalar(select(User).where(User.email == ADMIN_EMAIL))
        assert admin is not None
        admin.password_hash = weak_hash
        db.commit()

    response = client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )

    assert response.status_code == 200
    with session_factory() as db:
        updated_hash = db.scalar(select(User.password_hash).where(User.email == ADMIN_EMAIL))
        assert updated_hash is not None
        assert updated_hash != weak_hash


def test_auth_me_returns_safe_user_and_slides_idle_activity(
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, session_factory = login_test_context
    login_response = client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert login_response.status_code == 200

    with session_factory() as db:
        original_last_used = db.scalar(select(Session.last_used_at))
        assert original_last_used is not None

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": ADMIN_EMAIL,
        "first_name": "Avery",
        "last_name": "Admin",
        "role": "ADMIN",
        "is_active": True,
    }
    assert "password_hash" not in response.text

    with session_factory() as db:
        updated_last_used = db.scalar(select(Session.last_used_at))
        assert updated_last_used is not None
        assert updated_last_used > original_last_used


def test_session_expiry_boundaries_are_inclusive() -> None:
    now = datetime(2026, 6, 29, 12, tzinfo=UTC)
    session = Session(
        user_id=1,
        token_hash="a" * 64,
        created_at=now - timedelta(hours=1),
        last_used_at=now - timedelta(minutes=30),
        expires_at=now + timedelta(hours=1),
    )

    # Exactly reaching the idle or absolute deadline must fail closed.
    assert _session_is_expired(session, now, idle_minutes=30)
    session.last_used_at = now
    session.expires_at = now
    assert _session_is_expired(session, now, idle_minutes=30)


def test_auth_me_rejects_missing_and_invalid_session_tokens(
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, _session_factory = login_test_context
    missing_response = client.get("/api/auth/me")

    client.cookies.set(HOST_SESSION_COOKIE_NAME, "invalid-session-token")
    invalid_response = client.get("/api/auth/me")

    assert missing_response.status_code == 401
    assert invalid_response.status_code == 401
    assert missing_response.json() == invalid_response.json() == UNAUTHENTICATED_ERROR


@pytest.mark.parametrize("invalid_state", ["revoked", "absolute_expired", "idle_expired"])
def test_auth_me_rejects_invalid_server_side_session_state(
    invalid_state: str,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, session_factory = login_test_context
    login_response = client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert login_response.status_code == 200

    now = datetime.now(UTC)
    with session_factory() as db:
        session = db.scalar(select(Session))
        assert session is not None
        if invalid_state == "revoked":
            session.revoked_at = now
        elif invalid_state == "absolute_expired":
            session.expires_at = now
        else:
            # Equality is the boundary: exactly 30 idle minutes is already expired.
            session.last_used_at = now - timedelta(minutes=30)
        db.commit()

    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json() == UNAUTHENTICATED_ERROR


def test_auth_me_rejects_session_for_inactive_user(
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, session_factory = login_test_context
    login_response = client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert login_response.status_code == 200

    with session_factory() as db:
        admin = db.scalar(select(User).where(User.email == ADMIN_EMAIL))
        assert admin is not None
        admin.is_active = False
        db.commit()

    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json() == UNAUTHENTICATED_ERROR


def test_logout_revokes_server_side_clears_cookies_and_audits(
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, session_factory = login_test_context
    login_response = client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert login_response.status_code == 200
    old_raw_token = login_response.cookies.get(HOST_SESSION_COOKIE_NAME)
    csrf_token = login_response.cookies.get("csrf_token")
    assert old_raw_token is not None
    assert csrf_token is not None

    response = client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 204
    cookie_headers = response.headers.get_list("set-cookie")
    session_clear = next(
        header for header in cookie_headers if header.startswith(f"{HOST_SESSION_COOKIE_NAME}=")
    )
    csrf_clear = next(header for header in cookie_headers if header.startswith("csrf_token="))

    # Both browser cookies are expired, but the database assertion below proves real revocation.
    for header in (session_clear, csrf_clear):
        assert "max-age=0" in header.lower()
        assert "expires=" in header.lower()
        assert "path=/" in header.lower()
        assert "secure" in header.lower()
        assert "samesite=strict" in header.lower()
    assert "httponly" in session_clear.lower()
    assert "httponly" not in csrf_clear.lower()

    with session_factory() as db:
        revoked_session = db.scalar(select(Session))
        assert revoked_session is not None
        assert revoked_session.revoked_at is not None
        logout_audit = db.scalar(select(AuditEvent).where(AuditEvent.event_type == "logout"))
        assert logout_audit is not None
        assert logout_audit.actor_user_id == revoked_session.user_id
        assert logout_audit.entity_id == str(revoked_session.id)

    # Reintroducing the old raw cookie cannot bypass the durable revoked_at check.
    client.cookies.set(HOST_SESSION_COOKIE_NAME, old_raw_token)
    reused_response = client.get("/api/auth/me")
    assert reused_response.status_code == 401
    assert reused_response.json() == UNAUTHENTICATED_ERROR


def test_logout_requires_a_valid_current_session(
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    client, session_factory = login_test_context

    # Supplying a matching double-submit pair isolates authentication as the rejected boundary.
    client.cookies.set("csrf_token", "matching-test-csrf-token")
    response = client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": "matching-test-csrf-token"},
    )

    assert response.status_code == 401
    assert response.json() == UNAUTHENTICATED_ERROR
    assert not response.headers.get_list("set-cookie")
    with session_factory() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "logout")
            )
            == 0
        )
