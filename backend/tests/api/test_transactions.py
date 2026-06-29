from datetime import datetime

import pytest
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
    account_number: str,
) -> int:
    with session_factory() as db:
        account_id = db.scalar(
            select(Account.id)
            .join(User, User.id == Account.user_id)
            .where(
                User.email == owner_email,
                Account.account_number == account_number,
            )
        )
    assert account_id is not None
    return account_id


def test_owned_account_history_is_newest_first_and_paginated(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    checking_id = _account_id_for(session_factory, CUSTOMER_EMAIL, "1000000001")

    first_page = customer_client.get(
        f"/api/accounts/{checking_id}/transactions",
        params={"limit": 2, "offset": 0},
    )
    second_page = customer_client.get(
        f"/api/accounts/{checking_id}/transactions",
        params={"limit": 2, "offset": 2},
    )

    assert first_page.status_code == second_page.status_code == 200
    assert [item["transaction_type"] for item in first_page.json()] == [
        "TRANSFER_OUT",
        "WITHDRAWAL",
    ]
    assert [item["transaction_type"] for item in second_page.json()] == ["DEPOSIT"]
    assert first_page.json()[0]["amount"] == "200.00"
    assert first_page.json()[0]["balance_after"] == "1175.00"


def test_cross_account_history_is_chronological_owned_and_paginated(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    owned_ids = {
        _account_id_for(session_factory, CUSTOMER_EMAIL, "1000000001"),
        _account_id_for(session_factory, CUSTOMER_EMAIL, "1000000002"),
    }

    first_page = customer_client.get("/api/transactions", params={"limit": 3, "offset": 0})
    second_page = customer_client.get("/api/transactions", params={"limit": 3, "offset": 3})

    assert first_page.status_code == second_page.status_code == 200
    first_items = first_page.json()
    second_items = second_page.json()
    assert len(first_items) == len(second_items) == 3
    assert {item["account_id"] for item in [*first_items, *second_items]} == owned_ids
    assert {item["id"] for item in first_items}.isdisjoint(item["id"] for item in second_items)

    timestamps = [
        datetime.fromisoformat(item["created_at"]) for item in [*first_items, *second_items]
    ]
    assert timestamps == sorted(timestamps, reverse=True)


def test_non_owned_account_history_returns_not_found(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    other_account_id = _account_id_for(
        session_factory,
        OTHER_CUSTOMER_EMAIL,
        "1000000003",
    )

    response = customer_client.get(f"/api/accounts/{other_account_id}/transactions")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_ERROR


@pytest.mark.parametrize(
    "path",
    [
        "/api/transactions?limit=0",
        "/api/transactions?limit=101",
        "/api/transactions?offset=-1",
    ],
)
def test_invalid_pagination_returns_validation_error(
    path: str,
    customer_client: TestClient,
) -> None:
    response = customer_client.get(path)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_admin_cannot_read_customer_transaction_history(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    customer_account_id = _account_id_for(
        session_factory,
        CUSTOMER_EMAIL,
        "1000000001",
    )

    account_response = admin_client.get(f"/api/accounts/{customer_account_id}/transactions")
    combined_response = admin_client.get("/api/transactions")

    assert account_response.status_code == combined_response.status_code == 403
    assert account_response.json() == combined_response.json() == FORBIDDEN_ERROR


def test_transaction_money_is_declared_as_string_in_openapi() -> None:
    transaction_schema = app.openapi()["components"]["schemas"]["TransactionResponse"]

    assert transaction_schema["properties"]["amount"]["type"] == "string"
    assert transaction_schema["properties"]["balance_after"]["type"] == "string"
