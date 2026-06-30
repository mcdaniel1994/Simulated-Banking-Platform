from decimal import Decimal

from app.core.security import verify_password
from app.main import app
from app.models import Account, AccountStatus, AccountType, AuditEvent, User, UserRole
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

NEW_EMAIL = "new.customer@example.test"
NEW_PASSWORD = "A-strong-passphrase"


def _csrf_headers(client: TestClient) -> dict[str, str]:
    token = client.cookies.get("csrf_token")
    assert token is not None
    return {"X-CSRF-Token": token}


def _customer_payload(**overrides: str) -> dict[str, str]:
    payload = {
        "first_name": "  Morgan  ",
        "last_name": "  Rivera  ",
        "email": f"  {NEW_EMAIL.upper()}  ",
        "password": NEW_PASSWORD,
    }
    payload.update(overrides)
    return payload


def test_admin_creates_customer_checking_account_and_audit_atomically(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context

    response = admin_client.post(
        "/api/admin/users",
        json=_customer_payload(),
        headers=_csrf_headers(admin_client),
    )

    assert response.status_code == 201
    assert response.json()["email"] == NEW_EMAIL
    assert response.json()["first_name"] == "Morgan"
    assert response.json()["last_name"] == "Rivera"
    assert "password" not in response.text
    with session_factory() as db:
        customer = db.scalar(select(User).where(User.email == NEW_EMAIL))
        assert customer is not None
        assert customer.role is UserRole.CUSTOMER
        assert customer.is_active is True
        assert customer.password_hash != NEW_PASSWORD
        assert verify_password(NEW_PASSWORD, customer.password_hash)

        account = db.scalar(select(Account).where(Account.user_id == customer.id))
        assert account is not None
        assert account.account_number == f"2{customer.id:09d}"
        assert account.account_type is AccountType.CHECKING
        assert account.status is AccountStatus.ACTIVE
        assert account.balance == Decimal("0.00")

        audit = db.scalar(
            select(AuditEvent).where(
                AuditEvent.event_type == "user_created",
                AuditEvent.entity_id == str(customer.id),
            )
        )
        assert audit is not None
        assert audit.event_metadata == {"initial_account_type": "CHECKING"}
        assert NEW_PASSWORD not in str(audit.event_metadata)

    # The supplied credential is immediately usable and resolves only the new owned account.
    with TestClient(app, base_url="https://testserver") as customer_client:
        login = customer_client.post(
            "/api/auth/login",
            json={"email": NEW_EMAIL, "password": NEW_PASSWORD},
        )
        accounts = customer_client.get("/api/accounts")
    assert login.status_code == 200
    assert accounts.status_code == 200
    assert len(accounts.json()) == 1
    assert accounts.json()[0]["balance"] == "0.00"


def test_duplicate_customer_email_returns_field_conflict_without_partial_rows(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    headers = _csrf_headers(admin_client)
    first = admin_client.post("/api/admin/users", json=_customer_payload(), headers=headers)
    duplicate = admin_client.post(
        "/api/admin/users",
        json=_customer_payload(first_name="Different"),
        headers=headers,
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"
    assert duplicate.json()["error"]["fields"] == {
        "email": "A customer with this email already exists."
    }
    with session_factory() as db:
        customers = list(db.scalars(select(User).where(User.email == NEW_EMAIL)))
        assert len(customers) == 1
        assert len(customers[0].accounts) == 1


def test_customer_creation_requires_csrf_and_admin_role(
    customer_client: TestClient,
) -> None:
    forbidden = customer_client.post(
        "/api/admin/users",
        json=_customer_payload(),
        headers=_csrf_headers(customer_client),
    )

    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "FORBIDDEN"


def test_customer_creation_rejects_missing_csrf_and_redacts_invalid_password(
    admin_client: TestClient,
) -> None:
    rejected_password = "too-short"
    missing_csrf = admin_client.post("/api/admin/users", json=_customer_payload())
    invalid = admin_client.post(
        "/api/admin/users",
        json=_customer_payload(password=rejected_password),
        headers=_csrf_headers(admin_client),
    )

    assert missing_csrf.status_code == 403
    assert missing_csrf.json()["error"]["code"] == "CSRF_INVALID"
    assert invalid.status_code == 422
    assert invalid.json()["error"]["fields"] == {"password": "Invalid value"}
    assert rejected_password not in invalid.text
