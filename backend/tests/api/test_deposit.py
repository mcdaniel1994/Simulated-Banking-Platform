from decimal import Decimal

import pytest
from app.models import Account, AccountStatus, AuditEvent, Transaction, TransactionType, User
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

CUSTOMER_EMAIL = "alex.customer@demo.bank.test"
ACCOUNT_NUMBER = "1000000001"


def _account_id(
    session_factory: sessionmaker[DatabaseSession],
) -> int:
    with session_factory() as db:
        account_id = db.scalar(
            select(Account.id)
            .join(User, User.id == Account.user_id)
            .where(
                User.email == CUSTOMER_EMAIL,
                Account.account_number == ACCOUNT_NUMBER,
            )
        )
    assert account_id is not None
    return account_id


def _csrf_headers(client: TestClient) -> dict[str, str]:
    token = client.cookies.get("csrf_token")
    assert token is not None
    return {"X-CSRF-Token": token}


def test_deposit_atomically_updates_balance_history_and_audit(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    account_id = _account_id(session_factory)

    response = customer_client.post(
        f"/api/accounts/{account_id}/deposits",
        json={"amount": "100.25"},
        headers=_csrf_headers(customer_client),
    )

    assert response.status_code == 200
    assert response.json()["balance"] == "1275.25"
    with session_factory() as db:
        account = db.get(Account, account_id)
        transaction = db.scalar(
            select(Transaction)
            .where(
                Transaction.account_id == account_id,
                Transaction.transaction_type == TransactionType.DEPOSIT,
                Transaction.description == "Demo funding deposit",
            )
            .order_by(Transaction.id.desc())
        )
        audit = db.scalar(
            select(AuditEvent).where(
                AuditEvent.event_type == "deposit",
                AuditEvent.entity_id == str(account_id),
            )
        )
        assert account is not None
        assert account.balance == Decimal("1275.25")
        assert transaction is not None
        assert transaction.amount == Decimal("100.25")
        assert transaction.balance_after == Decimal("1275.25")
        assert audit is not None
        assert audit.event_metadata == {"amount": "100.25"}


@pytest.mark.parametrize(
    "amount",
    ["0.00", "-1.00", "1.001", "1000000000000.00"],
)
def test_deposit_rejects_invalid_amount_without_writes(
    amount: str,
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    account_id = _account_id(session_factory)

    response = customer_client.post(
        f"/api/accounts/{account_id}/deposits",
        json={"amount": amount},
        headers=_csrf_headers(customer_client),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    with session_factory() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "deposit")
            )
            == 0
        )


def test_deposit_rejects_json_number_to_keep_float_out_of_money_path(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    account_id = _account_id(session_factory)

    response = customer_client.post(
        f"/api/accounts/{account_id}/deposits",
        json={"amount": 10.25},
        headers=_csrf_headers(customer_client),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize("account_status", [AccountStatus.FROZEN, AccountStatus.CLOSED])
def test_deposit_rejects_non_active_account_without_writes(
    account_status: AccountStatus,
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    account_id = _account_id(session_factory)
    with session_factory() as db:
        account = db.get(Account, account_id)
        assert account is not None
        account.status = account_status
        db.commit()

    response = customer_client.post(
        f"/api/accounts/{account_id}/deposits",
        json={"amount": "10.00"},
        headers=_csrf_headers(customer_client),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INACTIVE_ACCOUNT"
    with session_factory() as db:
        account = db.get(Account, account_id)
        assert account is not None
        assert account.balance == Decimal("1175.00")
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "deposit")
            )
            == 0
        )


def test_deposit_requires_matching_csrf_before_writes(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    account_id = _account_id(session_factory)

    response = customer_client.post(
        f"/api/accounts/{account_id}/deposits",
        json={"amount": "10.00"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "CSRF_INVALID"
    with session_factory() as db:
        account = db.get(Account, account_id)
        assert account is not None
        assert account.balance == Decimal("1175.00")
