"""ARCH-ENERGY-005：增加独立表计定义，保留原能耗事实。"""
import os

from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR

revision = "9e0c5d41b7a2"
down_revision = "b52e9c416a07"
branch_labels = None
depends_on = None

TABLE = "energy_meters"


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError("energy meters require an inspected online target")
    connection = op.get_bind()
    if connection.dialect.name != "mysql":
        raise RuntimeError("energy meters require MySQL")
    uuid, schema = connection.execute(sa.text("SELECT @@server_uuid, DATABASE()")).one()
    if (not schema or schema.lower() in {"mysql", "sys", "information_schema", "performance_schema"}
            or schema != os.environ.get("ENERGY_METER_EXPECTED_SCHEMA")
            or uuid != os.environ.get("ENERGY_METER_EXPECTED_SERVER_UUID")):
        raise RuntimeError("energy meter migration target mismatch")
    if list(connection.execute(sa.text("SELECT version_num FROM alembic_version")).scalars()) != [down_revision]:
        raise RuntimeError("energy meters require the exact predecessor")
    inspector = sa.inspect(connection)
    if inspector.has_table(TABLE):
        raise RuntimeError("energy meter table already exists")
    required = {
        "energy_metric_configs": {"meter_id", "group_key", "metric_key", "slot_no"},
        "energy_consumption_main": {"meter_id", "group_key", "observed_at", "local_values"},
        "energy_ingest_receipts": {"id", "producer_id", "event_id"},
        "energy_write_sources": {"source_key", "storage_identity", "enabled"},
    }
    for table, columns in required.items():
        if (not inspector.has_table(table) or inspector.get_table_options(table).get("mysql_engine") != "InnoDB"
                or not columns.issubset({column["name"] for column in inspector.get_columns(table)})):
            raise RuntimeError("required energy predecessor layout missing")
    op.create_table(
        TABLE,
        sa.Column("meter_id", VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), primary_key=True),
        sa.Column("name_zh", sa.String(128), nullable=False),
        sa.Column("name_en", sa.String(128), nullable=False),
        sa.Column("read_roles", sa.JSON, nullable=False),
        sa.Column("created_at", DATETIME(fsp=6), nullable=False),
        sa.Column("updated_at", DATETIME(fsp=6), nullable=False),
        mysql_engine="InnoDB", mysql_charset="utf8mb4",
    )


def downgrade():
    raise RuntimeError("retain energy meter definitions when rolling back application code")
