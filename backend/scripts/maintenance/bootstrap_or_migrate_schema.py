"""Explicit Alembic entry point for an authorized environment operation.

This module intentionally has no project table list and is never called by
FastAPI lifespan.  A project or operator must invoke it explicitly after
reviewing the target database and migration plan.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text

BACKEND_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_ROOT))

from database import sync_engine


def _emit(**payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def _alembic_config() -> Config:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    return config


def _table_names() -> set[str]:
    with sync_engine.connect() as connection:
        return set(inspect(connection).get_table_names())


def _head(config: Config) -> str:
    head = ScriptDirectory.from_config(config).get_current_head()
    if not head:
        raise RuntimeError("active Alembic head is missing")
    return head


def _version_rows() -> list[str]:
    with sync_engine.connect() as connection:
        return list(connection.execute(text("SELECT version_num FROM alembic_version")).scalars())


def bootstrap_or_migrate_schema() -> int:
    """Apply the active Alembic head only after explicit operator invocation."""
    config = _alembic_config()
    head = _head(config)
    tables = _table_names()

    if tables and "alembic_version" not in tables:
        _emit(
            target="schema",
            action="refuse_unversioned_database",
            status="failed",
            reason="tables_exist_without_alembic_version",
        )
        return 2

    versions = _version_rows() if "alembic_version" in tables else []
    if versions and versions != [head]:
        _emit(
            target="schema",
            action="refuse_unknown_revision",
            status="failed",
            reason="database_revision_requires_authorized_review",
        )
        return 2

    _emit(target="schema", action="alembic_upgrade", status="started", target_revision=head)
    command.upgrade(config, "head")
    _emit(target="schema", action="alembic_upgrade", status="completed", target_revision=head)
    return 0


if __name__ == "__main__":
    raise SystemExit(bootstrap_or_migrate_schema())
