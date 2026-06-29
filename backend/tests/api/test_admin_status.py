from app.main import app
from app.models import Account, AccountStatus, AuditEvent, Session, User
from app.seed import CUSTOMER_PASSWORD
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

CUSTOMER_EMAIL = "alex.customer@demo.bank.test"
ACCOUNT_NUMBER = "1000000001"


def _csrf_headers(client: TestClient) -> dict[str, str]:
    token = client.cookies.get("csrf_token")
    assert token is not None
    return {"X-CSRF-Token": token}


def _customer_and_account_ids(
    session_factory: sessionmaker[DatabaseSession],
) -> tuple[int, int]:
    with session_factory() as db:
        customer_id = db.scalar(select(User.id).where(User.email == CUSTOMER_EMAIL))
        account_id = db.scalar(select(Account.id).where(Account.account_number == ACCOUNT_NUMBER))
    assert customer_id is not None and account_id is not None
    return customer_id, account_id


def test_deactivation_revokes_live_session_blocks_login_and_audits(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _shared_client, session_factory = login_test_context
    customer_id, _account_id = _customer_and_account_ids(session_factory)
    with TestClient(app, base_url="https://testserver") as customer:
        login = customer.post(
            "/api/auth/login",
            json={"email": CUSTOMER_EMAIL, "password": CUSTOMER_PASSWORD},
        )
        assert login.status_code == 200

        response = admin_client.patch(
            f"/api/admin/users/{customer_id}/status",
            json={"is_active": False},
            headers=_csrf_headers(admin_client),
        )
        me_response = customer.get("/api/auth/me")
        relogin = customer.post(
            "/api/auth/login",
            json={"email": CUSTOMER_EMAIL, "password": CUSTOMER_PASSWORD},
        )

    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert me_response.status_code == relogin.status_code == 401
    with session_factory() as db:
        active_sessions = db.scalar(
            select(func.count())
            .select_from(Session)
            .where(
                Session.user_id == customer_id,
                Session.revoked_at.is_(None),
            )
        )
        audit = db.scalar(select(AuditEvent).where(AuditEvent.event_type == "user_deactivated"))
        assert active_sessions == 0
        assert audit is not None


def test_activation_restores_login(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    customer_id, _account_id = _customer_and_account_ids(session_factory)
    with session_factory() as db:
        customer = db.get(User, customer_id)
        assert customer is not None
        customer.is_active = False
        db.commit()

    response = admin_client.patch(
        f"/api/admin/users/{customer_id}/status",
        json={"is_active": True},
        headers=_csrf_headers(admin_client),
    )
    with TestClient(app, base_url="https://testserver") as customer:
        login = customer.post(
            "/api/auth/login",
            json={"email": CUSTOMER_EMAIL, "password": CUSTOMER_PASSWORD},
        )

    assert response.status_code == 200
    assert response.json()["is_active"] is True
    assert login.status_code == 200
    with session_factory() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "user_activated")
            )
            == 1
        )


def test_freeze_blocks_customer_deposit_and_admin_is_not_owner(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _shared_client, session_factory = login_test_context
    _customer_id, account_id = _customer_and_account_ids(session_factory)
    with TestClient(app, base_url="https://testserver") as customer:
        login = customer.post(
            "/api/auth/login",
            json={"email": CUSTOMER_EMAIL, "password": CUSTOMER_PASSWORD},
        )
        assert login.status_code == 200

        freeze = admin_client.patch(
            f"/api/admin/accounts/{account_id}/status",
            json={"status": "FROZEN"},
            headers=_csrf_headers(admin_client),
        )
        customer_deposit = customer.post(
            f"/api/accounts/{account_id}/deposits",
            json={"amount": "10.00"},
            headers=_csrf_headers(customer),
        )
        admin_deposit = admin_client.post(
            f"/api/accounts/{account_id}/deposits",
            json={"amount": "10.00"},
            headers=_csrf_headers(admin_client),
        )

    assert freeze.status_code == 200
    assert freeze.json()["status"] == "FROZEN"
    assert customer_deposit.status_code == 409
    assert customer_deposit.json()["error"]["code"] == "INACTIVE_ACCOUNT"
    assert admin_deposit.status_code == 403
    assert admin_deposit.json()["error"]["code"] == "FORBIDDEN"
    with session_factory() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "account_frozen")
            )
            == 1
        )


def test_unfreeze_restores_active_account_status_and_audits(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    _customer_id, account_id = _customer_and_account_ids(session_factory)
    with session_factory() as db:
        account = db.get(Account, account_id)
        assert account is not None
        account.status = AccountStatus.FROZEN
        db.commit()

    response = admin_client.patch(
        f"/api/admin/accounts/{account_id}/status",
        json={"status": "ACTIVE"},
        headers=_csrf_headers(admin_client),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ACTIVE"
    with session_factory() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "account_unfrozen")
            )
            == 1
        )


def test_admin_status_mutations_require_csrf_and_validate_state(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    customer_id, account_id = _customer_and_account_ids(session_factory)

    missing_csrf = admin_client.patch(
        f"/api/admin/users/{customer_id}/status",
        json={"is_active": False},
    )
    invalid_account_status = admin_client.patch(
        f"/api/admin/accounts/{account_id}/status",
        json={"status": "CLOSED"},
        headers=_csrf_headers(admin_client),
    )

    assert missing_csrf.status_code == 403
    assert missing_csrf.json()["error"]["code"] == "CSRF_INVALID"
    assert invalid_account_status.status_code == 422
    assert invalid_account_status.json()["error"]["code"] == "VALIDATION_ERROR"
