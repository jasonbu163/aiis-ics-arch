"""ARCH-TASK-001 部分写入、配置和 HTTP 数据事务，在进程内 SQLite 验证。"""
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI, HTTPException
import httpx
import pytest
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from app.performance.api.routes import router as performance_router
from app.performance.models import Performance
from app.performance.services import async_workflow as performance_service
from app.plan.api.routes import router as plan_router
from app.plan.models import Plan
from app.plan.services import async_workflow as plan_service
from app.task.api.routes import router as field_router
from app.task.models import FieldConfigState, FieldConfigUse, FieldConfigVersion, FieldDefinition
from core.deps import get_current_user
from database import get_db

pytestmark = pytest.mark.no_db
PLAN = '/integration/plans'
PERF = '/integration/performances'
CONFIG = '/task-field-configs'


class Transactions:
    def __init__(self, session):
        self.session = session

    def add(self, row):
        self.session.add(row)

    def add_all(self, rows):
        self.session.add_all(rows)

    async def execute(self, statement):
        return self.session.execute(statement)

    async def get(self, model, key, **options):
        return self.session.get(model, key, **options)

    async def flush(self):
        self.session.flush()

    async def commit(self):
        self.session.commit()

    async def rollback(self):
        self.session.rollback()


@pytest.fixture
async def client():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False})
    statements = (
        'CREATE TABLE task_field_config_state (id INTEGER PRIMARY KEY, active_version INTEGER NOT NULL, config_revision INTEGER NOT NULL, created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL)',
        'CREATE TABLE plan_dispatch_attempts (dispatch_id TEXT PRIMARY KEY, field_config_version INTEGER NOT NULL)',
        'CREATE TABLE task_field_config_versions (config_version INTEGER PRIMARY KEY, definition_count INTEGER NOT NULL)',
        'CREATE TABLE task_field_config_uses (config_version INTEGER NOT NULL, subject_kind TEXT NOT NULL, subject_key TEXT NOT NULL, PRIMARY KEY (config_version, subject_kind, subject_key), FOREIGN KEY (config_version) REFERENCES task_field_config_versions (config_version))',
        '''CREATE TABLE task_field_definitions (
             id INTEGER PRIMARY KEY, config_version INTEGER NOT NULL, scope TEXT NOT NULL, slot_no INTEGER NOT NULL, name TEXT NOT NULL,
             value_type TEXT NOT NULL, label_zh_cn TEXT NOT NULL, label_en_us TEXT NOT NULL, unit TEXT,
             is_nullable BOOLEAN NOT NULL, enabled BOOLEAN NOT NULL, sync_enabled BOOLEAN NOT NULL,
             plan_editable BOOLEAN NOT NULL, performance_editable BOOLEAN NOT NULL, performance_owner TEXT,
             plan_visible BOOLEAN NOT NULL, performance_visible BOOLEAN NOT NULL, plan_order INTEGER, performance_order INTEGER,
             created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL,
             UNIQUE(config_version, scope, slot_no), UNIQUE(config_version, scope, name))''',
        '''CREATE TABLE plan_main (
             id INTEGER PRIMARY KEY, task_no TEXT NOT NULL UNIQUE, target_key TEXT, field_config_version INTEGER NOT NULL,
             remark TEXT, created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL, production_status TEXT NOT NULL,
             priority INTEGER NOT NULL, dispatch_status TEXT NOT NULL, local_values JSON NOT NULL, sync_values JSON NOT NULL)''',
        '''CREATE TABLE performance_main (
             id INTEGER PRIMARY KEY, task_no TEXT NOT NULL UNIQUE, target_key TEXT, field_config_version INTEGER NOT NULL, remark TEXT,
             created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL, production_status TEXT NOT NULL, started_at DATETIME,
             completed_at DATETIME, last_observed_at DATETIME, observation_seq INTEGER, observation_digest BLOB, record_source TEXT,
             local_values JSON NOT NULL, sync_values JSON NOT NULL)''',
    )
    with engine.begin() as connection:
        connection.exec_driver_sql('PRAGMA foreign_keys=ON')
        for ddl in statements:
            connection.exec_driver_sql(ddl)
    with Session(engine, expire_on_commit=False, autoflush=False) as session:
        now = datetime(2026, 11, 18, 10)
        session.add(FieldConfigState(id=1, active_version=1, config_revision=1, created_at=now, updated_at=now))
        session.add(FieldConfigVersion(config_version=1, definition_count=0))
        session.commit()

        async def sqlite_session():
            adapter = Transactions(session)
            try:
                yield adapter
                await adapter.commit()
            except Exception:
                await adapter.rollback()
                raise

        def user():
            return SimpleNamespace(id=7, role=identity.role)

        identity = SimpleNamespace(role='admin')
        app = FastAPI()
        for router in (field_router, plan_router, performance_router):
            app.include_router(router)
        app.state.role_api_permissions = {'supervisor': ('plan', 'performance'), 'operator': ('performance',)}
        app.dependency_overrides[get_current_user] = user
        app.dependency_overrides[get_db] = sqlite_session
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://fixture') as http:
            yield http, session, identity, app
    engine.dispose()


def field(scope, slot, name, kind='string', **options):
    return {'scope': scope, 'slotNo': slot, 'name': name, 'type': kind, 'enabled': True,
            'labels': {'zh-CN': name, 'en-US': name}, **options}


async def configure(http, module, *changes):
    current = data(await http.get(CONFIG, params={'module': 'plan' if module == 'shared' else module}))
    return data(await http.put(CONFIG, json={'module': module, 'configRevision': current['configRevision'], 'changes': changes}))


def data(response):
    assert response.status_code == 200, response.text
    assert set(response.json()) == {'code', 'message', 'data', 'timestamp'}
    return response.json()['data']


def rejection(response, status, code, field=None, reason=None):
    assert response.status_code == status, response.text
    body = response.json()
    assert body['errorCode'] == 'task.' + code and body['data'] is None
    if field is not None:
        assert body['details']['field'] == field
    if reason is not None:
        assert body['details']['reason'] == reason


async def put(http, route, number, **body):
    return data(await http.post(route + '/upsert', json={'taskNo': number, **body}))


async def get(http, route, number):
    return data(await http.get(route + '/by-task/' + number))


async def fields(http):
    await configure(http, 'shared',
                    field('shared_sync', 1, 'product', performanceOwner='order_snapshot', planEditable=True),
                    field('shared_sync', 2, 'length', 'number', performanceOwner='automated',
                          planEditable=True, syncEnabled=True, isNullable=True),
                    field('shared_sync', 3, 'checked', 'boolean', performanceOwner='manual',
                          performanceEditable=True, syncEnabled=True, isNullable=True))
    await configure(http, 'plan', field('plan_local', 1, 'local', planEditable=True))
    await configure(http, 'performance', field('performance_local', 1, 'local', 'number', performanceOwner='automated'))


