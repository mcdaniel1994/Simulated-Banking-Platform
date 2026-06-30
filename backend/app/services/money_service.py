from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession

from app.errors import (
    InactiveAccountError,
    InsufficientFundsError,
    NotFoundError,
    ValidationError,
)
from app.models import Account, AccountStatus, AuditEvent, Transaction, TransactionType, User
from app.schemas.money import MAX_MONEY_AMOUNT


def _lock_owned_account(
    db: DatabaseSession,
    *,
    account_id: int,
    customer_id: int,
) -> Account:
    """Lock one customer-owned account for the current money transaction."""

    # Read ownership and balance only after PostgreSQL grants the row lock.
    account = db.scalar(
        select(Account)
        .where(
            Account.id == account_id,
            Account.user_id == customer_id,
        )
        .with_for_update()
    )
    if account is None:
        raise NotFoundError
    return account


def deposit(
    db: DatabaseSession,
    *,
    customer: User,
    account_id: int,
    amount: Decimal,
) -> Account:
    """Atomically increase one active account and append its history and audit rows."""

    try:
        # Re-lock because the route's earlier ownership dependency performed an unlocked read.
        account = _lock_owned_account(
            db,
            account_id=account_id,
            customer_id=customer.id,
        )
        if account.status is not AccountStatus.ACTIVE:
            raise InactiveAccountError

        # Validate the resulting stored value before PostgreSQL NUMERIC could overflow.
        updated_balance = account.balance + amount
        if updated_balance > MAX_MONEY_AMOUNT:
            raise ValidationError(fields={"amount": "Resulting balance exceeds supported limit"})

        account.balance = updated_balance
        # Balance cache, append-only history, and audit evidence share one commit.
        db.add_all(
            [
                Transaction(
                    account=account,
                    transaction_type=TransactionType.DEPOSIT,
                    amount=amount,
                    description="Demo funding deposit",
                    balance_after=updated_balance,
                ),
                AuditEvent(
                    actor=customer,
                    event_type="deposit",
                    entity_type="account",
                    entity_id=str(account.id),
                    event_metadata={"amount": format(amount, ".2f")},
                ),
            ]
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return account


def withdraw(
    db: DatabaseSession,
    *,
    customer: User,
    account_id: int,
    amount: Decimal,
) -> Account:
    """Atomically debit one active account without permitting an overdraft."""

    try:
        account = _lock_owned_account(
            db,
            account_id=account_id,
            customer_id=customer.id,
        )
        if account.status is not AccountStatus.ACTIVE:
            raise InactiveAccountError
        # Checking funds under the lock prevents concurrent requests from using stale balances.
        if account.balance < amount:
            raise InsufficientFundsError

        updated_balance = account.balance - amount
        account.balance = updated_balance
        # Any failed commit rolls back the balance, history, and audit together.
        db.add_all(
            [
                Transaction(
                    account=account,
                    transaction_type=TransactionType.WITHDRAWAL,
                    amount=amount,
                    description="Customer withdrawal",
                    balance_after=updated_balance,
                ),
                AuditEvent(
                    actor=customer,
                    event_type="withdrawal",
                    entity_type="account",
                    entity_id=str(account.id),
                    event_metadata={"amount": format(amount, ".2f")},
                ),
            ]
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return account
