"""Alembic environment for the reusable AIIS ICS Core metadata surface."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.control_agent.models.gate_token import ControlAgentGateToken
from app.module_registry import import_model_packages
from app.monitor.models import (
    MonitorCollectorState,
    PlcDbBlockLatestSnapshot,
    PlcDbBlockRawSnapshot,
)
from app.system.models import (
    ProjectionMappingAuditEvent,
    ProjectionMappingBinding,
    ProjectionMappingRevision,
    ProjectionMappingSet,
    ProjectionRuntimeAuditEvent,
    ProjectionRuntimeCursor,
    SysDict,
    SysDictItem,
)
from app.user.models.token_blacklist import TokenBlacklist
from app.user.models.user import User
from database import Base
from settings import settings


config = context.config

# Alembic ConfigParser treats percent signs as interpolation markers.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
import_model_packages()


def run_migrations_offline() -> None:
    """Run migrations without opening a database connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Configure online migration execution against one explicit database."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create one short-lived async migration connection."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
