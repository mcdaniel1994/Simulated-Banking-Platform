from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

from app.errors import InsufficientFundsError
from app.models import Account, AuditEvent, Transaction, TransactionType, User
from app.services.money_service import withdraw
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

CUSTOMER_EMAIL = "alex.customer@demo.bank.test"
ACCOUNT_NUMBER = "1000000001"


def test_concurrent_withdrawals_cannot_overdraw_locked_account(
    login_test_context: tuple[object, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    with session_factory() as db:
        customer_id = db.scalar(select(User.id).where(User.email == CUSTOMER_EMAIL))
        account_id = db.scalar(select(Account.id).where(Account.account_number == ACCOUNT_NUMBER))
        assert customer_id is not None and account_id is not None
        account = db.get(Account, account_id)
        assert account is not None
        account.balance = Decimal("100.00")
        db.commit()

    start = Barrier(2)

    def attempt_withdrawal() -> str:
        with session_factory() as db:
            customer = db.get(User, customer_id)
            assert customer is not None
            start.wait()
            try:
                withdraw(
                    db,
                    customer=customer,
                    account_id=account_id,
                    amount=Decimal("80.00"),
                )
            except InsufficientFundsError:
                return "insufficient"
            return "success"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _index: attempt_withdrawal(), range(2)))

    assert sorted(outcomes) == ["insufficient", "success"]
    with session_factory() as db:
        account = db.get(Account, account_id)
        assert account is not None
        assert account.balance == Decimal("20.00")
        assert account.balance >= 0
        assert (
            db.scalar(
                select(func.count())
                .select_from(Transaction)
                .where(
                    Transaction.account_id == account_id,
                    Transaction.transaction_type == TransactionType.WITHDRAWAL,
                    Transaction.description == "Customer withdrawal",
                )
            )
            == 1
        )
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "withdrawal")
            )
            == 1
        )
