from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DatabaseSession

from app.api.deps import AdminUser
from app.db.session import get_db
from app.schemas.admin import AdminDashboardResponse
from app.services.admin_service import AdminDashboardSummary, get_dashboard_summary

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=AdminDashboardResponse)
def admin_dashboard_route(
    _admin: AdminUser,
    db: Annotated[DatabaseSession, Depends(get_db)],
) -> AdminDashboardSummary:
    """Return aggregate statistics only to the authenticated SQL administrator."""

    return get_dashboard_summary(db)
