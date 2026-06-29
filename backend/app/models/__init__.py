# Importing this package registers every mapped table on the shared Base metadata.
from app.models.account import Account, AccountStatus, AccountType
from app.models.audit_event import AuditEvent
from app.models.session import Session
from app.models.transaction import Transaction, TransactionType
from app.models.transfer import Transfer, TransferStatus
from app.models.user import User, UserRole

# Explicit exports give services, tests, and future Alembic setup one stable model entry point.
__all__ = [
    "Account",
    "AccountStatus",
    "AccountType",
    "AuditEvent",
    "Session",
    "Transaction",
    "TransactionType",
    "Transfer",
    "TransferStatus",
    "User",
    "UserRole",
]
