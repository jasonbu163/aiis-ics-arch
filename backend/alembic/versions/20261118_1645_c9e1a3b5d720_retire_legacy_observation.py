"""清退已核对为空的旧设备、过程和能耗表，保留当前观测回执。"""

import hashlib
import json
import os
import unicodedata

from alembic import context, op
from sqlalchemy import text

revision = "c9e1a3b5d720"
down_revision = "ae20b4d6f831"
branch_labels = None
depends_on = None

# 固定子表在父表之前，同一条 InnoDB DROP 语句处理整个集合。
RETIRED_TABLES = (
    "equipment_status_r8_archive",
    "process_monitor_r8_archive",
    "equipment_metric_slot_bindings_r8_archive",
    "equipment_metric_configs_r8_archive",
    "equipment_card_configs_r8_archive",
    "monitor_curve_group_configs_r8_archive",
    "equipment_temperature_sample_receipts",
    "equipment_mapping_receipts",
    "equipment_integration_receipts",
    "equipment_drive",
    "equipment_temperature",
    "equipment_production_parameters",
    "equipment_temperature_samples",
    "monitor_mapping_receipts",
    "monitor_integration_receipts",
    "monitor_history_process_curves",
    "monitor_history_energy_consumptions",
    "monitor_collector_states",
)
RECEIPTS = "metric_ingest_receipts"
RESULT_TABLES = {
    "latest": "equipment_status_main",
    "history": "process_monitor_main",
    "energy": "energy_consumption_main",
}
LOCKED_TABLES = (*RETIRED_TABLES, RECEIPTS, *RESULT_TABLES.values(), "alembic_version")
KNOWN_FK_PAIRS = {
    ("equipment_status_r8_archive", RECEIPTS),
    ("process_monitor_r8_archive", RECEIPTS),
    ("equipment_metric_slot_bindings_r8_archive", "equipment_metric_configs_r8_archive"),
    ("equipment_temperature_sample_receipts", "equipment_temperature_samples"),
    ("equipment_mapping_receipts", "equipment_drive"),
    ("equipment_mapping_receipts", "equipment_production_parameters"),
    ("equipment_integration_receipts", "equipment_drive"),
    ("equipment_integration_receipts", "equipment_production_parameters"),
    ("equipment_integration_receipts", "equipment_temperature_samples"),
    ("monitor_mapping_receipts", "monitor_history_process_curves"),
    ("monitor_integration_receipts", "monitor_history_process_curves"),
}
SYSTEM_SCHEMAS = {"information_schema", "mysql", "performance_schema", "sys"}
RECEIPT_DEFAULTS = {"contract_version": "aiis.metric-ingest/v1", "result_version": "r8"}


def _execute(connection, sql, **parameters):
    return connection.execute(text(sql), parameters)


def _target(connection):
    version, server_uuid, schema, offset = _execute(connection, """
        SELECT VERSION(), @@server_uuid, DATABASE(),
               TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(), CURRENT_TIMESTAMP())
    """).one()
    if (
        not str(version).startswith("8.4.")
        or not schema or schema.lower() in SYSTEM_SCHEMAS
        or schema != os.environ.get("OBS_RETIREMENT_EXPECTED_SCHEMA")
        or server_uuid != os.environ.get("OBS_RETIREMENT_EXPECTED_SERVER_UUID")
        or offset != 28800
    ):
        raise RuntimeError("observation retirement target, MySQL version or timezone mismatch")
    if os.environ.get("OBS_RETIREMENT_WINDOW_CONFIRMED") != f"{schema}:{server_uuid}":
        raise RuntimeError("confirm the inspected maintenance window, metadata visibility and quiescent writers")
    if list(_execute(connection, "SELECT version_num FROM alembic_version").scalars()) != [down_revision]:
        raise RuntimeError("observation retirement requires the single exact predecessor revision")
    return schema


