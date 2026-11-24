"""在已核验的前驱上新增质量结果表与本地字段配置表。"""
from datetime import datetime
import os
from pathlib import Path

from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import DATETIME, VARCHAR

from common.integration.envelope import BUSINESS_TIMEZONE

revision = "f0a2b4c6d8e1"
down_revision = "e9f3b5d7c021"
branch_labels = None
depends_on = None


def _preflight(connection):
    dialect = connection.dialect.name
    if dialect == "mysql":
        version, uuid, schema, offset = connection.execute(sa.text(
            "SELECT VERSION(), @@server_uuid, DATABASE(), "
            "TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))"
        )).one()
        if (not version.startswith("8.4.") or not schema
                or schema.lower() in {"mysql", "sys", "information_schema", "performance_schema"}
                or schema != os.environ.get("QUALITY_EXPECTED_SCHEMA")
                or uuid != os.environ.get("QUALITY_EXPECTED_SERVER_UUID") or offset != 28800):
            raise RuntimeError("quality migration target, MySQL version or timezone mismatch")
    elif dialect == "sqlite":
        path = next((row[2] for row in connection.exec_driver_sql("PRAGMA database_list")
                     if row[1] == "main"), "")
        expected = os.environ.get("QUALITY_EXPECTED_SQLITE_PATH")
        if not path or not expected or Path(path).resolve() != Path(expected).resolve():
            raise RuntimeError("quality migration requires an explicit SQLite fixture path")
    else:
        raise RuntimeError("quality migration requires an inspected MySQL or SQLite target")

    revisions = list(connection.execute(sa.text("SELECT version_num FROM alembic_version")).scalars())
    if revisions != [down_revision]:
        raise RuntimeError("quality migration requires the exact single predecessor")
    existing = set(sa.inspect(connection).get_table_names())
    if existing & {"quality_main", "quality_field_config"}:
        raise RuntimeError("new quality table names are already occupied")
    return dialect


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError("quality migration requires an inspected online target")
    connection = op.get_bind()
    dialect = _preflight(connection)
    mysql = dialect == "mysql"
    options = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"} if mysql else {}

    def key(size):
        return VARCHAR(size, charset="ascii", collation="ascii_bin") if mysql else sa.String(size)

    def stamp(name):
        return sa.Column(name, DATETIME(fsp=6) if mysql else sa.String(32), nullable=False)

    op.create_table(
        "quality_main",
        sa.Column("id", sa.BigInteger() if mysql else sa.Integer(), primary_key=True),
        sa.Column("task_no", key(50), nullable=False),
        sa.Column("target_key", key(64)),
        sa.Column("items", sa.JSON(), nullable=False),
        stamp("created_at"), stamp("updated_at"),
        sa.CheckConstraint("lower(json_type(items)) = 'object'", name="ck_quality_main_items"),
        sa.UniqueConstraint("task_no", name="uq_quality_main_task_no"),
        **options,
    )
    op.create_index("ix_quality_main_created_id", "quality_main", ["created_at", "id"])
    op.create_index("ix_quality_main_target_created_id", "quality_main", ["target_key", "created_at", "id"])
    config = op.create_table(
        "quality_field_config",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("definitions", sa.JSON(), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        stamp("created_at"), stamp("updated_at"),
        sa.CheckConstraint("lower(json_type(definitions)) = 'array'", name="ck_quality_config_definitions"),
        sa.CheckConstraint("id = 1", name="ck_quality_config_singleton"),
        sa.CheckConstraint("revision >= 1", name="ck_quality_config_revision"),
        **options,
    )
    now = datetime.now(BUSINESS_TIMEZONE)
    stored_now = now.replace(tzinfo=None) if mysql else now.isoformat(timespec="microseconds")
    op.bulk_insert(config, [{
        "id": 1, "revision": 1, "definitions": [],
        "created_at": stored_now, "updated_at": stored_now,
    }])


def downgrade():
    raise RuntimeError("quality results require explicit, data-preserving rollback planning")
