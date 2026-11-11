"""清退空的旧采集九表；仅在可确认的 MySQL 目标与维护窗口执行。"""

import os
import re

from alembic import context, op
from sqlalchemy import text

revision = "3d5f7a9c1e23"
down_revision = "2c4e6a8b0d12"
branch_labels = None
depends_on = None

RETIRED_TABLES = (
    "plc_facts_batches", "plc_facts_cycles", "plc_facts_latest_points",
    "plc_facts_raw_samples", "plc_facts_sample_receipts", "plc_facts_source_bindings",
    "plc_facts_stream_state", "plc_db_block_latest_snapshots", "plc_db_block_raw_snapshots",
)
EXPECTED_TABLES = frozenset((
    "applicants",
    "assessments",
    "attendances",
    "control_agent_gate_tokens",
    "daily_production_stats",
    "defect_records",
    "departments",
    "downtime_records",
    "employees",
    "energy_price_hours",
    "energy_prices",
    "equipment_drive",
    "equipment_integration_receipts",
    "equipment_mapping_receipts",
    "equipment_production_parameters",
    "equipment_temperature",
    "equipment_temperature_sample_receipts",
    "equipment_temperature_samples",
    "maintenance",
    "maintenance_logs",
    "monitor_collector_states",
    "monitor_history_energy_consumptions",
    "monitor_history_process_curves",
    "monitor_integration_receipts",
    "monitor_mapping_receipts",
    "performance_integration_observation_events",
    "performance_integration_receipts",
    "performance_lineage",
    "performance_main",
    "performance_mapping_observation_state",
    "performance_mapping_receipts",
    "performance_process_speed",
    "performance_process_temperature",
    "performance_process_tension",
    "performance_push_down_record",
    "performance_split",
    "performance_targets",
    "performance_transform",
    "plans",
    "plc_db_block_latest_snapshots",
    "plc_db_block_raw_snapshots",
    "plc_facts_batches",
    "plc_facts_cycles",
    "plc_facts_latest_points",
    "plc_facts_latest_points_v2",
    "plc_facts_raw_samples",
    "plc_facts_sample_receipts",
    "plc_facts_samples_v2",
    "plc_facts_source_bindings",
    "plc_facts_stream_state",
    "print_records",
    "production_reports",
    "production_status_records",
    "project_milestones",
    "project_tasks",
    "projection_mapping_audit_events",
    "projection_mapping_bindings",
    "projection_mapping_revisions",
    "projection_mapping_sets",
    "projection_runtime_audit_events",
    "projection_runtime_cursors",
    "projects",
    "quality_defect_records",
    "quality_grade_stats",
    "quality_inspections",
    "quality_records",
    "quality_spc_measurements",
    "recruitments",
    "shift_rules",
    "shift_teams",
    "shifts",
    "stop_records",
    "sys_dict_items",
    "sys_dicts",
    "temperature_zone_records",
    "token_blacklist",
    "users",
))


def _execute(connection, sql, parameters=None):
    return connection.execute(text(sql), parameters or {})


