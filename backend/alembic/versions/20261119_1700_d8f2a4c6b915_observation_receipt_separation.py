"""统一观测表名并按目标拆分写入回执，保留原始主键与重放证据。"""

import os

from alembic import context, op
from sqlalchemy import text

revision = "d8f2a4c6b915"
down_revision = "da6c32f8a701"
branch_labels = None
depends_on = None

OLD_RECEIPTS = "metric_ingest_receipts"
OBS_RECEIPTS = "observation_ingest_receipts"
ENERGY_RECEIPTS = "energy_ingest_receipts"
ENERGY_SAMPLE = "energy_consumption_main"
RENAMES = {
    "equipment_status_main": "equipment_main",
    "process_monitor_main": "monitor_main",
    "equipment_metric_groups": "observation_metric_groups",
    "equipment_metric_configs": "observation_metric_configs",
    "equipment_metric_slot_bindings": "observation_metric_slot_bindings",
    OLD_RECEIPTS: OBS_RECEIPTS,
}
EXPECTED_FKS = {
    ("equipment_status_main", "fk_obs_r10_latest_receipt", "ingest_receipt_id", OLD_RECEIPTS, "id"),
    ("process_monitor_main", "fk_obs_r10_history_receipt", "ingest_receipt_id", OLD_RECEIPTS, "id"),
    (ENERGY_SAMPLE, "fk_obs_r10_energy_receipt", "ingest_receipt_id", OLD_RECEIPTS, "id"),
    ("equipment_metric_slot_bindings", "fk_obs_r10_binding_metric", "metric_key",
     "equipment_metric_configs", "metric_key"),
}
RECEIPT_TYPES = {
    "id": "bigint unsigned", "target": "varchar(7)", "producer_id": "varchar(64)",
    "event_id": "varchar(128)", "request_digest": "binary(32)", "outcome": "varchar(24)",
    "processed_at": "datetime(6)", "result_record_id": "bigint unsigned",
    "mapping_id": "varchar(64)", "mapping_revision": "varchar(32)", "source_refs": "json",
    "task_evidence": "json", "contract_version": "varchar(32)", "result_version": "varchar(8)",
    "result_detail": "json",
}
RECEIPT_REQUIRED = {
    "id", "target", "producer_id", "event_id", "request_digest", "outcome", "processed_at",
    "contract_version", "result_version",
}
RECEIPT_DEFAULTS = {
    "processed_at": "CURRENT_TIMESTAMP(6)", "contract_version": "aiis.metric-ingest/v2", "result_version": "r10",
}
RECEIPT_EXTRA = {"id": "auto_increment", "processed_at": "DEFAULT_GENERATED"}
RECEIPT_INDEXES = ((0, "PRIMARY", "id"), (0, "uq_obs_receipt_event", "target,producer_id,event_id"))
SYSTEM_SCHEMAS = {"information_schema", "mysql", "performance_schema", "sys"}
SUPPORTED_DEFAULT_COLLATIONS = {"utf8mb4_0900_ai_ci", "utf8mb4_unicode_ci"}