async def test_equivalent_raw_zero_keeps_plan_performance_and_sync_timestamps(client):
    http, session, _, _ = client
    await configure(http, 'shared',
                    field('shared_sync', 1, 'amount', 'number', performanceOwner='automated',
                          planEditable=True, syncEnabled=True),
                    field('shared_sync', 2, 'reference', performanceOwner='order_snapshot', planEditable=True))
    headers = {'Content-Type': 'application/json'}
    observation = b',"observedAt":"2026-11-18T02:01:02.123456Z"'

    async def post_raw(path, amount, extra=b''):
        raw = b'{"taskNo":"EQUAL-ZERO","items":{"amount":' + amount + b'}' + extra + b'}'
        return await http.post(path + '/upsert', headers=headers, content=raw)

    await put(http, PLAN, 'EQUAL-ZERO', productionStatus='running', items={'amount': 0, 'reference': '-0'})
    data(await post_raw(PERF, b'0', observation))
    initial_plan = await get(http, PLAN, 'EQUAL-ZERO')
    initial_performance = await get(http, PERF, 'EQUAL-ZERO')
    assert initial_plan['items'] == initial_performance['items'] == {'amount': 0, 'reference': '-0'}
    assert initial_performance['lastObservedAt'] == '2026-11-18T10:01:02.123456+08:00'

    for token in (b'0', b'-0', b'-0.0', b'0.0000', b'-0e-400'):
        plan = data(await post_raw(PLAN, token))
        assert plan['outcome'] == 'unchanged' and plan['plan'] == initial_plan
        performance = data(await post_raw(PERF, token, observation))
        assert performance['outcome'] == 'unchanged' and performance['performance'] == initial_performance
        assert performance['planSync'] == {'outcome': 'unchanged', 'reason': None, 'statusChanged': False, 'fieldsChanged': []}
        assert await get(http, PLAN, 'EQUAL-ZERO') == initial_plan
        assert await get(http, PERF, 'EQUAL-ZERO') == initial_performance

    for model in (Plan, Performance):
        record = session.scalar(select(model).where(model.task_no == 'EQUAL-ZERO'))
        assert record.sync_values == {'01': '0', '02': '-0'}
    for token in (b'"0"', b'"-0"'):
        rejection(await post_raw(PLAN, token), 422, 'invalid_request', 'items.amount', 'type_mismatch')
        rejection(await post_raw(PERF, token, observation), 422, 'invalid_request', 'items.amount', 'type_mismatch')
        assert await get(http, PLAN, 'EQUAL-ZERO') == initial_plan
        assert await get(http, PERF, 'EQUAL-ZERO') == initial_performance

    divergent = (await put(http, PLAN, 'EQUAL-ZERO', items={'amount': 7}))['plan']
    repaired = data(await post_raw(PERF, b'-0.0', observation))
    assert repaired['outcome'] == 'unchanged' and repaired['performance'] == initial_performance
    assert repaired['planSync']['outcome'] == 'synced' and repaired['planSync']['fieldsChanged'] == ['amount']
    aligned_plan = await get(http, PLAN, 'EQUAL-ZERO')
    assert aligned_plan['items']['amount'] == 0 and aligned_plan['updatedAt'] != divergent['updatedAt']

    plan_at, perf_at = aligned_plan['updatedAt'], initial_performance['updatedAt']
    for token, expected in ((b'1.25', 1.25), (b'-1.25', -1.25)):
        result = data(await post_raw(PERF, token, observation))
        assert result['outcome'] == 'updated'
        assert result['planSync']['fieldsChanged'] == ['amount'] and result['planSync']['outcome'] == 'synced'
        plan = await get(http, PLAN, 'EQUAL-ZERO')
        perf = await get(http, PERF, 'EQUAL-ZERO')
        assert plan['items']['amount'] == perf['items']['amount'] == expected
        assert perf['lastObservedAt'] == initial_performance['lastObservedAt']
        assert plan['updatedAt'] != plan_at and perf['updatedAt'] != perf_at
        plan_at, perf_at = plan['updatedAt'], perf['updatedAt']

    changed_text = await put(http, PLAN, 'EQUAL-ZERO', items={'reference': '0'})
    assert changed_text['outcome'] == 'updated' and changed_text['plan']['items']['reference'] == '0'
    assert (await get(http, PERF, 'EQUAL-ZERO'))['items']['reference'] == '-0'


@pytest.mark.parametrize(('endpoint', 'route', 'owner'), [
    (PLAN + '/upsert', PLAN, 'automated'),
    ('/plans/upsert', PLAN, 'automated'),
    (PERF + '/upsert', PERF, 'automated'),
    ('/performances/upsert', PERF, 'manual'),
])
async def test_raw_http_numbers_preserve_decimal_bounds_and_atomicity(client, endpoint, route, owner):
    http, session, _, _ = client
    await configure(http, 'shared', *(
        field('shared_sync', slot, name, kind, performanceOwner=owner,
              performanceEditable=owner == 'manual', planEditable=True, isNullable=True)
        for slot, (name, kind) in enumerate((('amount', 'number'), ('flag', 'boolean'), ('text', 'string')), 1)
    ))
    await put(http, route, 'PRECISION', remark='retained')
    key, model = ('plan', Plan) if route == PLAN else ('performance', Performance)
    headers = {'Content-Type': 'application/json'}

    async def post_number(token):
        return await http.post(endpoint, headers=headers, content=(
            b'{"taskNo":"PRECISION","remark":"mixed","items":{"flag":false,"text":"0007","amount":' + token + b'}}'
        ))

    before = await get(http, route, 'PRECISION')
    for invalid in (b'9999999999.0001001', b'1e-400', b'10000000000', b'-10000000000',
                    b'1000000000000000000000000000000000', b'1e1000000000',
                    b'1e-1000000000', b'1e9999999999999999999999999999', b'-1e-9999999999999999999999999999', b'1' + b'0' * 5000):
        rejection(await post_number(invalid), 422, 'invalid_request', 'items.amount', 'number_out_of_range')
        assert await get(http, route, 'PRECISION') == before
    for invalid_type in (b'true', b'"0.0001"'):
        rejection(await post_number(invalid_type), 422, 'invalid_request', 'items.amount', 'type_mismatch')
        assert await get(http, route, 'PRECISION') == before

    bad_json = await http.post(endpoint, headers=headers, content=b'{"taskNo":"PRECISION","items":{"amount":1e}}')
    rejection(bad_json, 422, 'invalid_request', reason='json_invalid')
    assert await get(http, route, 'PRECISION') == before

    for token, expected in ((b'9999999999.9999', Decimal('9999999999.9999')),
                            (b'-9999999999.9999', Decimal('-9999999999.9999')),
                            (b'1e-4', Decimal('0.0001')), (b'1200.00e-3', Decimal('1.2')),
                            (b'9999999999', 9999999999), (b'0', 0), (b'null', None)):
        result = await post_number(token)
        data(result)
        result = json.loads(result.content, parse_float=Decimal)['data'][key]
        assert result['items'] == {'amount': expected, 'flag': False, 'text': '0007'}
        assert type(result['items']['amount']) is type(expected)
        stored = session.scalar(select(model).where(model.task_no == 'PRECISION'))
        assert stored.sync_values.get('01') == (None if expected is None else str(expected))


