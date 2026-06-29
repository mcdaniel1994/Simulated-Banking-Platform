from app.errors import FORBIDDEN_ERROR, NOT_FOUND_ERROR
from app.main import app
from app.models import Account, User
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

CUSTOMER_EMAIL = "alex.customer@demo.bank.test"
OTHER_CUSTOMER_EMAIL = "jordan.customer@demo.bank.test"


def _account_id_for(
    session_factory: sessionmaker[DatabaseSession],
    owner_email: str,
) -> int:
    with session_factory() as db:
        account_id = db.scalar(
            select(Account.id)
            .join(User, User.id == Account.user_id)
            .where(User.email == owner_email)
            .order_by(Account.id)
        )
    assert account_id is not None
    return account_id


def test_account_list_contains_only_customer_accounts_with_string_balances(
    customer_client: TestClient,
) -> None:
    response = customer_client.get("/api/accounts")

    assert response.status_code == 200
    accounts = response.json()
    assert [account["account_number"] for account in accounts] == ["1000000001", "1000000002"]
    assert [account["balance"] for account in accounts] == ["1175.00", "3450.00"]
    assert all(isinstance(account["balance"], str) for account in accounts)
    assert all(
        set(account)
        == {
            "id",
            "account_number",
            "account_type",
            "balance",
            "status",
            "created_at",
            "updated_at",
        }
        for account in accounts
    )


def test_customer_can_get_owned_account_detail(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    account_id = _account_id_for(session_factory, CUSTOMER_EMAIL)

    response = customer_client.get(f"/api/accounts/{account_id}")

    assert response.status_code == 200
    assert response.json()["id"] == account_id
    assert response.json()["balance"] == "1175.00"
    assert "user_id" not in response.json()


def test_customer_cannot_get_another_customers_account(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    other_account_id = _account_id_for(session_factory, OTHER_CUSTOMER_EMAIL)

    response = customer_client.get(f"/api/accounts/{other_account_id}")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_ERROR


def test_admin_cannot_use_customer_account_routes(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    account_id = _account_id_for(session_factory, CUSTOMER_EMAIL)

    list_response = admin_client.get("/api/accounts")
    detail_response = admin_client.get(f"/api/accounts/{account_id}")

    assert list_response.status_code == 403
    assert detail_response.status_code == 403
    assert list_response.json() == detail_response.json() == FORBIDDEN_ERROR


def test_account_balance_is_declared_as_string_in_openapi() -> None:
    account_schema = app.openapi()["components"]["schemas"]["AccountResponse"]

    assert account_schema["properties"]["balance"]["type"] == "string"
