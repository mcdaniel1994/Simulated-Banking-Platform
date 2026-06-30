from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession

from app.models import Account, User


def list_owned_accounts(db: DatabaseSession, *, customer: User) -> list[Account]:
    """Return only accounts owned by the authenticated SQL customer."""

    # Ownership stays in SQL, and ID ordering gives the API a deterministic response.
    return list(
        db.scalars(select(Account).where(Account.user_id == customer.id).order_by(Account.id))
    )
