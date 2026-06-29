import pytest
from app.api.deps import FORBIDDEN_ERROR, NOT_FOUND_ERROR, OwnedAccount
from app.main import app
from app.models import Account, User
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

CUSTOMER_EMAIL = "alex.customer@demo.bank.test"
OTHER_CUSTOMER_EMAIL = "jordan.customer@demo.bank.test"


# This probe verifies dependency wiring without introducing Phase 18 account response behavior.
@app.get("/api/test-only/accounts/{account_id}")
def owned_account_probe(account: OwnedAccount) -> dict[str, int]:
    return {"id": account.id, "user_id": account.user_id}


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


def test_customer_can_load_an_owned_account(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    own_account_id = _account_id_for(session_factory, CUSTOMER_EMAIL)

    response = customer_client.get(f"/api/test-only/accounts/{own_account_id}")

    assert response.status_code == 200
    assert response.json()["id"] == own_account_id


@pytest.mark.parametrize("resource_state", ["other-owner", "missing"])
def test_customer_receives_same_not_found_for_non_owned_or_missing_account(
    resource_state: str,
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    if resource_state == "other-owner":
        account_id = _account_id_for(session_factory, OTHER_CUSTOMER_EMAIL)
    else:
        with session_factory() as db:
            highest_id = db.scalar(select(func.max(Account.id)))
        assert highest_id is not None
        account_id = highest_id + 1
    response = customer_client.get(f"/api/test-only/accounts/{account_id}")

    assert response.status_code == 404
    assert response.json() == NOT_FOUND_ERROR


def test_admin_cannot_use_customer_ownership_dependency(
    admin_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    customer_account_id = _account_id_for(session_factory, CUSTOMER_EMAIL)

    response = admin_client.get(f"/api/test-only/accounts/{customer_account_id}")

    assert response.status_code == 403
    assert response.json() == FORBIDDEN_ERROR
