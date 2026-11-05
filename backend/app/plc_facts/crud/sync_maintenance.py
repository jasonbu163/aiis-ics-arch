"""只操作七表的同步SQL/结构核验；调用者拥有事务及运行授权。"""
import re
from sqlalchemy import inspect,select,text,func,or_,and_
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import UniqueConstraint,CheckConstraint,ForeignKeyConstraint
from ..models import TABLES,StreamState,SourceBinding,LatestPoint,RawSample,Cycle,BatchReceipt,SampleReceipt
from ..canonical import sha,canonical
from ..error_codes import FactsError
from ..retention import db_instant

PENDING={'equipment_integration_receipts','performance_integration_receipts','monitor_integration_receipts','performance_integration_observation_events'}
BASELINE_TABLES = ('applicants', 'assessments', 'attendances', 'control_agent_gate_tokens', 'daily_production_stats', 'defect_records', 'departments', 'downtime_records', 'employees', 'energy_price_hours', 'energy_prices', 'equipment_drive', 'equipment_mapping_receipts', 'equipment_production_parameters', 'equipment_temperature', 'equipment_temperature_sample_receipts', 'equipment_temperature_samples', 'maintenance', 'maintenance_logs', 'monitor_collector_states', 'monitor_history_energy_consumptions', 'monitor_history_process_curves', 'monitor_mapping_receipts', 'performance_lineage', 'performance_main', 'performance_mapping_observation_state', 'performance_mapping_receipts', 'performance_process_speed', 'performance_process_temperature', 'performance_process_tension', 'performance_push_down_record', 'performance_split', 'performance_targets', 'performance_transform', 'plans', 'plc_db_block_latest_snapshots', 'plc_db_block_raw_snapshots', 'print_records', 'production_reports', 'production_status_records', 'project_milestones', 'project_tasks', 'projection_mapping_audit_events', 'projection_mapping_bindings', 'projection_mapping_revisions', 'projection_mapping_sets', 'projection_runtime_audit_events', 'projection_runtime_cursors', 'projects', 'quality_defect_records', 'quality_grade_stats', 'quality_inspections', 'quality_records', 'quality_spc_measurements', 'recruitments', 'shift_rules', 'shift_teams', 'shifts', 'stop_records', 'sys_dict_items', 'sys_dicts', 'temperature_zone_records', 'token_blacklist', 'users')
PROFILES={'0a2c4e6f8b10':('BE009-B',71),'1b3d5f7a9c20':('BE009-BE010-JOINT',75)}

def normalized_type(typ):
    s=str(typ.compile(dialect=mysql.dialect())).upper()
    # MySQL反射会把库继承的collation附到VARCHAR类型；F7类型口径不含库默认排序规则。
    s=re.sub(r' COLLATE [A-Z0-9_]+$', '', s)
    if s in ('BOOL','BOOLEAN','TINYINT(1)'): s='BOOLEAN'
    if s=='INTEGER': s='INTEGER'
    return s

def check_text(value):
    text=re.sub(r"_[a-zA-Z0-9]+(?=')",'',str(value))
    return re.sub(r'[\s`()]','',text).lower()

def schema_shape(connection=None):
    """语义F7：稳定排序列/类型/NULL/default和命名约束，不hash SHOW CREATE排版。"""
    inspector=inspect(connection) if connection is not None else None
    result=[]
    for table in sorted(TABLES,key=lambda t:t.name):
        if inspector:
            cols=[dict(name=c['name'],type=normalized_type(c['type']),nullable=c['nullable'],default=None if c['default'] is None else str(c['default'])) for c in inspector.get_columns(table.name)]
            pk=inspector.get_pk_constraint(table.name)['constrained_columns']
            unique=[dict(name=c['name'],columns=c['column_names']) for c in inspector.get_unique_constraints(table.name)]
            checks=[dict(name=c['name'],sql=check_text(c['sqltext'])) for c in inspector.get_check_constraints(table.name)]
            indexes=[dict(name=c['name'],columns=c['column_names'],unique=bool(c['unique'])) for c in inspector.get_indexes(table.name) if not c.get('duplicates_constraint') and c['name'] not in {u['name'] for u in unique}]
            fks=inspector.get_foreign_keys(table.name)
        else:
            cols=[dict(name=c.name,type=normalized_type(c.type),nullable=c.nullable,default=None if c.server_default is None else str(c.server_default.arg)) for c in table.columns]
            pk=[c.name for c in table.primary_key.columns]
            unique=[dict(name=c.name or '_'.join(x.name for x in c.columns),columns=[x.name for x in c.columns]) for c in table.constraints if isinstance(c,UniqueConstraint)]
            checks=[dict(name=c.name,sql=check_text(c.sqltext)) for c in table.constraints if isinstance(c,CheckConstraint)]
            indexes=[dict(name=c.name,columns=[x.name for x in c.columns],unique=bool(c.unique)) for c in table.indexes]
            fks=[dict(name=c.name) for c in table.constraints if isinstance(c,ForeignKeyConstraint)]
        # PK columns in MySQL always NOT NULL, model already specifies that by primary_key.
        result.append(dict(table=table.name,columns=sorted(cols,key=lambda c:c['name']),primaryKey=pk,
            unique=sorted(unique,key=lambda c:c['name']),checks=sorted(checks,key=lambda c:c['name']),
            indexes=sorted(indexes,key=lambda c:c['name']),foreignKeys=fks))
    return result

