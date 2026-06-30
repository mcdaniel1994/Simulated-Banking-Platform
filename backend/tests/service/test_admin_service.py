import pytest
from app.models import Account, AuditEvent, User, UserRole
from app.services.admin_service import create_customer
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker


def test_create_customer_rolls_back_every_record_when_commit_fails(
    login_test_context: tuple[object, sessionmaker[DatabaseSession]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _client, session_factory = login_test_context
    email = "rollback.customer@example.test"
    with session_factory() as db:
        admin = db.scalar(select(User).where(User.role == UserRole.ADMIN))
        assert admin is not None

        def fail_commit() -> None:
            raise RuntimeError("forced commit failure")

        monkeypatch.setattr(db, "commit", fail_commit)
        with pytest.raises(RuntimeError, match="forced commit failure"):
            create_customer(
                db,
                admin=admin,
                email=email,
                password="Rollback-passphrase",
                first_name="Roll",
                last_name="Back",
            )

    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(User).where(User.email == email)) == 0
        assert (
            db.scalar(
                select(func.count()).select_from(Account).join(User).where(User.email == email)
            )
            == 0
        )
        assert (
            db.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.event_type == "user_created")
            )
            == 0
        )
