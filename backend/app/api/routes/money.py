from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DatabaseSession

from app.api.deps import CsrfProtected, CustomerUser, OwnedAccount
from app.db.session import get_db
from app.models import Account
from app.schemas.account import AccountResponse
from app.schemas.money import MoneyAmountRequest
from app.services.money_service import deposit, withdraw

router = APIRouter(tags=["money"])


@router.post(
    "/accounts/{account_id}/deposits",
    response_model=AccountResponse,
)
def deposit_route(
    request_body: MoneyAmountRequest,
    _csrf: CsrfProtected,
    customer: CustomerUser,
    account: OwnedAccount,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> Account:
    """Apply one CSRF-protected demo-funding deposit to an owned account."""

    # The service re-loads this authorized account under a row lock before reading its balance.
    return deposit(
        db,
        customer=customer,
        account_id=account.id,
        amount=request_body.amount,
    )


@router.post(
    "/accounts/{account_id}/withdrawals",
    response_model=AccountResponse,
)
def withdrawal_route(
    request_body: MoneyAmountRequest,
    _csrf: CsrfProtected,
    customer: CustomerUser,
    account: OwnedAccount,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> Account:
    """Apply one CSRF-protected withdrawal without allowing an overdraft."""

    return withdraw(
        db,
        customer=customer,
        account_id=account.id,
        amount=request_body.amount,
    )
