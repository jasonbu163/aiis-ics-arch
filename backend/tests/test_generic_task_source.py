"""ARCH-TASK-001 的无数据库合同、纯规则和并发重试源码自检。"""
import hashlib
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from pydantic import ValidationError
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateTable

from app.task.domain import encode_value, decode_value, task_number, local_time, merge_values
from app.task.eligibility import parse_profile
from app.task.errors import TaskError
from app.task.schemas.fields import FieldChange
from app.plan.schemas.workflow import Report
from app.performance.schemas.workflow import Snapshot
from app.plan.services import async_workflow as plans
from app.task.models import FieldConfigState, FieldDefinition
from app.plan.models import Plan, DispatchAttempt, ActionEvent
from app.performance.models import Performance
from app.module_registry import import_model_packages
from core.registrar import create_app
from database import Base, get_db

pytestmark = pytest.mark.no_db


def field(kind, nullable=False):
    return SimpleNamespace(value_type=kind, is_nullable=nullable)


def test_values_preserve_zero_false_empty_and_type_boundaries():
    assert encode_value(field('number'), 0) == '0'
    assert decode_value(field('number'), '0') == 0
    assert encode_value(field('boolean'), False) == 'false'
    assert decode_value(field('boolean'), 'false') is False
    assert encode_value(field('string'), '') == ''
    assert encode_value(field('string'), '0007') == '0007'
    assert encode_value(field('string'), '\U0001f600' * 255) == '\U0001f600' * 255
    assert encode_value(field('string', True), None) is None
    assert merge_values({'01':'x','02':'false'}, {'01':None,'03':'0'}) == {'02':'false','03':'0'}
    for definition, value in ((field('number'), True), (field('number'), 1.00001),
                              (field('number'), 10000000000), (field('string'), None),
                              (field('string'), '界'*256), (field('string'), '\ud800')):
        with pytest.raises(TaskError) as exc:
            encode_value(definition, value)
        assert exc.value.key == 'task.invalid_request'


def test_task_identity_shanghai_and_strict_request_types():
    assert task_number('  gt1-a_2.x  ') == 'GT1-A_2.X'
    with pytest.raises(TaskError): task_number('ß')
    assert local_time(datetime.fromisoformat('2026-11-11T05:00:00+00:00')).isoformat() == '2026-11-11T13:00:00'
    with pytest.raises(TaskError): local_time(datetime(2026, 11, 11))
    with pytest.raises(ValidationError): FieldChange(scope='shared_sync', slotNo=1, enabled='true')
    with pytest.raises(ValidationError): Report(dispatchId='x', taskNo='X', targetKey='T', producerId='p', outcome='plc_accepted', ackObservedAt='2026-01-01T00:00:00.1234567+08:00')


@pytest.mark.parametrize('field_name', ['ackObservedAt', 'observedAt', 'startedAt', 'completedAt'])
def test_all_task_body_times_require_an_offset_and_at_most_six_fractional_digits(field_name):
    if field_name == 'ackObservedAt':
        model, body = Report, {'dispatchId':'x','taskNo':'X','targetKey':'T','producerId':'p','outcome':'plc_accepted'}
    else:
        model, body = Snapshot, {'producerId':'sma-01','taskNo':'X','targetKey':'T','fieldConfigVersion':1,
            'productionStatus':'running','observationSeq':1,'observedAt':None,'syncValues':{},'localValues':{}}
    for value in ('1794381599', 1794381599, '2026-11-11T10:00:00',
                  '2026-11-11T10:00:00.1234567+08:00', '2026-11-11T10:00:00+08:60'):
        with pytest.raises(ValidationError):
            model.model_validate({**body,field_name:value})
    local=model.model_validate({**body,field_name:'2026-11-11T10:00:00.123456+08:00'})
    utc=model.model_validate({**body,field_name:'2026-11-11T02:00:00.123456Z'})
    assert getattr(local,field_name)==getattr(utc,field_name)
    assert local_time(getattr(local,field_name))==datetime(2026,11,11,10,0,0,123456)


