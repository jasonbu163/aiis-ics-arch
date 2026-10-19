"""BE006唯一e4后继：七业务表HTTP域、三回执及生产观察水位。

只增nullable HTTP键，不回填/清理旧行；DDL非事务。downgrade仅供另批可丢弃副本，
任何HTTP数据、NULL旧NOT NULL指标或非零毫秒均拒绝，绝不删除观测或补零/截断。
"""
from alembic import op, context
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import DATETIME, VARBINARY
revision = "f6a8c0e2b4d6"
down_revision = "e4f6a8b0c2d4"
branch_labels = None
depends_on = None

def identifier_type():
    return sa.String(128).with_variant(sa.String(128, collation="utf8mb4_bin"), "mysql")
def millisecond_type():
    return sa.DateTime().with_variant(DATETIME(fsp=3), "mysql")

def binary_key_type():
    return sa.LargeBinary(200).with_variant(VARBINARY(200), "mysql")

def upgrade():
    op.add_column('equipment_drive', sa.Column('equipment_id', identifier_type(), nullable=True))
    op.add_column('equipment_production_parameters', sa.Column('equipment_id', identifier_type(), nullable=True))
    op.add_column('equipment_production_parameters', sa.Column('http_coil_key', binary_key_type(), nullable=True))
    op.add_column('performance_main', sa.Column('equipment_id', identifier_type(), nullable=True))
    op.add_column('performance_main', sa.Column('http_coil_key', binary_key_type(), nullable=True))
    op.add_column('performance_main', sa.Column('reported_start_time', millisecond_type(), nullable=True))
    op.add_column('performance_main', sa.Column('reported_end_time', millisecond_type(), nullable=True))
    op.add_column('monitor_history_process_curves', sa.Column('equipment_id', identifier_type(), nullable=True))
    op.add_column('monitor_history_process_curves', sa.Column('sampled_at', millisecond_type(), nullable=True))
    op.add_column('monitor_history_process_curves', sa.Column('fingerprint', sa.String(64), nullable=True))
    op.add_column('performance_process_temperature', sa.Column('equipment_id', identifier_type(), nullable=True))
    op.add_column('performance_process_temperature', sa.Column('http_zone_key', binary_key_type(), nullable=True))
    op.add_column('performance_process_tension', sa.Column('equipment_id', identifier_type(), nullable=True))
    op.add_column('performance_process_tension', sa.Column('http_zone_key', binary_key_type(), nullable=True))
    op.add_column('performance_process_speed', sa.Column('equipment_id', identifier_type(), nullable=True))
    op.add_column('performance_process_speed', sa.Column('http_zone_key', binary_key_type(), nullable=True))
    op.alter_column('equipment_drive', 'timestamp', existing_type=sa.DateTime(), type_=millisecond_type(), existing_nullable=False, existing_server_default=sa.func.now(), server_default=sa.func.current_timestamp(3))
    op.alter_column('equipment_production_parameters', 'timestamp', existing_type=sa.DateTime(), type_=millisecond_type(), existing_nullable=False, existing_server_default=sa.func.now(), server_default=sa.func.current_timestamp(3))
    op.alter_column('equipment_production_parameters', 'entry_time', existing_type=sa.DateTime(), type_=millisecond_type(), existing_nullable=True)
    op.alter_column('performance_main', 'first_observed_at', existing_type=sa.DateTime(), type_=millisecond_type(), existing_nullable=True)
    op.alter_column('performance_main', 'last_observed_at', existing_type=sa.DateTime(), type_=millisecond_type(), existing_nullable=True)
    op.alter_column('performance_process_temperature', 'record_time', existing_type=sa.DateTime(), type_=millisecond_type(), existing_nullable=False)
    op.alter_column('performance_process_tension', 'record_time', existing_type=sa.DateTime(), type_=millisecond_type(), existing_nullable=False)
    op.alter_column('performance_process_speed', 'record_time', existing_type=sa.DateTime(), type_=millisecond_type(), existing_nullable=False)
    op.alter_column('equipment_drive', 'tv', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'km', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'dew_point_set', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'dew_point_actual', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'oxygen', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'muffle_pressure', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'nh3_flow_set', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'nh3_flow_actual', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'ng_flow_set', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'ng_flow_actual', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'uncoiler_set', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'uncoiler_actual', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'entry_looper_set', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'entry_looper_actual', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'furnace_set', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'furnace_actual', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'exit_looper_set', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'exit_looper_actual', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'recoiler_set', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_drive', 'recoiler_actual', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_production_parameters', 'grade', existing_type=sa.String(50), nullable=True)
    op.alter_column('equipment_production_parameters', 'thickness', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_production_parameters', 'width', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_production_parameters', 'total_time', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_production_parameters', 'weight', existing_type=sa.Float(), nullable=True)
    op.alter_column('equipment_production_parameters', 'speed', existing_type=sa.Float(), nullable=True)
    op.alter_column('performance_main', 'output_quantity', existing_type=sa.Numeric(10,4), nullable=True)
    op.alter_column('performance_main', 'qualified_quantity', existing_type=sa.Numeric(10,4), nullable=True)
    op.alter_column('monitor_history_process_curves', 'device_id', existing_type=sa.Integer(), nullable=True)
    op.create_unique_constraint('uq_equipment_drive_http_business', 'equipment_drive', ['equipment_id', 'timestamp'])
    op.create_unique_constraint('uq_equipment_drive_http_target', 'equipment_drive', ['id', 'equipment_id'])
    op.create_unique_constraint('uq_equipment_production_parameters_http_business', 'equipment_production_parameters', ['equipment_id', 'http_coil_key', 'timestamp'])
    op.create_unique_constraint('uq_equipment_production_parameters_http_target', 'equipment_production_parameters', ['id', 'equipment_id'])
    op.create_unique_constraint('uq_performance_main_http_business', 'performance_main', ['equipment_id', 'http_coil_key'])
    op.create_unique_constraint('uq_performance_main_http_target', 'performance_main', ['id', 'equipment_id'])
    op.create_unique_constraint('uq_monitor_curve_http_business', 'monitor_history_process_curves', ['equipment_id', 'sampled_at'])
    op.create_unique_constraint('uq_monitor_curve_http_target', 'monitor_history_process_curves', ['id', 'equipment_id'])
    op.create_unique_constraint('uq_process_temperature_http_business', 'performance_process_temperature', ['equipment_id', 'performance_id', 'http_zone_key', 'record_time'])
    op.create_unique_constraint('uq_process_temperature_http_target', 'performance_process_temperature', ['id', 'equipment_id', 'performance_id'])
    op.create_unique_constraint('uq_process_tension_http_business', 'performance_process_tension', ['equipment_id', 'performance_id', 'http_zone_key', 'record_time'])
    op.create_unique_constraint('uq_process_tension_http_target', 'performance_process_tension', ['id', 'equipment_id', 'performance_id'])
    op.create_unique_constraint('uq_process_speed_http_business', 'performance_process_speed', ['equipment_id', 'performance_id', 'http_zone_key', 'record_time'])
    op.create_unique_constraint('uq_process_speed_http_target', 'performance_process_speed', ['id', 'equipment_id', 'performance_id'])
    op.create_table('equipment_mapping_receipts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('actor_user_id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', identifier_type(), nullable=False),
        sa.Column('stream', identifier_type(), nullable=False),
        sa.Column('sample_id', identifier_type(), nullable=False),
        sa.Column('fingerprint', sa.String(64), nullable=False),
        sa.Column('sampled_at', millisecond_type(), nullable=False),
        sa.Column('outcome', sa.String(16), nullable=False),
        sa.Column('result', sa.JSON(), nullable=False),
        sa.Column('created_at', millisecond_type(), nullable=False, server_default=sa.text('(UTC_TIMESTAMP(3))')),
        sa.Column('updated_at', millisecond_type(), nullable=False, server_default=sa.text('(UTC_TIMESTAMP(3))')),
        sa.Column('drive_record_id', sa.Integer(), nullable=True),
        sa.Column('parameter_record_id', sa.Integer(), nullable=True),
        sa.CheckConstraint("(stream = 'drive' AND drive_record_id IS NOT NULL AND parameter_record_id IS NULL) OR (stream = 'production_parameters' AND drive_record_id IS NULL AND parameter_record_id IS NOT NULL)", name='ck_equipment_mapping_stream_target'),
        sa.ForeignKeyConstraint(['drive_record_id', 'equipment_id'], ['equipment_drive.id', 'equipment_drive.equipment_id'], name='fk_equipment_receipt_drive_record_id'),
        sa.ForeignKeyConstraint(['parameter_record_id', 'equipment_id'], ['equipment_production_parameters.id', 'equipment_production_parameters.equipment_id'], name='fk_equipment_receipt_parameter_record_id'),
        sa.UniqueConstraint('actor_user_id', 'equipment_id', 'stream', 'sample_id', name='uq_equipment_mapping_delivery'),
    )
    op.create_table('performance_mapping_receipts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('actor_user_id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', identifier_type(), nullable=False),
        sa.Column('stream', identifier_type(), nullable=False),
        sa.Column('sample_id', identifier_type(), nullable=False),
        sa.Column('fingerprint', sa.String(64), nullable=False),
        sa.Column('sampled_at', millisecond_type(), nullable=False),
        sa.Column('outcome', sa.String(16), nullable=False),
        sa.Column('result', sa.JSON(), nullable=False),
        sa.Column('performance_id', sa.Integer(), nullable=True),
        sa.Column('temperature_record_id', sa.Integer(), nullable=True),
        sa.Column('tension_record_id', sa.Integer(), nullable=True),
        sa.Column('speed_record_id', sa.Integer(), nullable=True),
        sa.Column('created_at', millisecond_type(), nullable=False, server_default=sa.text('(UTC_TIMESTAMP(3))')),
        sa.Column('updated_at', millisecond_type(), nullable=False, server_default=sa.text('(UTC_TIMESTAMP(3))')),
        sa.CheckConstraint("(stream = 'production_observation' AND temperature_record_id IS NULL AND tension_record_id IS NULL AND speed_record_id IS NULL) OR (stream = 'process_temperature' AND performance_id IS NOT NULL AND temperature_record_id IS NOT NULL AND tension_record_id IS NULL AND speed_record_id IS NULL) OR (stream = 'process_tension' AND performance_id IS NOT NULL AND temperature_record_id IS NULL AND tension_record_id IS NOT NULL AND speed_record_id IS NULL) OR (stream = 'process_speed' AND performance_id IS NOT NULL AND temperature_record_id IS NULL AND tension_record_id IS NULL AND speed_record_id IS NOT NULL)", name='ck_performance_mapping_stream_target'),
        sa.ForeignKeyConstraint(['performance_id', 'equipment_id'], ['performance_main.id', 'performance_main.equipment_id'], name='fk_performance_receipt_parent'),
        sa.ForeignKeyConstraint(['speed_record_id', 'equipment_id', 'performance_id'], ['performance_process_speed.id', 'performance_process_speed.equipment_id', 'performance_process_speed.performance_id'], name='fk_performance_receipt_speed'),
        sa.ForeignKeyConstraint(['temperature_record_id', 'equipment_id', 'performance_id'], ['performance_process_temperature.id', 'performance_process_temperature.equipment_id', 'performance_process_temperature.performance_id'], name='fk_performance_receipt_temperature'),
        sa.ForeignKeyConstraint(['tension_record_id', 'equipment_id', 'performance_id'], ['performance_process_tension.id', 'performance_process_tension.equipment_id', 'performance_process_tension.performance_id'], name='fk_performance_receipt_tension'),
        sa.UniqueConstraint('actor_user_id', 'equipment_id', 'stream', 'sample_id', name='uq_performance_mapping_delivery'),
    )
    op.create_table('monitor_mapping_receipts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('actor_user_id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', identifier_type(), nullable=False),
        sa.Column('stream', identifier_type(), nullable=False),
        sa.Column('sample_id', identifier_type(), nullable=False),
        sa.Column('fingerprint', sa.String(64), nullable=False),
        sa.Column('sampled_at', millisecond_type(), nullable=False),
        sa.Column('outcome', sa.String(16), nullable=False),
        sa.Column('result', sa.JSON(), nullable=False),
        sa.Column('created_at', millisecond_type(), nullable=False, server_default=sa.text('(UTC_TIMESTAMP(3))')),
        sa.Column('updated_at', millisecond_type(), nullable=False, server_default=sa.text('(UTC_TIMESTAMP(3))')),
        sa.Column('curve_record_id', sa.Integer(), nullable=True),
        sa.CheckConstraint("(stream = 'process_curve' AND curve_record_id IS NOT NULL)", name='ck_monitor_mapping_stream_target'),
        sa.ForeignKeyConstraint(['curve_record_id', 'equipment_id'], ['monitor_history_process_curves.id', 'monitor_history_process_curves.equipment_id'], name='fk_monitor_receipt_curve_record_id'),
        sa.UniqueConstraint('actor_user_id', 'equipment_id', 'stream', 'sample_id', name='uq_monitor_mapping_delivery'),
    )
    op.create_table('performance_mapping_observation_state',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('equipment_id', identifier_type(), nullable=False),
        sa.Column('last_sampled_at', millisecond_type(), nullable=True),
        sa.Column('fingerprint', sa.String(64), nullable=True),
        sa.Column('performance_id', sa.Integer(), nullable=True),
        sa.Column('observation_status', sa.String(32), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('created_at', millisecond_type(), nullable=False, server_default=sa.text('(UTC_TIMESTAMP(3))')),
        sa.Column('updated_at', millisecond_type(), nullable=False, server_default=sa.text('(UTC_TIMESTAMP(3))')),
        sa.ForeignKeyConstraint(['performance_id', 'equipment_id'], ['performance_main.id', 'performance_main.equipment_id'], name='fk_performance_observation_parent'),
        sa.UniqueConstraint('equipment_id', name='uq_performance_observation_equipment'),
    )

def _assert_reversible():
    if context.is_offline_mode():
        raise RuntimeError("BE006 downgrade requires separately approved disposable database inspection")
    connection = op.get_bind()
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE equipment_id IS NOT NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses HTTP business data")
    if connection.execute(sa.text("SELECT 1 FROM equipment_production_parameters WHERE equipment_id IS NOT NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses HTTP business data")
    if connection.execute(sa.text("SELECT 1 FROM performance_main WHERE equipment_id IS NOT NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses HTTP business data")
    if connection.execute(sa.text("SELECT 1 FROM monitor_history_process_curves WHERE equipment_id IS NOT NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses HTTP business data")
    if connection.execute(sa.text("SELECT 1 FROM performance_process_temperature WHERE equipment_id IS NOT NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses HTTP business data")
    if connection.execute(sa.text("SELECT 1 FROM performance_process_tension WHERE equipment_id IS NOT NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses HTTP business data")
    if connection.execute(sa.text("SELECT 1 FROM performance_process_speed WHERE equipment_id IS NOT NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses HTTP business data")
    if connection.execute(sa.text("SELECT 1 FROM equipment_mapping_receipts LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses receipt/observation state")
    if connection.execute(sa.text("SELECT 1 FROM performance_mapping_receipts LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses receipt/observation state")
    if connection.execute(sa.text("SELECT 1 FROM monitor_mapping_receipts LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses receipt/observation state")
    if connection.execute(sa.text("SELECT 1 FROM performance_mapping_observation_state LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses receipt/observation state")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE tv IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE km IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE dew_point_set IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE dew_point_actual IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE oxygen IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE muffle_pressure IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE nh3_flow_set IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE nh3_flow_actual IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE ng_flow_set IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE ng_flow_actual IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE uncoiler_set IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE uncoiler_actual IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE entry_looper_set IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE entry_looper_actual IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE furnace_set IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE furnace_actual IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE exit_looper_set IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE exit_looper_actual IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE recoiler_set IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE recoiler_actual IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_production_parameters WHERE grade IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_production_parameters WHERE thickness IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_production_parameters WHERE width IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_production_parameters WHERE total_time IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_production_parameters WHERE weight IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_production_parameters WHERE speed IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM performance_main WHERE output_quantity IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM performance_main WHERE qualified_quantity IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM monitor_history_process_curves WHERE device_id IS NULL LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses nullable legacy measurement")
    if connection.execute(sa.text("SELECT 1 FROM equipment_drive WHERE MICROSECOND(timestamp) <> 0 LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses millisecond truncation")
    if connection.execute(sa.text("SELECT 1 FROM equipment_production_parameters WHERE MICROSECOND(timestamp) <> 0 LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses millisecond truncation")
    if connection.execute(sa.text("SELECT 1 FROM equipment_production_parameters WHERE MICROSECOND(entry_time) <> 0 LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses millisecond truncation")
    if connection.execute(sa.text("SELECT 1 FROM performance_main WHERE MICROSECOND(first_observed_at) <> 0 LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses millisecond truncation")
    if connection.execute(sa.text("SELECT 1 FROM performance_main WHERE MICROSECOND(last_observed_at) <> 0 LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses millisecond truncation")
    if connection.execute(sa.text("SELECT 1 FROM performance_process_temperature WHERE MICROSECOND(record_time) <> 0 LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses millisecond truncation")
    if connection.execute(sa.text("SELECT 1 FROM performance_process_tension WHERE MICROSECOND(record_time) <> 0 LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses millisecond truncation")
    if connection.execute(sa.text("SELECT 1 FROM performance_process_speed WHERE MICROSECOND(record_time) <> 0 LIMIT 1")).first():
        raise RuntimeError("BE006 downgrade refuses millisecond truncation")

def downgrade():
    _assert_reversible()
    op.drop_table('equipment_mapping_receipts')
    op.drop_table('performance_mapping_receipts')
    op.drop_table('monitor_mapping_receipts')
    op.drop_table('performance_mapping_observation_state')
    op.drop_constraint('uq_process_speed_http_target', 'performance_process_speed', type_="unique")
    op.drop_constraint('uq_process_speed_http_business', 'performance_process_speed', type_="unique")
    op.drop_constraint('uq_process_tension_http_target', 'performance_process_tension', type_="unique")
    op.drop_constraint('uq_process_tension_http_business', 'performance_process_tension', type_="unique")
    op.drop_constraint('uq_process_temperature_http_target', 'performance_process_temperature', type_="unique")
    op.drop_constraint('uq_process_temperature_http_business', 'performance_process_temperature', type_="unique")
    op.drop_constraint('uq_monitor_curve_http_target', 'monitor_history_process_curves', type_="unique")
    op.drop_constraint('uq_monitor_curve_http_business', 'monitor_history_process_curves', type_="unique")
    op.drop_constraint('uq_performance_main_http_target', 'performance_main', type_="unique")
    op.drop_constraint('uq_performance_main_http_business', 'performance_main', type_="unique")
    op.drop_constraint('uq_equipment_production_parameters_http_target', 'equipment_production_parameters', type_="unique")
    op.drop_constraint('uq_equipment_production_parameters_http_business', 'equipment_production_parameters', type_="unique")
    op.drop_constraint('uq_equipment_drive_http_target', 'equipment_drive', type_="unique")
    op.drop_constraint('uq_equipment_drive_http_business', 'equipment_drive', type_="unique")
    op.alter_column('equipment_drive', 'tv', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'km', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'dew_point_set', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'dew_point_actual', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'oxygen', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'muffle_pressure', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'nh3_flow_set', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'nh3_flow_actual', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'ng_flow_set', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'ng_flow_actual', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'uncoiler_set', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'uncoiler_actual', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'entry_looper_set', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'entry_looper_actual', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'furnace_set', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'furnace_actual', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'exit_looper_set', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'exit_looper_actual', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'recoiler_set', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_drive', 'recoiler_actual', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_production_parameters', 'grade', existing_type=sa.String(50), nullable=False)
    op.alter_column('equipment_production_parameters', 'thickness', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_production_parameters', 'width', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_production_parameters', 'total_time', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_production_parameters', 'weight', existing_type=sa.Float(), nullable=False)
    op.alter_column('equipment_production_parameters', 'speed', existing_type=sa.Float(), nullable=False)
    op.alter_column('performance_main', 'output_quantity', existing_type=sa.Numeric(10,4), nullable=False)
    op.alter_column('performance_main', 'qualified_quantity', existing_type=sa.Numeric(10,4), nullable=False)
    op.alter_column('monitor_history_process_curves', 'device_id', existing_type=sa.Integer(), nullable=False)
    op.alter_column('equipment_drive', 'timestamp', existing_type=millisecond_type(), type_=sa.DateTime(timezone=True), existing_nullable=False, existing_server_default=sa.func.current_timestamp(3), server_default=sa.func.now())
    op.alter_column('equipment_production_parameters', 'timestamp', existing_type=millisecond_type(), type_=sa.DateTime(timezone=True), existing_nullable=False, existing_server_default=sa.func.current_timestamp(3), server_default=sa.func.now())
    op.alter_column('equipment_production_parameters', 'entry_time', existing_type=millisecond_type(), type_=sa.DateTime(), existing_nullable=True)
    op.alter_column('performance_main', 'first_observed_at', existing_type=millisecond_type(), type_=sa.DateTime(), existing_nullable=True)
    op.alter_column('performance_main', 'last_observed_at', existing_type=millisecond_type(), type_=sa.DateTime(), existing_nullable=True)
    op.alter_column('performance_process_temperature', 'record_time', existing_type=millisecond_type(), type_=sa.DateTime(), existing_nullable=False)
    op.alter_column('performance_process_tension', 'record_time', existing_type=millisecond_type(), type_=sa.DateTime(), existing_nullable=False)
    op.alter_column('performance_process_speed', 'record_time', existing_type=millisecond_type(), type_=sa.DateTime(), existing_nullable=False)
    op.drop_column('performance_process_speed', 'http_zone_key')
    op.drop_column('performance_process_speed', 'equipment_id')
    op.drop_column('performance_process_tension', 'http_zone_key')
    op.drop_column('performance_process_tension', 'equipment_id')
    op.drop_column('performance_process_temperature', 'http_zone_key')
    op.drop_column('performance_process_temperature', 'equipment_id')
    op.drop_column('monitor_history_process_curves', 'fingerprint')
    op.drop_column('monitor_history_process_curves', 'sampled_at')
    op.drop_column('monitor_history_process_curves', 'equipment_id')
    op.drop_column('performance_main', 'reported_end_time')
    op.drop_column('performance_main', 'reported_start_time')
    op.drop_column('performance_main', 'http_coil_key')
    op.drop_column('performance_main', 'equipment_id')
    op.drop_column('equipment_production_parameters', 'http_coil_key')
    op.drop_column('equipment_production_parameters', 'equipment_id')
    op.drop_column('equipment_drive', 'equipment_id')
