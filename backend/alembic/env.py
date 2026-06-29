from logging.config import fileConfig

from alembic import context
from app.core.config import get_settings
from app.db.base import Base, load_models
from sqlalchemy import engine_from_config, pool

# Alembic owns this Config object for both CLI commands and programmatic migration tests.
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import every model before exposing metadata so autogenerate can detect the complete schema.
load_models()
target_metadata = Base.metadata


def get_database_url() -> str:
    """Resolve an explicit test override or the normal runtime database URL."""

    test_override = config.attributes.get("database_url")
    if test_override is not None:
        return str(test_override)
    return get_settings().database_url.get_secret_value()


def run_migrations_offline() -> None:
    """Generate SQL without opening a database connection."""

    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations through a short-lived connection outside the application pool."""

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