@pytest.mark.asyncio
async def test_both_lists_validate_query_times_and_target_before_query():
    from core.deps import get_current_user
    app=create_app(testing=True)
    class EmptyDB:
        async def execute(self, statement): return SimpleNamespace(scalar_one=lambda:0)
    async def no_db(): yield EmptyDB()
    app.dependency_overrides[get_db]=no_db
    app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(id=7,role='admin')
    headers={'Authorization':'Bearer fixture'}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture') as client:
        for path in ('/api/v1/plans','/api/v1/performances'):
            for key in ('createdFrom','createdTo'):
                for value in ('1794381599','2026-11-11T10:00:00',
                              '2026-11-11T10:00:00.1234567+08:00','2026-11-11T10:00:00+08:60'):
                    res=await client.get(path,headers=headers,params={key:value})
                    assert (res.status_code,res.json()['errorCode'])==(422,'task.invalid_request')
                for value in ('2026-11-11T10:00:00.123456+08:00','2026-11-11T02:00:00.123456Z'):
                    assert (await client.get(path,headers=headers,params={key:value})).status_code==200
            for target in ('LINE-01 ',' LINE-01','LINE 01','LINE-01\n','产线'):
                res=await client.get(path,headers=headers,params={'targetKey':target})
                assert (res.status_code,res.json()['errorCode'])==(422,'task.invalid_request')
            for target in ('LINE-01','line-01'):
                assert (await client.get(path,headers=headers,params={'targetKey':target})).status_code==200
    for path in ('/api/v1/plans','/api/v1/performances'):
        for param in app.openapi()['paths'][path]['get']['parameters']:
            if param['name'] in ('createdFrom','createdTo'):
                assert {'type':'string','format':'date-time'} in param['schema']['anyOf']


@pytest.mark.asyncio
async def test_task_body_time_validation_uses_http_error_envelope(monkeypatch):
    import app.plan.api.routes as plan_api
    import app.performance.api.routes as perf_api
    app=create_app(testing=True)
    async def no_db(): yield object()
    app.dependency_overrides[get_db]=no_db
    monkeypatch.setattr(plan_api,'admit',lambda *args:None)
    monkeypatch.setattr(plan_api,'report',AsyncMock(return_value={'taskNo':'GT1-A','dispatchId':'fixture','outcome':'accepted'}))
    monkeypatch.setattr(perf_api,'receive_snapshot',AsyncMock(return_value={'taskNo':'GT1-A','outcome':'created'}))
    monkeypatch.setattr(plan_api,'commit',AsyncMock())
    monkeypatch.setattr(perf_api,'commit',AsyncMock())
    report={'dispatchId':'fixture','taskNo':'GT1-A','targetKey':'LINE-01','producerId':'ff-01',
            'outcome':'plc_accepted','requestSeq':1,'ackSeq':1}
    snapshot={'producerId':'sma-01','taskNo':'GT1-A','targetKey':'LINE-01','fieldConfigVersion':1,
              'productionStatus':'running','observationSeq':1,'observedAt':None,'syncValues':{},'localValues':{}}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture') as client:
        for path,body,fields in (('/api/v1/integration/plans/dispatch/report',report,('ackObservedAt',)),
                                 ('/api/v1/integration/performances/upsert',snapshot,('observedAt','startedAt','completedAt'))):
            for name in fields:
                for value in ('1794381599',1794381599,'2026-11-11T10:00:00','2026-11-11T10:00:00.1234567+08:00'):
                    res=await client.post(path,json={**body,name:value})
                    assert (res.status_code,res.json()['errorCode'])==(422,'task.invalid_request')
                for value in ('2026-11-11T10:00:00.123456+08:00','2026-11-11T02:00:00.123456Z'):
                    assert (await client.post(path,json={**body,name:value})).status_code==200


