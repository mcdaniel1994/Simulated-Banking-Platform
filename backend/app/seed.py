from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession

from app.core.security import hash_password, needs_rehash, verify_password
from app.db.session import SessionLocal
from app.models import (
    Account,
    AccountStatus,
    AccountType,
    Transaction,
    TransactionType,
    Transfer,
    TransferStatus,
    User,
    UserRole,
)

# These synthetic credentials are intentionally public and will appear on the future login page.
ADMIN_EMAIL = "admin@demo.bank.test"
ADMIN_PASSWORD = "AdminDemo!2026"
CUSTOMER_PASSWORD = "CustomerDemo!2026"


@dataclass(frozen=True)
class DemoUser:
    email: str
    password: str
    first_name: str
    last_name: str
    role: UserRole


@dataclass(frozen=True)
class DemoAccountPair:
    owner_email: str
    checking_number: str
    savings_number: str
    checking_opening: Decimal
    checking_withdrawal: Decimal
    savings_opening: Decimal
    savings_deposit: Decimal
    transfer_amount: Decimal
    timeline_start: datetime


DEMO_USERS = (
    DemoUser(ADMIN_EMAIL, ADMIN_PASSWORD, "Avery", "Admin", UserRole.ADMIN),
    DemoUser(
        "alex.customer@demo.bank.test",
        CUSTOMER_PASSWORD,
        "Alex",
        "Carter",
        UserRole.CUSTOMER,
    ),
    DemoUser(
        "jordan.customer@demo.bank.test",
        CUSTOMER_PASSWORD,
        "Jordan",
        "Lee",
        UserRole.CUSTOMER,
    ),
)

# Fixed natural keys, amounts, and timestamps keep every clean seed reproducible.
DEMO_ACCOUNT_PAIRS = (
    DemoAccountPair(
        owner_email="alex.customer@demo.bank.test",
        checking_number="1000000001",
        savings_number="1000000002",
        checking_opening=Decimal("1500.00"),
        checking_withdrawal=Decimal("125.00"),
        savings_opening=Decimal("3000.00"),
        savings_deposit=Decimal("250.00"),
        transfer_amount=Decimal("200.00"),
        timeline_start=datetime(2026, 1, 15, 12, tzinfo=UTC),
    ),
    DemoAccountPair(
        owner_email="jordan.customer@demo.bank.test",
        checking_number="1000000003",
        savings_number="1000000004",
        checking_opening=Decimal("2200.00"),
        checking_withdrawal=Decimal("180.00"),
        savings_opening=Decimal("4200.00"),
        savings_deposit=Decimal("150.00"),
        transfer_amount=Decimal("300.00"),
        timeline_start=datetime(2026, 2, 1, 12, tzinfo=UTC),
    ),
)


def _get_or_create_user(db: DatabaseSession, spec: DemoUser) -> User:
    user = db.scalar(select(User).where(User.email == spec.email))
    if user is None:
        # Hash only on creation so idempotent reruns do not churn randomly salted values.
        user = User(
            email=spec.email,
            password_hash=hash_password(spec.password),
            first_name=spec.first_name,
            last_name=spec.last_name,
            role=spec.role,
            is_active=True,
            created_at=datetime(2026, 1, 1, 12, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, 12, tzinfo=UTC),
        )
        db.add(user)
        return user

    # Restore public demo access or stronger parameters without exposing the plaintext or hash.
    password_matches = verify_password(spec.password, user.password_hash)
    if not password_matches or needs_rehash(user.password_hash):
        user.password_hash = hash_password(spec.password)

    # Keep role/profile drift deterministic while preserving unrelated user state.
    user.first_name = spec.first_name
    user.last_name = spec.last_name
    user.role = spec.role
    user.is_active = True
    return user


def _get_account(db: DatabaseSession, account_number: str) -> Account | None:
    return db.scalar(select(Account).where(Account.account_number == account_number))