def _schema_preflight(connection, schema):
    tables = dict(_execute(connection, """
        SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = :schema AND TABLE_TYPE = 'BASE TABLE'
    """, schema=schema).all())
    if any(str(tables.get(name)).lower() != "innodb" for name in LOCKED_TABLES):
        raise RuntimeError("expected InnoDB tables missing or changed; inspect partial DDL state")

    defaults = dict(_execute(connection, """
        SELECT COLUMN_NAME, COLUMN_DEFAULT FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table
          AND COLUMN_NAME IN ('contract_version', 'result_version')
    """, schema=schema, table=RECEIPTS).all())
    if defaults != RECEIPT_DEFAULTS:
        raise RuntimeError("unexpected receipt defaults; inspect partial DDL state")

    foreign_keys = _execute(connection, """
        SELECT DISTINCT TABLE_SCHEMA, TABLE_NAME, CONSTRAINT_NAME,
                        REFERENCED_TABLE_SCHEMA, REFERENCED_TABLE_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE REFERENCED_TABLE_NAME IS NOT NULL
          AND (TABLE_SCHEMA = :schema OR REFERENCED_TABLE_SCHEMA = :schema)
    """, schema=schema)
    seen = set()
    for owner, source, _, referenced_schema, destination in foreign_keys:
        if not ((owner == schema and source in RETIRED_TABLES)
                or (referenced_schema == schema and destination in RETIRED_TABLES)):
            continue
        pair = source, destination
        if owner != schema or referenced_schema != schema or pair not in KNOWN_FK_PAIRS or pair in seen:
            raise RuntimeError("unexpected foreign key involving an observation retirement table")
        seen.add(pair)
    if seen != KNOWN_FK_PAIRS:
        raise RuntimeError("expected observation foreign keys have changed")

    queries = (
        "SELECT TABLE_SCHEMA, NULL, VIEW_DEFINITION FROM information_schema.VIEWS",
        "SELECT TRIGGER_SCHEMA, EVENT_OBJECT_TABLE, ACTION_STATEMENT FROM information_schema.TRIGGERS",
        "SELECT ROUTINE_SCHEMA, NULL, ROUTINE_DEFINITION FROM information_schema.ROUTINES",
        "SELECT EVENT_SCHEMA, NULL, EVENT_DEFINITION FROM information_schema.EVENTS",
    )
    # 完整权限、动态 SQL 与库外消费者由维护窗口另行核验。
    for query in queries:
        for owner, event_table, definition in _execute(connection, query):
            if owner in SYSTEM_SCHEMAS:
                continue
            if definition is None or (owner == schema and event_table in RETIRED_TABLES):
                raise RuntimeError("observation retirement cannot rule out a database object dependency")
            if any(name in definition.lower() for name in RETIRED_TABLES):
                raise RuntimeError("visible database object uses an observation retirement table")


def _validate_data(connection):
    for name in RETIRED_TABLES:
        if _execute(connection, f"SELECT 1 FROM `{name}` LIMIT 1").first() is not None:
            raise RuntimeError(f"observation retirement table is not empty: {name}")
    _validate_receipts(connection)


def _closed_object(**properties):
    return {"type": "object", "properties": properties, "required": list(properties),
            "additionalProperties": False}


# 这些键是 v2 业务标识，可含 Unicode，也可能刚好等于历史表名。
_RESULT_KEY = {"type": "string", "minLength": 1, "maxLength": 64}
_NONEMPTY_METRIC_KEYS = {"type": "array", "items": _RESULT_KEY, "minItems": 1,
                         "maxItems": 100, "uniqueItems": True}
_STORED_DEVICE = {"type": "array", "items": _closed_object(groupKey=_RESULT_KEY,
                                                              metricKeys=_NONEMPTY_METRIC_KEYS)}
# sourceRefs 的其余字段由调用方声明，与回执结果的存储位置无关。
_SOURCE_REFS = {"type": "array", "maxItems": 128, "items": {
    "type": "object", "required": ["kind"],
    "properties": {"kind": {"type": "string", "minLength": 1, "maxLength": 128}},
}}


def _device_detail(reason):
    skipped = _closed_object(groupKey=_RESULT_KEY, metricKey=_RESULT_KEY, reason={"enum": [reason]})
    return _closed_object(stored=_STORED_DEVICE, skipped={"type": "array", "items": skipped})


_RECEIPT_KEY_PAGE_SIZE = 64


