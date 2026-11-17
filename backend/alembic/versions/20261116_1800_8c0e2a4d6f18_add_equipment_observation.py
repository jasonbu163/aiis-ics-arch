"""设备状态、过程历史和配置表的显式后继迁移。"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "8c0e2a4d6f18"
down_revision = "7b9d1f3a5c7e"
branch_labels = None
depends_on = None


def upgrade():
    stamp = sa.text("CURRENT_TIMESTAMP(6)")
    op.create_table(
        "equipment_metric_configs",
        sa.Column("metric_key", sa.String(64, collation="utf8mb4_bin"), primary_key=True),
        sa.Column("source_group_key", sa.String(64, collation="utf8mb4_bin"), nullable=False),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("name_zh", sa.String(128), nullable=False),
        sa.Column("name_en", sa.String(128), nullable=False),
        sa.Column("value_type", sa.String(16), nullable=False),
        sa.Column("unit", sa.String(24)),
        sa.Column("decimals", mysql.TINYINT(unsigned=True)),
        sa.CheckConstraint("value_type IN ('number','boolean','string')", name="ck_obs_metric_type"),
    )
    op.create_table(
        "equipment_metric_slot_bindings",
        sa.Column("target", sa.String(7), primary_key=True),
        sa.Column("group_key", sa.String(64, collation="utf8mb4_bin"), primary_key=True),
        sa.Column("slot_no", mysql.TINYINT(unsigned=True), primary_key=True),
        sa.Column("metric_key", sa.String(64, collation="utf8mb4_bin"), sa.ForeignKey("equipment_metric_configs.metric_key", ondelete="RESTRICT"), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("list_visible", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("list_order", sa.Integer),
        sa.Column("first_used_at", mysql.DATETIME(fsp=6)),
        sa.UniqueConstraint("target", "group_key", "metric_key", name="uq_obs_binding_metric"),
        sa.CheckConstraint("target IN ('latest','history') AND slot_no BETWEEN 1 AND 100", name="ck_obs_binding_scope"),
        sa.CheckConstraint("list_order IS NULL OR list_order >= 0", name="ck_obs_binding_list_order"),
    )
    op.create_table(
        "equipment_card_configs",
        sa.Column("card_key", sa.String(64, collation="utf8mb4_bin"), primary_key=True),
        sa.Column("page_key", sa.String(32), nullable=False),
        sa.Column("title_zh", sa.String(128), nullable=False),
        sa.Column("title_en", sa.String(128), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("sort_order", mysql.BIGINT, nullable=False),
        sa.Column("items", sa.JSON, nullable=False),
    )
    op.create_index("ix_obs_card_page", "equipment_card_configs", ["page_key", "sort_order", "card_key"])
    op.create_table(
        "monitor_curve_group_configs",
        sa.Column("curve_group_key", sa.String(64, collation="utf8mb4_bin"), primary_key=True),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("title_zh", sa.String(128), nullable=False),
        sa.Column("title_en", sa.String(128), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("sort_order", mysql.BIGINT, nullable=False),
        sa.Column("series", sa.JSON, nullable=False),
    )
    op.create_index("ix_obs_curve_category", "monitor_curve_group_configs", ["category", "sort_order", "curve_group_key"])
    op.create_table(
        "metric_ingest_receipts",
        sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column("target", sa.String(7), nullable=False),
        sa.Column("producer_id", sa.String(64, collation="utf8mb4_bin"), nullable=False),
        sa.Column("event_id", sa.String(128, collation="utf8mb4_bin"), nullable=False),
        sa.Column("request_digest", mysql.BINARY(32), nullable=False),
        sa.Column("outcome", sa.String(24), nullable=False),
        sa.Column("processed_at", mysql.DATETIME(fsp=6), nullable=False, server_default=stamp),
        sa.Column("result_record_id", mysql.BIGINT(unsigned=True)),
        sa.Column("mapping_id", sa.String(64), nullable=False),
        sa.Column("mapping_revision", sa.String(32), nullable=False),
        sa.Column("source_refs", sa.JSON, nullable=False),
        sa.Column("task_evidence", sa.JSON, nullable=False),
        sa.UniqueConstraint("target", "producer_id", "event_id", name="uq_obs_receipt_event"),
    )
    def columns():
        return [
            sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True),
            sa.Column("equipment_id", sa.String(64, collation="utf8mb4_bin"), nullable=False),
            sa.Column("group_key", sa.String(64, collation="utf8mb4_bin"), nullable=False),
            sa.Column("task_no", sa.String(50, collation="utf8mb4_bin"), nullable=False),
            sa.Column("sampled_at", mysql.DATETIME(fsp=6), nullable=False),
            sa.Column("quality", sa.String(16), nullable=False),
            sa.Column("source_sample_key", mysql.BINARY(32), nullable=False),
            sa.Column("ingest_receipt_id", mysql.BIGINT(unsigned=True), sa.ForeignKey("metric_ingest_receipts.id", ondelete="RESTRICT"), nullable=False),
            sa.Column("local_values", sa.JSON, nullable=False),
            sa.Column("remark", sa.Text),
            sa.Column("created_at", mysql.DATETIME(fsp=6), nullable=False, server_default=stamp),
            sa.Column("updated_at", mysql.DATETIME(fsp=6), nullable=False, server_default=stamp),
        ]
    op.create_table(
        "equipment_status_main", *columns(),
        sa.UniqueConstraint("equipment_id", "task_no", "group_key", name="uq_obs_latest_task_group"),
    )
    op.create_index("ix_obs_latest_task", "equipment_status_main", ["task_no", "id"])
    op.create_table(
        "process_monitor_main", *columns(), sa.Column("review_mark", sa.String(16)),
        sa.UniqueConstraint("equipment_id", "task_no", "group_key", "sampled_at", "source_sample_key", name="uq_obs_history_source"),
        sa.CheckConstraint("review_mark IS NULL OR review_mark IN ('abnormal','reviewed')", name="ck_obs_review_mark"),
    )
    op.create_index("ix_obs_history_task_time", "process_monitor_main", ["task_no", "sampled_at", "id"])
    op.create_index("ix_obs_history_group_time", "process_monitor_main", ["equipment_id", "group_key", "sampled_at", "id"])


def downgrade():
    for name in ("process_monitor_main", "equipment_status_main", "metric_ingest_receipts",
                 "monitor_curve_group_configs", "equipment_card_configs", "equipment_metric_slot_bindings",
                 "equipment_metric_configs"):
        op.drop_table(name)