# 冻结 da6 迁移链上涉及改名或外键切换的原列、业务键和索引。
# ? 表示可空；bin 表示精确标识排序规则；stamp 表示现有微秒默认值。
_SAMPLE_COLUMNS = (
    "id:bigint unsigned", "equipment_id:varchar(64):bin", "task_no:varchar(50):bin",
    "observed_at:datetime(6)", "quality:varchar(16)", "source_sample_key:binary(32)",
    "ingest_receipt_id:bigint unsigned", "local_values:json", "remark:text:?",
    "created_at:datetime(6):stamp", "updated_at:datetime(6):stamp",
)
COLUMNS = {
    "equipment_status_main": _SAMPLE_COLUMNS,
    "process_monitor_main": (*_SAMPLE_COLUMNS, "review_mark:varchar(16):?"),
    ENERGY_SAMPLE: (
        "id:bigint unsigned", "meter_id:varchar(64):bin", "group_key:varchar(64):bin",
        "observed_at:datetime(6)", "quality:varchar(16)", "interval_start_at:datetime(6):?",
        "interval_end_at:datetime(6):?", "ingest_receipt_id:bigint unsigned", "local_values:json",
        "remark:text:?", "review_mark:varchar(16):?", "created_at:datetime(6):stamp", "updated_at:datetime(6):stamp",
    ),
    "equipment_metric_groups": (
        "group_key:varchar(64):bin", "category:varchar(32)", "name_zh:varchar(128)", "name_en:varchar(128)",
        "enabled:tinyint(1)", "sort_order:bigint",
    ),
    "equipment_metric_configs": (
        "metric_key:varchar(64):bin", "source_group_key:varchar(64):bin", "category:varchar(32)",
        "name_zh:varchar(128)", "name_en:varchar(128)", "value_type:varchar(16)", "unit:varchar(24):?",
        "decimals:tinyint unsigned:?",
    ),
    "equipment_metric_slot_bindings": (
        "target:varchar(7)", "group_key:varchar(64):bin", "slot_no:tinyint unsigned", "metric_key:varchar(64):bin",
        "enabled:tinyint(1)", "list_visible:tinyint(1)", "list_order:int:?", "first_used_at:datetime(6):?",
    ),
}
INDEXES = {
    "equipment_status_main": (
        (0, "PRIMARY", "id"), (0, "uq_obs_latest_task", "equipment_id,task_no"),
        (1, "ix_obs_latest_task_v2", "task_no,id"), (1, "fk_obs_r10_latest_receipt", "ingest_receipt_id"),
    ),
    "process_monitor_main": (
        (0, "PRIMARY", "id"), (1, "ix_obs_history_task_time_v2", "task_no,observed_at,id"),
        (1, "ix_obs_history_equipment_time_v2", "equipment_id,observed_at,id"),
        (1, "fk_obs_r10_history_receipt", "ingest_receipt_id"),
    ),
    ENERGY_SAMPLE: (
        (0, "PRIMARY", "id"), (1, "ix_energy_sample_meter_time", "meter_id,group_key,observed_at,id"),
        (1, "fk_obs_r10_energy_receipt", "ingest_receipt_id"),
    ),
    "equipment_metric_groups": ((0, "PRIMARY", "group_key"),),
    "equipment_metric_configs": ((0, "PRIMARY", "metric_key"),),
    "equipment_metric_slot_bindings": (
        (0, "PRIMARY", "target,group_key,slot_no"), (0, "uq_obs_r10_binding_metric", "target,group_key,metric_key"),
        (1, "fk_obs_r10_binding_metric", "metric_key"),
    ),
}
# MySQL 8.4 CHECK_CLAUSE 使用自身规范化的字面量和标识符格式。
_REVIEW_CHECK = r"((`review_mark` is null) or (`review_mark` in (_utf8mb4\'abnormal\',_utf8mb4\'reviewed\')))"
CHECKS = {
    "process_monitor_main": {"ck_obs_review_mark_v2": _REVIEW_CHECK},
    ENERGY_SAMPLE: {"ck_energy_review_mark": _REVIEW_CHECK},
    "equipment_metric_groups": {
        "ck_obs_group_category": (
            r"(`category` in (_utf8mb4\'production\',_utf8mb4\'cleaning\',"
            r"_utf8mb4\'temperature\',_utf8mb4\'drive\'))"
        ),
    },
    "equipment_metric_configs": {
        "ck_obs_r10_metric_type": r"(`value_type` in (_utf8mb4\'number\',_utf8mb4\'boolean\',_utf8mb4\'string\'))",
    },
    "equipment_metric_slot_bindings": {
        "ck_obs_r10_binding_order": "((`list_order` is null) or (`list_order` >= 0))",
        "ck_obs_r10_binding_scope": (
            r"((`target` in (_utf8mb4\'latest\',_utf8mb4\'history\')) and (`slot_no` between 1 and 100))"
        ),
    },
}


def _execute(connection, sql, **parameters):
    return connection.execute(text(sql), parameters)


def _target(connection):
    version, server_uuid, schema, offset = _execute(connection, """
        SELECT VERSION(), @@server_uuid, DATABASE(),
               TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(), CURRENT_TIMESTAMP())
    """).one()
    if (
        not str(version).startswith("8.4.") or not schema or schema.lower() in SYSTEM_SCHEMAS
        or schema != os.environ.get("OBS_RECEIPT_EXPECTED_SCHEMA")
        or server_uuid != os.environ.get("OBS_RECEIPT_EXPECTED_SERVER_UUID") or offset != 28800
        or os.environ.get("OBS_RECEIPT_WINDOW_CONFIRMED") != f"{schema}:{server_uuid}"
    ):
        raise RuntimeError("observation receipt target, MySQL version, timezone or maintenance window mismatch")
    if list(_execute(connection, "SELECT version_num FROM alembic_version").scalars()) != [down_revision]:
        raise RuntimeError("observation receipt separation requires the single exact predecessor revision")
    return schema


