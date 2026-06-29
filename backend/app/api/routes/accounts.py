from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DatabaseSession

from app.api.deps import CustomerUser, OwnedAccount
from app.db.session import get_db
from app.models import Account
from app.schemas.account import AccountResponse
from app.services.account_service import list_owned_accounts

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountResponse])
def list_accounts_route(
    customer: CustomerUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> list[Account]:
    """List the authenticated customer's accounts in deterministic order."""

    # The route translates HTTP concerns while the service owns the reusable SQL query.
    return list_owned_accounts(db, customer=customer)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account_route(account: OwnedAccount) -> Account:
    """Return the account already loaded through the shared ownership boundary."""

    # Re-querying here would duplicate and risk drifting from the Phase 15 IDOR protection.
    return account
