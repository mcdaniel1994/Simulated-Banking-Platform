from decimal import Decimal

from app.models import Account, User
from app.services.money_service import deposit, withdraw
from app.services.reconciliation import reconcile_account
from app.services.transfer_service import transfer_money
from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

CUSTOMER_EMAIL = "alex.customer@demo.bank.test"


def test_reconciliation_holds_for_seeded_and_freshly_mutated_accounts(
    login_test_context: tuple[object, sessionmaker[DatabaseSession]],
) -> None:
    _client, session_factory = login_test_context
    with session_factory() as db:
        customer = db.scalar(select(User).where(User.email == CUSTOMER_EMAIL))
        account_ids = list(
            db.scalars(
                select(Account.id).where(Account.user_id == customer.id).order_by(Account.id)
            )
        )
        assert customer is not None
        assert len(account_ids) == 2

        deposit(db, customer=customer, account_id=account_ids[0], amount=Decimal("25.00"))
        withdraw(db, customer=customer, account_id=account_ids[0], amount=Decimal("10.00"))
        transfer_money(
            db,
            customer=customer,
            source_account_id=account_ids[0],
            destination_account_id=account_ids[1],
            amount=Decimal("15.00"),
        )

        results = [reconcile_account(db, account_id=account_id) for account_id in account_ids]

    assert all(result.matches for result in results)
    assert all(result.stored_balance == result.calculated_balance for result in results)
