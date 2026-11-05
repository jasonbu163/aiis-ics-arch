"""新增四张永久业务回执/生产事件表；不转换历史时间，不自动采用。"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "1b3d5f7a9c20"
down_revision = "0a2c4e6f8b10"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('equipment_integration_receipts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('producer_id', sa.LargeBinary(512).with_variant(mysql.VARBINARY(512), "mysql"), nullable=False),
        sa.Column('event_id', sa.LargeBinary(512).with_variant(mysql.VARBINARY(512), "mysql"), nullable=False),
        sa.Column('contract_version', sa.String(64), nullable=False),
        sa.Column('digest_profile', sa.String(32), nullable=False),
        sa.Column('equipment_id', sa.String(128).with_variant(sa.String(128, collation='utf8mb4_bin'), "mysql"), nullable=False),
        sa.Column('stream', sa.String(32), nullable=False),
        sa.Column('mapping_id', sa.String(128), nullable=False),
        sa.Column('mapping_revision', sa.String(128), nullable=False),
        sa.Column('source_refs', sa.JSON(), nullable=False),
        sa.Column('request_digest', sa.String(71), nullable=False),
        sa.Column('business_digest', sa.String(71), nullable=False),
        sa.Column('source_time', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('committed_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('outcome', sa.String(16), nullable=False),
        sa.Column('result', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('updated_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('temperature_record_id', sa.Integer(), nullable=True),
        sa.Column('drive_record_id', sa.Integer(), nullable=True),
        sa.Column('parameter_record_id', sa.Integer(), nullable=True),
        sa.CheckConstraint("outcome IN ('created', 'updated', 'duplicate')", name='ck_equipment_integration_outcome'),
        sa.CheckConstraint("(stream = 'temperature' AND temperature_record_id IS NOT NULL AND drive_record_id IS NULL AND parameter_record_id IS NULL) OR (stream = 'drive' AND temperature_record_id IS NULL AND drive_record_id IS NOT NULL AND parameter_record_id IS NULL) OR (stream = 'production_parameters' AND temperature_record_id IS NULL AND drive_record_id IS NULL AND parameter_record_id IS NOT NULL)", name='ck_equipment_integration_target'),
        sa.ForeignKeyConstraint(['drive_record_id', 'equipment_id'], ['equipment_drive.id', 'equipment_drive.equipment_id'], name='fk_equipment_integration_drive'),
        sa.ForeignKeyConstraint(['parameter_record_id', 'equipment_id'], ['equipment_production_parameters.id', 'equipment_production_parameters.equipment_id'], name='fk_equipment_integration_parameter'),
        sa.ForeignKeyConstraint(['temperature_record_id', 'equipment_id'], ['equipment_temperature_samples.id', 'equipment_temperature_samples.equipment_id'], name='fk_equipment_integration_temperature'),
        sa.UniqueConstraint('producer_id', 'event_id', name='uq_equipment_integration_delivery'),
    )
    op.create_table('performance_integration_receipts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('producer_id', sa.LargeBinary(512).with_variant(mysql.VARBINARY(512), "mysql"), nullable=False),
        sa.Column('event_id', sa.LargeBinary(512).with_variant(mysql.VARBINARY(512), "mysql"), nullable=False),
        sa.Column('contract_version', sa.String(64), nullable=False),
        sa.Column('digest_profile', sa.String(32), nullable=False),
        sa.Column('equipment_id', sa.String(128).with_variant(sa.String(128, collation='utf8mb4_bin'), "mysql"), nullable=False),
        sa.Column('stream', sa.String(32), nullable=False),
        sa.Column('mapping_id', sa.String(128), nullable=False),
        sa.Column('mapping_revision', sa.String(128), nullable=False),
        sa.Column('source_refs', sa.JSON(), nullable=False),
        sa.Column('request_digest', sa.String(71), nullable=False),
        sa.Column('business_digest', sa.String(71), nullable=False),
        sa.Column('source_time', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('committed_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('outcome', sa.String(16), nullable=False),
        sa.Column('result', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('updated_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('temperature_record_id', sa.Integer(), nullable=True),
        sa.Column('tension_record_id', sa.Integer(), nullable=True),
        sa.Column('speed_record_id', sa.Integer(), nullable=True),
        sa.Column('performance_id', sa.Integer(), nullable=True),
        sa.CheckConstraint("outcome IN ('created', 'updated', 'duplicate', 'stale')", name='ck_performance_integration_outcome'),
        sa.CheckConstraint("(stream = 'production_observation' AND temperature_record_id IS NULL AND tension_record_id IS NULL AND speed_record_id IS NULL) OR (stream = 'process_temperature' AND performance_id IS NOT NULL AND temperature_record_id IS NOT NULL AND tension_record_id IS NULL AND speed_record_id IS NULL) OR (stream = 'process_tension' AND performance_id IS NOT NULL AND temperature_record_id IS NULL AND tension_record_id IS NOT NULL AND speed_record_id IS NULL) OR (stream = 'process_speed' AND performance_id IS NOT NULL AND temperature_record_id IS NULL AND tension_record_id IS NULL AND speed_record_id IS NOT NULL)", name='ck_performance_integration_target'),
        sa.ForeignKeyConstraint(['performance_id', 'equipment_id'], ['performance_main.id', 'performance_main.equipment_id'], name='fk_performance_integration_parent'),
        sa.ForeignKeyConstraint(['speed_record_id', 'equipment_id', 'performance_id'], ['performance_process_speed.id', 'performance_process_speed.equipment_id', 'performance_process_speed.performance_id'], name='fk_performance_integration_speed'),
        sa.ForeignKeyConstraint(['temperature_record_id', 'equipment_id', 'performance_id'], ['performance_process_temperature.id', 'performance_process_temperature.equipment_id', 'performance_process_temperature.performance_id'], name='fk_performance_integration_temperature'),
        sa.ForeignKeyConstraint(['tension_record_id', 'equipment_id', 'performance_id'], ['performance_process_tension.id', 'performance_process_tension.equipment_id', 'performance_process_tension.performance_id'], name='fk_performance_integration_tension'),
        sa.UniqueConstraint('producer_id', 'event_id', name='uq_performance_integration_delivery'),
    )
    op.create_table('performance_integration_observation_events',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('equipment_id', sa.String(128).with_variant(sa.String(128, collation='utf8mb4_bin'), "mysql"), nullable=False),
        sa.Column('sampled_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('business_digest', sa.String(71), nullable=False),
        sa.Column('observation_status', sa.String(32), nullable=False),
        sa.Column('performance_id', sa.Integer(), nullable=True),
        sa.Column('mapping_id', sa.String(128), nullable=False),
        sa.Column('mapping_revision', sa.String(128), nullable=False),
        sa.Column('source_refs', sa.JSON(), nullable=False),
        sa.Column('result', sa.JSON(), nullable=False),
        sa.Column('committed_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('updated_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.CheckConstraint("observation_status IN ('in_production', 'not_in_production', 'unknown')", name='ck_performance_integration_event_status'),
        sa.ForeignKeyConstraint(['performance_id', 'equipment_id'], ['performance_main.id', 'performance_main.equipment_id'], name='fk_performance_integration_event_parent'),
        sa.UniqueConstraint('equipment_id', 'sampled_at', name='uq_performance_integration_observation_time'),
    )
    op.create_table('monitor_integration_receipts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('producer_id', sa.LargeBinary(512).with_variant(mysql.VARBINARY(512), "mysql"), nullable=False),
        sa.Column('event_id', sa.LargeBinary(512).with_variant(mysql.VARBINARY(512), "mysql"), nullable=False),
        sa.Column('contract_version', sa.String(64), nullable=False),
        sa.Column('digest_profile', sa.String(32), nullable=False),
        sa.Column('equipment_id', sa.String(128).with_variant(sa.String(128, collation='utf8mb4_bin'), "mysql"), nullable=False),
        sa.Column('stream', sa.String(32), nullable=False),
        sa.Column('mapping_id', sa.String(128), nullable=False),
        sa.Column('mapping_revision', sa.String(128), nullable=False),
        sa.Column('source_refs', sa.JSON(), nullable=False),
        sa.Column('request_digest', sa.String(71), nullable=False),
        sa.Column('business_digest', sa.String(71), nullable=False),
        sa.Column('source_time', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('committed_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('outcome', sa.String(16), nullable=False),
        sa.Column('result', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('updated_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=3), "mysql"), nullable=False),
        sa.Column('curve_record_id', sa.Integer(), nullable=True),
        sa.CheckConstraint("outcome IN ('created', 'duplicate')", name='ck_monitor_integration_outcome'),
        sa.CheckConstraint("(stream = 'process_curve' AND curve_record_id IS NOT NULL)", name='ck_monitor_integration_target'),
        sa.ForeignKeyConstraint(['curve_record_id', 'equipment_id'], ['monitor_history_process_curves.id', 'monitor_history_process_curves.equipment_id'], name='fk_monitor_integration_curve'),
        sa.UniqueConstraint('producer_id', 'event_id', name='uq_monitor_integration_delivery'),
    )


def downgrade():
    connection = op.get_bind()
    # 有数据时拒绝破坏性回退；默认停入口、保留回执与业务。
    for table in ("equipment_integration_receipts", "performance_integration_receipts",
                  "performance_integration_observation_events", "monitor_integration_receipts"):
        if connection.execute(sa.text("SELECT 1 FROM " + table + " LIMIT 1")).first() is not None:
            raise RuntimeError("nonempty business integration tables prohibit downgrade")
    op.drop_table("monitor_integration_receipts")
    op.drop_table("performance_integration_observation_events")
    op.drop_table("performance_integration_receipts")
    op.drop_table("equipment_integration_receipts")