async def test_raw_task_upserts_preserve_authentication_and_strict_metadata(client):
    http, _, identity, app = client
    await put(http, PLAN, 'GUARDED', remark='original')
    await put(http, PERF, 'GUARDED', remark='original')
    before = [await get(http, route, 'GUARDED') for route in (PLAN, PERF)]
    headers = {'Content-Type': 'application/json'}
    payload = b'{"taskNo":"GUARDED","remark":"mixed","items":{"amount":1e-400}}'

    identity.role = 'operator'
    rejection(await http.post('/plans/upsert', content=payload, headers=headers), 403, 'forbidden')

    def unauthenticated():
        raise HTTPException(status_code=401)

    app.dependency_overrides[get_current_user] = unauthenticated
    for path in ('/plans/upsert', '/performances/upsert'):
        rejection(await http.post(path, content=payload, headers=headers), 401, 'unauthenticated')
    for route in (PLAN, PERF):
        numeric_metadata = b'{"taskNo":"GUARDED","remark":"mixed","fieldConfigVersion":1e0}'
        rejection(await http.post(route + '/upsert', content=numeric_metadata, headers=headers),
                  422, 'invalid_request', 'fieldConfigVersion')
    assert [await get(http, route, 'GUARDED') for route in (PLAN, PERF)] == before


@pytest.mark.parametrize(('timestamp', 'expected'), [
    ('1990-07-01T00:00:00Z', '1990-07-01T08:00:00+08:00'),
    ('1990-01-01T00:00:00Z', '1990-01-01T08:00:00+08:00'),
    ('2026-07-01T00:00:00Z', '2026-07-01T08:00:00+08:00'),
    ('1990-06-30T20:30:00.123456-04:00', '1990-07-01T08:30:00.123456+08:00'),
    ('0999-12-31T16:00:00.000001Z', '1000-01-01T00:00:00.000001+08:00'),
])
async def test_business_times_use_fixed_utc_plus_eight(client, timestamp, expected):
    http, session, _, _ = client
    payload = dict.fromkeys(('observedAt', 'startedAt', 'completedAt'), timestamp)
    await put(http, PERF, 'FIXED-TIME', **payload)
    stored = session.scalar(select(Performance).where(Performance.task_no == 'FIXED-TIME'))
    wall_time = datetime.fromisoformat(expected).replace(tzinfo=None)
    assert (stored.last_observed_at, stored.started_at, stored.completed_at) == (wall_time,) * 3
    record = await get(http, PERF, 'FIXED-TIME')
    for field in ('lastObservedAt', 'startedAt', 'completedAt'):
        assert record[field] == expected


async def test_business_date_filters_use_the_same_fixed_offset(client, monkeypatch):
    http, _, _, _ = client
    wall_time = datetime(1990, 7, 1, 8, 0, 0, 123456)
    monkeypatch.setattr(plan_service, 'business_now', lambda: wall_time)
    monkeypatch.setattr(performance_service, 'business_now', lambda: wall_time)
    for route, listing in ((PLAN, '/plans'), (PERF, '/performances')):
        await put(http, route, 'DATE-FILTER', productionStatus='running')
        record = await get(http, route, 'DATE-FILTER')
        assert record['createdAt'] == '1990-07-01T08:00:00.123456+08:00'
        for instant in ('1990-07-01T00:00:00.123456Z', '1990-06-30T20:00:00.123456-04:00',
                        '1990-07-01T08:00:00.123456+08:00'):
            assert data(await http.get(listing, params={'createdFrom': instant}))['total'] == 1
            assert data(await http.get(listing, params={'createdTo': instant}))['total'] == 0
        assert data(await http.get(listing, params={'createdTo': '1990-07-01T00:00:00.123457Z'}))['total'] == 1
        rejection(await http.get(listing, params={'createdFrom': '0999-12-31T15:59:59.999999Z'}),
                  422, 'invalid_request', 'createdFrom', 'time_out_of_range')


async def test_partial_writes_current_configuration_and_independent_times(client):
    http, session, _, _ = client
    await fields(http)
    initial = await put(http, PLAN, ' job-7 ', targetKey='Demo', items={'product': '', 'length': 12, 'local': '0007'})
    assert initial['plan']['taskNo'] == 'JOB-7' and initial['plan']['productionStatus'] == 'new'
    assert initial['plan']['items'] == {'product': '', 'length': 12, 'local': '0007', 'checked': None}
    report = await put(http, PERF, 'job-7', fieldConfigVersion=936, observedAt='2026-11-18T02:01:02.012345Z',
                       observationSeq=9, items={'length': 0, 'local': 8})
    assert report['performance']['lastObservedAt'] == '2026-11-18T10:01:02.012345+08:00'
    assert report['performance']['targetKey'] == 'Demo'
    assert report['performance']['items'] == {'product': '', 'length': 0, 'local': 8, 'checked': None}
    assert report['planSync'] == {'outcome':'synced', 'reason':None, 'statusChanged':True, 'fieldsChanged':['length']}
    first = await get(http, PLAN, 'job-7')
    assert first['items']['local'] == '0007' and first['items']['length'] == 0
    await put(http, PLAN, 'job-7', productionStatus='error', items={'product': 'NEW', 'length': 5})
    now = await put(http, PERF, 'job-7', items={}, observationSeq=9)
    assert now['outcome'] == 'unchanged' and now['performance']['updatedAt'] == report['performance']['updatedAt']
    assert now['planSync']['statusChanged'] and not now['planSync']['fieldsChanged']
    assert now['performance']['items']['product'] == ''
    assert (await get(http, PLAN, 'job-7'))['items']['length'] == 5
    report = await put(http, PERF, 'job-7', items={'length': 0}, observationSeq=1)
    assert report['outcome'] == 'updated' and report['performance']['lastObservedAt'] is None
    assert report['planSync']['fieldsChanged'] == ['length']
    await put(http, PLAN, 'job-7', items={'length': 20})
    identical = await put(http, PERF, 'job-7', items={'length': 0})
    assert identical['outcome'] == 'unchanged' and identical['planSync']['outcome'] == 'synced'
    complete = await put(http, PERF, 'job-7', productionStatus='completed', completedAt='2026-11-18T04:00:00Z')
    resumed = await put(http, PERF, 'job-7', productionStatus='running', observationSeq=None)
    assert resumed['performance']['completedAt'] == complete['performance']['completedAt']
    assert (await get(http, PLAN, 'job-7'))['productionStatus'] == 'running'
    manual = await put(http, '/performances', 'job-7', items={'checked': False})
    assert manual['performance']['items']['checked'] is False
    assert (await get(http, PLAN, 'job-7'))['items']['checked'] is False
    await put(http, '/performances', 'job-7', items={'checked': None})
    assert (await get(http, PLAN, 'job-7'))['items']['checked'] is None
    assert session.scalar(select(func.count()).select_from(Plan)) == 1
    assert session.scalar(select(func.count()).select_from(Performance)) == 1


