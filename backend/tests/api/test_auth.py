from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from app.core.security import HOST_SESSION_COOKIE_NAME, hash_session_token
from app.db.session import get_db
from app.main import app
from app.models import AuditEvent, Session, User
from app.seed import ADMIN_EMAIL, ADMIN_PASSWORD, seed_database
from argon2 import PasswordHasher, Type
from fastapi.testclient import TestClient
from sqlalchemy import Engine, func, select, text
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

from tests.conftest import DatabaseTestSettings

BACKEND_ROOT = Path(__file__).resolve().parents[2]

# Tests assert the complete public contract so future refactors cannot reintroduce enumeration.
GENERIC_LOGIN_ERROR = {
    "error": {
        "code": "UNAUTHENTICATED",
        "message": "Invalid email or password",
        "fields": {},
    }
}


@pytest.fixture
def login_test_context(
    database_test_settings: DatabaseTestSettings,
    test_engine: Engine,
    test_session_factory: sessionmaker[DatabaseSession],
) -> Generator[tuple[TestClient, sessionmaker[DatabaseSession]], None, None]:
    # Recreate only test data while applying the same migration and seed used by development.
    alembic_config = Config(BACKEND_ROOT / "alembic.ini")
    alembic_config.attributes["database_url"] = (
        database_test_settings.test_database_url.get_secret_value()
    )
    command.upgrade(alembic_config, "head")
    with test_engine.begin() as connection:
        connection.execute(
            text(
                """
                TRUNCATE TABLE
                    transactions, transfers, sessions, audit_events, accounts, users
                RESTART IDENTITY CASCADE
                """
            )
        )

    seed_session = test_session_factory()
    try:
        # Production seed logic supplies real Argon2 users instead of hand-built authentication mocks.
        seed_database(seed_session)
    finally:
        seed_session.close()

    def override_get_db() -> Generator[DatabaseSession, None, None]:
        # FastAPI receives request-scoped sessions bound only to simulated_banking_test.
        db = test_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app, base_url="https://testserver") as client:
            yield client, test_session_factory
    finally:
        # Restore global FastAPI state and remove every row created by the current test.
        app.dependency_overrides.clear()
        with test_engine.begin() as connection:
            connection.execute(
                text(
                    """
                    TRUNCATE TABLE
                        transactions, transfers, sessions, audit_events, accounts, users
                    RESTART IDENTITY CASCADE
                    """
                )
            )


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
