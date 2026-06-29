import logging

from app.main import app
from app.models import Account, AuditEvent, User
from app.seed import ADMIN_EMAIL, ADMIN_PASSWORD, CUSTOMER_PASSWORD
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

CUSTOMER_EMAIL = "alex.customer@demo.bank.test"
OTHER_CUSTOMER_EMAIL = "jordan.customer@demo.bank.test"


def _login(client: TestClient, email: str, password: str) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200


def _csrf_headers(client: TestClient) -> dict[str, str]:
    token = client.cookies.get("csrf_token")
    assert token is not None
    return {"X-CSRF-Token": token}


def test_required_mvp_audit_events_are_wired_end_to_end(
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _shared_client, session_factory = login_test_context
    with session_factory() as db:
        customer_id = db.scalar(select(User.id).where(User.email == CUSTOMER_EMAIL))
        other_customer_id = db.scalar(select(User.id).where(User.email == OTHER_CUSTOMER_EMAIL))
        account_ids = list(
            db.scalars(
                select(Account.id).where(Account.user_id == customer_id).order_by(Account.id)
            )
        )
    assert customer_id is not None and other_customer_id is not None
    assert len(account_ids) == 2

    with (
        TestClient(app, base_url="https://testserver") as admin,
        TestClient(app, base_url="https://testserver") as customer,
    ):
        _login(admin, ADMIN_EMAIL, ADMIN_PASSWORD)
        _login(customer, CUSTOMER_EMAIL, CUSTOMER_PASSWORD)
        failed_login = customer.post(
            "/api/auth/login",
            json={"email": "unknown@demo.bank.test", "password": "not-the-password"},
        )
        denied = customer.get("/api/admin/dashboard")
        deposit = customer.post(
            f"/api/accounts/{account_ids[0]}/deposits",
            json={"amount": "10.00"},
            headers=_csrf_headers(customer),
        )
        withdrawal = customer.post(
            f"/api/accounts/{account_ids[0]}/withdrawals",
            json={"amount": "5.00"},
            headers=_csrf_headers(customer),
        )
        transfer = customer.post(
            "/api/transfers",
            json={
                "source_account_id": account_ids[0],
                "destination_account_id": account_ids[1],
                "amount": "2.00",
            },
            headers=_csrf_headers(customer),
        )
        logout = customer.post(
            "/api/auth/logout",
            headers=_csrf_headers(customer),
        )
        deactivate = admin.patch(
            f"/api/admin/users/{other_customer_id}/status",
            json={"is_active": False},
            headers=_csrf_headers(admin),
        )
        activate = admin.patch(
            f"/api/admin/users/{other_customer_id}/status",
            json={"is_active": True},
            headers=_csrf_headers(admin),
        )
        freeze = admin.patch(
            f"/api/admin/accounts/{account_ids[0]}/status",
            json={"status": "FROZEN"},
            headers=_csrf_headers(admin),
        )
        unfreeze = admin.patch(
            f"/api/admin/accounts/{account_ids[0]}/status",
            json={"status": "ACTIVE"},
            headers=_csrf_headers(admin),
        )

    assert failed_login.status_code == 401
    assert denied.status_code == 403
    assert deposit.status_code == withdrawal.status_code == 200
    assert transfer.status_code == 201
    assert logout.status_code == 204
    assert deactivate.status_code == activate.status_code == 200
    assert freeze.status_code == unfreeze.status_code == 200

    required_events = {
        "login_success",
        "login_failure",
        "logout",
        "deposit",
        "withdrawal",
        "transfer",
        "user_activated",
        "user_deactivated",
        "account_frozen",
        "account_unfrozen",
        "permission_denied",
    }
    with session_factory() as db:
        observed_events = set(db.scalars(select(AuditEvent.event_type)))
    assert required_events <= observed_events


def test_auth_and_permission_logs_redact_sensitive_values(
    caplog: object,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    shared_client, _session_factory = login_test_context
    password = "sensitive-password-value"
    raw_cookie = "sensitive-cookie-value"
    account_number = "1000000001"

    with caplog.at_level(logging.INFO):
        shared_client.cookies.set("__Host-session", raw_cookie)
        failed_login = shared_client.post(
            "/api/auth/login",
            json={"email": account_number + "@example.test", "password": password},
        )
        shared_client.cookies.clear()
        _login(shared_client, CUSTOMER_EMAIL, CUSTOMER_PASSWORD)
        denied = shared_client.get("/api/admin/dashboard")

    assert failed_login.status_code == 401
    assert denied.status_code == 403
    combined = caplog.text + failed_login.text + denied.text
    for secret in (password, raw_cookie, account_number, "Cookie", "Authorization"):
        assert secret not in combined
    for expected_event in ("login_failure", "login_success", "permission_denied"):
        assert expected_event in caplog.text