async def test_backfill_versions_targets_errors_and_pagination(client):
    http, session, _, _ = client
    await fields(http)
    for number in ('A', 'B', 'C'):
        result = await put(http, PERF, number, targetKey='Demo', producerId=None, items={'length': 40})
        assert not result['performance']['hasPlan'] and result['planSync']['reason'] == 'no_plan'
    default = await put(http, PLAN, 'A')
    assert default['plan']['productionStatus'] == 'running'
    assert default['plan']['targetKey'] is None and default['plan']['items']['length'] is None
    priority = await put(http, PLAN, 'B', backfillExisting=True, productionStatus='new', items={'length': 20})
    assert priority['plan']['items']['length'] == 20 and priority['plan']['productionStatus'] == 'new'
    copied = await put(http, PLAN, 'C', backfillExisting=True)
    assert copied['plan']['items']['length'] == 40
    assert (await get(http, PERF, 'C'))['items']['product'] is None
    rejection(await http.post(PLAN+'/upsert', json={'taskNo':'Z','backfillExisting':True}),
              422,'invalid_request','backfillExisting')
    rejection(await http.post(PERF+'/upsert', json={'taskNo':'B','targetKey':'demo','items':{'length':5}}),
              409,'target_conflict','targetKey')
    rejection(await http.post(PERF+'/upsert', json={'taskNo':'B', 'items':{'length':'5','local':4}}),
              422,'invalid_request','items.length','type_mismatch')
    rejection(await http.post(PERF+'/upsert', json={'taskNo':'B', 'items':{'product':'no'}}),
              403,'forbidden','items.product','field_owner')
    rejection(await http.post(PLAN+'/upsert', json={'taskNo':'B', 'items':{'product':None}}),
              422,'invalid_request','items.product','null_not_allowed')
    assert (await get(http, PERF, 'B'))['items']['local'] is None
    page = data(await http.get(PLAN, params={'productionStatus':'new','pageSize':1}))
    assert [row['taskNo'] for row in page['items']] == ['B']
    assert page['total'] == page['totalPages'] == 1
    empty = data(await http.get(PLAN, params={'targetKey':'Demo','page':2}))
    assert empty == {'items':[], 'page':2, 'pageSize':20, 'total':0, 'totalPages':0}
    assert [r['taskNo'] for r in data(await http.get(PLAN, params={'sortOrder':'asc'}))['items']] == ['A','B','C']
    assert (await get(http, PERF, 'B'))['hasPlan']
    await configure(http,'shared', field('shared_sync',4,'after','boolean',performanceOwner='order_snapshot'))
    assert (await get(http, PLAN, 'A'))['items']['after'] is None
    await configure(http,'shared', {'scope':'shared_sync','slotNo':2,'enabled':False})
    assert 'length' not in (await get(http, PERF, 'A'))['items']
    rejection(await http.post(PERF+'/upsert', json={'taskNo':'A','items':{'length':0}}),
              422,'invalid_request','items.length','disabled_field')
    assert session.scalar(select(Performance.sync_values).where(Performance.task_no=='A'))['02'] == '40'
    await configure(http,'shared', {'scope':'shared_sync','slotNo':2,'enabled':True})
    assert (await get(http, PERF, 'A'))['items']['length'] == 40


async def test_real_rollback_after_performance_flush_preserves_both_rows_and_evidence(client, monkeypatch):
    http, session, _, _ = client
    await put(http, PLAN, 'R')
    await put(http, PERF, 'R', productionStatus='new', remark='before')
    await configure(http, 'performance', field('performance_local', 2, 'feedback', performanceOwner='automated'))
    plan_before, perf_before = await get(http, PLAN, 'R'), await get(http, PERF, 'R')
    evidence_before = session.scalar(select(func.count()).select_from(FieldConfigUse))

    async def fail(db, plan, *args, **options):
        assert (await db.execute(select(Performance.remark))).scalar_one() == 'pending'
        plan.production_status = 'error'
        await db.flush()
        raise RuntimeError('fixture failure')

    monkeypatch.setattr(performance_service,'sync_plan',fail)
    rejection(await http.post(PERF+'/upsert', json={'taskNo':'R','remark':'pending','items':{'feedback':'x'}}),
              503,'unavailable')
    assert await get(http, PLAN, 'R') == plan_before
    assert await get(http, PERF, 'R') == perf_before
    assert session.scalar(select(func.count()).select_from(FieldConfigUse)) == evidence_before


async def test_scoped_configuration_delete_uses_history_and_get_creates_no_evidence(client):
    http, session, _, _ = client
    await put(http, PLAN, 'H')
    shared = await configure(http, 'shared', field('shared_sync',1,'unused',performanceOwner='order_snapshot'))
    await get(http, PLAN, 'H')
    rejection(await http.post(CONFIG+'/delete', json={'scope':'shared_sync','slotNo':1,'name':'unused','configRevision':'1'}),
              409,'config_revision_conflict')
    result = data(await http.post(CONFIG+'/delete', json={'scope':'shared_sync','slotNo':1,'name':'unused',
                                                          'configRevision':shared['configRevision']}))
    assert result['outcome'] == 'deleted'
    await configure(http,'shared',field('shared_sync',1,'newKey',performanceOwner='order_snapshot',enabled=False))
    same = await put(http, PLAN, 'H')
    assert same['outcome'] == 'unchanged'
    current = data(await http.get(CONFIG, params={'module':'plan'}))
    rejection(await http.post(CONFIG+'/delete', json={'scope':'shared_sync','slotNo':1,'name':'newKey','configRevision':current['configRevision']}),
              409,'field_in_use')
    local = await configure(http,'performance',field('performance_local',1,'mine',performanceOwner='automated'))
    await put(http, PLAN, 'H', productionStatus='error')
    data(await http.post(CONFIG+'/delete', json={'scope':'performance_local','slotNo':1,'name':'mine',
                                                 'configRevision':local['configRevision']}))
    unused = await configure(http,'plan',field('plan_local',1,'frozen'))
    session.add(FieldConfigUse(config_version=unused['configVersion'], subject_kind='dispatch', subject_key='fixture'))
    session.commit()
    rejection(await http.post(CONFIG+'/delete', json={'scope':'plan_local','slotNo':1,'name':'frozen',
                                                      'configRevision':unused['configRevision']}),409,'field_in_use')
    session.query(FieldConfigVersion).filter_by(config_version=2).delete()
    session.commit()
    rejection(await http.post(CONFIG+'/delete', json={'scope':'plan_local','slotNo':1,'name':'frozen',
                                                      'configRevision':unused['configRevision']}),409,'field_in_use')


