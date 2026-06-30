from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session as DatabaseSession

from app.api.deps import AdminUser, CsrfProtected
from app.api.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.db.session import get_db
from app.models import Account, User
from app.schemas.account import AccountResponse
from app.schemas.admin import (
    AccountStatusRequest,
    AdminCustomerCreateRequest,
    AdminCustomerDetailResponse,
    AdminCustomerResponse,
    AdminDashboardResponse,
    UserStatusRequest,
)
from app.services.admin_service import (
    AdminCustomerDetail,
    AdminDashboardSummary,
    create_customer,
    get_customer_detail,
    get_dashboard_summary,
    list_customers,
    set_account_status,
    set_customer_active_status,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=AdminDashboardResponse)
def admin_dashboard_route(
    _admin: AdminUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> AdminDashboardSummary:
    """Return aggregate statistics only to the authenticated SQL administrator."""

    # The route enforces the role; aggregate definitions and SQL stay in the admin service.
    return get_dashboard_summary(db)


@router.get("/users", response_model=list[AdminCustomerResponse])
def list_customers_route(
    _admin: AdminUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> list[User]:
    """List every managed customer without exposing password or session state."""

    # Response validation selects safe identity fields from the ORM users returned by the service.
    return list_customers(db)


@router.post(
    "/users",
    response_model=AdminCustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_route(
    request_body: AdminCustomerCreateRequest,
    _csrf: CsrfProtected,
    admin: AdminUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> User:
    """Provision one customer identity and its initial checking account."""

    # The service fixes role, lifecycle state, account type, and opening balance server-side.
    return create_customer(
        db,
        admin=admin,
        email=request_body.email,
        password=request_body.password,
        first_name=request_body.first_name,
        last_name=request_body.last_name,
    )


@router.get("/users/{user_id}", response_model=AdminCustomerDetailResponse)
def get_customer_detail_route(
    user_id: int,
    _admin: AdminUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AdminCustomerDetail:
    """Return one customer's accounts and stable transaction page."""

    # Shared query bounds keep admin and customer transaction pagination behavior aligned.
    return get_customer_detail(db, user_id=user_id, limit=limit, offset=offset)


@router.patch("/users/{user_id}/status", response_model=AdminCustomerResponse)
def set_customer_status_route(
    user_id: int,
    request_body: UserStatusRequest,
    _csrf: CsrfProtected,
    admin: AdminUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> User:
    """Activate or deactivate a customer, revoking sessions on deactivation."""

    # CSRF and ADMIN checks finish before the service opens the status-change transaction.
    return set_customer_active_status(
        db,
        admin=admin,
        user_id=user_id,
        is_active=request_body.is_active,
    )


@router.patch("/accounts/{account_id}/status", response_model=AccountResponse)
def set_account_status_route(
    account_id: int,
    request_body: AccountStatusRequest,
    _csrf: CsrfProtected,
    admin: AdminUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> Account:
    """Freeze or unfreeze an account without granting the admin ownership."""

    # This admin management path is intentionally separate from customer ownership dependencies.
    return set_account_status(
        db,
        admin=admin,
        account_id=account_id,
        account_status=request_body.status,
    )
