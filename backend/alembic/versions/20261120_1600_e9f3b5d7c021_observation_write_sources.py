"""在经核验的 OBS 前驱上仅新增一张来源登记表。"""
import os

from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR

revision = "e9f3b5d7c021"
down_revision = "d8f2a4c6b915"
branch_labels = None
depends_on = None

TABLE = "observation_write_sources"
REQUIRED = {
    "equipment_main": {"id", "equipment_id", "task_no", "observed_at", "quality", "source_sample_key",
                       "local_values", "ingest_receipt_id", "created_at", "updated_at"},
    "monitor_main": {"id", "equipment_id", "task_no", "observed_at", "quality", "source_sample_key",
                     "local_values", "ingest_receipt_id", "created_at", "updated_at"},
    "observation_ingest_receipts": {"id", "target", "producer_id", "event_id", "request_digest", "processed_at",
                                   "outcome", "result_record_id", "contract_version", "result_version"},
    "observation_metric_groups": {"group_key", "enabled"},
    "observation_metric_configs": {"metric_key", "source_group_key", "value_type"},
    "observation_metric_slot_bindings": {"target", "group_key", "slot_no", "metric_key", "enabled", "first_used_at"},
    "equipment_card_configs": {"card_key", "items"},
    "monitor_curve_group_configs": {"curve_group_key", "series"},
}
IDENTITIES = {("equipment_main", "equipment_id"), ("monitor_main", "equipment_id"),
              ("observation_ingest_receipts", "producer_id")}


def _target(connection, expected_revision):
    if context.is_offline_mode() or connection.dialect.name != "mysql":
        raise RuntimeError("observation write sources require an inspected online MySQL 8.4 target")
    version, uuid, schema, offset = connection.execute(sa.text(
        "SELECT VERSION(), @@server_uuid, DATABASE(), "
        "TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))"
    )).one()
    if (not version.startswith("8.4.") or not schema or schema.lower() in
            {"mysql", "sys", "information_schema", "performance_schema"}
            or schema != os.environ.get("OBS_WRITE_EXPECTED_SCHEMA")
            or uuid != os.environ.get("OBS_WRITE_EXPECTED_SERVER_UUID") or offset != 28800):
        raise RuntimeError("observation write source target, MySQL version or timezone mismatch")
    if list(connection.execute(sa.text("SELECT version_num FROM alembic_version")).scalars()) != [expected_revision]:
        raise RuntimeError("observation write sources require the exact single schema revision")
    return schema


def _preflight(connection, schema):
    tables = dict(connection.execute(sa.text(
        "SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA = :schema"
    ), {"schema": schema}).all())
    if TABLE in tables or any(tables.get(name) != "InnoDB" for name in REQUIRED):
        raise RuntimeError("observation write source table occupied or required predecessor table missing")
    columns = {}
    for table, name, kind, nullable, collation in connection.execute(sa.text(
        "SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLLATION_NAME "
        "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = :schema"
    ), {"schema": schema}):
        columns[table, name] = (kind, nullable, collation)
    if any((table, field) not in columns for table, fields in REQUIRED.items() for field in fields):
        raise RuntimeError("required observation predecessor columns missing")
    expected = {key: ("varchar(64)", "NO", "utf8mb4_bin") for key in IDENTITIES}
    for table in ("equipment_main", "monitor_main"):
        expected[table, "task_no"] = ("varchar(50)", "NO", "utf8mb4_bin")
        expected[table, "observed_at"] = ("datetime(6)", "NO", None)
        expected[table, "local_values"] = ("json", "NO", None)
    expected["observation_ingest_receipts", "request_digest"] = ("binary(32)", "NO", None)
    if any(columns[key] != signature for key, signature in expected.items()):
        raise RuntimeError("required observation predecessor column layout changed")
    indexes = {}
    for table, name, field in connection.execute(sa.text(
        "SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME FROM information_schema.STATISTICS "
        "WHERE TABLE_SCHEMA = :schema AND NON_UNIQUE = 0 AND SUB_PART IS NULL ORDER BY SEQ_IN_INDEX"
    ), {"schema": schema}):
        indexes.setdefault((table, name), []).append(field)
    if (indexes.get(("equipment_main", "uq_obs_latest_task")) != ["equipment_id", "task_no"]
            or indexes.get(("observation_ingest_receipts", "uq_obs_receipt_event")) != ["target", "producer_id", "event_id"]):
        raise RuntimeError("required observation predecessor uniqueness changed")
    references = set(connection.execute(sa.text(
        "SELECT k.TABLE_NAME, k.CONSTRAINT_NAME, k.COLUMN_NAME, k.REFERENCED_TABLE_NAME, "
        "k.REFERENCED_COLUMN_NAME, r.DELETE_RULE FROM information_schema.KEY_COLUMN_USAGE k "
        "JOIN information_schema.REFERENTIAL_CONSTRAINTS r "
        "ON r.CONSTRAINT_SCHEMA = k.CONSTRAINT_SCHEMA AND r.TABLE_NAME = k.TABLE_NAME "
        "AND r.CONSTRAINT_NAME = k.CONSTRAINT_NAME "
        "WHERE k.TABLE_SCHEMA = :schema AND k.REFERENCED_TABLE_SCHEMA = :schema "
        "AND k.TABLE_NAME IN ('equipment_main', 'monitor_main', 'observation_metric_slot_bindings')"
    ), {"schema": schema}).all())
    if references != {
        ("equipment_main", "fk_obs_r10_latest_receipt", "ingest_receipt_id", "observation_ingest_receipts", "id", "RESTRICT"),
        ("monitor_main", "fk_obs_r10_history_receipt", "ingest_receipt_id", "observation_ingest_receipts", "id", "RESTRICT"),
        ("observation_metric_slot_bindings", "fk_obs_r10_binding_metric", "metric_key",
         "observation_metric_configs", "metric_key", "RESTRICT"),
    }:
        raise RuntimeError("required observation predecessor foreign keys changed")


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError("observation write sources require an inspected online target")
    connection = op.get_bind()
    _preflight(connection, _target(connection, down_revision))
    op.create_table(
        TABLE,
        sa.Column("source_key", VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), primary_key=True),
        sa.Column("storage_identity", VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), nullable=False),
        sa.Column("name", sa.String(128)),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", DATETIME(fsp=6), nullable=False),
        sa.Column("updated_at", DATETIME(fsp=6), nullable=False),
        sa.Column("deleted_at", DATETIME(fsp=6)),
        sa.UniqueConstraint("storage_identity", name="uq_obs_write_source_identity"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4",
    )


def downgrade():
    raise RuntimeError("observation write source mappings are forward-only; review actual data before any rollback")