def test_profile_keeps_v1_and_v2_mappings_distinct():
    item = {'targets': {'LINE-01': {'mes': ['mes-01'], 'executors': ['ff-01'], 'versions': {
        '1': {'dispatch': ['productCode'], 'plcSeqMax': 65535, 'automatic': {'producerId': 'sma-01', 'recordSource': 'sma'}},
        '2': {'dispatch': ['productCode','targetLength'], 'plcSeqMax': 65535, 'automatic': {'producerId': 'sma-01', 'recordSource': 'sma'}}}}}}
    assert parse_profile(item)['targets']['LINE-01']['versions']['1']['dispatch'] == ['productCode']
    assert parse_profile(item)['targets']['LINE-01']['versions']['2']['dispatch'] == ['productCode','targetLength']
    item['targets']['LINE-01']['versions']['2']['automatic']['recordSource'] = 'unknown'
    with pytest.raises(ValueError): parse_profile(item)


def test_mysql_table_options_and_registered_metadata():
    import_model_packages()
    old = {'plans','performance_split','performance_transform','performance_lineage', 'performance_process_temperature',
           'performance_process_tension','performance_process_speed','performance_push_down_record',
           'performance_integration_receipts','performance_integration_observation_events',
           'performance_mapping_receipts','performance_mapping_observation_state','quality_records','defect_records',
           'print_records','production_reports','performance_targets','assessments'}
    assert not old.intersection(Base.metadata.tables)
    assert {'quality_inspections','quality_defect_records','quality_spc_measurements'} <= set(Base.metadata.tables)
    for cls in (Plan, Performance, DispatchAttempt, ActionEvent, FieldConfigState, FieldDefinition):
        ddl = str(CreateTable(cls.__table__).compile(dialect=mysql.dialect()))
        for part in ('InnoDB','DYNAMIC','utf8mb4','utf8mb4_unicode_ci'):
            assert part in ddl


