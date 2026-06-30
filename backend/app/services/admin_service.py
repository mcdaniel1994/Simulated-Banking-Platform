from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session as DatabaseSession

from app.errors import NotFoundError
from app.models import (
    Account,
    AccountStatus,
    AuditEvent,
    Session,
    Transaction,
    User,
    UserRole,
)

RECENT_TRANSACTION_DAYS = 30


@dataclass(frozen=True)
class AdminDashboardSummary:
    # Dataclasses carry service results without coupling aggregate SQL to Pydantic or HTTP.
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

    # Separate scalar queries keep each dashboard definition explicit and independently testable.
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

    # Filtering in SQL prevents administrator identities from reaching response shaping.
    return list(db.scalars(select(User).where(User.role == UserRole.CUSTOMER).order_by(User.id)))


def get_customer_detail(
    db: DatabaseSession,
    *,
    user_id: int,
    limit: int,
    offset: int,
) -> AdminCustomerDetail:
    """Load one customer drill-down without reusing customer ownership dependencies."""

    # Admin visibility is distinct from ownership, but only CUSTOMER identities are managed here.
    customer = db.scalar(
        select(User).where(
            User.id == user_id,
            User.role == UserRole.CUSTOMER,
        )
    )
    if customer is None:
        raise NotFoundError

    # Accounts and history are separate so pagination applies only to the append-only feed.
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


def set_customer_active_status(
    db: DatabaseSession,
    *,
    admin: User,
    user_id: int,
    is_active: bool,
) -> User:
    """Atomically change customer status and revoke sessions on deactivation."""

    # Restricting this lookup to CUSTOMER prevents an admin from deactivating another admin.
    customer = db.scalar(
        select(User).where(
            User.id == user_id,
            User.role == UserRole.CUSTOMER,
        )
    )
    if customer is None:
        raise NotFoundError

    now = datetime.now(UTC)
    event_type = "user_activated" if is_active else "user_deactivated"
    try:
        customer.is_active = is_active
        if not is_active:
            # Bulk revocation makes every existing customer cookie unusable immediately.
            db.execute(
                update(Session)
                .where(
                    Session.user_id == customer.id,
                    Session.revoked_at.is_(None),
                )
                .values(revoked_at=now)
            )
        # State, session revocations, and audit evidence share one transaction boundary.
        db.add(
            AuditEvent(
                actor=admin,
                event_type=event_type,
                entity_type="user",
                entity_id=str(customer.id),
                event_metadata={"is_active": is_active},
                created_at=now,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return customer


def set_account_status(
    db: DatabaseSession,
    *,
    admin: User,
    account_id: int,
    account_status: AccountStatus,
) -> Account:
    """Atomically freeze or unfreeze an account and record the admin action."""

    # Admin management loads by ID without pretending the administrator owns the account.
    account = db.get(Account, account_id)
    if account is None:
        raise NotFoundError

    event_type = "account_frozen" if account_status is AccountStatus.FROZEN else "account_unfrozen"
    try:
        account.status = account_status
        # Record the numeric ID and state, never the sensitive account number.
        db.add(
            AuditEvent(
                actor=admin,
                event_type=event_type,
                entity_type="account",
                entity_id=str(account.id),
                event_metadata={"status": account_status.value},
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return account