def _metadata_access(connection):
    # 迁移账号需要跨库可见性；库外客户端和动态 SQL 依赖由维护方确认。
    privileges = set()
    for grant in _execute(connection, "SHOW GRANTS").scalars():
        if grant.startswith("GRANT ") and " ON *.* TO " in grant:
            privileges.update(grant[6:].split(" ON ", 1)[0].split(", "))
    if "ALL PRIVILEGES" not in privileges and not {"SELECT", "SHOW VIEW", "TRIGGER", "EVENT"} <= privileges:
        raise RuntimeError("observation receipt migration requires global database object visibility")


def _dependencies(connection, schema, affected, expected):
    found = set()
    rows = _execute(connection, """
        SELECT TABLE_SCHEMA, TABLE_NAME, CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_SCHEMA,
               REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME, ORDINAL_POSITION
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE REFERENCED_TABLE_NAME IS NOT NULL
          AND (TABLE_SCHEMA = :schema OR REFERENCED_TABLE_SCHEMA = :schema)
    """, schema=schema)
    for owner, source, name, column, referenced, destination, target_column, position in rows:
        if (owner == schema and source in affected) or (referenced == schema and destination in affected):
            fk = source, name, column, destination, target_column
            if owner != schema or referenced != schema or position != 1 or fk not in expected or fk in found:
                raise RuntimeError("unexpected foreign key involving OBS receipt separation")
            found.add(fk)
    rules = {(source, name): (delete, update) for source, name, delete, update in _execute(connection, """
        SELECT TABLE_NAME, CONSTRAINT_NAME, DELETE_RULE, UPDATE_RULE
        FROM information_schema.REFERENTIAL_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = :schema
    """, schema=schema)}
    if found != expected or any(
        (rules.get((source, name)) or (None, None))[0] != "RESTRICT"
        or (rules.get((source, name)) or (None, None))[1] not in {"RESTRICT", "NO ACTION"}
        for source, name, *_ in expected
    ):
        raise RuntimeError("observation receipt foreign keys or referential actions changed")


def _objects(connection, schema, affected):
    queries = (
        "SELECT TABLE_SCHEMA, NULL, VIEW_DEFINITION FROM information_schema.VIEWS",
        "SELECT TRIGGER_SCHEMA, EVENT_OBJECT_TABLE, ACTION_STATEMENT FROM information_schema.TRIGGERS",
        "SELECT ROUTINE_SCHEMA, NULL, ROUTINE_DEFINITION FROM information_schema.ROUTINES",
        "SELECT EVENT_SCHEMA, NULL, EVENT_DEFINITION FROM information_schema.EVENTS",
    )
    for query in queries:
        for owner, subject, definition in _execute(connection, query):
            if owner in SYSTEM_SCHEMAS:
                continue
            if (definition is None or (owner == schema and subject in affected)
                    or any(name in definition.lower() for name in affected)):
                raise RuntimeError("visible or unreadable object may depend on an OBS receipt separation table")


def _expected_collation(kind, default, binary=False):
    if binary:
        return "utf8mb4_bin"
    return default if kind.startswith("varchar(") or kind == "text" else None


def _validate_indexes_and_checks(connection, schema, table, expected_indexes, expected_checks):
    indexes = set(_execute(connection, """
        SELECT NON_UNIQUE, INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME, SUB_PART, COLLATION, IS_VISIBLE, INDEX_TYPE, EXPRESSION
        FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table
    """, schema=schema, table=table))
    expected = {(unique, name, position, column, None, "A", "YES", "BTREE", None)
                for unique, name, fields in expected_indexes
                for position, column in enumerate(fields.split(","), 1)}
    if indexes != expected:
        raise RuntimeError(f"unexpected index definitions in {table}")
    checks = set(_execute(connection, """
        SELECT t.CONSTRAINT_NAME, t.ENFORCED, c.CHECK_CLAUSE
        FROM information_schema.TABLE_CONSTRAINTS t
        JOIN information_schema.CHECK_CONSTRAINTS c
          USING (CONSTRAINT_CATALOG, CONSTRAINT_SCHEMA, CONSTRAINT_NAME)
        WHERE t.TABLE_SCHEMA = :schema AND t.TABLE_NAME = :table AND t.CONSTRAINT_TYPE = 'CHECK'
    """, schema=schema, table=table))
    if checks != {(name, "YES", clause) for name, clause in expected_checks.items()}:
        raise RuntimeError(f"unexpected check constraints in {table}")


