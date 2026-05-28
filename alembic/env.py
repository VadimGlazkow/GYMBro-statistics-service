# alembic/env.py
# -*- coding: utf-8 -*-

from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection

from alembic import context

from app.database import Base, create_db_engine, normalize_database_url
from app.config import settings
from app.models import *  # noqa: F401,F403

config = context.config
config.set_main_option(
    "sqlalchemy.url",
    normalize_database_url(settings.DATABASE_URL),
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в offline режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в online режиме (синхронный)."""
    connectable = create_db_engine(poolclass=pool.NullPool)

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
