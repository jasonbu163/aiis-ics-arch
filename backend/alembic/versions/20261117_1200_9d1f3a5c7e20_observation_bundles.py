"""保全 r8 原行并建立 r10 整包、区域和独立表计样本。"""
from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "9d1f3a5c7e20"
down_revision = "8c0e2a4d6f18"
branch_labels = None
depends_on = None


def _legacy_preflight():
    if context.is_offline_mode():
        # The generated SQL is for review only: a raw SQL runner cannot perform
        # the verified-writer/time/schema checks performed by online Alembic.
        op.execute("SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'r10 offline SQL is review-only; use guarded online migration'")
        return
    bind = op.get_bind()
    args = context.get_x_argument(as_dictionary=True)
    if args.get("obs_r10_writers_quiesced") != "yes":
        raise RuntimeError("r10 requires verified quiescent writers (-x obs_r10_writers_quiesced=yes)")
    if bind.execute(sa.text("SELECT TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(), CURRENT_TIMESTAMP())")).scalar_one() != 28800:
        raise RuntimeError("r10 requires verified Asia/Shanghai database time")
    names = ("equipment_status_r8_archive", "process_monitor_r8_archive",
             "equipment_metric_configs_r8_archive", "equipment_metric_slot_bindings_r8_archive",
             "equipment_card_configs_r8_archive", "monitor_curve_group_configs_r8_archive",
             "equipment_metric_groups", "energy_metric_configs", "energy_consumption_main")
    inspector = sa.inspect(bind)
    if any(inspector.has_table(name) for name in names):
        raise RuntimeError("r10 destination or archive already exists; inspect partial migration")
    counts = [bind.execute(sa.text(f"SELECT COUNT(*) FROM {name}")).scalar_one()
              for name in ("equipment_status_main", "process_monitor_main")]
    if any(counts) and args.get("obs_r10_legacy_time_basis") != "verified_shanghai_observed":
        raise RuntimeError("r8 sampled_at meaning and timezone must be independently verified before migration")
    ambiguous = bind.execute(sa.text("SELECT COUNT(*) FROM (SELECT source_group_key FROM equipment_metric_configs "
                                     "GROUP BY source_group_key HAVING COUNT(DISTINCT category) <> 1 "
                                     "OR MIN(category) NOT IN ('production','cleaning','temperature','drive')) AS bad")).scalar_one()
    if ambiguous:
        raise RuntimeError("r8 group categories are ambiguous; preserve and review before migration")
    for table in ("equipment_status_main", "process_monitor_main"):
        missing = bind.execute(sa.text(f"SELECT COUNT(*) FROM {table} r LEFT JOIN "
                                       "(SELECT DISTINCT source_group_key FROM equipment_metric_configs) g "
                                       "ON g.source_group_key=r.group_key WHERE g.source_group_key IS NULL")).scalar_one()
        if missing:
            raise RuntimeError("r8 rows have no decodable group configuration; preserve and review")