@pytest.mark.parametrize(('scope', 'module', 'route', 'subject', 'items'), [
    ('shared_sync', 'shared', PLAN, 'plan', {'guarded': 'retained'}),
    ('shared_sync', 'shared', PERF, 'performance', {}),
    ('plan_local', 'plan', PLAN, 'plan', {}),
    ('performance_local', 'performance', PERF, 'performance', {'guarded': 'retained'}),
])
async def test_delete_rejects_missing_bound_task_usage(client, scope, module, route, subject, items):
    http, session, _, _ = client
    options = {} if module == 'plan' else {'performanceOwner': 'automated'}
    cfg = await configure(http, module, field(scope, 1, 'guarded', **options))
    await put(http, route, 'HISTORY', items=items)
    row = await get(http, route, 'HISTORY')
    session.query(FieldConfigUse).filter_by(subject_kind=subject, subject_key='HISTORY').delete()
    session.commit()
    payload = {'scope': scope, 'slotNo': 1, 'name': 'guarded', 'configRevision': cfg['configRevision']}
    rejection(await http.post(CONFIG+'/delete', json=payload), 409, 'field_in_use')
    assert await get(http, route, 'HISTORY') == row
    assert (await http.get(CONFIG, params={'module': subject})).json()['data']['configRevision'] == cfg['configRevision']


@pytest.mark.parametrize(('scope', 'module'), [
    ('shared_sync', 'shared'), ('plan_local', 'plan'), ('performance_local', 'performance'),
])
async def test_delete_rejects_missing_historical_dispatch_usage(client, scope, module):
    http, session, _, _ = client
    options = {} if module == 'plan' else {'performanceOwner': 'automated'}
    cfg = await configure(http, module, field(scope, 1, 'frozen', **options))
    # Seed a legacy batch in the private SQLite fixture. Production creation is retired.
    session.execute(text('INSERT INTO plan_dispatch_attempts VALUES (:identity, :version)'),
                    {'identity': '3524b77f-f5a4-46bd-b77a-031a8681a92e', 'version': cfg['configVersion']})
    session.commit()
    delete = {'scope': scope, 'slotNo': 1, 'name': 'frozen', 'configRevision': cfg['configRevision']}
    rejection(await http.post(CONFIG+'/delete', json=delete), 409, 'field_in_use')


@pytest.mark.parametrize(('later', 'expected'), [
    ('stored value', 409), ('status only', 409), ('missing creation evidence', 409),
    ('unknown creation version', 409), ('unchanged with evidence', 409), ('read only', 200),
])
async def test_delete_verifies_evidence_for_tasks_created_before_field_publication(client, later, expected):
    http, session, _, _ = client
    await put(http, PLAN, 'OLDER')
    cfg = await configure(http, 'plan', field('plan_local', 1, 'laterField'))
    if later == 'stored value':
        await put(http, PLAN, 'OLDER', items={'laterField': ''})
    elif later == 'status only':
        await put(http, PLAN, 'OLDER', productionStatus='error')
    elif later == 'unchanged with evidence':
        assert (await put(http, PLAN, 'OLDER'))['outcome'] == 'unchanged'
    elif later == 'unknown creation version':
        session.execute(text("UPDATE plan_main SET field_config_version=999 WHERE task_no='OLDER'"))
        session.commit()
    removed_version = {
        'stored value': cfg['configVersion'], 'status only': cfg['configVersion'],
        'missing creation evidence': 1,
    }.get(later)
    if removed_version:
        session.query(FieldConfigUse).filter_by(config_version=removed_version, subject_key='OLDER').delete()
        session.commit()
    before = await get(http, PLAN, 'OLDER')
    payload = {'scope': 'plan_local', 'slotNo': 1, 'name': 'laterField', 'configRevision': cfg['configRevision']}
    response = await http.post(CONFIG+'/delete', json=payload)
    if expected == 409:
        rejection(response, 409, 'field_in_use')
        assert await get(http, PLAN, 'OLDER') == before
    else:
        assert data(response)['outcome'] == 'deleted'
        await configure(http, 'plan', field('plan_local', 1, 'reusedSlot'))
        result = await put(http, PLAN, 'OLDER', items={'reusedSlot': 'normal'})
        assert result['plan']['items']['reusedSlot'] == 'normal'


async def test_unused_field_can_be_reintroduced_after_a_gap_with_task_writes(client):
    http, _, _, _ = client
    await put(http, PLAN, 'IN-GAP')
    definition = field('plan_local', 1, 'unused')
    payload = {'scope': 'plan_local', 'slotNo': 1, 'name': 'unused'}
    v2 = await configure(http, 'plan', definition)
    assert data(await http.post(CONFIG+'/delete', json={**payload, 'configRevision':v2['configRevision']}))['outcome'] == 'deleted'
    await put(http, PLAN, 'IN-GAP', productionStatus='error')
    v4 = await configure(http, 'plan', definition)
    assert data(await http.post(CONFIG+'/delete', json={**payload, 'configRevision':v4['configRevision']}))['outcome'] == 'deleted'


async def test_delete_does_not_publish_when_subject_query_fails(client, monkeypatch):
    http, _, _, _ = client
    cfg = await configure(http, 'shared', field('shared_sync', 1, 'audit', performanceOwner='automated'))
    original_execute = Transactions.execute

    async def failed_query(self, statement):
        if 'FROM plan_main LEFT OUTER JOIN' in str(statement):
            raise RuntimeError('historical read failed')
        return await original_execute(self, statement)

    monkeypatch.setattr(Transactions, 'execute', failed_query)
    payload = {'scope': 'shared_sync', 'slotNo': 1, 'name': 'audit', 'configRevision': cfg['configRevision']}
    rejection(await http.post(CONFIG+'/delete', json=payload), 503, 'unavailable')
    assert data(await http.get(CONFIG, params={'module':'plan'})) == cfg


async def test_delete_history_reads_use_mysql_current_locking_selects():
    from sqlalchemy.dialects.mysql import dialect
    from app.task.services.async_fields import _verify_subject_history

    queries = []
    class NoReferences:
        async def execute(self, query):
            queries.append(str(query.compile(dialect=dialect())))
            return SimpleNamespace(first=lambda: None)

    active = SimpleNamespace(config_version=2, slot_no=1, scope='shared_sync', created_at=datetime(2026, 11, 18, 10))
    await _verify_subject_history(NoReferences(), ('plan', 'performance', 'dispatch'), [active], active, 'name')
    assert [stmt.split('FROM ', 1)[1].split()[0] for stmt in queries] == ['plan_main', 'performance_main', 'plan_dispatch_attempts']
    assert all('LEFT OUTER JOIN task_field_config_uses' in stmt and stmt.endswith('FOR UPDATE') for stmt in queries)
    assert all('JSON_EXTRACT' in stmt and '.updated_at' in stmt for stmt in queries[:2])
    assert 'JSON_EXTRACT' not in queries[2]