def _receipt_layout(connection, schema, table, default_collation):
    columns = {name: (kind, nullable, default, extra, collation) for name, kind, nullable, default, extra, collation in
               _execute(connection, """
        SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA, COLLATION_NAME
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table ORDER BY ORDINAL_POSITION
    """, schema=schema, table=table)}
    if tuple(columns) != tuple(RECEIPT_TYPES):
        raise RuntimeError("unexpected receipt columns")
    for name, (kind, nullable, default, extra, collation) in columns.items():
        if (kind != RECEIPT_TYPES[name] or nullable != ("NO" if name in RECEIPT_REQUIRED else "YES")
                or default != RECEIPT_DEFAULTS.get(name)
                or extra != RECEIPT_EXTRA.get(name, "")
                or collation != _expected_collation(kind, default_collation, name in {"producer_id", "event_id"})):
            raise RuntimeError(f"unexpected receipt column definition: {name}")
    # 两张回执表在分流前均应保持原生布局，不应存在任何 CHECK。
    _validate_indexes_and_checks(connection, schema, table, RECEIPT_INDEXES, {})
    return columns


def _business_layout(connection, schema, table, default_collation):
    rows = list(_execute(connection, """
        SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA, COLLATION_NAME
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table ORDER BY ORDINAL_POSITION
    """, schema=schema, table=table))
    if len(rows) != len(COLUMNS[table]):
        raise RuntimeError(f"unexpected column count in {table}")
    for row, spec in zip(rows, COLUMNS[table]):
        name, kind, nullable, default, extra, collation = row
        wanted, wanted_type, *flags = spec.split(":")
        clock = "stamp" in flags
        expected_extra = "auto_increment" if wanted == "id" else "DEFAULT_GENERATED" if clock else ""
        if ((name, kind, nullable, default, extra) !=
                (wanted, wanted_type, "YES" if "?" in flags else "NO",
                 "CURRENT_TIMESTAMP(6)" if clock else None, expected_extra)
                or collation != _expected_collation(wanted_type, default_collation, "bin" in flags)):
            raise RuntimeError(f"unexpected column definition: {table}.{name}")
    _validate_indexes_and_checks(connection, schema, table, INDEXES[table], CHECKS.get(table, {}))

def _preflight(connection, schema, created=False):
    affected = set(RENAMES) | set(RENAMES.values()) | {ENERGY_SAMPLE, ENERGY_RECEIPTS}
    charset, default_collation = _execute(connection, """
        SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME
        FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = :schema
    """, schema=schema).one()
    if charset != "utf8mb4" or default_collation not in SUPPORTED_DEFAULT_COLLATIONS:
        raise RuntimeError("unsupported observation predecessor default collation")
    layouts = {table: (engine, collation) for table, engine, collation in _execute(connection, """
        SELECT TABLE_NAME, ENGINE, TABLE_COLLATION FROM information_schema.TABLES WHERE TABLE_SCHEMA = :schema
    """, schema=schema)}
    required = set(RENAMES) | {ENERGY_SAMPLE, "alembic_version"}
    reserved = set(RENAMES.values()) | {ENERGY_RECEIPTS}
    if created:
        required.add(ENERGY_RECEIPTS)
        reserved.remove(ENERGY_RECEIPTS)
    if reserved & layouts.keys() or any(layouts.get(name, (None, None))[0] != "InnoDB" for name in required):
        raise RuntimeError("missing source, occupied destination or partial OBS receipt separation")
    # 前驱 DDL 从库默认继承表排序规则，仅少数字段显式为 utf8mb4_bin。
    if any(layouts[name][1] != default_collation for name in required - {"alembic_version"}):
        raise RuntimeError("unexpected observation predecessor table collation")
    _dependencies(connection, schema, affected, EXPECTED_FKS)
    _objects(connection, schema, affected)
    for table in COLUMNS:
        _business_layout(connection, schema, table, default_collation)
    layout = _receipt_layout(connection, schema, OLD_RECEIPTS, default_collation)
    if created and _receipt_layout(connection, schema, ENERGY_RECEIPTS, default_collation) != layout:
        raise RuntimeError("copied energy receipt table layout differs")


