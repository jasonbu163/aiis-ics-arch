"""ARCH-ENERGY-002：增加独立能耗曲线组配置，保留原能耗事实。"""
import os

import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.dialects.mysql import VARCHAR

revision = "af6d8b2c4e90"
down_revision = "9e0c5d41b7a2"
branch_labels = None
depends_on = None

TABLE = "energy_curve_group_configs"


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError("energy curve groups require an inspected online target")
    connection = op.get_bind()
    if connection.dialect.name != "mysql":
        raise RuntimeError("energy curve groups require MySQL")
    uuid, schema = connection.execute(sa.text("SELECT @@server_uuid, DATABASE()")).one()
    if (not schema or schema.lower() in {"mysql", "sys", "information_schema", "performance_schema"}
            or schema != os.environ.get("ENERGY_CURVE_EXPECTED_SCHEMA")
            or uuid != os.environ.get("ENERGY_CURVE_EXPECTED_SERVER_UUID")):
        raise RuntimeError("energy curve group migration target mismatch")
    if list(connection.execute(sa.text("SELECT version_num FROM alembic_version")).scalars()) != [down_revision]:
        raise RuntimeError("energy curve groups require the exact predecessor")
    inspector = sa.inspect(connection)
    if inspector.has_table(TABLE):
        raise RuntimeError("energy curve group table already exists")
    required = {
        "energy_meters": {"meter_id", "read_roles"},
        "energy_metric_configs": {"meter_id", "group_key", "metric_key", "value_type", "quantity_key", "unit"},
    }
    for table, columns in required.items():
        if (not inspector.has_table(table) or inspector.get_table_options(table).get("mysql_engine") != "InnoDB"
                or not columns.issubset({column["name"] for column in inspector.get_columns(table)})):
            raise RuntimeError("required energy curve predecessor layout missing")
    op.create_table(
        TABLE,
        sa.Column("curve_group_key", VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), primary_key=True),
        sa.Column("title_zh", sa.String(128), nullable=False),
        sa.Column("title_en", sa.String(128), nullable=False),
        sa.Column("meter_id", VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), nullable=False),
        sa.Column("group_key", VARCHAR(64, charset="utf8mb4", collation="utf8mb4_bin"), nullable=False),
        sa.Column("sort_order", sa.BigInteger(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("series", sa.JSON(), nullable=False),
        sa.Index("ix_energy_curve_groups_meter", "meter_id"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4",
    )


def downgrade():
    raise RuntimeError("retain energy curve groups when rolling back application code")