async def test_delete_first_does_not_accept_a_following_write_to_old_field(client):
    http, session, _, _ = client
    cfg = await configure(http, 'shared', field('shared_sync', 1, 'removed', performanceOwner='automated'))
    delete = {'scope': 'shared_sync', 'slotNo': 1, 'name': 'removed', 'configRevision': cfg['configRevision']}
    assert data(await http.post(CONFIG+'/delete', json=delete))['outcome'] == 'deleted'
    for route in (PLAN, PERF):
        rejection(await http.post(route+'/upsert', json={'taskNo':'AFTER-DELETE', 'items':{'removed':'late'}}),
                  422, 'invalid_request', 'items.removed', 'unknown_field')
        rejection(await http.get(route+'/by-task/AFTER-DELETE'), 404, 'not_found')
    assert session.query(FieldConfigUse).count() == 0


async def test_query_validation_roles_and_retired_actions(client):
    http, _, identity, app = client
    schema = app.openapi()
    old_paths = ('/integration/plans/dispatch/claim','/integration/plans/dispatch/report',
                 '/plans/1/actions/cancel','/performances/1/actions/supplement-plan')
    for path in old_paths:
        assert path not in schema['paths']
        rejection(await http.post(path, content=b'broken JSON'), 410,'endpoint_retired')
    assert not any('/actions/' in path for path in schema['paths'])
    for invalid in ({'productionStatus':'queued'}, {'pageSize':101},
                    {'createdFrom':'2026-11-18T04:00:00'}, {'createdTo':'2026-11-18T04:00:00.1234567+08:00'}):
        rejection(await http.get(PLAN, params=invalid),422,'invalid_request')
    identity.role = 'operator'
    rejection(await http.get('/plans'),403,'forbidden')
    rejection(await http.put(CONFIG, json={'module':'shared','configRevision':'1','changes':[]}),403,'forbidden')
    rejection(await http.post('/performances/upsert', json={'taskNo':'missing'}),404,'not_found')
    assert (await put(http, PLAN, 'public', producerId=None))['outcome']=='created'

    def unauthenticated():
        raise HTTPException(status_code=401)

    app.dependency_overrides[get_current_user] = unauthenticated
    rejection(await http.get('/performances'),401,'unauthenticated')


async def test_all_three_sets_hold_100_slots_and_cross_scope_names_are_independent(client):
    http, session, _, _ = client
    for module, scope in (('shared','shared_sync'), ('plan','plan_local'), ('performance','performance_local')):
        prefix = 's' if module == 'shared' else 'l'
        owner = {} if module == 'plan' else {'performanceOwner':'automated'}
        await configure(http,module,*(field(scope, i, f'{prefix}{i}', 'number', **owner) for i in range(1,101)))
    values = {f'{prefix}{i}':i for prefix in ('s','l') for i in range(1,101)}
    assert (await put(http, PLAN, 'FULL', items=values))['plan']['items'] == values
    assert (await put(http, PERF, 'FULL', items=values))['performance']['items'] == values
    for model in (Plan, Performance):
        row = session.scalar(select(model).where(model.task_no=='FULL'))
        assert len(row.local_values) == len(row.sync_values) == 100
    rejection(await http.post(PERF+'/upsert', json={'taskNo':'FULL','items':{**values,'l101':1}}),
              422,'invalid_request','items.l101','unknown_field')
    plan_config = data(await http.get(CONFIG, params={'module':'plan'}))
    for item in (field('plan_local',1,'s1'), field('plan_local',101,'l101')):
        rejection(await http.put(CONFIG, json={'module':'plan','configRevision':plan_config['configRevision'],
             'changes':[item]}), 422,'invalid_request')
    assert (await get(http, PERF, 'FULL'))['items'] == values


async def test_presentation_only_revision_and_protected_field_uniqueness(client):
    http, _, _, _ = client
    initial = await configure(http, 'shared', field('shared_sync',1,'shared', performanceOwner='manual'))
    presented = await configure(http, 'shared', {'scope':'shared_sync','slotNo':1, 'planVisible':True,
                                                'labels':{'zh-CN':'共用','en-US':'Shared'}})
    assert presented['configVersion'] == initial['configVersion']
    assert int(presented['configRevision']) == int(initial['configRevision']) + 1
    no_change = await configure(http,'shared',{'scope':'shared_sync','slotNo':1,'planVisible':True})
    assert no_change == presented
    for module, item, reason in (
        ('plan',field('shared_sync',2,'no'),'scope_mismatch'),
        ('plan',field('plan_local',2,'shared'),'duplicate_field_name'),
        ('plan',field('plan_local',2,'productionStatus'),'invalid_field_name'),
        ('shared',{'scope':'shared_sync','slotNo':1,'type':'number'},'immutable_field_identity'),
    ):
        rejection(await http.put(CONFIG,json={'module':module,'configRevision':presented['configRevision'],
            'changes':[item]}),422,'invalid_request',reason=reason)


async def test_candidate_examples_match_registered_openapi_and_actual_responses(client):
    http, _, _, app = client
    candidate = Path(__file__).resolve().parents[2] / 'contracts/published/http-api/generic-task-workflow-v2'
    requests = json.loads((candidate / 'examples/requests.json').read_text())
    schema = json.loads((candidate / 'openapi.json').read_text())
    assert len(schema['paths']) == 16
    runtime = app.openapi()
    for path, methods in schema['paths'].items():
        assert set(methods) == set(runtime['paths'][path.removeprefix('/api/v1')])
        for method, operation in methods.items():
            current = runtime['paths'][path.removeprefix('/api/v1')][method]
            assert operation['responses'] == current['responses']
            assert operation.get('requestBody') == current.get('requestBody')
            assert operation.get('security') == current.get('security')
    for name, shape in schema['components']['schemas'].items():
        assert runtime['components']['schemas'][name] == shape
    results = {}
    for example in requests:
        kwargs = {'json':example['body']} if 'body' in example else {'params':example['query']}
        result = await http.request(example['method'], example['path'].removeprefix('/api/v1'), **kwargs)
        results[example['id']] = data(result)
    assert results['query-new']['items'][0]['items']['productCode'] == '0007'
    assert results['performance']['performance']['lastObservedAt'] == '2026-11-18T10:00:00.123456+08:00'
    assert results['performance']['planSync']['fieldsChanged'] == ['completedLength']
    assert results['finish']['performance']['productionStatus'] == 'completed'
    assert results['performance-first']['performance']['hasPlan'] is False
    assert results['plan-after-performance']['plan']['items']['completedLength'] == 35
    assert [item['name'] for item in results['batch-delete-shared-fields']['deleted']] == ['operatorNote', 'qualityFlag']
    assert results['batch-delete-shared-fields']['configRevision'] == '4'
    assert [item['name'] for item in results['batch-delete-plan-local']['deleted']] == ['workNote', 'workInstruction']
    assert [item['name'] for item in results['batch-delete-performance-local']['deleted']] == ['operatorNote', 'shiftNote']
    assert results['batch-delete-performance-local']['configRevision'] == '8'


