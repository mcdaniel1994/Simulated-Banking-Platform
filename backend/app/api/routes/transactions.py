from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DatabaseSession

from app.api.deps import CustomerUser, OwnedAccount
from app.api.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.db.session import get_db
from app.models import Transaction
from app.schemas.transaction import TransactionResponse
from app.services.transaction_service import (
    list_account_transactions,
    list_customer_transactions,
)

router = APIRouter(tags=["transactions"])


@router.get(
    "/accounts/{account_id}/transactions",
    response_model=list[TransactionResponse],
)
def list_account_transactions_route(
    account: OwnedAccount,
    db: Annotated[DatabaseSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Transaction]:
    """Return one owned account's stable newest-first history page."""

    # OwnedAccount resolves IDOR protection before the service applies ordering and pagination.
    return list_account_transactions(db, account=account, limit=limit, offset=offset)


@router.get("/transactions", response_model=list[TransactionResponse])
def list_customer_transactions_route(
    customer: CustomerUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Transaction]:
    """Return stable newest-first history across the customer's accounts."""

    # The SQL-backed customer principal becomes the ownership predicate for the combined feed.
    return list_customer_transactions(db, customer=customer, limit=limit, offset=offset)
