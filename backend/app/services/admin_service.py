from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DatabaseSession

from app.errors import NotFoundError
from app.models import Account, Transaction, User, UserRole

RECENT_TRANSACTION_DAYS = 30


@dataclass(frozen=True)
class AdminDashboardSummary:
    customer_count: int
    account_count: int
    total_simulated_balance: Decimal
    recent_transaction_count: int
    recent_window_days: int = RECENT_TRANSACTION_DAYS


@dataclass(frozen=True)
class AdminCustomerDetail:
    customer: User
    accounts: list[Account]
    transactions: list[Transaction]
    transaction_limit: int
    transaction_offset: int


def get_dashboard_summary(db: DatabaseSession) -> AdminDashboardSummary:
    """Compute administrator aggregates directly in PostgreSQL."""

    recent_cutoff = datetime.now(UTC) - timedelta(days=RECENT_TRANSACTION_DAYS)
    customer_count = db.scalar(
        select(func.count()).select_from(User).where(User.role == UserRole.CUSTOMER)
    )
    account_count = db.scalar(select(func.count()).select_from(Account))
    total_balance = db.scalar(select(func.coalesce(func.sum(Account.balance), Decimal("0.00"))))
    recent_count = db.scalar(
        select(func.count()).select_from(Transaction).where(Transaction.created_at >= recent_cutoff)
    )

    return AdminDashboardSummary(
        customer_count=customer_count or 0,
        account_count=account_count or 0,
        total_simulated_balance=total_balance or Decimal("0.00"),
        recent_transaction_count=recent_count or 0,
    )


def list_customers(db: DatabaseSession) -> list[User]:
    """List managed customers without including administrator identities."""

    return list(db.scalars(select(User).where(User.role == UserRole.CUSTOMER).order_by(User.id)))


def get_customer_detail(
    db: DatabaseSession,
    *,
    user_id: int,
    limit: int,
    offset: int,
) -> AdminCustomerDetail:
    """Load one customer drill-down without reusing customer ownership dependencies."""

    customer = db.scalar(
        select(User).where(
            User.id == user_id,
            User.role == UserRole.CUSTOMER,
        )
    )
    if customer is None:
        raise NotFoundError

    accounts = list(
        db.scalars(select(Account).where(Account.user_id == customer.id).order_by(Account.id))
    )
    transactions = list(
        db.scalars(
            select(Transaction)
            .join(Account, Account.id == Transaction.account_id)
            .where(Account.user_id == customer.id)
            .order_by(Transaction.created_at.desc(), Transaction.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return AdminCustomerDetail(
        customer=customer,
        accounts=accounts,
        transactions=transactions,
        transaction_limit=limit,
        transaction_offset=offset,
    )