async def test_mysql_locking_reads_precede_usage_audit_and_writes(monkeypatch):
    """核对 MySQL 方言 SQL；不替代实库竞争验证。"""
    from sqlalchemy.dialects.mysql import dialect
    from app.task.services.async_fields import current_config, record_use

    statements = []
    class Result:
        def scalar_one_or_none(self): return SimpleNamespace(active_version=9)
        def scalars(self): return self
        def all(self): return []
    class Queries:
        async def execute(self, stmt):
            statements.append(str(stmt.compile(dialect=dialect())))
            return Result()
        async def get(self, model, identity, *, with_for_update):
            assert model is FieldConfigUse and with_for_update is True
            assert identity == {'config_version':9,'subject_kind':'plan','subject_key':'DB'}
            return None
        def add(self, row):
            assert row.subject_kind == 'plan'

    db = Queries()
    state, _ = await current_config(db, lock=True)
    from app.plan.services.async_workflow import lock_plan
    await lock_plan(db, 'DB')
    await record_use(db,state.active_version,'plan','DB')
    assert [next(table for table in ['task_field_config_state','task_field_definitions','plan_main'] if 'FROM '+table in stmt)
            for stmt in statements] == ['task_field_config_state','task_field_definitions','plan_main']
    assert all(stmt.endswith('FOR UPDATE') for stmt in statements)


def shared_identity(slot, name):
    return {'scope': 'shared_sync', 'slotNo': slot, 'name': name}


@pytest.mark.parametrize('count', [1, 2, 100])
async def test_delete_shared_batch_publishes_once_and_preserves_history(client, count):
    http, session, _, _ = client
    cfg = await configure(http, 'shared', *[
        field('shared_sync', slot, f'field{slot}', performanceOwner='manual') for slot in range(1, count + 1)
    ])
    local = await configure(http, 'plan', field('plan_local', 1, 'localField'))
    requested = [shared_identity(slot, f'field{slot}') for slot in range(count, 0, -1)]
    versions = session.scalar(select(func.count()).select_from(FieldConfigVersion))
    result = data(await http.post(CONFIG+'/batch-delete', json={'configRevision': local['configRevision'], 'fields': requested}))
    assert result == {'outcome': 'deleted', 'deleted': requested, 'configVersion': local['configVersion'] + 1,
                      'configRevision': str(int(local['configRevision']) + 1)}
    assert session.scalar(select(func.count()).select_from(FieldConfigVersion)) == versions + 1
    assert session.scalar(select(func.count()).select_from(FieldDefinition).where(
        FieldDefinition.config_version == cfg['configVersion'])) == count
    current = data(await http.get(CONFIG, params={'module': 'plan'}))
    assert [item['name'] for item in current['fields']] == ['localField']
    reused = await configure(http, 'shared', field('shared_sync', 1, 'reusedSlot', performanceOwner='manual'))
    assert [item['name'] for item in reused['fields']] == ['reusedSlot']


async def test_delete_shared_batch_validation_and_authority(client):
    http, _, identity, app = client
    cfg = await configure(http, 'shared', field('shared_sync', 1, 'first', performanceOwner='manual'))
    payload = {'configRevision': cfg['configRevision'], 'fields': [shared_identity(1, 'first')]}
    for invalid_fields in ([], [payload['fields'][0]] * 101, [payload['fields'][0]] * 2,
                           [dict(scope='plan_local', slotNo=1, name='local')],
                           [dict(scope='shared_sync', slotNo=True, name='first')],
                           [dict(scope='shared_sync', slotNo=1, name='first', other='extra')]):
        rejection(await http.post(CONFIG+'/batch-delete', json={**payload, 'fields': invalid_fields}), 422, 'invalid_request')
    rejection(await http.post(CONFIG+'/batch-delete', json={**payload, 'configRevision': '1'}),
              409, 'config_revision_conflict')
    rejection(await http.post(CONFIG+'/batch-delete', json={**payload, 'fields': [
        shared_identity(1, 'first'), shared_identity(2, 'missing')
    ]}), 404, 'not_found', 'fields.1.name', 'field_identity_not_found')
    for role in ('supervisor', 'operator'):
        identity.role = role
        rejection(await http.post(CONFIG+'/batch-delete', json=payload), 403, 'forbidden')
    identity.role = 'admin'
    original_user = app.dependency_overrides[get_current_user]
    def no_user():
        raise HTTPException(401)
    app.dependency_overrides[get_current_user] = no_user
    try:
        rejection(await http.post(CONFIG+'/batch-delete', json=payload), 401, 'unauthenticated')
    finally:
        app.dependency_overrides[get_current_user] = original_user
    assert data(await http.get(CONFIG, params={'module': 'plan'})) == cfg


@pytest.mark.parametrize('evidence', ['plan', 'performance', 'dispatch', 'missing', 'version'])
@pytest.mark.parametrize('used_index', [0, 1])
async def test_delete_shared_batch_preserves_all_rows_on_protection(client, evidence, used_index):
    http, session, _, _ = client
    used = await configure(http, 'shared', field('shared_sync', 1, 'used', performanceOwner='automated', enabled=False))
    if evidence in ('plan', 'performance', 'missing'):
        await put(http, PERF if evidence == 'performance' else PLAN, 'USED')
    if evidence == 'dispatch':
        session.add(FieldConfigUse(config_version=used['configVersion'], subject_kind='dispatch', subject_key='prior'))
        session.commit()
    if evidence == 'missing':
        session.query(FieldConfigUse).filter_by(subject_key='USED').delete()
        session.commit()
    # A later definition was never part of the earlier task's configuration.
    current = await configure(http, 'shared', field('shared_sync', 2, 'unused', performanceOwner='manual'))
    if evidence == 'version':
        session.query(FieldConfigVersion).filter_by(config_version=1).delete()
        session.commit()
    requested = [shared_identity(2, 'unused')]
    requested.insert(used_index, shared_identity(1, 'used'))
    before = (
        session.scalar(select(func.count()).select_from(FieldConfigVersion)),
        session.scalar(select(func.count()).select_from(FieldDefinition)),
        session.scalar(select(func.count()).select_from(FieldConfigUse)),
    )
    response = await http.post(CONFIG+'/batch-delete', json={'configRevision': current['configRevision'], 'fields': requested})
    if evidence == 'version':
        rejection(response, 409, 'field_in_use', 'fields', 'historical_configuration_unverifiable')
    elif evidence == 'missing':
        # Missing evidence can affect both candidates because the bound task is unverifiable.
        rejection(response, 409, 'field_in_use', 'fields.0.name', 'historical_usage_unverifiable')
    else:
        rejection(response, 409, 'field_in_use', f'fields.{used_index}.name', 'referenced_by_task_or_dispatch')
    assert data(await http.get(CONFIG, params={'module': 'plan'})) == current
    assert before == (
        session.scalar(select(func.count()).select_from(FieldConfigVersion)),
        session.scalar(select(func.count()).select_from(FieldDefinition)),
        session.scalar(select(func.count()).select_from(FieldConfigUse)),
    )


