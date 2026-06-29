from decimal import Decimal

import pytest
from app.models import Account, AccountStatus, AuditEvent, Transaction, TransactionType, User
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

CUSTOMER_EMAIL = "alex.customer@demo.bank.test"
ACCOUNT_NUMBER = "1000000001"


def _account_id(session_factory: sessionmaker[DatabaseSession]) -> int:
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


def test_withdrawal_atomically_updates_balance_history_and_audit(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    account_id = _account_id(session_factory)

    response = customer_client.post(
        f"/api/accounts/{account_id}/withdrawals",
        json={"amount": "100.25"},
        headers=_csrf_headers(customer_client),
    )

    assert response.status_code == 200
    assert response.json()["balance"] == "1074.75"
    with session_factory() as db:
        account = db.get(Account, account_id)
        transaction = db.scalar(
            select(Transaction)
            .where(
                Transaction.account_id == account_id,
                Transaction.transaction_type == TransactionType.WITHDRAWAL,
                Transaction.description == "Customer withdrawal",
            )
            .order_by(Transaction.id.desc())
        )
        audit = db.scalar(
            select(AuditEvent).where(
                AuditEvent.event_type == "withdrawal",
                AuditEvent.entity_id == str(account_id),
            )
        )
        assert account is not None
        assert account.balance == Decimal("1074.75")
        assert transaction is not None
        assert transaction.amount == Decimal("100.25")
        assert transaction.balance_after == Decimal("1074.75")
        assert audit is not None


def test_insufficient_funds_changes_nothing(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    account_id = _account_id(session_factory)
    with session_factory() as db:
        original_transaction_count = db.scalar(
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.account_id == account_id)
        )

    response = customer_client.post(
        f"/api/accounts/{account_id}/withdrawals",
        json={"amount": "2000.00"},
        headers=_csrf_headers(customer_client),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INSUFFICIENT_FUNDS"
    with session_factory() as db:
        account = db.get(Account, account_id)
        assert account is not None
        assert account.balance == Decimal("1175.00")
        assert (
            db.scalar(
                select(func.count())
                .select_from(Transaction)
                .where(Transaction.account_id == account_id)
            )
            == original_transaction_count
        )
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "withdrawal")
            )
            == 0
        )


@pytest.mark.parametrize("account_status", [AccountStatus.FROZEN, AccountStatus.CLOSED])
def test_withdrawal_rejects_non_active_account(
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
        f"/api/accounts/{account_id}/withdrawals",
        json={"amount": "10.00"},
        headers=_csrf_headers(customer_client),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INACTIVE_ACCOUNT"


def test_withdrawal_rejects_invalid_amount_and_missing_csrf(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    account_id = _account_id(session_factory)

    invalid_response = customer_client.post(
        f"/api/accounts/{account_id}/withdrawals",
        json={"amount": "0.00"},
        headers=_csrf_headers(customer_client),
    )
    csrf_response = customer_client.post(
        f"/api/accounts/{account_id}/withdrawals",
        json={"amount": "10.00"},
    )

    assert invalid_response.status_code == 422
    assert invalid_response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert csrf_response.status_code == 403
    assert csrf_response.json()["error"]["code"] == "CSRF_INVALID"
