"""
File Path: /backend/tests/test_core_migration_baseline.py
Description: Static parity checks for the Core Alembic baseline.
Main Features:
    - Executes the migration's real Alembic operations through a recording op surface
    - Compares the recorded SQLAlchemy schema with the imported Core metadata
    - Verifies the single revision graph and reverse-order downgrade contract
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import sqlalchemy as sa
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, Index, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.schema import MetaData, Table

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


TASK_ROOT = Path(__file__).resolve().parents[1]
VERSIONS_DIR = TASK_ROOT / "alembic" / "versions"
MIGRATION_PATH = VERSIONS_DIR / "20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py"
EXPECTED_CORE_TABLES = {
    "users",
    "token_blacklist",
    "sys_dicts",
    "sys_dict_items",
    "projection_mapping_sets",
    "projection_mapping_revisions",
    "projection_mapping_bindings",
    "projection_mapping_audit_events",
    "projection_runtime_cursors",
    "projection_runtime_audit_events",
    "control_agent_gate_tokens",
    "monitor_collector_states",
    "plc_db_block_raw_snapshots",
    "plc_db_block_latest_snapshots",
}
FORBIDDEN_PROJECT_RESIDUE = (
    "applicants",
    "equipment_",
    "performance_",
    "projects",
    "quality_",
    "a9d7e5c3b1f0",
    "b68d7e5c3b1f",
    "c17d9e8f4a21",
)


class MigrationRecorder:
    """Small Alembic-op substitute that retains actual schema operations."""

    def __init__(self) -> None:
        self.metadata = MetaData()
        self.operations: list[tuple[Any, ...]] = []

    def create_table(self, name: str, *elements: Any, **kwargs: Any) -> Table:
        table = Table(name, self.metadata, *elements, **kwargs)
        self.operations.append(("create_table", name))
        return table

    def create_foreign_key(
        self,
        name: str,
        source: str,
        referent: str,
        local_cols: list[str],
        remote_cols: list[str],
        **kwargs: Any,
    ) -> None:
        constraint = ForeignKeyConstraint(
            local_cols,
            [f"{referent}.{column}" for column in remote_cols],
            name=name,
            ondelete=kwargs.get("ondelete"),
        )
        self.metadata.tables[source].append_constraint(constraint)
        self.operations.append(("create_foreign_key", name, source, referent))

    def create_index(
        self,
        name: str,
        table_name: str,
        columns: list[str],
        unique: bool = False,
        **kwargs: Any,
    ) -> None:
        table = self.metadata.tables[table_name]
        Index(name, *(table.c[column] for column in columns), unique=unique)
        self.operations.append(("create_index", name, table_name, tuple(columns), unique))

    def drop_constraint(self, name: str, table_name: str, **kwargs: Any) -> None:
        table = self.metadata.tables[table_name]
        for constraint in tuple(table.constraints):
            if constraint.name == name:
                table.constraints.remove(constraint)
                break
        self.operations.append(("drop_constraint", name, table_name))

    def drop_table(self, name: str, **kwargs: Any) -> None:
        self.metadata.remove(self.metadata.tables[name])
        self.operations.append(("drop_table", name))


def _load_migration() -> ModuleType:
    spec = importlib.util.spec_from_file_location("core_schema_baseline", MIGRATION_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _type_signature(column: sa.Column[Any]) -> tuple[Any, ...]:
    column_type = column.type
    return (
        type(column_type).__module__,
        type(column_type).__name__,
        getattr(column_type, "length", None),
        getattr(column_type, "precision", None),
        getattr(column_type, "scale", None),
        getattr(column_type, "timezone", None),
    )


def _server_default_signature(column: sa.Column[Any]) -> str | None:
    if column.server_default is None:
        return None
    return str(column.server_default.arg).replace(" ", "").lower()


def _constraint_signature(constraint: sa.Constraint) -> tuple[Any, ...]:
    columns = tuple(column.name for column in constraint.columns)
    if isinstance(constraint, ForeignKeyConstraint):
        targets = tuple(element.target_fullname for element in constraint.elements)
        return (
            "foreign_key",
            constraint.name,
            columns,
            targets,
            constraint.ondelete,
        )
    if isinstance(constraint, CheckConstraint):
        return (
            "check",
            constraint.name,
            " ".join(str(constraint.sqltext).split()),
        )
    if isinstance(constraint, PrimaryKeyConstraint):
        return ("primary_key", columns)
    if isinstance(constraint, UniqueConstraint):
        return ("unique", constraint.name, columns)
    raise AssertionError(f"Unexpected constraint type: {type(constraint).__name__}")


def _table_signature(table: Table) -> dict[str, Any]:
    return {
        "columns": tuple(
            (
                column.name,
                _type_signature(column),
                column.nullable,
                column.primary_key,
                _server_default_signature(column),
            )
            for column in table.columns
        ),
        "constraints": frozenset(_constraint_signature(constraint) for constraint in table.constraints),
        "indexes": frozenset(
            (
                index.name,
                bool(index.unique),
                tuple(expression.name for expression in index.expressions),
            )
            for index in table.indexes
        ),
    }


@pytest.mark.no_db
def test_core_baseline_executes_real_operations_and_matches_metadata() -> None:
    """The parity assertion must consume migration operations, not a second schema list."""
    import_model_packages()
    assert set(Base.metadata.tables) == EXPECTED_CORE_TABLES

    migration = _load_migration()
    recorder = MigrationRecorder()
    migration.op = recorder
    migration.upgrade()

    create_tables = [operation[1] for operation in recorder.operations if operation[0] == "create_table"]
    create_indexes = [operation[1] for operation in recorder.operations if operation[0] == "create_index"]
    create_fks = [operation[1] for operation in recorder.operations if operation[0] == "create_foreign_key"]
    assert create_tables == [
        "users",
        "token_blacklist",
        "sys_dicts",
        "sys_dict_items",
        "projection_mapping_sets",
        "projection_mapping_revisions",
        "projection_mapping_bindings",
        "projection_mapping_audit_events",
        "projection_runtime_cursors",
        "projection_runtime_audit_events",
        "control_agent_gate_tokens",
        "monitor_collector_states",
        "plc_db_block_raw_snapshots",
        "plc_db_block_latest_snapshots",
    ]
    assert len(create_indexes) == 39
    assert create_fks == ["fk_projection_mapping_set_active_revision"]
    assert set(recorder.metadata.tables) == EXPECTED_CORE_TABLES

    for table_name in EXPECTED_CORE_TABLES:
        assert _table_signature(recorder.metadata.tables[table_name]) == _table_signature(
            Base.metadata.tables[table_name]
        ), table_name


@pytest.mark.no_db
def test_downgrade_drops_every_core_table_in_reverse_dependency_order() -> None:
    migration = _load_migration()
    recorder = MigrationRecorder()
    migration.op = recorder
    migration.upgrade()
    migration.downgrade()

    dropped_tables = [operation[1] for operation in recorder.operations if operation[0] == "drop_table"]
    assert dropped_tables == [
        "plc_db_block_latest_snapshots",
        "plc_db_block_raw_snapshots",
        "monitor_collector_states",
        "control_agent_gate_tokens",
        "projection_runtime_audit_events",
        "projection_runtime_cursors",
        "projection_mapping_audit_events",
        "projection_mapping_bindings",
        "projection_mapping_revisions",
        "projection_mapping_sets",
        "sys_dict_items",
        "sys_dicts",
        "token_blacklist",
        "users",
    ]
    assert recorder.metadata.tables == {}


@pytest.mark.no_db
def test_active_versions_are_one_core_revision_without_project_residue() -> None:
    active_files = sorted(path.name for path in VERSIONS_DIR.glob("*.py"))
    assert active_files == [MIGRATION_PATH.name]
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    assert not any(forbidden in source for forbidden in FORBIDDEN_PROJECT_RESIDUE)
    assert "revision: str = \"d4e6f8a0b2c4\"" in source
    assert "down_revision: Union[str, None] = None" in source
