from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession

from app.errors import NotFoundError
from app.models import Account, Transaction, TransactionType

POSITIVE_TYPES = frozenset({TransactionType.DEPOSIT, TransactionType.TRANSFER_IN})


@dataclass(frozen=True)
class ReconciliationResult:
    """Comparison between the balance cache and signed append-only history."""

    account_id: int
    stored_balance: Decimal
    calculated_balance: Decimal

    @property
    def matches(self) -> bool:
        return self.stored_balance == self.calculated_balance


def reconcile_account(
    db: DatabaseSession,
    *,
    account_id: int,
) -> ReconciliationResult:
    """Calculate one account balance from its immutable transaction history."""

    account = db.get(Account, account_id)
    if account is None:
        raise NotFoundError

    calculated = Decimal("0.00")
    rows = db.execute(
        select(Transaction.transaction_type, Transaction.amount).where(
            Transaction.account_id == account_id
        )
    )
    for transaction_type, amount in rows:
        calculated += amount if transaction_type in POSITIVE_TYPES else -amount

    return ReconciliationResult(
        account_id=account.id,
        stored_balance=account.balance,
        calculated_balance=calculated,
    )
