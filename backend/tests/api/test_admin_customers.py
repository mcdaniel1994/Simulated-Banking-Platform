from app.errors import FORBIDDEN_ERROR, NOT_FOUND_ERROR
from app.models import User, UserRole
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

CUSTOMER_EMAIL = "alex.customer@demo.bank.test"


def _user_id(
    session_factory: sessionmaker[DatabaseSession],
    *,
    email: str | None = None,
    role: UserRole | None = None,
) -> int:
    with session_factory() as db:
        statement = select(User.id)
        if email is not None:
            statement = statement.where(User.email == email)
        if role is not None:
            statement = statement.where(User.role == role)
        user_id = db.scalar(statement.order_by(User.id))
    assert user_id is not None
    return user_id


def test_admin_lists_only_safe_customer_records(admin_client: TestClient) -> None:
    response = admin_client.get("/api/admin/users")

    assert response.status_code == 200
    customers = response.json()
    assert [customer["email"] for customer in customers] == [
        "alex.customer@demo.bank.test",
        "jordan.customer@demo.bank.test",
    ]
    assert all("password_hash" not in customer for customer in customers)


def test_admin_customer_detail_includes_accounts_and_paginated_transactions(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    customer_id = _user_id(session_factory, email=CUSTOMER_EMAIL)

    first_page = admin_client.get(
        f"/api/admin/users/{customer_id}",
        params={"limit": 2, "offset": 0},
    )
    second_page = admin_client.get(
        f"/api/admin/users/{customer_id}",
        params={"limit": 2, "offset": 2},
    )

    assert first_page.status_code == second_page.status_code == 200
    assert first_page.json()["customer"]["email"] == CUSTOMER_EMAIL
    assert len(first_page.json()["accounts"]) == 2
    assert all(isinstance(account["balance"], str) for account in first_page.json()["accounts"])
    assert len(first_page.json()["transactions"]) == 2
    assert first_page.json()["transaction_limit"] == 2
    assert second_page.json()["transaction_offset"] == 2
    assert {item["id"] for item in first_page.json()["transactions"]}.isdisjoint(
        item["id"] for item in second_page.json()["transactions"]
    )


def test_admin_detail_rejects_missing_or_admin_identity(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    admin_id = _user_id(session_factory, role=UserRole.ADMIN)

    missing_response = admin_client.get("/api/admin/users/999999")
    admin_response = admin_client.get(f"/api/admin/users/{admin_id}")

    assert missing_response.status_code == admin_response.status_code == 404
    assert missing_response.json() == admin_response.json() == NOT_FOUND_ERROR


def test_customer_is_forbidden_from_admin_customer_reads(
    customer_client: TestClient,
) -> None:
    list_response = customer_client.get("/api/admin/users")
    detail_response = customer_client.get("/api/admin/users/1")

    assert list_response.status_code == detail_response.status_code == 403
    assert list_response.json() == detail_response.json() == FORBIDDEN_ERROR