def _reject_dependency(connection, schema):
    """检查当前账号可见元数据；跨库完整可见性与动态 SQL 另由维护窗口预检。"""
    rows = _execute(connection, """
        SELECT TABLE_SCHEMA, TABLE_NAME, REFERENCED_TABLE_SCHEMA, REFERENCED_TABLE_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE REFERENCED_TABLE_NAME IS NOT NULL
          AND (TABLE_SCHEMA = :schema OR REFERENCED_TABLE_SCHEMA = :schema)
    """, {"schema": schema})
    for local_schema, local_table, remote_schema, remote_table in rows:
        if ((local_schema == schema and local_table in RETIRED_TABLES)
                or (remote_schema == schema and remote_table in RETIRED_TABLES)):
            raise RuntimeError("retired table has a visible foreign key dependency")

    queries = (
        "SELECT TABLE_SCHEMA, VIEW_DEFINITION FROM information_schema.VIEWS",
        "SELECT TRIGGER_SCHEMA, ACTION_STATEMENT FROM information_schema.TRIGGERS",
        "SELECT ROUTINE_SCHEMA, ROUTINE_DEFINITION FROM information_schema.ROUTINES",
        "SELECT EVENT_SCHEMA, EVENT_DEFINITION FROM information_schema.EVENTS",
    )
    excluded = {"information_schema", "mysql", "performance_schema", "sys"}
    for query in queries:
        for object_schema, definition in _execute(connection, query):
            if object_schema in excluded:
                continue
            if definition is None:
                raise RuntimeError("visible object definition unavailable for dependency inspection")
            if any(name in definition.lower() for name in RETIRED_TABLES):
                raise RuntimeError("retired table has a visible object dependency")


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError("retirement requires online target and data preflight; offline SQL prohibited")
    connection = op.get_bind()
    if connection.dialect.name != "mysql":
        raise RuntimeError("retirement requires MySQL 8.4")
    server_version, server_uuid, schema = _execute(
        connection, "SELECT VERSION(), @@server_uuid, DATABASE()"
    ).one()
    expected_uuid = os.environ.get("ACQ_RETIREMENT_EXPECTED_SERVER_UUID", "")
    expected_schema = os.environ.get("ACQ_RETIREMENT_EXPECTED_SCHEMA", "")
    if (not str(server_version).startswith("8.4.") or not schema or not expected_uuid
            or server_uuid != expected_uuid or schema != expected_schema):
        raise RuntimeError("retirement target, server UUID, schema or MySQL version mismatch")
    revisions = [row[0] for row in _execute(connection, "SELECT version_num FROM alembic_version")]
    if revisions != [down_revision]:
        raise RuntimeError("retirement requires the single exact predecessor revision")
    table_rows = list(_execute(connection, """
        SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE'
    """))
    tables = {name: engine for name, engine in table_rows if name != "alembic_version"}
    present = set(tables) & set(RETIRED_TABLES)
    if set(tables) not in (EXPECTED_TABLES, EXPECTED_TABLES - set(RETIRED_TABLES)):
        raise RuntimeError("unexpected table set or partially retired table set")
    if present and any(str(tables[name]).lower() != "innodb" for name in RETIRED_TABLES):
        raise RuntimeError("retirement requires nine InnoDB tables")
    _reject_dependency(connection, schema)
    if not present:
        evidence = os.environ.get("ACQ_RETIREMENT_RECOVERY_EVIDENCE_SHA256", "")
        confirmation = os.environ.get("ACQ_RETIREMENT_RECOVERY_CONFIRMED", "")
        if not re.fullmatch(r"[0-9a-f]{64}", evidence) or confirmation != f"{schema}:{server_uuid}":
            raise RuntimeError("all tables absent: confirmed DDL evidence and protected-data audit required")
        # Only the operator's independently verified evidence permits Alembic to register the revision.
        return
    # Explicit table locks close the gap between emptiness checks and DDL. MySQL
    # implicitly commits LOCK TABLES; this operation must run in the maintenance window.
    previous_timeout = _execute(connection, "SELECT @@SESSION.lock_wait_timeout").one()[0]
    _execute(connection, "SET SESSION lock_wait_timeout = 5")
    try:
        _execute(connection, "LOCK TABLES " + ", ".join(f"`{name}` WRITE" for name in RETIRED_TABLES))
        _reject_dependency(connection, schema)
        for name in RETIRED_TABLES:
            if _execute(connection, f"SELECT 1 FROM `{name}` LIMIT 1").first() is not None:
                raise RuntimeError(f"retired table is not empty: {name}")
        # One fixed atomic InnoDB multi-table DDL, using the same locked connection.
        op.execute("DROP TABLE " + ", ".join(f"`{name}`" for name in RETIRED_TABLES))
    finally:
        try:
            _execute(connection, "UNLOCK TABLES")
        finally:
            _execute(connection, "SET SESSION lock_wait_timeout = :timeout", {"timeout": previous_timeout})


def downgrade():
    raise RuntimeError("retirement is forward-only; restore requires a separately approved recovery procedure")
