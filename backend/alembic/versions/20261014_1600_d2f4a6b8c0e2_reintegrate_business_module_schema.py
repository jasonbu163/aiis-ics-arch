"""回迁业务显式42表增量；不seed，downgrade仅撤本增量且会丢新增业务数据。"""
from alembic import op
import sqlalchemy as sa

revision = "d2f4a6b8c0e2"
down_revision = "b8d0f2a4c6e8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('daily_production_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stats_date', sa.Date(), nullable=False, comment='统计日期'),
        sa.Column('production_weight', sa.Numeric(precision=12, scale=4), nullable=False, comment='生产重量(吨)'),
        sa.Column('completed_coils', sa.Integer(), nullable=False, comment='完成卷数'),
        sa.Column('target_weight', sa.Numeric(precision=12, scale=4), nullable=False, comment='目标重量(吨)'),
        sa.Column('oee_rate', sa.Numeric(precision=5, scale=2), nullable=False, comment='OEE比率(%)'),
        sa.Column('availability_rate', sa.Numeric(precision=5, scale=2), nullable=False, comment='可用率(%)'),
        sa.Column('performance_rate', sa.Numeric(precision=5, scale=2), nullable=False, comment='性能效率(%)'),
        sa.Column('quality_rate', sa.Numeric(precision=5, scale=2), nullable=False, comment='质量指数(%)'),
        sa.Column('energy_electricity', sa.Numeric(precision=12, scale=2), nullable=False, comment='电力消耗(kWh)'),
        sa.Column('energy_gas', sa.Numeric(precision=12, scale=2), nullable=False, comment='天然气消耗(m³)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_daily_production_stats_id', 'daily_production_stats', ['id'], unique=False)
    op.create_index('ix_daily_production_stats_stats_date', 'daily_production_stats', ['stats_date'], unique=True)
    op.create_table('departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['parent_id'], ['departments.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name=None),
    )
    op.create_index('ix_departments_id', 'departments', ['id'], unique=False)
    op.create_table('downtime_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stats_date', sa.Date(), nullable=False, comment='统计日期'),
        sa.Column('reason', sa.String(length=100), nullable=False, comment='停机原因'),
        sa.Column('duration_minutes', sa.Integer(), nullable=False, comment='停机时长(分钟)'),
        sa.Column('color', sa.String(length=20), nullable=False, comment='显示颜色'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_downtime_records_id', 'downtime_records', ['id'], unique=False)
    op.create_index('ix_downtime_records_stats_date', 'downtime_records', ['stats_date'], unique=False)
    op.create_table('equipment_drive',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('tv', sa.Float(), nullable=False),
        sa.Column('km', sa.Float(), nullable=False),
        sa.Column('dew_point_set', sa.Float(), nullable=False),
        sa.Column('dew_point_actual', sa.Float(), nullable=False),
        sa.Column('oxygen', sa.Float(), nullable=False),
        sa.Column('muffle_pressure', sa.Float(), nullable=False),
        sa.Column('nh3_flow_set', sa.Float(), nullable=False),
        sa.Column('nh3_flow_actual', sa.Float(), nullable=False),
        sa.Column('ng_flow_set', sa.Float(), nullable=False),
        sa.Column('ng_flow_actual', sa.Float(), nullable=False),
        sa.Column('uncoiler_set', sa.Float(), nullable=False),
        sa.Column('uncoiler_actual', sa.Float(), nullable=False),
        sa.Column('entry_looper_set', sa.Float(), nullable=False),
        sa.Column('entry_looper_actual', sa.Float(), nullable=False),
        sa.Column('furnace_set', sa.Float(), nullable=False),
        sa.Column('furnace_actual', sa.Float(), nullable=False),
        sa.Column('exit_looper_set', sa.Float(), nullable=False),
        sa.Column('exit_looper_actual', sa.Float(), nullable=False),
        sa.Column('recoiler_set', sa.Float(), nullable=False),
        sa.Column('recoiler_actual', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_equipment_drive_id', 'equipment_drive', ['id'], unique=False)
    op.create_index('ix_equipment_drive_timestamp', 'equipment_drive', ['timestamp'], unique=False)
    op.create_table('equipment_production_parameters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('coil_no', sa.String(length=50), nullable=False),
        sa.Column('grade', sa.String(length=50), nullable=False),
        sa.Column('thickness', sa.Float(), nullable=False),
        sa.Column('width', sa.Float(), nullable=False),
        sa.Column('entry_time', sa.DateTime(), nullable=True),
        sa.Column('total_time', sa.Float(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('speed', sa.Float(), nullable=False),
        sa.Column('process_steps', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_equipment_production_parameters_id', 'equipment_production_parameters', ['id'], unique=False)
    op.create_index('ix_equipment_production_parameters_timestamp', 'equipment_production_parameters', ['timestamp'], unique=False)
    op.create_table('equipment_temperature',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('zone1_set', sa.Float(), nullable=False),
        sa.Column('zone1_act', sa.Float(), nullable=False),
        sa.Column('zone2_set', sa.Float(), nullable=False),
        sa.Column('zone2_act', sa.Float(), nullable=False),
        sa.Column('zone3_set', sa.Float(), nullable=False),
        sa.Column('zone3_act', sa.Float(), nullable=False),
        sa.Column('zone4_set', sa.Float(), nullable=False),
        sa.Column('zone4_act', sa.Float(), nullable=False),
        sa.Column('zone5_set', sa.Float(), nullable=False),
        sa.Column('zone5_act', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_equipment_temperature_id', 'equipment_temperature', ['id'], unique=False)
    op.create_index('ix_equipment_temperature_timestamp', 'equipment_temperature', ['timestamp'], unique=False)
    op.create_table('maintenance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('maintenance_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('manufacturer', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('remark', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_maintenance_code', 'maintenance', ['code'], unique=True)
    op.create_index('ix_maintenance_id', 'maintenance', ['id'], unique=False)
    op.create_table('monitor_history_energy_consumptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('coil_number', sa.String(length=50), nullable=True, comment='钢卷号'),
        sa.Column('elect_consum', sa.Float(), nullable=True, comment='本卷用电量KWh'),
        sa.Column('n2_total', sa.Float(), nullable=True, comment='本卷氮气量m³'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_monitor_history_energy_consumptions_coil_number', 'monitor_history_energy_consumptions', ['coil_number'], unique=False)
    op.create_index('ix_monitor_history_energy_consumptions_created_at', 'monitor_history_energy_consumptions', ['created_at'], unique=False)
    op.create_index('ix_monitor_history_energy_consumptions_device_id', 'monitor_history_energy_consumptions', ['device_id'], unique=False)
    op.create_table('monitor_history_process_curves',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('coil_number', sa.String(length=50), nullable=True, comment='当前生产钢卷号'),
        sa.Column('line_speed_set', sa.Float(), nullable=True, comment='产线设定速度m/min'),
        sa.Column('line_speed_act', sa.Float(), nullable=True, comment='产线实际速度m/min'),
        sa.Column('z1_temp_set', sa.Integer(), nullable=True, comment='1区设定温度℃'),
        sa.Column('z1_temp_act', sa.Integer(), nullable=True, comment='1区实际温度℃'),
        sa.Column('z2_temp_set', sa.Integer(), nullable=True, comment='2区设定温度℃'),
        sa.Column('z2_temp_act', sa.Integer(), nullable=True, comment='2区实际温度℃'),
        sa.Column('z3_temp_set', sa.Integer(), nullable=True, comment='3区设定温度℃'),
        sa.Column('z3_temp_act', sa.Integer(), nullable=True, comment='3区实际温度℃'),
        sa.Column('z4_temp_set', sa.Integer(), nullable=True, comment='4区设定温度℃'),
        sa.Column('z4_temp_act', sa.Integer(), nullable=True, comment='4区实际温度℃'),
        sa.Column('z5_temp_set', sa.Integer(), nullable=True, comment='5区设定温度℃'),
        sa.Column('z5_temp_act', sa.Integer(), nullable=True, comment='5区实际温度℃'),
        sa.Column('z6_temp_set', sa.Integer(), nullable=True, comment='6区设定温度℃'),
        sa.Column('z6_temp_act', sa.Integer(), nullable=True, comment='6区实际温度℃'),
        sa.Column('unc_set_tension_p', sa.Float(), nullable=True, comment='开卷机张力设定%'),
        sa.Column('unc_act_tension_p', sa.Float(), nullable=True, comment='开卷机实际张力%'),
        sa.Column('unc_set_tension_kg', sa.Float(), nullable=True, comment='开卷机张力设定Kg'),
        sa.Column('rec_set_tension_p', sa.Float(), nullable=True, comment='收卷机张力设定%'),
        sa.Column('rec_act_tension_p', sa.Float(), nullable=True, comment='收卷机实际张力%'),
        sa.Column('rec_set_tension_kg', sa.Float(), nullable=True, comment='收卷机张力设定Kg'),
        sa.Column('furn_set_tension_kg', sa.Float(), nullable=True, comment='炉内张力设定Kg'),
        sa.Column('furn_act_tension_kg', sa.Float(), nullable=True, comment='炉内实际张力Kg'),
        sa.Column('cool_fan1_set_fre', sa.Float(), nullable=True, comment='风冷1设定频率Hz'),
        sa.Column('cool_fan1_act_fre', sa.Float(), nullable=True, comment='风冷1实际频率Hz'),
        sa.Column('cool_fan2_set_fre', sa.Float(), nullable=True, comment='风冷2设定频率Hz'),
        sa.Column('cool_fan2_act_fre', sa.Float(), nullable=True, comment='风冷2实际频率Hz'),
        sa.Column('n2_total', sa.Float(), nullable=True, comment='氮气累计量m³'),
        sa.Column('elect_consum', sa.Float(), nullable=True, comment='用电累计量KWh'),
        sa.Column('h2_flow', sa.Float(), nullable=True, comment='耗氢量m³/h'),
        sa.Column('n2_flow', sa.Float(), nullable=True, comment='耗氮量m³/h'),
        sa.Column('oxygen_content', sa.Float(), nullable=True, comment='氧含量ppm'),
        sa.Column('dew_point', sa.Float(), nullable=True, comment='露点值℃'),
        sa.Column('muffle_pressure', sa.Float(), nullable=True, comment='马弗压力Pa'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_monitor_history_process_curves_coil_number', 'monitor_history_process_curves', ['coil_number'], unique=False)
    op.create_index('ix_monitor_history_process_curves_created_at', 'monitor_history_process_curves', ['created_at'], unique=False)
    op.create_index('ix_monitor_history_process_curves_device_id', 'monitor_history_process_curves', ['device_id'], unique=False)
    op.create_table('plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coil_no', sa.String(length=50), nullable=False),
        sa.Column('grade', sa.String(length=20), nullable=False),
        sa.Column('spec', sa.String(length=50), nullable=False),
        sa.Column('weight', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('thickness', sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column('width', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('material_status', sa.String(length=20), nullable=False),
        sa.Column('density', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('entry_length', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('uncoiler1_tension', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('exit_tension', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('process1_tension', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('entry_loop_tension', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('exit_loop_tension', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('entry_unit_tension', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('entry_loop_unit_tension', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('process_unit_tension', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('exit_loop_unit_tension', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('exit_unit_tension', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.SmallInteger(), nullable=False),
        sa.Column('remark', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_plans_coil_no', 'plans', ['coil_no'], unique=True)
    op.create_index('ix_plans_id', 'plans', ['id'], unique=False)
    op.create_index('ix_plans_priority', 'plans', ['priority'], unique=False)
    op.create_index('ix_plans_status', 'plans', ['status'], unique=False)
    op.create_table('production_status_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('record_time', sa.DateTime(timezone=True), nullable=False, comment='记录时间'),
        sa.Column('online_coil_id', sa.String(length=50), nullable=True, comment='在线卷号'),
        sa.Column('online_coil_progress', sa.Integer(), nullable=False, comment='在线卷进度(%)'),
        sa.Column('online_coil_status', sa.String(length=50), nullable=False, comment='在线卷状态'),
        sa.Column('ready_coil_id', sa.String(length=50), nullable=True, comment='准备卷号'),
        sa.Column('ready_coil_grade', sa.String(length=20), nullable=True, comment='准备卷牌号'),
        sa.Column('ready_coil_weight', sa.Numeric(precision=12, scale=4), nullable=False, comment='准备卷重量'),
        sa.Column('current_speed', sa.Numeric(precision=10, scale=2), nullable=False, comment='当前速度(m/min)'),
        sa.Column('furnace_temp', sa.Numeric(precision=10, scale=2), nullable=False, comment='炉区温度(℃)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_production_status_records_id', 'production_status_records', ['id'], unique=False)
    op.create_index('ix_production_status_records_record_time', 'production_status_records', ['record_time'], unique=False)
    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('progress', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_projects_id', 'projects', ['id'], unique=False)
    op.create_index('ix_projects_name', 'projects', ['name'], unique=False)
    op.create_index('ix_projects_status', 'projects', ['status'], unique=False)
    op.create_table('quality_grade_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stats_date', sa.Date(), nullable=False, comment='统计日期'),
        sa.Column('grade_name', sa.String(length=50), nullable=False, comment='等级名称'),
        sa.Column('grade_count', sa.Integer(), nullable=False, comment='数量'),
        sa.Column('grade_color', sa.String(length=20), nullable=False, comment='显示颜色'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_quality_grade_stats_id', 'quality_grade_stats', ['id'], unique=False)
    op.create_index('ix_quality_grade_stats_stats_date', 'quality_grade_stats', ['stats_date'], unique=False)
    op.create_table('quality_inspections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coil_no', sa.String(length=50), nullable=False, comment='料卷号'),
        sa.Column('grade', sa.String(length=20), nullable=True, comment='牌号'),
        sa.Column('spec', sa.String(length=50), nullable=True, comment='规格'),
        sa.Column('weight', sa.Numeric(precision=12, scale=4), nullable=True, comment='重量(吨)'),
        sa.Column('start_time', sa.DateTime(), nullable=True, comment='生产开始时间'),
        sa.Column('end_time', sa.DateTime(), nullable=True, comment='生产结束时间'),
        sa.Column('operator', sa.String(length=100), nullable=True, comment='操作员'),
        sa.Column('shift', sa.String(length=20), nullable=True, comment='班次'),
        sa.Column('quality_items', sa.JSON(), nullable=True, comment='质量检查项目JSON'),
        sa.Column('judgment', sa.String(length=20), nullable=True, comment='综合判定'),
        sa.Column('quality_grade', sa.String(length=20), nullable=True, comment='质量等级'),
        sa.Column('comment', sa.Text(), nullable=True, comment='质量评语'),
        sa.Column('inspector', sa.String(length=100), nullable=True, comment='检验员'),
        sa.Column('inspect_time', sa.DateTime(), nullable=True, comment='检验时间'),
        sa.Column('coil_images', sa.JSON(), nullable=True, comment='钢卷图片URL列表'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_quality_inspections_coil_no', 'quality_inspections', ['coil_no'], unique=False)
    op.create_index('ix_quality_inspections_id', 'quality_inspections', ['id'], unique=False)
    op.create_table('quality_spc_measurements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coil_no', sa.String(length=50), nullable=False, comment='料卷号'),
        sa.Column('grade', sa.String(length=20), nullable=True, comment='牌号'),
        sa.Column('item', sa.String(length=50), nullable=False, comment='分析项目'),
        sa.Column('value', sa.Numeric(precision=12, scale=4), nullable=False, comment='测量值'),
        sa.Column('operator', sa.String(length=100), nullable=True, comment='操作员'),
        sa.Column('measured_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='测量时间'),
        sa.Column('is_normal', sa.Boolean(), nullable=False, comment='是否正常点'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_quality_spc_measurements_coil_no', 'quality_spc_measurements', ['coil_no'], unique=False)
    op.create_index('ix_quality_spc_measurements_grade', 'quality_spc_measurements', ['grade'], unique=False)
    op.create_index('ix_quality_spc_measurements_id', 'quality_spc_measurements', ['id'], unique=False)
    op.create_index('ix_quality_spc_measurements_item', 'quality_spc_measurements', ['item'], unique=False)
    op.create_index('ix_quality_spc_measurements_measured_at', 'quality_spc_measurements', ['measured_at'], unique=False)
    op.create_table('recruitments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('applicants', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('publish_date', sa.Date(), nullable=True),
        sa.Column('requirements', sa.String(length=1000), nullable=True),
        sa.Column('salary_range', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_recruitments_id', 'recruitments', ['id'], unique=False)
    op.create_table('shift_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False, comment='规则名称'),
        sa.Column('shift_mode', sa.String(length=20), nullable=False, comment='班制类型'),
        sa.Column('cycle_name', sa.String(length=50), nullable=False, comment='轮班周期'),
        sa.Column('day_shift_start', sa.String(length=20), nullable=False, comment='白班开始时间'),
        sa.Column('day_shift_end', sa.String(length=20), nullable=False, comment='白班结束时间'),
        sa.Column('middle_shift_start', sa.String(length=20), nullable=True, comment='中班开始时间'),
        sa.Column('middle_shift_end', sa.String(length=20), nullable=True, comment='中班结束时间'),
        sa.Column('night_shift_start', sa.String(length=20), nullable=False, comment='夜班开始时间'),
        sa.Column('night_shift_end', sa.String(length=20), nullable=False, comment='夜班结束时间'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='状态'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_shift_rules_id', 'shift_rules', ['id'], unique=False)
    op.create_table('shift_teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_name', sa.String(length=50), nullable=False, comment='班组名称'),
        sa.Column('leader', sa.String(length=50), nullable=True, comment='班组长'),
        sa.Column('members', sa.Integer(), nullable=False, comment='成员数量'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='联系电话'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='状态'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_name', name=None),
    )
    op.create_index('ix_shift_teams_id', 'shift_teams', ['id'], unique=False)
    op.create_table('stop_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False, comment='开始时间'),
        sa.Column('end_time', sa.DateTime(), nullable=True, comment='结束时间'),
        sa.Column('duration', sa.Integer(), nullable=True, comment='持续时间(分钟)'),
        sa.Column('shift', sa.String(length=50), nullable=True, comment='班次'),
        sa.Column('operator', sa.String(length=50), nullable=True, comment='操作员'),
        sa.Column('reason', sa.String(length=500), nullable=True, comment='停机原因'),
        sa.Column('stop_type', sa.String(length=50), nullable=True, comment='停机类型'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='状态'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_stop_records_id', 'stop_records', ['id'], unique=False)
    op.create_table('temperature_zone_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('record_time', sa.DateTime(timezone=True), nullable=False, comment='记录时间'),
        sa.Column('zone_name', sa.String(length=50), nullable=False, comment='区域名称'),
        sa.Column('temperature', sa.Numeric(precision=10, scale=2), nullable=False, comment='温度(℃)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_temperature_zone_records_id', 'temperature_zone_records', ['id'], unique=False)
    op.create_index('ix_temperature_zone_records_record_time', 'temperature_zone_records', ['record_time'], unique=False)
    op.create_table('applicants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recruitment_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('education', sa.String(length=50), nullable=True),
        sa.Column('experience', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('apply_date', sa.DateTime(), nullable=True),
        sa.Column('remark', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['recruitment_id'], ['recruitments.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_applicants_id', 'applicants', ['id'], unique=False)
    op.create_index('ix_applicants_recruitment_id', 'applicants', ['recruitment_id'], unique=False)
    op.create_table('assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('employee_name', sa.String(length=100), nullable=True),
        sa.Column('assessment_type', sa.String(length=50), nullable=True),
        sa.Column('assessment_period', sa.String(length=20), nullable=True),
        sa.Column('production_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('quality_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('efficiency_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('overall_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('grade', sa.String(length=10), nullable=True),
        sa.Column('comments', sa.String(length=1000), nullable=True),
        sa.Column('assessor_id', sa.Integer(), nullable=True),
        sa.Column('assessment_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['assessor_id'], ['users.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_assessments_employee_id', 'assessments', ['employee_id'], unique=False)
    op.create_index('ix_assessments_id', 'assessments', ['id'], unique=False)
    op.create_table('employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('join_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_employees_id', 'employees', ['id'], unique=False)
    op.create_table('maintenance_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('maintenance_id', sa.Integer(), nullable=False),
        sa.Column('maintenance_type', sa.String(length=50), nullable=True),
        sa.Column('content', sa.String(length=500), nullable=True),
        sa.Column('last_date', sa.Date(), nullable=True),
        sa.Column('next_date', sa.Date(), nullable=True),
        sa.Column('cycle_days', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('operator', sa.String(length=100), nullable=True),
        sa.Column('remark', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['maintenance_id'], ['maintenance.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_maintenance_logs_id', 'maintenance_logs', ['id'], unique=False)
    op.create_index('ix_maintenance_logs_maintenance_id', 'maintenance_logs', ['maintenance_id'], unique=False)
    op.create_table('performance_main',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('coil_no', sa.String(length=50), nullable=False),
        sa.Column('parent_coil_no', sa.String(length=50), nullable=False),
        sa.Column('grade', sa.String(length=20), nullable=True),
        sa.Column('spec', sa.String(length=50), nullable=True),
        sa.Column('weight', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('total_length', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('diameter', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('density', sa.Numeric(precision=5, scale=3), nullable=True),
        sa.Column('production_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('output_quantity', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('qualified_quantity', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('efficiency_rate', sa.Numeric(precision=5, scale=2), nullable=True, server_default=sa.text('0.00')),
        sa.Column('quality_score', sa.Numeric(precision=5, scale=2), nullable=True, server_default=sa.text('0.00')),
        sa.Column('collected_weight', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('manual_override_weight', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('effective_weight', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('effective_weight_source', sa.String(length=32), nullable=True),
        sa.Column('manual_override_by_id', sa.Integer(), nullable=True),
        sa.Column('manual_override_at', sa.DateTime(), nullable=True),
        sa.Column('manual_override_reason', sa.String(length=500), nullable=True),
        sa.Column('total_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('total_duration_source', sa.String(length=32), nullable=True),
        sa.Column('is_split', sa.Boolean(), nullable=False),
        sa.Column('remark', sa.String(length=500), nullable=True),
        sa.Column('device_id', sa.Integer(), nullable=True),
        sa.Column('observation_status', sa.String(length=32), nullable=True),
        sa.Column('record_source', sa.String(length=32), nullable=True),
        sa.Column('first_observed_at', sa.DateTime(), nullable=True),
        sa.Column('last_observed_at', sa.DateTime(), nullable=True),
        sa.Column('first_raw_snapshot_id', sa.Integer(), nullable=True),
        sa.Column('last_raw_snapshot_id', sa.Integer(), nullable=True),
        sa.Column('plc_key', sa.String(length=80), nullable=True),
        sa.Column('db_number', sa.Integer(), nullable=True),
        sa.Column('group_name', sa.String(length=120), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['manual_override_by_id'], ['users.id'], name=None, ondelete=None),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_id', 'coil_no', name='uq_performance_main_device_coil'),
    )
    op.create_index('ix_performance_main_device_observation_status', 'performance_main', ['device_id', 'observation_status'], unique=False)
    op.create_index('ix_performance_main_id', 'performance_main', ['id'], unique=False)
    op.create_table('performance_targets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_value', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('period_type', sa.String(length=20), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_performance_targets_id', 'performance_targets', ['id'], unique=False)
    op.create_table('performance_transform',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transform_type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('quantity_dimension', sa.String(length=20), nullable=False),
        sa.Column('requested_by_id', sa.Integer(), nullable=True),
        sa.Column('requested_reason', sa.String(length=500), nullable=True),
        sa.Column('confirmed_by_id', sa.Integer(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('effective_weight_context', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['confirmed_by_id'], ['users.id'], name=None, ondelete=None),
        sa.ForeignKeyConstraint(['requested_by_id'], ['users.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_performance_transform_id', 'performance_transform', ['id'], unique=False)
    op.create_index('ix_performance_transform_status', 'performance_transform', ['status'], unique=False)
    op.create_index('ix_performance_transform_transform_type', 'performance_transform', ['transform_type'], unique=False)
    op.create_table('production_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=False),
        sa.Column('shift', sa.String(length=20), nullable=True),
        sa.Column('total_coils', sa.Integer(), nullable=True),
        sa.Column('total_weight', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('qualified_coils', sa.Integer(), nullable=True),
        sa.Column('qualified_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('oee', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('efficiency', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('energy_consumption', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_production_reports_id', 'production_reports', ['id'], unique=False)
    op.create_index('ix_production_reports_report_date', 'production_reports', ['report_date'], unique=False)
    op.create_table('project_milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('reached', sa.Boolean(), nullable=False),
        sa.Column('reached_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=None, ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_project_milestones_id', 'project_milestones', ['id'], unique=False)
    op.create_index('ix_project_milestones_project_id', 'project_milestones', ['project_id'], unique=False)
    op.create_index('ix_project_milestones_reached', 'project_milestones', ['reached'], unique=False)
    op.create_table('project_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('assignee', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name=None, ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_project_tasks_id', 'project_tasks', ['id'], unique=False)
    op.create_index('ix_project_tasks_priority', 'project_tasks', ['priority'], unique=False)
    op.create_index('ix_project_tasks_project_id', 'project_tasks', ['project_id'], unique=False)
    op.create_index('ix_project_tasks_status', 'project_tasks', ['status'], unique=False)
    op.create_table('quality_defect_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inspection_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=True, comment='缺陷位置'),
        sa.Column('defect_type', sa.String(length=50), nullable=True, comment='缺陷类型'),
        sa.Column('level', sa.String(length=20), nullable=True, comment='缺陷等级'),
        sa.Column('length', sa.Numeric(precision=10, scale=2), nullable=True, comment='缺陷长度(mm)'),
        sa.Column('description', sa.Text(), nullable=True, comment='缺陷描述'),
        sa.Column('image_url', sa.String(length=500), nullable=True, comment='缺陷图片URL'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['inspection_id'], ['quality_inspections.id'], name=None, ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_quality_defect_records_id', 'quality_defect_records', ['id'], unique=False)
    op.create_index('ix_quality_defect_records_inspection_id', 'quality_defect_records', ['inspection_id'], unique=False)
    op.create_table('shifts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False, comment='班组ID'),
        sa.Column('date', sa.Date(), nullable=False, comment='日期'),
        sa.Column('day_leader', sa.String(length=50), nullable=True, comment='白班负责人'),
        sa.Column('night_leader', sa.String(length=50), nullable=True, comment='夜班负责人'),
        sa.Column('day_members', sa.String(length=500), nullable=True, comment='白班成员'),
        sa.Column('night_members', sa.String(length=500), nullable=True, comment='夜班成员'),
        sa.Column('remark', sa.String(length=500), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['team_id'], ['shift_teams.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_shifts_id', 'shifts', ['id'], unique=False)
    op.create_index('ix_shifts_team_id', 'shifts', ['team_id'], unique=False)
    op.create_table('attendances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('check_in', sa.DateTime(), nullable=True),
        sa.Column('check_out', sa.DateTime(), nullable=True),
        sa.Column('work_hours', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('remark', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_attendances_date', 'attendances', ['date'], unique=False)
    op.create_index('ix_attendances_employee_id', 'attendances', ['employee_id'], unique=False)
    op.create_index('ix_attendances_id', 'attendances', ['id'], unique=False)
    op.create_table('performance_lineage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transform_id', sa.Integer(), nullable=False),
        sa.Column('performance_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('allocated_weight', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('effective_weight_snapshot', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('effective_weight_source_snapshot', sa.String(length=32), nullable=False),
        sa.Column('available_weight_before_snapshot', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('available_weight_after_snapshot', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['performance_id'], ['performance_main.id'], name=None, ondelete=None),
        sa.ForeignKeyConstraint(['transform_id'], ['performance_transform.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_performance_lineage_id', 'performance_lineage', ['id'], unique=False)
    op.create_index('ix_performance_lineage_performance_role', 'performance_lineage', ['performance_id', 'role'], unique=False)
    op.create_index('ix_performance_lineage_transform_role', 'performance_lineage', ['transform_id', 'role'], unique=False)
    op.create_table('performance_process_speed',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('performance_id', sa.Integer(), nullable=False),
        sa.Column('zone', sa.String(length=50), nullable=False),
        sa.Column('set_speed', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('avg_speed', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('max_speed', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('record_time', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['performance_id'], ['performance_main.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_performance_process_speed_id', 'performance_process_speed', ['id'], unique=False)
    op.create_index('ix_performance_process_speed_performance_id', 'performance_process_speed', ['performance_id'], unique=False)
    op.create_table('performance_process_temperature',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('performance_id', sa.Integer(), nullable=False),
        sa.Column('zone', sa.String(length=50), nullable=False),
        sa.Column('set_temp', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('max_temp', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('min_temp', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('avg_temp', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('duration', sa.Numeric(), nullable=True),
        sa.Column('record_time', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['performance_id'], ['performance_main.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_performance_process_temperature_id', 'performance_process_temperature', ['id'], unique=False)
    op.create_index('ix_performance_process_temperature_performance_id', 'performance_process_temperature', ['performance_id'], unique=False)
    op.create_table('performance_process_tension',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('performance_id', sa.Integer(), nullable=False),
        sa.Column('zone', sa.String(length=50), nullable=False),
        sa.Column('set_tension', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('avg_tension', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('max_tension', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('min_tension', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('record_time', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['performance_id'], ['performance_main.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_performance_process_tension_id', 'performance_process_tension', ['id'], unique=False)
    op.create_index('ix_performance_process_tension_performance_id', 'performance_process_tension', ['performance_id'], unique=False)
    op.create_table('performance_push_down_record',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('performance_id', sa.Integer(), nullable=False),
        sa.Column('push_down_type', sa.String(length=20), nullable=False),
        sa.Column('target_system', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('message', sa.String(length=500), nullable=True),
        sa.Column('operator_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], name=None, ondelete=None),
        sa.ForeignKeyConstraint(['performance_id'], ['performance_main.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_performance_push_down_record_id', 'performance_push_down_record', ['id'], unique=False)
    op.create_index('ix_performance_push_down_record_performance_id', 'performance_push_down_record', ['performance_id'], unique=False)
    op.create_table('performance_split',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('performance_id', sa.Integer(), nullable=False),
        sa.Column('split_no', sa.String(length=50), nullable=False),
        sa.Column('weight', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('spec', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['performance_id'], ['performance_main.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_performance_split_id', 'performance_split', ['id'], unique=False)
    op.create_table('print_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('performance_id', sa.Integer(), nullable=False),
        sa.Column('print_type', sa.String(length=50), nullable=True),
        sa.Column('print_status', sa.String(length=20), nullable=False),
        sa.Column('print_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('operator_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], name=None, ondelete=None),
        sa.ForeignKeyConstraint(['performance_id'], ['performance_main.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_print_records_id', 'print_records', ['id'], unique=False)
    op.create_index('ix_print_records_performance_id', 'print_records', ['performance_id'], unique=False)
    op.create_table('quality_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('performance_id', sa.Integer(), nullable=False),
        sa.Column('item_name', sa.String(length=100), nullable=False),
        sa.Column('standard_value', sa.String(length=100), nullable=True),
        sa.Column('actual_value', sa.String(length=100), nullable=True),
        sa.Column('result', sa.String(length=20), nullable=True),
        sa.Column('inspector', sa.String(length=100), nullable=True),
        sa.Column('inspect_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('remark', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['performance_id'], ['performance_main.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_quality_records_id', 'quality_records', ['id'], unique=False)
    op.create_index('ix_quality_records_performance_id', 'quality_records', ['performance_id'], unique=False)
    op.create_table('defect_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quality_record_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('defect_type', sa.String(length=50), nullable=True),
        sa.Column('defect_level', sa.String(length=20), nullable=True),
        sa.Column('length', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['quality_record_id'], ['quality_records.id'], name=None, ondelete=None),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_defect_records_id', 'defect_records', ['id'], unique=False)
    op.create_index('ix_defect_records_quality_record_id', 'defect_records', ['quality_record_id'], unique=False)


def downgrade():
    # 此动作会删除本增量业务数据；实际执行必须另行获批。
    op.drop_table('defect_records')
    op.drop_table('quality_records')
    op.drop_table('print_records')
    op.drop_table('performance_split')
    op.drop_table('performance_push_down_record')
    op.drop_table('performance_process_tension')
    op.drop_table('performance_process_temperature')
    op.drop_table('performance_process_speed')
    op.drop_table('performance_lineage')
    op.drop_table('attendances')
    op.drop_table('shifts')
    op.drop_table('quality_defect_records')
    op.drop_table('project_tasks')
    op.drop_table('project_milestones')
    op.drop_table('production_reports')
    op.drop_table('performance_transform')
    op.drop_table('performance_targets')
    op.drop_table('performance_main')
    op.drop_table('maintenance_logs')
    op.drop_table('employees')
    op.drop_table('assessments')
    op.drop_table('applicants')
    op.drop_table('temperature_zone_records')
    op.drop_table('stop_records')
    op.drop_table('shift_teams')
    op.drop_table('shift_rules')
    op.drop_table('recruitments')
    op.drop_table('quality_spc_measurements')
    op.drop_table('quality_inspections')
    op.drop_table('quality_grade_stats')
    op.drop_table('projects')
    op.drop_table('production_status_records')
    op.drop_table('plans')
    op.drop_table('monitor_history_process_curves')
    op.drop_table('monitor_history_energy_consumptions')
    op.drop_table('maintenance')
    op.drop_table('equipment_temperature')
    op.drop_table('equipment_production_parameters')
    op.drop_table('equipment_drive')
    op.drop_table('downtime_records')
    op.drop_table('departments')
    op.drop_table('daily_production_stats')
