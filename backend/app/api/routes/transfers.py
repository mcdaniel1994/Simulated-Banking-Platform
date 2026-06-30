from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as DatabaseSession

from app.api.deps import CsrfProtected, CustomerUser
from app.db.session import get_db
from app.models import Transfer
from app.schemas.transfer import TransferRequest, TransferResponse
from app.services.transfer_service import get_owned_transfer, transfer_money

router = APIRouter(prefix="/transfers", tags=["transfers"])


@router.post("", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer_route(
    request_body: TransferRequest,
    _csrf: CsrfProtected,
    customer: CustomerUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> Transfer:
    """Atomically transfer money between two active accounts owned by the customer."""

    # CSRF and authentication are HTTP concerns; locking and atomic movement belong to the service.
    return transfer_money(
        db,
        customer=customer,
        source_account_id=request_body.source_account_id,
        destination_account_id=request_body.destination_account_id,
        amount=request_body.amount,
    )


@router.get("/{transfer_id}", response_model=TransferResponse)
def get_transfer_route(
    transfer_id: int,
    customer: CustomerUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> Transfer:
    """Return one transfer whose source and destination are both customer-owned."""

    # The service verifies ownership of both account roles before returning the parent record.
    return get_owned_transfer(db, customer=customer, transfer_id=transfer_id)