def _validate_links(connection, receipts, sample, target):
    if _execute(connection, f"""
        SELECT 1 FROM `{sample}` LEFT JOIN `{receipts}`
             ON `{receipts}`.id = `{sample}`.ingest_receipt_id
        WHERE NOT (BINARY `{receipts}`.target <=> :target)
           OR NOT (BINARY `{receipts}`.outcome <=> 'stored')
           OR NOT (`{receipts}`.result_record_id <=> `{sample}`.id)
        LIMIT 1
    """, target=target).first() is not None:
        raise RuntimeError(f"invalid {target} sample owner before or after receipt separation")
    if _execute(connection, f"""
        SELECT 1 FROM `{receipts}` LEFT JOIN `{sample}` ON `{sample}`.id = `{receipts}`.result_record_id
        WHERE BINARY `{receipts}`.target = :target AND `{receipts}`.result_record_id IS NOT NULL
          AND (`{sample}`.id IS NULL OR (:target <> 'latest' AND `{sample}`.ingest_receipt_id <> `{receipts}`.id))
        LIMIT 1
    """, target=target).first() is not None:
        raise RuntimeError(f"invalid {target} receipt result before or after receipt separation")


def _validate_source(connection):
    if _execute(connection, f"""
        SELECT 1 FROM `{OLD_RECEIPTS}`
        WHERE NOT (BINARY contract_version <=> 'aiis.metric-ingest/v2')
           OR NOT (BINARY result_version <=> 'r10')
           OR NOT COALESCE(CASE BINARY target
                 WHEN 'latest' THEN BINARY outcome IN ('stored','stale','already_stored') AND result_record_id > 0
                 WHEN 'history' THEN (BINARY outcome = 'stored' AND result_record_id > 0)
                                     OR (BINARY outcome = 'no_history_metrics' AND result_record_id IS NULL)
                 WHEN 'energy' THEN BINARY outcome = 'stored' AND result_record_id > 0
                 ELSE FALSE END, FALSE)
        LIMIT 1
    """).first() is not None:
        raise RuntimeError("unknown observation receipt target, version or result prevents separation")
    for target, table in (("latest", "equipment_status_main"), ("history", "process_monitor_main"),
                          ("energy", ENERGY_SAMPLE)):
        _validate_links(connection, OLD_RECEIPTS, table, target)


def _verify_energy_copy(connection, source):
    equal_fields = " AND ".join(
        f"(BINARY `{source}`.`{column}` <=> BINARY `{ENERGY_RECEIPTS}`.`{column}`)"
        for column in RECEIPT_TYPES
    )
    source_count = _execute(connection, f"SELECT COUNT(*) FROM `{source}` WHERE BINARY target = 'energy'").scalar_one()
    destination_count = _execute(connection, f"SELECT COUNT(*) FROM `{ENERGY_RECEIPTS}`").scalar_one()
    identical_count = _execute(connection, f"""
        SELECT COUNT(*) FROM `{source}` INNER JOIN `{ENERGY_RECEIPTS}`
          ON `{source}`.id = `{ENERGY_RECEIPTS}`.id
        WHERE BINARY `{source}`.target = 'energy' AND {equal_fields}
    """).scalar_one()
    return source_count, destination_count, identical_count


def _watermark(connection, schema, table):
    next_id = _execute(connection, """
        SELECT AUTO_INCREMENT FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table
    """, schema=schema, table=table).scalar_one()
    maximum = _execute(connection, f"SELECT COALESCE(MAX(id), 0) FROM `{table}`").scalar_one()
    if next_id is None or not maximum < next_id < 2**64 - 1:
        raise RuntimeError("invalid or exhausted receipt AUTO_INCREMENT")
    return int(next_id)