def upgrade():
    _legacy_preflight()
    stamp = sa.text("CURRENT_TIMESTAMP(6)")
    key = lambda: sa.String(64, collation="utf8mb4_bin")
    # Preserve original r8 tables including their indexes, constraints and rows.
    op.execute("RENAME TABLE equipment_status_main TO equipment_status_r8_archive, "
               "process_monitor_main TO process_monitor_r8_archive, "
               "equipment_metric_slot_bindings TO equipment_metric_slot_bindings_r8_archive, "
               "equipment_metric_configs TO equipment_metric_configs_r8_archive, "
               "equipment_card_configs TO equipment_card_configs_r8_archive, "
               "monitor_curve_group_configs TO monitor_curve_group_configs_r8_archive")
    # New writable copies keep r8 snapshots independent of subsequent edits.
    op.create_table("equipment_metric_configs",
        sa.Column("metric_key", key(), primary_key=True), sa.Column("source_group_key", key(), nullable=False),
        sa.Column("category", sa.String(32), nullable=False), sa.Column("name_zh", sa.String(128), nullable=False),
        sa.Column("name_en", sa.String(128), nullable=False), sa.Column("value_type", sa.String(16), nullable=False),
        sa.Column("unit", sa.String(24)), sa.Column("decimals", mysql.TINYINT(unsigned=True)),
        sa.CheckConstraint("value_type IN ('number','boolean','string')", name="ck_obs_r10_metric_type"))
    op.create_table("equipment_metric_slot_bindings",
        sa.Column("target", sa.String(7), primary_key=True), sa.Column("group_key", key(), primary_key=True),
        sa.Column("slot_no", mysql.TINYINT(unsigned=True), primary_key=True),
        sa.Column("metric_key", key(), sa.ForeignKey("equipment_metric_configs.metric_key", name="fk_obs_r10_binding_metric", ondelete="RESTRICT"), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False), sa.Column("list_visible", sa.Boolean, nullable=False),
        sa.Column("list_order", sa.Integer), sa.Column("first_used_at", mysql.DATETIME(fsp=6)),
        sa.UniqueConstraint("target", "group_key", "metric_key", name="uq_obs_r10_binding_metric"),
        sa.CheckConstraint("target IN ('latest','history') AND slot_no BETWEEN 1 AND 100", name="ck_obs_r10_binding_scope"),
        sa.CheckConstraint("list_order IS NULL OR list_order >= 0", name="ck_obs_r10_binding_order"))
    op.create_table("equipment_card_configs", sa.Column("card_key", key(), primary_key=True),
        sa.Column("page_key", sa.String(32), nullable=False), sa.Column("title_zh", sa.String(128), nullable=False),
        sa.Column("title_en", sa.String(128), nullable=False), sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("sort_order", mysql.BIGINT, nullable=False), sa.Column("items", sa.JSON, nullable=False))
    op.create_index("ix_obs_r10_card_page", "equipment_card_configs", ["page_key", "sort_order", "card_key"])
    op.create_table("monitor_curve_group_configs", sa.Column("curve_group_key", key(), primary_key=True),
        sa.Column("category", sa.String(32), nullable=False), sa.Column("title_zh", sa.String(128), nullable=False),
        sa.Column("title_en", sa.String(128), nullable=False), sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("sort_order", mysql.BIGINT, nullable=False), sa.Column("series", sa.JSON, nullable=False))
    op.create_index("ix_obs_r10_curve_category", "monitor_curve_group_configs", ["category", "sort_order", "curve_group_key"])
    op.execute("INSERT INTO equipment_metric_configs SELECT * FROM equipment_metric_configs_r8_archive")
    op.execute("INSERT INTO equipment_metric_slot_bindings SELECT * FROM equipment_metric_slot_bindings_r8_archive")
    op.execute("INSERT INTO equipment_card_configs SELECT * FROM equipment_card_configs_r8_archive")
    op.execute("INSERT INTO monitor_curve_group_configs SELECT * FROM monitor_curve_group_configs_r8_archive")
    for name, kind in (("mapping_id", sa.String(64)), ("mapping_revision", sa.String(32)),
                       ("source_refs", sa.JSON()), ("task_evidence", sa.JSON())):
        op.alter_column("metric_ingest_receipts", name, existing_type=kind, nullable=True)
    op.add_column("metric_ingest_receipts", sa.Column("contract_version", sa.String(32), nullable=False,
                                                       server_default="aiis.metric-ingest/v1"))
    op.add_column("metric_ingest_receipts", sa.Column("result_version", sa.String(8), nullable=False, server_default="r8"))
    op.add_column("metric_ingest_receipts", sa.Column("result_detail", sa.JSON()))
    op.create_table("equipment_metric_groups", sa.Column("group_key", key(), primary_key=True),
        sa.Column("category", sa.String(32), nullable=False), sa.Column("name_zh", sa.String(128), nullable=False),
        sa.Column("name_en", sa.String(128), nullable=False), sa.Column("enabled", sa.Boolean, nullable=False),
        sa.Column("sort_order", mysql.BIGINT, nullable=False),
        sa.CheckConstraint("category IN ('production','cleaning','temperature','drive')", name="ck_obs_group_category"))
    op.execute("INSERT INTO equipment_metric_groups (group_key,category,name_zh,name_en,enabled,sort_order) "
               "SELECT source_group_key,MIN(category),source_group_key,source_group_key,1,0 "
               "FROM equipment_metric_configs GROUP BY source_group_key")

    def columns(receipt_fk):
        return [sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True),
            sa.Column("equipment_id", key(), nullable=False), sa.Column("task_no", sa.String(50, collation="utf8mb4_bin"), nullable=False),
            sa.Column("observed_at", mysql.DATETIME(fsp=6), nullable=False), sa.Column("quality", sa.String(16), nullable=False),
            sa.Column("source_sample_key", mysql.BINARY(32), nullable=False),
            sa.Column("ingest_receipt_id", mysql.BIGINT(unsigned=True), sa.ForeignKey("metric_ingest_receipts.id", name=receipt_fk, ondelete="RESTRICT"), nullable=False),
            sa.Column("local_values", sa.JSON, nullable=False), sa.Column("remark", sa.Text),
            sa.Column("created_at", mysql.DATETIME(fsp=6), nullable=False, server_default=stamp),
            sa.Column("updated_at", mysql.DATETIME(fsp=6), nullable=False, server_default=stamp)]
    op.create_table("equipment_status_main", *columns("fk_obs_r10_latest_receipt"),
                    sa.UniqueConstraint("equipment_id", "task_no", name="uq_obs_latest_task"))
    op.create_index("ix_obs_latest_task_v2", "equipment_status_main", ["task_no", "id"])
    op.create_table("process_monitor_main", *columns("fk_obs_r10_history_receipt"),
                    sa.Column("review_mark", sa.String(16)),
                    sa.CheckConstraint("review_mark IS NULL OR review_mark IN ('abnormal','reviewed')", name="ck_obs_review_mark_v2"))
    op.create_index("ix_obs_history_task_time_v2", "process_monitor_main", ["task_no", "observed_at", "id"])
    op.create_index("ix_obs_history_equipment_time_v2", "process_monitor_main", ["equipment_id", "observed_at", "id"])
    op.execute("INSERT INTO process_monitor_main (id,equipment_id,task_no,observed_at,quality,source_sample_key,"
               "ingest_receipt_id,local_values,remark,created_at,updated_at,review_mark) "
               "SELECT id,equipment_id,task_no,sampled_at,quality,source_sample_key,ingest_receipt_id,"
               "JSON_OBJECT(group_key,local_values),remark,created_at,updated_at,review_mark FROM process_monitor_r8_archive")

    op.create_table("energy_metric_configs", sa.Column("meter_id", key(), primary_key=True),
        sa.Column("group_key", key(), primary_key=True), sa.Column("metric_key", key(), primary_key=True),
        sa.Column("slot_no", mysql.TINYINT(unsigned=True), nullable=False), sa.Column("name_zh", sa.String(128), nullable=False),
        sa.Column("name_en", sa.String(128), nullable=False), sa.Column("value_type", sa.String(16), nullable=False),
        sa.Column("quantity_key", key(), nullable=False), sa.Column("measurement_mode", sa.String(16), nullable=False),
        sa.Column("unit", sa.String(24)), sa.Column("decimals", mysql.TINYINT(unsigned=True)),
        sa.Column("enabled", sa.Boolean, nullable=False), sa.Column("list_visible", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("list_order", sa.Integer), sa.Column("rules", sa.JSON, nullable=False),
        sa.Column("first_used_at", mysql.DATETIME(fsp=6)),
        sa.UniqueConstraint("meter_id", "group_key", "slot_no", name="uq_energy_metric_slot"),
        sa.CheckConstraint("slot_no BETWEEN 1 AND 100 AND value_type = 'number'", name="ck_energy_metric_slot_type"),
        sa.CheckConstraint("measurement_mode IN ('cumulative','interval','instantaneous')", name="ck_energy_metric_mode"))
    op.create_table("energy_consumption_main", sa.Column("id", mysql.BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column("meter_id", key(), nullable=False), sa.Column("group_key", key(), nullable=False),
        sa.Column("observed_at", mysql.DATETIME(fsp=6), nullable=False), sa.Column("quality", sa.String(16), nullable=False),
        sa.Column("interval_start_at", mysql.DATETIME(fsp=6)), sa.Column("interval_end_at", mysql.DATETIME(fsp=6)),
        sa.Column("ingest_receipt_id", mysql.BIGINT(unsigned=True), sa.ForeignKey("metric_ingest_receipts.id", name="fk_obs_r10_energy_receipt", ondelete="RESTRICT"), nullable=False),
        sa.Column("local_values", sa.JSON, nullable=False), sa.Column("remark", sa.Text), sa.Column("review_mark", sa.String(16)),
        sa.Column("created_at", mysql.DATETIME(fsp=6), nullable=False, server_default=stamp),
        sa.Column("updated_at", mysql.DATETIME(fsp=6), nullable=False, server_default=stamp),
        sa.CheckConstraint("review_mark IS NULL OR review_mark IN ('abnormal','reviewed')", name="ck_energy_review_mark"))
    op.create_index("ix_energy_sample_meter_time", "energy_consumption_main", ["meter_id", "group_key", "observed_at", "id"])


def downgrade():
    if context.is_offline_mode():
        op.execute("SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'r10 recovery SQL is review-only; use guarded online downgrade'")
    else:
        args = context.get_x_argument(as_dictionary=True)
        if args.get("obs_r10_writers_quiesced") != "yes" or args.get("obs_r10_restore_preserved") != "yes":
            raise RuntimeError("recovery requires verified quiescent writers and explicit preservation confirmation")
        inspector = sa.inspect(op.get_bind())
        originals = ("equipment_status_r8_archive", "process_monitor_r8_archive", "equipment_metric_configs_r8_archive",
                     "equipment_metric_slot_bindings_r8_archive", "equipment_card_configs_r8_archive", "monitor_curve_group_configs_r8_archive",
                     "equipment_status_main", "process_monitor_main", "equipment_metric_configs", "equipment_metric_slot_bindings",
                     "equipment_card_configs", "monitor_curve_group_configs")
        preserved = ("equipment_status_r10_preserved", "process_monitor_r10_preserved", "equipment_metric_configs_r10_preserved",
                     "equipment_metric_slot_bindings_r10_preserved", "equipment_card_configs_r10_preserved", "monitor_curve_group_configs_r10_preserved")
        if any(not inspector.has_table(name) for name in originals) or any(inspector.has_table(name) for name in preserved):
            raise RuntimeError("incomplete archive or recovery destination collision; stop for manual reconciliation")
    op.execute("RENAME TABLE "
               "equipment_status_main TO equipment_status_r10_preserved, "
               "process_monitor_main TO process_monitor_r10_preserved, "
               "equipment_metric_slot_bindings TO equipment_metric_slot_bindings_r10_preserved, "
               "equipment_metric_configs TO equipment_metric_configs_r10_preserved, "
               "equipment_card_configs TO equipment_card_configs_r10_preserved, "
               "monitor_curve_group_configs TO monitor_curve_group_configs_r10_preserved, "
               "equipment_status_r8_archive TO equipment_status_main, "
               "process_monitor_r8_archive TO process_monitor_main, "
               "equipment_metric_configs_r8_archive TO equipment_metric_configs, "
               "equipment_metric_slot_bindings_r8_archive TO equipment_metric_slot_bindings, "
               "equipment_card_configs_r8_archive TO equipment_card_configs, "
               "monitor_curve_group_configs_r8_archive TO monitor_curve_group_configs")
