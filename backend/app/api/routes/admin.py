from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DatabaseSession

from app.api.deps import AdminUser
from app.api.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.db.session import get_db
from app.models import User
from app.schemas.admin import (
    AdminCustomerDetailResponse,
    AdminCustomerResponse,
    AdminDashboardResponse,
)
from app.services.admin_service import (
    AdminCustomerDetail,
    AdminDashboardSummary,
    get_customer_detail,
    get_dashboard_summary,
    list_customers,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=AdminDashboardResponse)
def admin_dashboard_route(
    _admin: AdminUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> AdminDashboardSummary:
    """Return aggregate statistics only to the authenticated SQL administrator."""

    return get_dashboard_summary(db)


@router.get("/users", response_model=list[AdminCustomerResponse])
def list_customers_route(
    _admin: AdminUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> list[User]:
    """List every managed customer without exposing password or session state."""

    return list_customers(db)


@router.get("/users/{user_id}", response_model=AdminCustomerDetailResponse)
def get_customer_detail_route(
    user_id: int,
    _admin: AdminUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AdminCustomerDetail:
    """Return one customer's accounts and stable transaction page."""

    return get_customer_detail(db, user_id=user_id, limit=limit, offset=offset)
