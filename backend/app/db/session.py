from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

# Build one process-wide engine; its pool reuses a bounded number of PostgreSQL connections.
engine = create_engine(
    get_settings().database_url.get_secret_value(),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
)

# Services receive independent sessions while sharing the engine's connection pool.
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Yield one session per request and always release its pooled connection."""

    db = SessionLocal()
    try:
        yield db
    except Exception:
        # Roll back unfinished work so a failed request cannot return a dirty transaction to the pool.
        db.rollback()
        raise
    finally:
        db.close()
