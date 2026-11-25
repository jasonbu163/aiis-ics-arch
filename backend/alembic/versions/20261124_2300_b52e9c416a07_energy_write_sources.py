"""ARCH-OBS-010：仅新增独立能耗写入登记，原有记录保持原位。"""
import os

from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR

revision = "b52e9c416a07"
down_revision = "a1c307f8d2e4"
branch_labels = None
depends_on = None

TABLE = "energy_write_sources"


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError("energy write sources require an inspected online target")
    connection = op.get_bind()
    if connection.dialect.name != "mysql":
        raise RuntimeError("energy write sources require MySQL")
    uuid, schema = connection.execute(sa.text("SELECT @@server_uuid, DATABASE()")).one()
    if (not schema or schema.lower() in {"mysql", "sys", "information_schema", "performance_schema"}
            or schema != os.environ.get("ENERGY_WRITE_EXPECTED_SCHEMA")
            or uuid != os.environ.get("ENERGY_WRITE_EXPECTED_SERVER_UUID")):
        raise RuntimeError("energy write source migration target mismatch")
    if list(connection.execute(sa.text("SELECT version_num FROM alembic_version")).scalars()) != [down_revision]:
        raise RuntimeError("energy write sources require the exact predecessor")
    inspector = sa.inspect(connection)
    if inspector.has_table(TABLE):
        raise RuntimeError("energy write source table already exists")
    required = {
        "energy_metric_configs": {"meter_id", "group_key", "metric_key", "slot_no", "first_used_at"},
        "energy_consumption_main": {"meter_id", "group_key", "observed_at", "local_values", "ingest_receipt_id"},
        "energy_ingest_receipts": {"target", "producer_id", "event_id", "request_digest",
                                   "contract_version", "result_version", "result_detail"},
    }
    for table, columns in required.items():
        if (not inspector.has_table(table) or inspector.get_table_options(table).get("mysql_engine") != "InnoDB"
                or not columns.issubset({column["name"] for column in inspector.get_columns(table)})):
            raise RuntimeError("required energy predecessor layout missing")
    keys = inspector.get_unique_constraints("energy_ingest_receipts")
    if not any(key["column_names"] == ["target", "producer_id", "event_id"] for key in keys):
        raise RuntimeError("required energy receipt uniqueness missing")
    op.create_table(
        TABLE,
        sa.Column("source_key", VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), primary_key=True),
        sa.Column("storage_identity", VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), nullable=False),
        sa.Column("name", sa.String(128)),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", DATETIME(fsp=6), nullable=False),
        sa.Column("updated_at", DATETIME(fsp=6), nullable=False),
        sa.Column("deleted_at", DATETIME(fsp=6)),
        sa.UniqueConstraint("storage_identity", name="uq_energy_write_source_identity"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4",
    )


def downgrade():
    raise RuntimeError("retain energy registrations, samples and receipts when rolling back application code")
