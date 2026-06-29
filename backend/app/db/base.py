from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared metadata registry inherited by every future ORM model."""


def load_models() -> None:
    """Import model modules once so migrations and metadata inspection see every table."""

    import app.models  # noqa: F401