def _create_account_history(
    db: DatabaseSession,
    owner: User,
    spec: DemoAccountPair,
) -> None:
    checking = _get_account(db, spec.checking_number)
    savings = _get_account(db, spec.savings_number)

    if checking is not None and savings is not None:
        # Existing account pairs retain any later append-only activity from reviewer use.
        if checking.user_id != owner.id or savings.user_id != owner.id:
            raise ValueError("demo account number belongs to an unexpected user")
        return
    if checking is not None or savings is not None:
        # A half-created pair indicates manual drift; guessing would risk corrupting reconciliation.
        raise ValueError("demo customer has a partial account pair")

    withdrawal_time = spec.timeline_start + timedelta(days=20)
    deposit_time = spec.timeline_start + timedelta(days=35)
    transfer_time = spec.timeline_start + timedelta(days=50)
    checking_balance = spec.checking_opening - spec.checking_withdrawal - spec.transfer_amount
    savings_balance = spec.savings_opening + spec.savings_deposit + spec.transfer_amount

    # Stored balances equal the final signed transaction sums built immediately below.
    checking = Account(
        user=owner,
        account_number=spec.checking_number,
        account_type=AccountType.CHECKING,
        balance=checking_balance,
        status=AccountStatus.ACTIVE,
        created_at=spec.timeline_start,
        updated_at=transfer_time,
    )
    savings = Account(
        user=owner,
        account_number=spec.savings_number,
        account_type=AccountType.SAVINGS,
        balance=savings_balance,
        status=AccountStatus.ACTIVE,
        created_at=spec.timeline_start + timedelta(hours=1),
        updated_at=transfer_time,
    )
    db.add_all([checking, savings])
    db.flush()

    # Opening deposits establish the transaction log as the source of truth from the first cent.
    transactions = [
        Transaction(
            account=checking,
            transaction_type=TransactionType.DEPOSIT,
            amount=spec.checking_opening,
            description="Demo opening balance",
            balance_after=spec.checking_opening,
            created_at=spec.timeline_start,
        ),
        Transaction(
            account=checking,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=spec.checking_withdrawal,
            description="Demo bill payment",
            balance_after=spec.checking_opening - spec.checking_withdrawal,
            created_at=withdrawal_time,
        ),
        Transaction(
            account=savings,
            transaction_type=TransactionType.DEPOSIT,
            amount=spec.savings_opening,
            description="Demo opening balance",
            balance_after=spec.savings_opening,
            created_at=spec.timeline_start + timedelta(hours=1),
        ),
        Transaction(
            account=savings,
            transaction_type=TransactionType.DEPOSIT,
            amount=spec.savings_deposit,
            description="Demo savings contribution",
            balance_after=spec.savings_opening + spec.savings_deposit,
            created_at=deposit_time,
        ),
    ]

    # One parent transfer links the matching debit and credit legs atomically.
    transfer = Transfer(
        source_account=checking,
        destination_account=savings,
        amount=spec.transfer_amount,
        status=TransferStatus.COMPLETED,
        created_at=transfer_time,
    )
    transactions.extend(
        [
            Transaction(
                account=checking,
                transfer=transfer,
                transaction_type=TransactionType.TRANSFER_OUT,
                amount=spec.transfer_amount,
                description="Demo transfer to savings",
                balance_after=checking_balance,
                created_at=transfer_time,
            ),
            Transaction(
                account=savings,
                transfer=transfer,
                transaction_type=TransactionType.TRANSFER_IN,
                amount=spec.transfer_amount,
                description="Demo transfer from checking",
                balance_after=savings_balance,
                created_at=transfer_time,
            ),
        ]
    )
    db.add_all([transfer, *transactions])


def seed_database(db: DatabaseSession) -> None:
    """Create or restore the deterministic demo dataset in one transaction."""

    try:
        users = {spec.email: _get_or_create_user(db, spec) for spec in DEMO_USERS}
        db.flush()
        for account_pair in DEMO_ACCOUNT_PAIRS:
            _create_account_history(db, users[account_pair.owner_email], account_pair)
        db.commit()
    except Exception:
        # Atomic rollback prevents a failed seed from leaving only part of the demo graph.
        db.rollback()
        raise


def print_demo_credentials() -> None:
    """Print only the intentionally public credentials needed by reviewers."""

    print("Demo administrator:")
    print(f"  Email: {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print("Demo customer:")
    print(f"  Email: {DEMO_USERS[1].email}")
    print(f"  Password: {CUSTOMER_PASSWORD}")


def main() -> None:
    """Seed the configured development database from the command line."""

    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    print_demo_credentials()


if __name__ == "__main__":
    main()
