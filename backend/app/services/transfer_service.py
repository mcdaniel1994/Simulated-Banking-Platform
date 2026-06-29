from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import aliased

from app.errors import (
    InactiveAccountError,
    InsufficientFundsError,
    NotFoundError,
    SameAccountTransferError,
    ValidationError,
)
from app.models import (
    Account,
    AccountStatus,
    AuditEvent,
    Transaction,
    TransactionType,
    Transfer,
    TransferStatus,
    User,
)
from app.schemas.money import MAX_MONEY_AMOUNT


def transfer_money(
    db: DatabaseSession,
    *,
    customer: User,
    source_account_id: int,
    destination_account_id: int,
    amount: Decimal,
) -> Transfer:
    """Move money atomically between two owned accounts locked in deterministic order."""

    if source_account_id == destination_account_id:
        raise SameAccountTransferError

    try:
        account_ids = sorted((source_account_id, destination_account_id))
        locked_accounts = list(
            db.scalars(
                select(Account)
                .where(
                    Account.id.in_(account_ids),
                    Account.user_id == customer.id,
                )
                .order_by(Account.id)
                .with_for_update()
            )
        )
        if len(locked_accounts) != 2:
            raise NotFoundError

        accounts_by_id = {account.id: account for account in locked_accounts}
        source = accounts_by_id[source_account_id]
        destination = accounts_by_id[destination_account_id]
        if (
            source.status is not AccountStatus.ACTIVE
            or destination.status is not AccountStatus.ACTIVE
        ):
            raise InactiveAccountError
        if source.balance < amount:
            raise InsufficientFundsError

        destination_balance = destination.balance + amount
        if destination_balance > MAX_MONEY_AMOUNT:
            raise ValidationError(fields={"amount": "Resulting balance exceeds supported limit"})

        source.balance -= amount
        destination.balance = destination_balance
        transfer = Transfer(
            source_account=source,
            destination_account=destination,
            amount=amount,
            status=TransferStatus.COMPLETED,
        )
        db.add(transfer)
        db.flush()

        db.add_all(
            [
                Transaction(
                    account=source,
                    transfer=transfer,
                    transaction_type=TransactionType.TRANSFER_OUT,
                    amount=amount,
                    description="Internal transfer out",
                    balance_after=source.balance,
                ),
                Transaction(
                    account=destination,
                    transfer=transfer,
                    transaction_type=TransactionType.TRANSFER_IN,
                    amount=amount,
                    description="Internal transfer in",
                    balance_after=destination.balance,
                ),
                AuditEvent(
                    actor=customer,
                    event_type="transfer",
                    entity_type="transfer",
                    entity_id=str(transfer.id),
                    event_metadata={
                        "amount": format(amount, ".2f"),
                        "source_account_id": source.id,
                        "destination_account_id": destination.id,
                    },
                ),
            ]
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return transfer


def get_owned_transfer(
    db: DatabaseSession,
    *,
    customer: User,
    transfer_id: int,
) -> Transfer:
    """Load a transfer only when both account roles belong to the customer."""

    source = aliased(Account)
    destination = aliased(Account)
    transfer = db.scalar(
        select(Transfer)
        .join(source, source.id == Transfer.source_account_id)
        .join(destination, destination.id == Transfer.destination_account_id)
        .where(
            Transfer.id == transfer_id,
            source.user_id == customer.id,
            destination.user_id == customer.id,
        )
    )
    if transfer is None:
        raise NotFoundError
    return transfer
