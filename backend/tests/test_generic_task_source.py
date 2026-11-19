"""ARCH-TASK-001 的无数据库合同、纯规则和并发重试源码自检。"""
import importlib.util
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
from app.performance.schemas.workflow import PerformanceUpsert
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


@pytest.mark.parametrize('field_name', ['observedAt', 'startedAt', 'completedAt'])
def test_all_task_body_times_require_an_offset_and_at_most_six_fractional_digits(field_name):
    model, body = PerformanceUpsert, {'taskNo': 'X'}
    for value in ('1794381599', 1794381599, '2026-11-11T10:00:00',
                  '2026-11-11T10:00:00.1234567+08:00', '2026-11-11T10:00:00+08:60'):
        with pytest.raises(ValidationError):
            model.model_validate({**body,field_name:value})
    local=model.model_validate({**body,field_name:'2026-11-11T10:00:00.123456+08:00'})
    utc=model.model_validate({**body,field_name:'2026-11-11T02:00:00.123456Z'})
    assert getattr(local,field_name)==getattr(utc,field_name)
    assert local_time(getattr(local,field_name))==datetime(2026,11,11,10,0,0,123456)


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
    monkeypatch.setattr(routes,'save_config',AsyncMock(return_value={'configVersion':1,'configRevision':'1'}))
    monkeypatch.setattr(routes,'commit',AsyncMock())
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture') as client:
        if mutation:
            res=await client.put('/api/v1/task-field-configs',json={'module':'plan','configRevision':'1','changes':[]})
        else:
            res=await client.get('/api/v1/task-field-configs?module=plan')
    assert res.status_code==503 and res.json()['errorCode']==expected
    assert 'synthetic' not in res.text


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
    monkeypatch.setattr(routes,'save_config',AsyncMock(return_value={'configVersion':1,'configRevision':'1'}))
    monkeypatch.setattr(routes,'commit',AsyncMock(side_effect=TaskError(TaskErrorCode.COMMIT_UNKNOWN,503)))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://fixture') as client:
        res=await client.put('/api/v1/task-field-configs',json={'module':'plan','configRevision':'1','changes':[]})
    assert res.status_code==503 and res.json()['errorCode']=='task.commit_unknown'
    assert 'failed' not in res.text