def local_identity(module, slot, name):
    return {'scope': f'{module}_local', 'slotNo': slot, 'name': name}


def local_definition(module, slot, name, **settings):
    if module == 'performance':
        settings.setdefault('performanceOwner', 'automated')
    return field(f'{module}_local', slot, name, **settings)


@pytest.mark.parametrize('module, count', [(module, size) for module in ('plan', 'performance') for size in (1, 2, 100)])
async def test_local_batch_delete_scopes_and_publishes_once(client, module, count):
    http, session, _, _ = client
    other = 'performance' if module == 'plan' else 'plan'
    await configure(http, 'shared', field('shared_sync', 1, 'sharedField', performanceOwner='manual'))
    await configure(http, other, local_definition(other, 1, 'sameKey1'))
    configured = await configure(http, module, *[
        local_definition(module, slot, f'sameKey{slot}') for slot in range(1, count + 1)
    ])
    requested = [local_identity(module, slot, f'sameKey{slot}') for slot in range(count, 0, -1)]
    other_before = data(await http.get(CONFIG, params={'module': other}))['fields']
    response = data(await http.post(CONFIG + '/local/batch-delete', json={
        'module': module, 'configRevision': configured['configRevision'], 'fields': requested,
    }))
    assert response == {
        'outcome': 'deleted', 'deleted': requested, 'configVersion': configured['configVersion'] + 1,
        'configRevision': str(int(configured['configRevision']) + 1),
    }
    assert session.scalar(select(func.count()).select_from(FieldConfigVersion)) == response['configVersion']
    assert session.scalar(select(func.count()).select_from(FieldDefinition).where(
        FieldDefinition.config_version == configured['configVersion'],
        FieldDefinition.scope == f'{module}_local')) == count
    assert data(await http.get(CONFIG, params={'module': other}))['fields'] == other_before
    assert [row['name'] for row in data(await http.get(CONFIG, params={'module': module}))['fields']] == ['sharedField']


@pytest.mark.parametrize('module', ['plan', 'performance'])
async def test_local_batch_delete_validation_and_authority(client, module):
    http, _, caller, app = client
    other = 'performance' if module == 'plan' else 'plan'
    cfg = await configure(http, module, local_definition(module, 1, 'first'))
    one = local_identity(module, 1, 'first')
    endpoint = CONFIG + '/local/batch-delete'
    valid = {'module': module, 'configRevision': cfg['configRevision'], 'fields': [one]}
    for payload in (
        {**valid, 'module': 'shared'}, {**valid, 'fields': []}, {**valid, 'fields': [one] * 101},
        {**valid, 'fields': [{**one, 'slotNo': True}]},
        {**valid, 'fields': [{**one, 'extra': 'bad'}]}, {**valid, 'extra': 'bad'},
        {**valid, 'fields': [{**one, 'scope': 'shared_sync'}]},
    ):
        rejection(await http.post(endpoint, json=payload), 422, 'invalid_request')
    for fields, path, reason in (
        ([one, one], 'fields.1.slotNo', 'duplicate_slot'),
        ([one, {**one, 'name': 'otherKey'}], 'fields.1.slotNo', 'duplicate_slot'),
        ([one, local_identity(other, 2, 'otherKey')], 'fields.1.scope', 'scope_mismatch'),
        ([local_identity(other, 1, 'first')], 'fields.0.scope', 'scope_mismatch'),
    ):
        rejection(await http.post(endpoint, json={**valid, 'fields': fields}), 422, 'invalid_request', path, reason)
    rejection(await http.post(endpoint, json={**valid, 'configRevision': '1'}),
              409, 'config_revision_conflict')
    rejection(await http.post(endpoint, json={**valid, 'fields': [one, local_identity(module, 2, 'missing')]}),
              404, 'not_found', 'fields.1.name', 'field_identity_not_found')
    for role in ('supervisor', 'operator', 'unknown'):
        caller.role = role
        rejection(await http.post(endpoint, json=valid), 403, 'forbidden')
    caller.role = 'admin'
    original_user = app.dependency_overrides[get_current_user]

    def no_user():
        raise HTTPException(401)

    app.dependency_overrides[get_current_user] = no_user
    try:
        rejection(await http.post(endpoint, json=valid), 401, 'unauthenticated')
    finally:
        app.dependency_overrides[get_current_user] = original_user
    assert data(await http.get(CONFIG, params={'module': module})) == cfg


@pytest.mark.parametrize('module', ['plan', 'performance'])
@pytest.mark.parametrize('evidence', ['task', 'disabled', 'dispatch', 'missing', 'version'])
@pytest.mark.parametrize('used_index', [0, 1])
async def test_local_batch_delete_keeps_every_definition_on_protection(client, module, evidence, used_index):
    http, session, _, _ = client
    original = await configure(http, module, local_definition(module, 1, 'protected', enabled=evidence != 'disabled'))
    if evidence in ('task', 'disabled', 'missing'):
        await put(http, PLAN if module == 'plan' else PERF, 'USED-LOCAL')
    if evidence == 'dispatch':
        session.add(FieldConfigUse(config_version=original['configVersion'], subject_kind='dispatch', subject_key='prior'))
        session.commit()
    if evidence == 'missing':
        session.query(FieldConfigUse).filter_by(subject_key='USED-LOCAL').delete()
        session.commit()
    cfg = await configure(http, module, local_definition(module, 2, 'unused'))
    if evidence == 'version':
        session.query(FieldConfigVersion).filter_by(config_version=1).delete()
        session.commit()
    requested = [local_identity(module, 2, 'unused')]
    requested.insert(used_index, local_identity(module, 1, 'protected'))

    def counts():
        return [session.scalar(select(func.count()).select_from(model)) for model in
                (FieldConfigVersion, FieldDefinition, FieldConfigUse, Plan, Performance)]

    before = counts()
    response = await http.post(CONFIG + '/local/batch-delete', json={
        'module': module, 'configRevision': cfg['configRevision'], 'fields': requested,
    })
    if evidence == 'version':
        rejection(response, 409, 'field_in_use', 'fields', 'historical_configuration_unverifiable')
    elif evidence == 'missing':
        rejection(response, 409, 'field_in_use', 'fields.0.name', 'historical_usage_unverifiable')
    else:
        rejection(response, 409, 'field_in_use', f'fields.{used_index}.name', 'referenced_by_task_or_dispatch')
    assert data(await http.get(CONFIG, params={'module': module})) == cfg
    assert counts() == before
