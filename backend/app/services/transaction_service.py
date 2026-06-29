from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession

from app.models import Account, Transaction, User


def list_account_transactions(
    db: DatabaseSession,
    *,
    account: Account,
    limit: int,
    offset: int,
) -> list[Transaction]:
    """Page newest-first history for one account already authorized by ownership."""

    return list(
        db.scalars(
            select(Transaction)
            .where(Transaction.account_id == account.id)
            .order_by(Transaction.created_at.desc(), Transaction.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )


def list_customer_transactions(
    db: DatabaseSession,
    *,
    customer: User,
    limit: int,
    offset: int,
) -> list[Transaction]:
    """Page newest-first history across only the authenticated customer's accounts."""

    # The ownership predicate is part of SQL so no other customer's history enters the service.
    return list(
        db.scalars(
            select(Transaction)
            .join(Account, Account.id == Transaction.account_id)
            .where(Account.user_id == customer.id)
            .order_by(Transaction.created_at.desc(), Transaction.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )
