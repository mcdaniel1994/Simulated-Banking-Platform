import pytest
from app.api.deps import CSRF_INVALID_ERROR
from app.models import AuditEvent, Session
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker


@pytest.mark.parametrize(
    "csrf_header",
    [None, "wrong-csrf-token"],
    ids=["missing-header", "mismatched-header"],
)
def test_logout_rejects_missing_or_mismatched_csrf_without_revoking(
    csrf_header: str | None,
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    headers = {} if csrf_header is None else {"X-CSRF-Token": csrf_header}

    response = admin_client.post("/api/auth/logout", headers=headers)

    assert response.status_code == 403
    assert response.json() == CSRF_INVALID_ERROR
    assert not response.headers.get_list("set-cookie")

    # Rejected CSRF requests cannot mutate revocation state or create a misleading audit record.
    with session_factory() as db:
        session = db.scalar(select(Session))
        assert session is not None
        assert session.revoked_at is None
        assert session.last_used_at == session.created_at
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "logout")
            )
            == 0
        )

    # Safe authenticated reads remain exempt after a rejected mutation.
    me_response = admin_client.get("/api/auth/me")
    assert me_response.status_code == 200