def fingerprint(connection=None): return sha(canonical(schema_shape(connection)))

def verify_profile(connection):
    if connection.dialect.name!='mysql': raise FactsError('not_ready',503)
    isolation=connection.execute(text('SELECT @@transaction_isolation')).scalar_one()
    if isolation!='REPEATABLE-READ': raise FactsError('not_ready',503)
    version=str(connection.execute(text('SELECT VERSION()')).scalar_one()).split('-')[0]
    if not version.startswith('8.4.'): raise FactsError('not_ready',503)
    revisions=list(connection.execute(text('SELECT version_num FROM alembic_version')).scalars())
    if len(revisions)!=1 or revisions[0] not in PROFILES: raise FactsError('not_ready',503)
    revision=revisions[0]; profile,count=PROFILES[revision]
    expected=set(BASELINE_TABLES) | {table.name for table in TABLES}
    if revision=='1b3d5f7a9c20': expected |= PENDING
    actual=set(inspect(connection).get_table_names())-{'alembic_version'}
    if len(expected)!=count or actual!=expected: raise FactsError('not_ready',503)
    frozen=fingerprint(); live=fingerprint(connection)
    if live!=frozen: raise FactsError('not_ready',503)
    return dict(schemaProfile=profile,revision=revision,fingerprint=frozen,applicationTables=count)

def clock(db,state=None):
    row=db.execute(text('SELECT CURRENT_TIMESTAMP(6), TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))')).one()
    now=db_instant(row[0])
    if row[1]!=28800 or state is not None and now.wall<state.last_db_time: raise FactsError('clock_invalid',503)
    return now

def lock(db): return db.execute(select(StreamState).where(StreamState.id==1).with_for_update(nowait=True).execution_options(populate_existing=True)).scalar_one_or_none()
def blob_bytes(db):
    total=0
    for model,fields in ((RawSample,('payload_utf8','projections')),(Cycle,('manifest_utf8','context_utf8','transport_manifest')),(LatestPoint,('point_fact',))):
        for field in fields: total+=db.execute(select(func.coalesce(func.sum(func.octet_length(getattr(model,field))),0))).scalar_one()
    return int(total)
def proof_rows(db): return sum(db.execute(select(func.count()).select_from(m)).scalar_one() for m in (BatchReceipt,SampleReceipt,Cycle))

def binding(db,plc): return db.get(SourceBinding,plc.encode('utf-8'))
def binding_count(db): return db.execute(select(func.count()).select_from(SourceBinding)).scalar_one()
def latest_rows(db,plc): return list(db.execute(select(LatestPoint).where(LatestPoint.plc_id==plc.encode('utf-8'))).scalars())
def _expired_at(model,now):
    return or_(model.expires_at<now.wall,and_(model.expires_at==now.wall,model.expires_ns<=now.ns))


def _cycle_has_values():
    # NULL与空BLOB都没有原值；同一资格同时用于清理、proof与status。
    return or_(*(func.coalesce(func.octet_length(column),0)>0 for column in
                 (Cycle.manifest_utf8,Cycle.context_utf8,Cycle.transport_manifest)))


def expired_rows(db,model,now,limit=200):
    statement=select(model).where(_expired_at(model,now))
    if model is Cycle: statement=statement.where(_cycle_has_values())
    return db.execute(statement.order_by(model.expires_at,model.expires_ns,*model.__table__.primary_key.columns).limit(limit)).scalars()
def expired_batches(db,now): return db.execute(select(BatchReceipt).where(BatchReceipt.proof_expires_at<=now.wall).order_by(BatchReceipt.proof_expires_at).limit(200)).scalars()
def prefix_rows(db):
    serial=db.execute(select(SampleReceipt.commit_serial).order_by(SampleReceipt.commit_serial).limit(1)).scalar_one_or_none()
    if serial is None: return []
    return list(db.execute(select(SampleReceipt).where(SampleReceipt.commit_serial==serial).order_by(SampleReceipt.ordinal)).scalars())
def expired_cycle_proofs(db,now):
    referenced=select(SampleReceipt.id).where(SampleReceipt.instance_id==Cycle.instance_id,
        SampleReceipt.cycle_id==Cycle.cycle_id).exists()
    # 合格资格必须在LIMIT之前裁定；有值/有引用的长期前缀不能饿死后续proof。
    return db.execute(select(Cycle).where(Cycle.proof_expires_at<=now.wall,~_cycle_has_values(),~referenced)
        .order_by(Cycle.proof_expires_at,Cycle.instance_id,Cycle.cycle_id).limit(200)).scalars()
def oldest_expired(db,model,now):
    stmt=select(func.min(model.expires_at)).where(_expired_at(model,now))
    if model is Cycle: stmt=stmt.where(_cycle_has_values())
    return db.execute(stmt).scalar_one()
def state_row(db): return db.get(StreamState,1)


def unadopted_owner_empty(db):
    return all(db.execute(select(func.count()).select_from(model)).scalar_one()==0 for model in (SourceBinding,RawSample,Cycle,LatestPoint,BatchReceipt,SampleReceipt))
