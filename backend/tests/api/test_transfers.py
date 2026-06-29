from decimal import Decimal

import pytest
from app.models import (
    Account,
    AccountStatus,
    AuditEvent,
    Transaction,
    TransactionType,
    Transfer,
)
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker


def _account_id(
    session_factory: sessionmaker[DatabaseSession],
    account_number: str,
) -> int:
    with session_factory() as db:
        account_id = db.scalar(select(Account.id).where(Account.account_number == account_number))
    assert account_id is not None
    return account_id


def _csrf_headers(client: TestClient) -> dict[str, str]:
    token = client.cookies.get("csrf_token")
    assert token is not None
    return {"X-CSRF-Token": token}


def _transfer_payload(
    source_account_id: int,
    destination_account_id: int,
    amount: str = "200.00",
) -> dict[str, int | str]:
    return {
        "source_account_id": source_account_id,
        "destination_account_id": destination_account_id,
        "amount": amount,
    }


def test_transfer_atomically_moves_money_writes_legs_and_audit(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    source_id = _account_id(session_factory, "1000000001")
    destination_id = _account_id(session_factory, "1000000002")

    response = customer_client.post(
        "/api/transfers",
        json=_transfer_payload(source_id, destination_id),
        headers=_csrf_headers(customer_client),
    )

    assert response.status_code == 201
    assert response.json()["amount"] == "200.00"
    transfer_id = response.json()["id"]
    with session_factory() as db:
        source = db.get(Account, source_id)
        destination = db.get(Account, destination_id)
        legs = list(
            db.scalars(
                select(Transaction)
                .where(Transaction.reference_id == transfer_id)
                .order_by(Transaction.id)
            )
        )
        audit = db.scalar(
            select(AuditEvent).where(
                AuditEvent.event_type == "transfer",
                AuditEvent.entity_id == str(transfer_id),
            )
        )
        assert source is not None and source.balance == Decimal("975.00")
        assert destination is not None and destination.balance == Decimal("3650.00")
        assert [leg.transaction_type for leg in legs] == [
            TransactionType.TRANSFER_OUT,
            TransactionType.TRANSFER_IN,
        ]
        assert [leg.balance_after for leg in legs] == [
            Decimal("975.00"),
            Decimal("3650.00"),
        ]
        assert audit is not None

    detail_response = customer_client.get(f"/api/transfers/{transfer_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == transfer_id


def test_same_account_transfer_is_rejected_without_writes(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    account_id = _account_id(session_factory, "1000000001")

    response = customer_client.post(
        "/api/transfers",
        json=_transfer_payload(account_id, account_id),
        headers=_csrf_headers(customer_client),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "SAME_ACCOUNT_TRANSFER"
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(Transfer)) == 2


@pytest.mark.parametrize("foreign_role", ["source", "destination"])
def test_non_owned_transfer_account_returns_not_found(
    foreign_role: str,
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    source_id = _account_id(session_factory, "1000000001")
    destination_id = _account_id(session_factory, "1000000002")
    foreign_id = _account_id(session_factory, "1000000003")
    if foreign_role == "source":
        source_id = foreign_id
    else:
        destination_id = foreign_id

    response = customer_client.post(
        "/api/transfers",
        json=_transfer_payload(source_id, destination_id),
        headers=_csrf_headers(customer_client),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_transfer_rejects_insufficient_funds_and_inactive_accounts(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    source_id = _account_id(session_factory, "1000000001")
    destination_id = _account_id(session_factory, "1000000002")

    insufficient = customer_client.post(
        "/api/transfers",
        json=_transfer_payload(source_id, destination_id, "2000.00"),
        headers=_csrf_headers(customer_client),
    )
    with session_factory() as db:
        destination = db.get(Account, destination_id)
        assert destination is not None
        destination.status = AccountStatus.FROZEN
        db.commit()
    inactive = customer_client.post(
        "/api/transfers",
        json=_transfer_payload(source_id, destination_id, "10.00"),
        headers=_csrf_headers(customer_client),
    )

    assert insufficient.status_code == 409
    assert insufficient.json()["error"]["code"] == "INSUFFICIENT_FUNDS"
    assert inactive.status_code == 409
    assert inactive.json()["error"]["code"] == "INACTIVE_ACCOUNT"


def test_induced_post_flush_failure_rolls_back_entire_transfer(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    source_id = _account_id(session_factory, "1000000001")
    destination_id = _account_id(session_factory, "1000000002")

    def fail_after_flush(_session: DatabaseSession, _flush_context: object) -> None:
        raise RuntimeError("induced transfer failure")

    event.listen(DatabaseSession, "after_flush_postexec", fail_after_flush)
    try:
        response = customer_client.post(
            "/api/transfers",
            json=_transfer_payload(source_id, destination_id),
            headers=_csrf_headers(customer_client),
        )
    finally:
        event.remove(DatabaseSession, "after_flush_postexec", fail_after_flush)

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    with session_factory() as db:
        source = db.get(Account, source_id)
        destination = db.get(Account, destination_id)
        assert source is not None and source.balance == Decimal("1175.00")
        assert destination is not None and destination.balance == Decimal("3450.00")
        assert db.scalar(select(func.count()).select_from(Transfer)) == 2
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "transfer")
            )
            == 0
        )


def test_transfer_requires_csrf_and_owned_detail(
    customer_client: TestClient,
    login_test_context: tuple[TestClient, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    source_id = _account_id(session_factory, "1000000001")
    destination_id = _account_id(session_factory, "1000000002")

    csrf_response = customer_client.post(
        "/api/transfers",
        json=_transfer_payload(source_id, destination_id),
    )
    foreign_transfer_id = 2
    detail_response = customer_client.get(f"/api/transfers/{foreign_transfer_id}")

    assert csrf_response.status_code == 403
    assert csrf_response.json()["error"]["code"] == "CSRF_INVALID"
    assert detail_response.status_code == 404
    assert detail_response.json()["error"]["code"] == "NOT_FOUND"