def _validate_identifier(value, limit=64):
    # 保存当期 writer 使用的 identifier 语义，避免历史迁移依赖可变的业务模块。
    if not isinstance(value, str) or not 1 <= len(value) <= limit or value.strip() != value:
        raise ValueError("invalid identifier")
    if any(unicodedata.category(character).startswith("C") for character in value):
        raise ValueError("invalid identifier")
    value.encode("utf-8", errors="strict")


def _result_keys(target, detail):
    if target == "energy":
        yield from detail["stored"]
        return
    for entry in detail["stored"]:
        yield entry["groupKey"]
        yield from entry["metricKeys"]
    for entry in detail["skipped"]:
        yield entry["groupKey"]
        yield entry["metricKey"]


def _source_sample_key(producer, event):
    # 冻结 writer 的 canonical_bytes 在两个字符串数组上的编码与摘要。
    encoded = json.dumps([producer, event], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", errors="strict")).digest()


def _validate_receipt_identifiers(connection):
    # 两个样本主键连接都至多匹配一行。实时旧回执不拥有当前快照。
    query = text("""
        SELECT metric_ingest_receipts.id, target, producer_id, event_id, mapping_id, mapping_revision,
               CAST(result_detail AS BINARY),
               COALESCE(equipment_status_main.id, process_monitor_main.id) IS NOT NULL,
               COALESCE(equipment_status_main.source_sample_key, process_monitor_main.source_sample_key)
        FROM metric_ingest_receipts
        LEFT JOIN equipment_status_main
          ON BINARY metric_ingest_receipts.target = 'latest'
         AND BINARY metric_ingest_receipts.outcome = 'stored'
         AND equipment_status_main.id = metric_ingest_receipts.result_record_id
         AND equipment_status_main.ingest_receipt_id = metric_ingest_receipts.id
        LEFT JOIN process_monitor_main
          ON BINARY metric_ingest_receipts.target = 'history'
         AND BINARY metric_ingest_receipts.outcome = 'stored'
         AND process_monitor_main.id = metric_ingest_receipts.result_record_id
         AND process_monitor_main.ingest_receipt_id = metric_ingest_receipts.id
        WHERE metric_ingest_receipts.id >= :first_id
        ORDER BY metric_ingest_receipts.id LIMIT :page_size
    """).execution_options(stream_results=True, max_row_buffer=1)
    first_id = 0
    while True:
        count = 0
        # 显式锁覆盖各页；每次关闭结果集后才可继续发查询或执行 DDL。
        with connection.execute(query, {"first_id": first_id, "page_size": _RECEIPT_KEY_PAGE_SIZE}) as rows:
            for receipt_id, target, producer, event, mapping, mapping_revision, payload, owns_sample, sample_key in rows:
                try:
                    _validate_identifier(producer)
                    _validate_identifier(event, 128)
                    if mapping is not None:
                        _validate_identifier(mapping)
                        _validate_identifier(mapping_revision, 32)
                    detail = json.loads(payload.decode("utf-8", errors="strict"))
                    for key in _result_keys(target, detail):
                        _validate_identifier(key)
                except ValueError:
                    raise RuntimeError("unknown observation receipt identifier prevents retirement") from None
                if owns_sample and sample_key != _source_sample_key(producer, event):
                    raise RuntimeError("unknown observation sample source identity prevents retirement")
                first_id = receipt_id + 1
                count += 1
        if count < _RECEIPT_KEY_PAGE_SIZE:
            return


def _validate_receipts(connection):
    if _execute(connection, """
        SELECT 1 FROM metric_ingest_receipts
        WHERE NOT (BINARY contract_version <=> 'aiis.metric-ingest/v2')
           OR NOT (BINARY result_version <=> 'r10')
           OR (mapping_id IS NULL) <> (mapping_revision IS NULL)
           OR COALESCE(JSON_TYPE(task_evidence) <> 'NULL', FALSE)
           OR (source_refs IS NOT NULL AND JSON_TYPE(source_refs) <> 'NULL'
               AND NOT JSON_SCHEMA_VALID(:source_refs_schema, source_refs))
           OR NOT COALESCE(CASE BINARY target
                   WHEN 'latest' THEN BINARY outcome IN ('stored', 'stale', 'already_stored')
                                      AND result_record_id > 0
                   WHEN 'history' THEN (BINARY outcome = 'stored' AND result_record_id > 0)
                                       OR (BINARY outcome = 'no_history_metrics' AND result_record_id IS NULL)
                   WHEN 'energy' THEN BINARY outcome = 'stored' AND result_record_id > 0
                   ELSE FALSE END, FALSE)
           OR NOT COALESCE(CASE BINARY target
                   WHEN 'latest' THEN JSON_SCHEMA_VALID(:latest_detail, result_detail)
                   WHEN 'history' THEN JSON_SCHEMA_VALID(:history_detail, result_detail)
                   WHEN 'energy' THEN JSON_SCHEMA_VALID(:energy_detail, result_detail)
                   ELSE FALSE END, FALSE)
           OR (BINARY outcome IN ('stale', 'no_history_metrics')
               AND JSON_LENGTH(JSON_EXTRACT(result_detail, '$.stored')) <> 0)
        LIMIT 1
    """, source_refs_schema=json.dumps(_SOURCE_REFS),
         latest_detail=json.dumps(_device_detail("latest_disabled")),
         history_detail=json.dumps(_device_detail("history_disabled")),
         energy_detail=json.dumps(_closed_object(stored=_NONEMPTY_METRIC_KEYS,
                                                skipped={"type": "array", "maxItems": 0}))).first() is not None:
        raise RuntimeError("legacy or unknown observation receipt prevents retirement")

    _validate_receipt_identifiers(connection)

    for target, table in RESULT_TABLES.items():
        # 实时快照覆盖时保留原行号，仅更新当前拥有该行的回执。
        if _execute(connection, f"""
            SELECT 1 FROM metric_ingest_receipts
            LEFT JOIN `{table}` ON `{table}`.id = metric_ingest_receipts.result_record_id
            WHERE BINARY metric_ingest_receipts.target = :target
              AND metric_ingest_receipts.result_record_id IS NOT NULL
              AND (`{table}`.id IS NULL
                   OR (:target <> 'latest' AND `{table}`.ingest_receipt_id <> metric_ingest_receipts.id))
            LIMIT 1
        """, target=target).first() is not None:
            raise RuntimeError(f"unknown observation receipt result for {target} prevents retirement")
        if _execute(connection, f"""
            SELECT 1 FROM `{table}`
            LEFT JOIN metric_ingest_receipts ON metric_ingest_receipts.id = `{table}`.ingest_receipt_id
            WHERE NOT (BINARY metric_ingest_receipts.target <=> :target)
               OR NOT (BINARY metric_ingest_receipts.outcome <=> 'stored')
               OR NOT (metric_ingest_receipts.result_record_id <=> `{table}`.id)
            LIMIT 1
        """, target=target).first() is not None:
            raise RuntimeError(f"unknown observation receipt owner for {target} prevents retirement")


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError("observation retirement requires inspected online target; offline SQL prohibited")
    connection = op.get_bind()
    if connection.dialect.name != "mysql":
        raise RuntimeError("observation retirement requires MySQL 8.4")
    schema = _target(connection)
    _schema_preflight(connection, schema)

    timeout = _execute(connection, "SELECT @@SESSION.lock_wait_timeout").scalar_one()
    _execute(connection, "SET SESSION lock_wait_timeout = 5")
    try:
        _execute(connection, "LOCK TABLES " + ", ".join(f"`{name}` WRITE" for name in LOCKED_TABLES))
        _target(connection)
        _schema_preflight(connection, schema)
        _validate_data(connection)
        _execute(connection, "DROP TABLE " + ", ".join(f"`{name}`" for name in RETIRED_TABLES))
        _execute(connection, """
            ALTER TABLE metric_ingest_receipts
              ALTER COLUMN contract_version SET DEFAULT 'aiis.metric-ingest/v2',
              ALTER COLUMN result_version SET DEFAULT 'r10'
        """)
    finally:
        try:
            _execute(connection, "UNLOCK TABLES")
        finally:
            _execute(connection, "SET SESSION lock_wait_timeout = :timeout", timeout=timeout)


def downgrade():
    raise RuntimeError("observation retirement is forward-only; reconcile and restore only with separate authorization")
