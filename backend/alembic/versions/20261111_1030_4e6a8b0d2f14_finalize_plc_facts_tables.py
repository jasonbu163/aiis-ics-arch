"""采集事实表改名与历史来源字段；仅允许经过核对的在线 MySQL 前向迁移。"""

import hashlib
import json
import os
import re
from datetime import date, datetime
from decimal import Decimal

from alembic import context, op
from sqlalchemy import text

revision = "4e6a8b0d2f14"
down_revision = "3d5f7a9c1e23"
branch_labels = None
depends_on = None

OLD_HISTORY = "plc_facts_samples_v2"
OLD_LATEST = "plc_facts_latest_points_v2"
HISTORY = "plc_facts_history"
LATEST = "plc_facts_latest"
RENAME_SQL = (f"RENAME TABLE `{OLD_HISTORY}` TO `{HISTORY}`, "
              f"`{OLD_LATEST}` TO `{LATEST}`")
ALTER_SQL = (f"ALTER TABLE `{HISTORY}` "
             "MODIFY COLUMN `group_id` VARBINARY(128) NULL, "
             "MODIFY COLUMN `config_revision` VARBINARY(128) NULL, "
             "ADD COLUMN `source_type` VARCHAR(8) NULL, "
             "ADD CONSTRAINT `ck_pfv2_source_type` CHECK "
             "(`source_type` IS NULL OR CAST(`source_type` AS BINARY) IN (X'646161',X'65787465726E616C'))")

# (column, exact MySQL column_type, nullable, extra). The original columns
# are also the complete, ordered logical fingerprint input after the ALTER.
HISTORY_COLUMNS = (
    ("id", "bigint", False, "auto_increment"),
    ("instance_id", "varbinary(128)", False, ""),
    ("sample_id", "varbinary(128)", False, ""),
    ("plc_id", "varbinary(128)", False, ""),
    ("db_number", "smallint unsigned", False, ""),
    ("group_id", "varbinary(128)", False, ""),
    ("config_revision", "varbinary(128)", False, ""),
    ("source_generation", "varbinary(128)", False, ""),
    ("source_seq", "bigint", False, ""),
    ("points_json", "json", False, ""),
    ("content_hash", "binary(32)", False, ""),
    ("sampled_at", "datetime(6)", False, ""),
    ("stored_at", "datetime(6)", False, ""),
    ("expires_at", "datetime(6)", False, ""),
)
LATEST_COLUMNS = (
    ("plc_id", "varbinary(128)", False, ""),
    ("db_number", "smallint unsigned", False, ""),
    ("point_id", "varbinary(128)", False, ""),
    ("point_name", "varchar(100)", True, ""),
    ("data_type", "varchar(16)", True, ""),
    ("value_json", "json", True, ""),
    ("quality", "varchar(4)", True, ""),
    ("reason", "varchar(128)", True, ""),
    ("observed_at", "datetime(6)", True, ""),
    ("expires_at", "datetime(6)", True, ""),
    ("instance_id", "varbinary(128)", False, ""),
    ("source_generation", "varbinary(128)", False, ""),
    ("source_seq", "bigint", False, ""),
    ("sample_id", "varbinary(128)", True, ""),
)
HISTORY_INDEXES = {
    "PRIMARY": (0, ("id",)),
    "uq_pfv2_sample_identity": (0, ("instance_id", "sample_id")),
    "uq_pfv2_sample_sequence": (0, ("instance_id", "plc_id", "db_number", "source_generation", "source_seq")),
    "ix_pfv2_sample_history": (1, ("plc_id", "db_number", "sampled_at", "id")),
    "ix_pfv2_sample_expiry": (1, ("expires_at", "id")),
}
LATEST_INDEXES = {
    "PRIMARY": (0, ("plc_id", "db_number", "point_id")),
    "ix_pfv2_latest_expiry": (1, ("expires_at", "plc_id", "db_number", "point_id")),
}


def _execute(connection, sql, parameters=None):
    return connection.execute(text(sql), parameters or {})