def _separate(connection, schema):
    _preflight(connection, schema, created=True)
    _validate_source(connection)
    watermark = _watermark(connection, schema, OLD_RECEIPTS)
    energy_count, copied_count, _ = _verify_energy_copy(connection, OLD_RECEIPTS)
    if copied_count:
        raise RuntimeError("energy receipt destination unexpectedly populated")
    observation_count = _execute(connection, f"""
        SELECT COUNT(*) FROM `{OLD_RECEIPTS}` WHERE BINARY target IN ('latest','history')
    """).scalar_one()
    columns = ", ".join(f"`{column}`" for column in RECEIPT_TYPES)
    _execute(connection, f"""
        INSERT INTO `{ENERGY_RECEIPTS}` ({columns})
        SELECT {columns} FROM `{OLD_RECEIPTS}` WHERE BINARY target = 'energy' ORDER BY id
    """)
    if tuple(_verify_energy_copy(connection, OLD_RECEIPTS)) != (energy_count,) * 3:
        raise RuntimeError("energy receipt copy did not match the original field by field")

    _execute(connection, f"""
        ALTER TABLE `{ENERGY_SAMPLE}` DROP FOREIGN KEY fk_obs_r10_energy_receipt,
          ADD CONSTRAINT fk_energy_sample_receipt FOREIGN KEY (ingest_receipt_id)
          REFERENCES `{ENERGY_RECEIPTS}` (id) ON DELETE RESTRICT
    """)
    _execute(connection, "RENAME TABLE " + ", ".join(f"`{old}` TO `{new}`" for old, new in RENAMES.items()))
    expected = {(RENAMES.get(source, source), "fk_energy_sample_receipt" if source == ENERGY_SAMPLE else name, column,
                 ENERGY_RECEIPTS if source == ENERGY_SAMPLE else RENAMES.get(dest, dest), target_column)
                for source, name, column, dest, target_column in EXPECTED_FKS}
    _dependencies(connection, schema, set(RENAMES) | set(RENAMES.values()) | {ENERGY_SAMPLE, ENERGY_RECEIPTS}, expected)
    _validate_links(connection, ENERGY_RECEIPTS, ENERGY_SAMPLE, "energy")
    if tuple(_verify_energy_copy(connection, OBS_RECEIPTS)) != (energy_count,) * 3:
        raise RuntimeError("energy receipt verification failed after foreign-key and table cutover")

    removed = _execute(connection, f"DELETE FROM `{OBS_RECEIPTS}` WHERE BINARY target = 'energy'").rowcount
    if removed != energy_count:
        raise RuntimeError("observation receipt separation removed an unexpected number of copied rows")
    for table, name, rule in (
        (OBS_RECEIPTS, "ck_observation_receipt_target", "BINARY target IN ('latest','history')"),
        (ENERGY_RECEIPTS, "ck_energy_receipt_target", "BINARY target = 'energy'"),
    ):
        _execute(connection, f"ALTER TABLE `{table}` ADD CONSTRAINT `{name}` CHECK ({rule}), AUTO_INCREMENT = {watermark}")
        if _watermark(connection, schema, table) < watermark:
            raise RuntimeError("receipt sequence fell below its original watermark")
    if _execute(connection, f"SELECT COUNT(*) FROM `{OBS_RECEIPTS}`").scalar_one() != observation_count:
        raise RuntimeError("observation receipt row count changed")
    _validate_links(connection, OBS_RECEIPTS, "equipment_main", "latest")
    _validate_links(connection, OBS_RECEIPTS, "monitor_main", "history")


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError("OBS receipt separation requires an inspected online maintenance target")
    connection = op.get_bind()
    if connection.dialect.name != "mysql":
        raise RuntimeError("OBS receipt separation requires MySQL 8.4")
    schema = _target(connection)
    _metadata_access(connection)
    _preflight(connection, schema)
    _validate_source(connection)
    timeout, expiry = _execute(connection, "SELECT @@SESSION.lock_wait_timeout, @@SESSION.information_schema_stats_expiry").one()
    try:
        _execute(connection, "SET SESSION lock_wait_timeout = 5")
        _execute(connection, "SET SESSION information_schema_stats_expiry = 0")
        _watermark(connection, schema, OLD_RECEIPTS)
        _execute(connection, f"CREATE TABLE `{ENERGY_RECEIPTS}` LIKE `{OLD_RECEIPTS}`")
        locked = (*RENAMES, ENERGY_SAMPLE, ENERGY_RECEIPTS, "alembic_version")
        _execute(connection, "LOCK TABLES " + ", ".join(f"`{name}` WRITE" for name in locked))
        _target(connection)
        _separate(connection, schema)
    except Exception:
        # UNLOCK TABLES 可能隐式提交。先回滚尚未提交的复制或移除语句；
        # 已提交的 DDL 仍保留给维护方核对和恢复。
        _execute(connection, "ROLLBACK")
        raise
    finally:
        try:
            _execute(connection, "UNLOCK TABLES")
        finally:
            _execute(connection, "SET SESSION lock_wait_timeout = :timeout", timeout=timeout)
            _execute(connection, "SET SESSION information_schema_stats_expiry = :expiry", expiry=expiry)


def downgrade():
    raise RuntimeError("OBS receipt separation is forward-only; inspect and restore under a separate authorization")