def migration():
    path = Path(__file__).resolve().parents[1] / 'alembic/versions/20261111_1400_5f7a9c1e3b25_generic_task.py'
    spec = importlib.util.spec_from_file_location('generic_task_migration', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_guard_rejects_occupied_view_and_topological_cycle(monkeypatch):
    revision = migration()
    class Rows(list):
        def first(self): return self[0] if self else None
    def fake_rows(connection, statement, parameters=None):
        if 'information_schema.TABLES' in statement:
            return Rows([(name,'BASE TABLE') for name in revision.OLD_TABLES] + [('plan_main','VIEW')])
        raise AssertionError('guard must stop before inspecting or mutating anything else')
    monkeypatch.setattr(revision, '_rows', fake_rows)
    with pytest.raises(RuntimeError, match='occupied'):
        revision._preflight(object(), 'fixture')
    with pytest.raises(RuntimeError, match='cyclic'):
        revision._drop_order({('plans','performance_main'),('performance_main','plans')})
    order = revision._drop_order({('performance_main','plans'),('performance_split','performance_main')})
    assert order.index('performance_split') < order.index('performance_main') < order.index('plans')


class Result:
    def __init__(self, value): self.value = value
    def scalar_one_or_none(self): return self.value
    def first(self): return self.value


@pytest.mark.asyncio
async def test_claim_rechecks_after_waiting_when_queue_is_now_empty(monkeypatch):
    monkeypatch.setattr(plans, 'config_state', AsyncMock())
    attempt = SimpleNamespace(claim_request_id='12345678-1234-4234-8234-123456789abc',
        dispatch_id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa', task_no='GT1-A', target_key='LINE-01',
        producer_id='ff-01', attempt_status='claimed', field_config_version=1, parameters={'x':1})
    db = SimpleNamespace(execute=AsyncMock(side_effect=[Result(None), Result(None), Result(None), Result(attempt)]))
    result = await plans.claim(db, {'targetKey':'LINE-01','producerId':'ff-01','claimRequestId':attempt.claim_request_id})
    assert result['outcome'] == 'existing_attempt' and result['attempt']['dispatchId'] == attempt.dispatch_id


@pytest.mark.asyncio
async def test_action_rechecks_identity_after_serialization(monkeypatch):
    monkeypatch.setattr(plans, 'config_state', AsyncMock())
    monkeypatch.setattr(plans, 'plan_by_id', AsyncMock(return_value=SimpleNamespace(dispatch_status='paused')))
    payload={'actionRequestId':'12345678-1234-4234-8234-123456789abc'}
    digest=hashlib.sha256(json.dumps({'id':'7','action':'pause','actorId':'2',**payload}, sort_keys=True,
        separators=(',', ':'), ensure_ascii=False).encode()).digest()
    event=SimpleNamespace(request_digest=digest, task_no='GT1-A', to_status='paused')
    db=SimpleNamespace(execute=AsyncMock(side_effect=[Result(None),Result(event)]))
    result=await plans.action(db, 7, 'pause', payload, 2)
    assert result == {'outcome':'duplicate','taskNo':'GT1-A','resultingDispatchStatus':'paused'}


@pytest.mark.asyncio
async def test_openapi_wire_shape_and_disabled_integration_before_lookup(monkeypatch):
    app=create_app(testing=True)
    paths=app.openapi()['paths']
    fields=paths['/api/v1/integration/task-field-configs']['get']['parameters']
    assert {p['name'] for p in fields if p.get('required')} == {'module'}
    for path in ('/api/v1/integration/plans/by-task/{taskNo}', '/api/v1/integration/performances/by-task/{taskNo}'):
        assert {p['name'] for p in paths[path]['get']['parameters'] if p.get('required')} == {'taskNo'}
    for path in ('/api/v1/splits','/api/v1/reports','/api/v1/dashboard','/api/v1/plans/xlsx/template'):
        assert path not in paths
    from app.task import eligibility
    monkeypatch.setattr(eligibility.TaskSettings, 'TASK_INTEGRATION_ENABLED', False, raising=False)
    import app.plan.api.routes as plan_api
    import app.performance.api.routes as perf_api
    def closed(): raise TaskError(eligibility.TaskErrorCode.FORBIDDEN, 403)
    monkeypatch.setattr(plan_api, 'get_profile', closed)
    monkeypatch.setattr(perf_api, 'get_profile', closed)
    async def no_db(): yield object()
    app.dependency_overrides[get_db]=no_db
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture') as client:
        for path in ('/api/v1/integration/plans/by-task/MISSING','/api/v1/integration/performances/by-task/MISSING'):
            res=await client.get(path)
            assert res.status_code == 403 and res.json()['errorCode'] == 'task.forbidden'


@pytest.mark.asyncio
async def test_synthetic_ab_service_flow_preserves_manual_values_and_task_attribution(monkeypatch):
    """In-memory service exercise only; real MySQL atomicity remains a runtime check."""
    from app.performance.services import async_workflow as perf
    from app.performance.schemas.workflow import Snapshot
    fields = [
        SimpleNamespace(scope='shared_sync', slot_no=1, name='productCode', value_type='string', enabled=True, performance_owner='order_snapshot', sync_enabled=False, is_nullable=False, plan_editable=True, performance_editable=False),
        SimpleNamespace(scope='shared_sync', slot_no=2, name='targetLength', value_type='number', enabled=True, performance_owner='order_snapshot', sync_enabled=False, is_nullable=False, plan_editable=True, performance_editable=False),
        SimpleNamespace(scope='shared_sync', slot_no=3, name='completedLength', value_type='number', enabled=True, performance_owner='automated', sync_enabled=True, is_nullable=False, plan_editable=False, performance_editable=False),
        SimpleNamespace(scope='performance_local', slot_no=1, name='currentSpeed', value_type='number', enabled=True, performance_owner='automated', sync_enabled=False, is_nullable=False, plan_editable=False, performance_editable=False),
        SimpleNamespace(scope='performance_local', slot_no=2, name='inspectionPassed', value_type='boolean', enabled=True, performance_owner='manual', sync_enabled=False, is_nullable=True, plan_editable=False, performance_editable=True),
    ]
    plan_rows={name: Plan(task_no=name,target_key='LINE-01',field_config_version=3,
                         production_status=None,sync_values={'01':product,'02':length},local_values={})
               for name,product,length in (('GT1-RUN-A','PRODUCT-A','1200'),('GT1-RUN-B','PRODUCT-B','800'))}
    class FakeDB:
        current = None
        def __init__(self): self.records={}
        async def execute(self, statement): return Result(self.records.get(self.current))
        def add(self, row): self.records[row.task_no]=row
        async def flush(self): pass
        async def refresh(self, row): pass
    db=FakeDB()
    monkeypatch.setattr(perf,'admit',lambda *args:None)
    monkeypatch.setattr(perf,'target_mapping',lambda *args:{'automatic':{'recordSource':'sma'}})
    monkeypatch.setattr(perf,'config_state',AsyncMock(return_value=SimpleNamespace(active_version=3)))
    monkeypatch.setattr(perf,'lock_plan',AsyncMock(side_effect=lambda db,task: plan_rows.get(task)))
    monkeypatch.setattr(perf,'definitions',AsyncMock(return_value=fields))
    monkeypatch.setattr(perf,'performance_wire',AsyncMock(return_value={'fixture': True}))
    def body(task,seq,status,length,speed,observed):
        return Snapshot.model_validate({'producerId':'sma-01','taskNo':task,'targetKey':'LINE-01','fieldConfigVersion':3,
            'productionStatus':status,'observationSeq':seq,'observedAt':observed,
            'syncValues':{'completedLength':length},'localValues':{'currentSpeed':speed}}).model_dump(exclude_unset=True)
    async def receive(payload):
        db.current=payload['taskNo']
        return await perf.receive_snapshot(db,payload)
    a12=body('GT1-RUN-A',12,'running',300,78.5,'2026-11-11T10:00:00+08:00')
    assert (await receive(a12))['outcome']=='created'
    assert plan_rows['GT1-RUN-A'].sync_values == {'01':'PRODUCT-A','02':'1200','03':'300'}
    db.current='GT1-RUN-A'
    await perf.edit_manual(db,{'taskNo':'GT1-RUN-A','fieldConfigVersion':3,'localValues':{'inspectionPassed':True}})
    assert (await receive(body('GT1-RUN-A',11,'running',250,70,'2026-11-11T09:59:59+08:00')))['outcome']=='late'
    assert (await receive(a12))['outcome']=='duplicate'
    with pytest.raises(TaskError) as error:
        await receive(body('GT1-RUN-A',12,'running',301,78.5,'2026-11-11T10:00:00+08:00'))
    assert error.value.key == 'task.observation_conflict'
    assert (await receive(body('GT1-RUN-B',1,'running',50,40,'2026-11-11T10:00:30+08:00')))['outcome']=='created'
    db.current='GT1-RUN-B'
    await perf.edit_manual(db,{'taskNo':'GT1-RUN-B','fieldConfigVersion':3,'localValues':{'inspectionPassed':False}})
    assert (await receive(body('GT1-RUN-A',13,'completed',1200,0,'2026-11-11T10:00:20+08:00')))['outcome']=='updated'
    assert db.records['GT1-RUN-A'].local_values == {'01':'0','02':'true'}
    assert db.records['GT1-RUN-B'].local_values == {'01':'40','02':'false'}
    assert plan_rows['GT1-RUN-A'].sync_values == {'01':'PRODUCT-A','02':'1200','03':'1200'}
    assert plan_rows['GT1-RUN-B'].sync_values == {'01':'PRODUCT-B','02':'800','03':'50'}
    assert (await receive(body('GT1-RUN-A',14,'completed',1201,0,'2026-11-11T10:00:40+08:00')))['outcome']=='already_completed'


@pytest.mark.asyncio
async def test_field_configuration_versions_display_overlay_and_stale_revision():
    """Exercises actual configuration service with an in-memory session substitute."""
    from app.task.services.async_fields import save_config, read_config
    class ScalarsResult:
        def __init__(self, rows): self.rows=rows
        def scalar_one_or_none(self): return self.rows[0] if self.rows else None
        def scalars(self): return iter(self.rows)
    class MemoryFields:
        def __init__(self):
            self.state=FieldConfigState(id=1,active_version=1,config_revision=1)
            self.rows=[]
        async def execute(self, statement):
            entity=statement.column_descriptions[0]['entity']
            if entity is FieldConfigState: return ScalarsResult([self.state])
            assert entity is FieldDefinition
            version=statement.compile().params.get('config_version_1')
            return ScalarsResult([row for row in self.rows if version is None or row.config_version==version])
        def add(self, row): self.rows.append(row)
        async def flush(self): pass
    examples=Path(__file__).resolve().parents[2]/'contracts/published/http-api/generic-task-workflow-v1/examples'
    db=MemoryFields()
    plan=json.loads((examples/'config-plan.json').read_text())
    result=await save_config(db,plan)
    assert (result['fieldConfigVersion'],result['configRevision']) == (2,'2') and len(result['fields'])==4
    perf=json.loads((examples/'config-performance.json').read_text())
    result=await save_config(db,perf)
    assert (result['fieldConfigVersion'],result['configRevision']) == (3,'3') and len(result['fields'])==5
    display={'module':'plan','fieldConfigVersion':3,'configRevision':'3',
             'changes':[{'scope':'shared_sync','slotNo':3,'labels':{'zh-CN':'新标签','en-US':'New label'}}]}
    assert (await save_config(db,display))['configRevision']=='4'
    assert db.state.active_version==3
    assert next(x for x in (await read_config(db,'performance',2))['fields'] if x['slotNo']==3 and x['scope']=='shared_sync')['labels']['en-US']=='New label'
    change={'module':'plan','fieldConfigVersion':3,'configRevision':'4','changes':[{'scope':'shared_sync','slotNo':3,'enabled':False}]}
    assert (await save_config(db,change))['fieldConfigVersion']==4
    old=await read_config(db,'performance',3); new=await read_config(db,'performance',4)
    assert next(x for x in old['fields'] if x['scope']=='shared_sync' and x['slotNo']==3)['enabled'] is True
    assert next(x for x in new['fields'] if x['scope']=='shared_sync' and x['slotNo']==3)['enabled'] is False
    with pytest.raises(TaskError) as exc: await save_config(db,change)
    assert exc.value.key=='task.config_revision_conflict'
    version_only={**change,'configRevision':'5'}
    with pytest.raises(TaskError) as exc: await save_config(db,version_only)
    assert exc.value.key=='task.field_version_conflict'
    stale={'module':'plan','fieldConfigVersion':4,'configRevision':'4','changes':[]}
    with pytest.raises(TaskError) as exc: await save_config(db,stale)
    assert exc.value.key=='task.config_revision_conflict'
    shared_name={'name':'commonNote','type':'string','labels':{'zh-CN':'备注','en-US':'Note'},'enabled':True}
    plan_local={'module':'plan','fieldConfigVersion':4,'configRevision':'5','changes':[
        {'scope':'plan_local','slotNo':2,**shared_name,'planEditable':True}]}
    assert (await save_config(db,plan_local))['fieldConfigVersion']==5
    perf_local={'module':'performance','fieldConfigVersion':5,'configRevision':'6','changes':[
        {'scope':'performance_local','slotNo':3,**shared_name,'performanceOwner':'manual','performanceEditable':True}]}
    assert (await save_config(db,perf_local))['fieldConfigVersion']==6


@pytest.mark.asyncio
async def test_field_config_permissions_and_closed_integration(monkeypatch):
    from core.deps import get_current_user
    from app.task.api import routes
    from app.task.errors import TaskErrorCode
    app=create_app(testing=True)
    async def no_db(): yield object()
    app.dependency_overrides[get_db]=no_db
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture') as client:
        missing=await client.get('/api/v1/task-field-configs?module=plan')
        assert missing.status_code==401 and missing.json()['errorCode']=='task.unauthenticated'
        actor=SimpleNamespace(id=7,role='operator')
        app.dependency_overrides[get_current_user]=lambda:actor
        app.state.role_api_permissions={'operator':(), 'supervisor':()}
        denied=await client.get('/api/v1/task-field-configs?module=plan',headers={'Authorization':'Bearer fixture'})
        assert denied.status_code==403 and denied.json()['errorCode']=='task.forbidden'
        app.state.role_api_permissions['operator']=('plan',)
        monkeypatch.setattr(routes,'read_config',AsyncMock(return_value={'fields':[]}))
        allowed=await client.get('/api/v1/task-field-configs?module=plan',headers={'Authorization':'Bearer fixture'})
        assert allowed.status_code==200 and allowed.json()['data']=={'fields':[]}
        denied=await client.put('/api/v1/task-field-configs',headers={'Authorization':'Bearer fixture'},json={'module':'plan','fieldConfigVersion':1,'configRevision':'1','changes':[]})
        assert denied.status_code==403 and denied.json()['errorCode']=='task.forbidden'
        def closed(): raise TaskError(TaskErrorCode.FORBIDDEN,403)
        monkeypatch.setattr(routes,'get_profile',closed)
        denied=await client.get('/api/v1/integration/task-field-configs?module=plan')
        assert denied.status_code==403 and denied.json()['errorCode']=='task.forbidden'


def test_tracking_log_is_bounded_and_failure_cannot_change_result(monkeypatch):
    from app.task import http
    seen=[]
    monkeypatch.setattr(http,'log_event',lambda *args, **kwargs: seen.append(kwargs))
    http.audit_event('event',task_no='GT1-RUN-A',producer_id='mes-01',event_id='event-1',outcome='created')
    assert seen[0]['event_id']=='event-1' and len(seen[0]['event_id_sha256'])==64
    http.audit_event('event',event_id='x'*500)
    assert 'event_id' not in seen[1] and len(seen[1]['event_id_sha256'])==64
    def broken(*args,**kwargs): raise RuntimeError('logging unavailable')
    monkeypatch.setattr(http,'log_event',broken)
    assert http.audit_event('event',event_id='event-1') is None


@pytest.mark.asyncio
@pytest.mark.parametrize('mutation,expected',[(False,'task.unavailable'),(True,'task.commit_unknown')])
async def test_task_route_waits_for_dependency_exit_before_success(monkeypatch,mutation,expected):
    from core.deps import get_current_user
    from app.task.api import routes
    app=create_app(testing=True)
    app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(role='admin',id=7)
    async def exiting():
        yield object()
        raise RuntimeError('synthetic cleanup failure')
    app.dependency_overrides[get_db]=exiting
    monkeypatch.setattr(routes,'read_config',AsyncMock(return_value={'fields':[]}))
    monkeypatch.setattr(routes,'save_config',AsyncMock(return_value={'fieldConfigVersion':1,'configRevision':'1'}))
    monkeypatch.setattr(routes,'commit',AsyncMock())
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture') as client:
        if mutation:
            res=await client.put('/api/v1/task-field-configs',json={'module':'plan','fieldConfigVersion':1,'configRevision':'1','changes':[]})
        else:
            res=await client.get('/api/v1/task-field-configs?module=plan')
    assert res.status_code==503 and res.json()['errorCode']==expected
    assert 'synthetic' not in res.text


@pytest.mark.asyncio
async def test_action_rejects_inapplicable_fields_before_locking():
    payload={'actionRequestId':'12345678-1234-4234-8234-123456789abc',
             'reason':'cancel', 'syncValues':{'completedLength':123}}
    with pytest.raises(TaskError) as exc:
        await plans.action(SimpleNamespace(), 7, 'cancel', payload, 2)
    assert exc.value.key=='task.invalid_request' and exc.value.status==422


@pytest.mark.asyncio
async def test_conflicting_plc_sequences_are_dispatch_conflict(monkeypatch):
    attempt=SimpleNamespace(task_no='GT1-A',target_key='LINE-01',producer_id='ff-01',
                            attempt_no=1,field_config_version=3,attempt_status='claimed')
    monkeypatch.setattr(plans,'lock_plan',AsyncMock(return_value=object()))
    monkeypatch.setattr(plans,'target_mapping',lambda *args:{'plcSeqMax':65535})
    db=SimpleNamespace(execute=AsyncMock(side_effect=[Result(attempt),Result(attempt)]))
    body={'dispatchId':'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','taskNo':'GT1-A',
          'targetKey':'LINE-01','producerId':'ff-01','outcome':'plc_accepted',
          'requestSeq':41,'ackSeq':42,'ackObservedAt':datetime.fromisoformat('2026-11-11T10:00:00+08:00')}
    with pytest.raises(TaskError) as exc: await plans.report(db,body)
    assert exc.value.key=='task.dispatch_conflict' and exc.value.status==409


@pytest.mark.asyncio
async def test_commit_unknown_survives_failed_rollback_and_dependency_cleanup(monkeypatch):
    from app.task.http import commit
    from core.deps import get_current_user
    from app.task.api import routes
    from app.task.errors import TaskErrorCode
    db=SimpleNamespace(commit=AsyncMock(side_effect=RuntimeError('commit failed')),
                       rollback=AsyncMock(side_effect=RuntimeError('rollback failed')))
    with pytest.raises(TaskError) as exc: await commit(db)
    assert exc.value.key=='task.commit_unknown' and exc.value.status==503
    app=create_app(testing=True)
    app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(role='admin',id=7)
    async def exiting():
        try: yield object()
        finally: raise RuntimeError('cleanup failed')
    app.dependency_overrides[get_db]=exiting
    monkeypatch.setattr(routes,'save_config',AsyncMock(return_value={'fieldConfigVersion':1,'configRevision':'1'}))
    monkeypatch.setattr(routes,'commit',AsyncMock(side_effect=TaskError(TaskErrorCode.COMMIT_UNKNOWN,503)))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture') as client:
        res=await client.put('/api/v1/task-field-configs',json={'module':'plan','fieldConfigVersion':1,'configRevision':'1','changes':[]})
    assert res.status_code==503 and res.json()['errorCode']=='task.commit_unknown'
    assert 'failed' not in res.text


@pytest.mark.asyncio
async def test_locked_configuration_reads_use_current_rows_after_serialization():
    from app.task.services.async_fields import definitions
    class QueryResult:
        def __init__(self, rows): self.rows=rows
        def scalar_one_or_none(self): return self.rows[0] if self.rows else None
        def scalars(self): return iter(self.rows)
    class Capture:
        def __init__(self): self.statements=[]
        async def execute(self, statement):
            self.statements.append(statement)
            entity=statement.column_descriptions[0]['entity']
            return QueryResult([SimpleNamespace(active_version=2)] if entity is FieldConfigState else [])
    db=Capture()
    await definitions(db,1,overlay=True,current=True)
    assert len(db.statements)==3
    assert all(statement._for_update_arg is not None for statement in db.statements)
    from sqlalchemy.dialects.mysql import dialect
    assert all(str(statement.compile(dialect=dialect())).endswith('FOR UPDATE') for statement in db.statements)