def _target(connection):
    if connection.dialect.name != "mysql":
        raise RuntimeError("facts migration requires online MySQL 8.4")
    version, server_uuid, schema, offset = _execute(connection, """
        SELECT VERSION(), @@server_uuid, DATABASE(),
               TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))
    """).one()
    expected_uuid = os.environ.get("ACQ_FACTS_EXPECTED_SERVER_UUID", "")
    expected_schema = os.environ.get("ACQ_FACTS_EXPECTED_SCHEMA", "")
    operation = os.environ.get("ACQ_FACTS_OPERATION_ID", "")
    if (not str(version).startswith("8.4.") or not schema or not expected_uuid
            or server_uuid != expected_uuid or schema != expected_schema or offset != 28800
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", operation)):
        raise RuntimeError("facts migration target, operation, MySQL version or timezone mismatch")
    return schema, server_uuid, operation


def _state(connection):
    rows = _execute(connection, """
        SELECT TABLE_NAME, ENGINE, TABLE_TYPE FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME IN (:old_history, :old_latest, :history, :latest)
    """, {"old_history": OLD_HISTORY, "old_latest": OLD_LATEST,
          "history": HISTORY, "latest": LATEST})
    tables = {}
    for name, engine, kind in rows:
        if kind != "BASE TABLE":
            raise RuntimeError("facts migration found a non-table object using a reserved table name")
        tables[name] = engine
    if any(str(engine).lower() != "innodb" for engine in tables.values()):
        raise RuntimeError("facts migration requires InnoDB tables")
    if set(tables) == {OLD_HISTORY, OLD_LATEST}:
        return "old", OLD_HISTORY, OLD_LATEST
    if set(tables) == {HISTORY, LATEST}:
        columns = {row[0] for row in _execute(connection, """
            SELECT COLUMN_NAME FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table
        """, {"table": HISTORY})}
        return ("altered" if "source_type" in columns else "renamed"), HISTORY, LATEST
    raise RuntimeError("facts migration found mixed or missing table names")


def _expected_columns(history, altered):
    if not history:
        return LATEST_COLUMNS
    if not altered:
        return HISTORY_COLUMNS
    result = [(name, kind, True if name in ("group_id", "config_revision") else nullable, extra)
              for name, kind, nullable, extra in HISTORY_COLUMNS]
    result.append(("source_type", "varchar(8)", True, ""))
    return tuple(result)


def _check_columns(connection, table, history, altered):
    defaults = _execute(connection, """
        SELECT s.DEFAULT_CHARACTER_SET_NAME, s.DEFAULT_COLLATION_NAME, t.TABLE_COLLATION
        FROM information_schema.SCHEMATA s JOIN information_schema.TABLES t
          ON t.TABLE_SCHEMA = s.SCHEMA_NAME
        WHERE s.SCHEMA_NAME = DATABASE() AND t.TABLE_NAME = :table
    """, {"table": table}).one()
    charset, schema_collation, table_collation = defaults
    if table_collation != schema_collation:
        raise RuntimeError("facts migration found an unexpected table collation")
    rows = list(_execute(connection, """
        SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, EXTRA, COLUMN_DEFAULT,
               CHARACTER_SET_NAME, COLLATION_NAME, DATETIME_PRECISION, GENERATION_EXPRESSION
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table ORDER BY ORDINAL_POSITION
    """, {"table": table}))
    actual = tuple((name, kind.lower(), nullable == "YES", extra.lower())
                   for name, kind, nullable, extra, default, char, collate, precision, generated in rows)
    if actual != _expected_columns(history, altered):
        raise RuntimeError("facts migration found an unexpected column definition")
    original = []
    for name, kind, nullable, extra, default, char, collate, precision, generated in rows:
        expected_char = charset if kind.lower().startswith("varchar(") else None
        expected_collation = table_collation if expected_char else None
        expected_precision = 6 if kind.lower() == "datetime(6)" else None
        if (default is not None or char != expected_char or collate != expected_collation
                or precision != expected_precision or generated):
            raise RuntimeError("facts migration found unexpected column defaults, charset or precision")
        if name != "source_type":
            # group/config nullability deliberately changes in the single ALTER.
            normalized_nullable = False if history and name in ("group_id", "config_revision") else nullable == "YES"
            original.append((name, kind.lower(), normalized_nullable, extra.lower(), default,
                             char, collate, precision, generated))
    return original


def _check_indexes(connection, table, expected):
    rows = _execute(connection, """
        SELECT INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME, SUB_PART,
               INDEX_TYPE, IS_VISIBLE, EXPRESSION, COLLATION, NULLABLE
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
    """, {"table": table})
    actual = {}
    for name, non_unique, position, column, subpart, index_type, visible, expression, direction, nullable in rows:
        expected_nullable = table in (OLD_LATEST, LATEST) and column == "expires_at"
        if (column is None or subpart is not None or index_type.upper() != "BTREE"
                or visible != "YES" or expression is not None or direction != "A"
                or (nullable == "YES") != expected_nullable):
            raise RuntimeError("facts migration found an unexpected index definition")
        entry = actual.setdefault(name, [int(non_unique), []])
        if entry[0] != int(non_unique) or position != len(entry[1]) + 1:
            raise RuntimeError("facts migration found an inconsistent index")
        entry[1].append(column)
    signature = {name: (value[0], tuple(value[1])) for name, value in actual.items()}
    if signature != expected:
        raise RuntimeError("facts migration found unexpected indexes or unique keys")
    return signature


def _normalized_check(clause):
    # MySQL may add identifier quoting, parentheses and charset introducers.
    value = re.sub(r"_[a-z0-9]+(?=')", "", clause.lower())
    return re.sub(r"[\s()`']", "", value)


def _check_checks(connection, table, history, altered):
    rows = _execute(connection, """
        SELECT tc.CONSTRAINT_NAME, tc.ENFORCED, cc.CHECK_CLAUSE
        FROM information_schema.TABLE_CONSTRAINTS tc
        JOIN information_schema.CHECK_CONSTRAINTS cc
          ON cc.CONSTRAINT_SCHEMA = tc.CONSTRAINT_SCHEMA AND cc.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
        WHERE tc.TABLE_SCHEMA = DATABASE() AND tc.TABLE_NAME = :table AND tc.CONSTRAINT_TYPE = 'CHECK'
    """, {"table": table})
    expected = {"ck_pfv2_sample_bounds" if history else "ck_pfv2_latest_bounds":
                "db_numberbetween1and65535andsource_seq>0"}
    if history and altered:
        expected["ck_pfv2_source_type"] = "source_typeisnullorcastsource_typeascharcharsetbinaryin0x646161,0x65787465726e616c"
    actual = {name: _normalized_check(clause) for name, enforced, clause in rows if enforced == "YES"}
    if actual != expected:
        raise RuntimeError("facts migration found unexpected or unenforced CHECK constraints")


def _check_dependencies(connection, schema):
    names = {OLD_HISTORY, OLD_LATEST, HISTORY, LATEST}
    rows = _execute(connection, """
        SELECT TABLE_SCHEMA, TABLE_NAME, REFERENCED_TABLE_SCHEMA, REFERENCED_TABLE_NAME
        FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_NAME IS NOT NULL
          AND (TABLE_SCHEMA = :schema OR REFERENCED_TABLE_SCHEMA = :schema)
    """, {"schema": schema})
    for local_schema, local_table, remote_schema, remote_table in rows:
        if ((local_schema == schema and local_table in names)
                or (remote_schema == schema and remote_table in names)):
            raise RuntimeError("facts migration found a visible foreign key dependency")
    excluded = {"information_schema", "mysql", "performance_schema", "sys"}
    queries = (
        "SELECT TABLE_SCHEMA, VIEW_DEFINITION FROM information_schema.VIEWS",
        "SELECT ROUTINE_SCHEMA, ROUTINE_DEFINITION FROM information_schema.ROUTINES",
        "SELECT EVENT_SCHEMA, EVENT_DEFINITION FROM information_schema.EVENTS",
    )
    for query in queries:
        for object_schema, definition in _execute(connection, query):
            if object_schema in excluded:
                continue
            if definition is None or any(name in definition.lower() for name in names):
                raise RuntimeError("facts migration cannot rule out a visible object dependency")
    for object_schema, object_table, definition in _execute(connection, """
        SELECT EVENT_OBJECT_SCHEMA, EVENT_OBJECT_TABLE, ACTION_STATEMENT FROM information_schema.TRIGGERS
    """):
        if object_schema in excluded:
            continue
        if (definition is None or (object_schema == schema and object_table in names)
                or any(name in definition.lower() for name in names)):
            raise RuntimeError("facts migration found a visible trigger dependency")


def _check_grants(connection, schema):
    """Reject old table-only grants not covered by equivalent new/schema/global grants.

    Information-schema visibility still requires the operator's independent
    privileged audit and effective application-account check at cutover.
    """
    names = (OLD_HISTORY, OLD_LATEST, HISTORY, LATEST)
    rows = list(_execute(connection, """
        SELECT GRANTEE, TABLE_NAME, PRIVILEGE_TYPE FROM information_schema.TABLE_PRIVILEGES
        WHERE TABLE_SCHEMA = :schema AND TABLE_NAME IN (:old_history, :old_latest, :history, :latest)
    """, {"schema": schema, "old_history": names[0], "old_latest": names[1],
          "history": names[2], "latest": names[3]}))
    schema_grants = {(g, p) for g, p in _execute(connection, """
        SELECT GRANTEE, PRIVILEGE_TYPE FROM information_schema.SCHEMA_PRIVILEGES WHERE TABLE_SCHEMA = :schema
    """, {"schema": schema})}
    global_grants = {(g, p) for g, p in _execute(connection, """
        SELECT GRANTEE, PRIVILEGE_TYPE FROM information_schema.USER_PRIVILEGES
    """)}
    table_grants = set(tuple(row) for row in rows)
    for grantee, old_name, privilege in table_grants:
        if old_name not in (OLD_HISTORY, OLD_LATEST):
            continue
        new_name = HISTORY if old_name == OLD_HISTORY else LATEST
        if ((grantee, new_name, privilege) not in table_grants
                and (grantee, privilege) not in schema_grants
                and (grantee, privilege) not in global_grants):
            raise RuntimeError("facts migration found a table-only grant without equivalent new access")


def _cell(value):
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {"bytes": bytes(value).hex()}
    if isinstance(value, (datetime, date)):
        return {"date": value.isoformat()}
    if isinstance(value, Decimal):
        return {"decimal": str(value)}
    return value


def _rows_digest(connection, table, columns, primary):
    columns_sql = ", ".join(f"`{name}`" for name, *_ in columns)
    order_sql = ", ".join(f"`{name}`" for name in primary)
    rows = connection.execution_options(stream_results=True).execute(
        text(f"SELECT {columns_sql} FROM `{table}` ORDER BY {order_sql}")
    )
    digest = hashlib.sha256()
    count = 0
    try:
        for row in rows:
            raw = json.dumps([_cell(value) for value in row], ensure_ascii=True,
                             separators=(",", ":"), allow_nan=False).encode("ascii")
            digest.update(len(raw).to_bytes(8, "big"))
            digest.update(raw)
            count += 1
    finally:
        rows.close()
        connection.execution_options(stream_results=False)
    return {"count": count, "sha256": digest.hexdigest()}


def _audit(connection, history, latest):
    """Original-column and schema evidence, independent of renamed table names."""
    stage, current_history, current_latest = _state(connection)
    if (history, latest) != (current_history, current_latest):
        raise RuntimeError("facts audit table identity mismatch")
    history_columns = _check_columns(connection, history, True, stage == "altered")
    latest_columns = _check_columns(connection, latest, False, False)
    history_indexes = _check_indexes(connection, history, HISTORY_INDEXES)
    latest_indexes = _check_indexes(connection, latest, LATEST_INDEXES)
    auto_increment = _execute(connection, """
        SELECT AUTO_INCREMENT FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table
    """, {"table": history}).scalar_one()
    return {
        "history": _rows_digest(connection, history, HISTORY_COLUMNS, ("id",)),
        "latest": _rows_digest(connection, latest, LATEST_COLUMNS, ("plc_id", "db_number", "point_id")),
        "historyAutoIncrement": auto_increment,
        "historyColumns": history_columns,
        "latestColumns": latest_columns,
        "historyIndexes": history_indexes,
        "latestIndexes": latest_indexes,
    }


def recovery_evidence_sha256(connection):
    """Return the operation-bound evidence hash for recording before DDL/recovery.

    Call only inside the stopped-writers maintenance window. The recorded hash
    must be independently reviewed and retained with the external operation log.
    This helper does not mutate data or establish permission to run DDL.
    """
    schema, server_uuid, operation = _target(connection)
    stage, history, latest = _state(connection)
    _check_columns(connection, history, True, stage == "altered")
    _check_columns(connection, latest, False, False)
    _check_indexes(connection, history, HISTORY_INDEXES)
    _check_indexes(connection, latest, LATEST_INDEXES)
    _check_checks(connection, history, True, stage == "altered")
    _check_checks(connection, latest, False, False)
    if stage == "altered" and _execute(connection, f"SELECT 1 FROM `{HISTORY}` WHERE source_type IS NOT NULL LIMIT 1").first():
        raise RuntimeError("facts recovery requires all newly added source types to be NULL")
    evidence = {"schema": schema, "serverUuid": server_uuid, "operationId": operation,
                "predecessor": down_revision, "successor": revision,
                "original": _audit(connection, history, latest)}
    return hashlib.sha256(json.dumps(evidence, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True).encode("ascii")).hexdigest()


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError("facts migration requires online preflight; offline SQL prohibited")
    connection = op.get_bind()
    schema, _, _ = _target(connection)
    if list(_execute(connection, "SELECT version_num FROM alembic_version").scalars()) != [down_revision]:
        raise RuntimeError("facts migration requires the exact single predecessor revision")
    previous_timeout = _execute(connection, "SELECT @@SESSION.lock_wait_timeout").scalar_one()
    _execute(connection, "SET SESSION lock_wait_timeout = 5")
    try:
        stage, history, latest = _state(connection)
        _check_dependencies(connection, schema)
        _check_grants(connection, schema)
        proof = recovery_evidence_sha256(connection)
        if stage != "old":
            expected_stage = os.environ.get("ACQ_FACTS_RECOVERY_STAGE", "")
            expected_digest = os.environ.get("ACQ_FACTS_RECOVERY_EVIDENCE_SHA256", "")
            if (expected_stage != stage or not re.fullmatch(r"[0-9a-f]{64}", expected_digest)
                    or expected_digest != proof):
                raise RuntimeError("facts recovery stage or independently recorded evidence mismatch")
        before = _audit(connection, history, latest)
        if stage == "old":
            op.execute(RENAME_SQL)
            stage, history, latest = _state(connection)
            if stage != "renamed" or recovery_evidence_sha256(connection) != proof:
                raise RuntimeError("facts rename preservation check failed; maintain the window")
        if stage == "renamed":
            op.execute(ALTER_SQL)
            stage, history, latest = _state(connection)
            if stage != "altered" or recovery_evidence_sha256(connection) != proof:
                raise RuntimeError("facts alter preservation check failed; maintain the window")
        if _audit(connection, history, latest) != before:
            raise RuntimeError("facts original-column preservation check failed")
        _check_grants(connection, schema)
        # Alembic registers the successor only after this function returns.
    finally:
        _execute(connection, "SET SESSION lock_wait_timeout = :timeout", {"timeout": previous_timeout})


def downgrade():
    raise RuntimeError("facts migration is forward-only; restore requires an approved recovery procedure")
