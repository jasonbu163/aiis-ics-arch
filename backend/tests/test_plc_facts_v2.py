"""PLC 事实 v2 离线合同、来源准入、事务和清理预算回归。"""
from copy import deepcopy
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import runpy
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.mysql import dialect
from sqlalchemy.exc import IntegrityError

from app.plc_facts import v2_config, v2_domain
from app.plc_facts.api import v2 as api
from app.plc_facts.crud import async_v2, sync_v2_maintenance
from app.plc_facts.services import async_v2 as service
from app.plc_facts.services import sync_v2_maintenance as maintenance

pytestmark = pytest.mark.no_db
NOW = datetime(2026, 11, 10, 10, 0, 3)


def sample(count=2):
    points = [{'pointId': f'point-{index}', 'name': '', 'dataType': 'BOOL', 'value': False,
               'quality': 'good', 'observedAt': '2026-11-10T10:00:02.120+08:00'}
              for index in range(count)]
    return {'contractVersion': 'plc-facts/v2', 'instanceId': 'daa-a', 'sampleId': 'sample-102-db21',
            'plcId': 'PLC-A', 'dbNumber': 21, 'groupId': 'temperature', 'configRevision': 'rev-12',
            'sourceGeneration': 'gen-a', 'sourceSeq': '102', 'points': points}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def profile():
    return {'target': {'alias': 'fixture', 'schema': 'fixture_schema',
                       'serverUuid': '00000000-0000-4000-8000-000000000001',
                       'schemaRevision': '5f7a9c1e3b25'},
            'instances': [{'instanceId': 'daa-a', 'sourceType': 'daa'}],
            'sources': [{'plcId': 'PLC-A', 'instanceId': 'daa-a', 'sourceGeneration': 'gen-a', 'dbNumbers': [21]}],
            'readScopes': {'admin': [{'plcId': 'PLC-A', 'dbNumbers': [21]}]}}


def install_registry_fixture(monkeypatch, value):
    """离线测试在登记访问边界注入同一份已登记事实，保留实际准入断言。"""
    async def initialized(_db): pass
    async def admit(_db, body):
        v2_config.admit_source(value, body)
        return value['instances'][body.instance_id]
    async def read(_db, _target):
        return {**value, 'sourceTypes': {plc: value['instances'][source[0]] for plc, source in value['sources'].items()}}
    monkeypatch.setattr(service.registry, 'admit', admit)
    monkeypatch.setattr(service.registry, 'read_profile', read)


@pytest.mark.parametrize('count', [400, 512])
def test_sample_point_limits(count):
    parsed, document, digest = v2_domain.parse_sample(encoded(sample(count)))
    assert len(parsed.points) == len(document['points']) == count
    assert len(digest) == 32


def test_body_and_point_boundaries_are_independent():
    raw = encoded(sample())
    exact = raw + b' ' * (524288 - len(raw))
    assert v2_domain.parse_sample(exact)[0].sample_id == 'sample-102-db21'
    with pytest.raises(v2_domain.V2Error) as too_large:
        v2_domain.parse_sample(exact + b' ')
    assert too_large.value.status == 413
    with pytest.raises(v2_domain.V2Error) as too_many:
        v2_domain.parse_sample(encoded(sample(513)))
    assert too_many.value.status == 422


@pytest.mark.parametrize('mutation', [
    lambda item: item.update(dbNumber=True),
    lambda item: item.update(sourceSeq='01'),
    lambda item: item.update(sourceSeq='9223372036854775807'),
    lambda item: item.update(plcId=' PLC-A'),
    lambda item: item['points'][0].update(value=0),
    lambda item: item['points'][0].update(observedAt='2026-11-10T10:00:02.1234567+08:00'),
    lambda item: item['points'][0].update(quality='bad', value=None),
    lambda item: item['points'][0].update(unknown='x'),
    lambda item: item['points'][1].update(pointId='point-0'),
])
def test_invalid_sample_fields(mutation):
    document = sample()
    mutation(document)
    with pytest.raises(v2_domain.V2Error) as error:
        v2_domain.parse_sample(encoded(document))
    assert error.value.status == 422


def test_duplicate_json_keys_and_nonfinite_numbers_rejected():
    raw = encoded(sample()).replace(b'"dbNumber":21', b'"dbNumber":21,"dbNumber":21')
    with pytest.raises(v2_domain.V2Error):
        v2_domain.parse_sample(raw)
    raw = encoded(sample()).replace(b'"value":false', b'"value":NaN', 1)
    with pytest.raises(v2_domain.V2Error):
        v2_domain.parse_sample(raw)


def test_types_bad_missing_and_zero_values():
    document = sample(4)
    document['points'][0].update(dataType='INT', value=0)
    document['points'][1].update(dataType='STRING[12]', value='')
    document['points'][2].update(dataType='REAL', value=820.5)
    document['points'][3].update(dataType='BOOL', value=None, quality='bad', reason='missing')
    parsed, _, _ = v2_domain.parse_sample(encoded(document))
    assert [point.value for point in parsed.points[:2]] == [0, '']
    assert str(parsed.points[2].value) == '820.5' and parsed.points[3].value is None
    document['points'][2]['value'] = 3.5e38
    with pytest.raises(v2_domain.V2Error):
        v2_domain.parse_sample(encoded(document))


def test_month_end_expiry_and_exact_boundary():
    assert v2_domain.expiry(datetime(2024, 11, 30, 8)) == datetime(2025, 2, 27, 8)
    assert v2_domain.expiry(datetime(2023, 11, 30, 8)) == datetime(2024, 2, 28, 8)
    parsed, _, _ = v2_domain.parse_sample(encoded(sample()))
    deadline = datetime(2027, 2, 9, 10, 0, 2, 120000)
    v2_domain.validate_times(parsed, deadline - timedelta(microseconds=1))
    with pytest.raises(v2_domain.V2Error) as expired:
        v2_domain.validate_times(parsed, deadline)
    assert expired.value.status == 410
    with pytest.raises(v2_domain.V2Error):
        v2_domain.validate_times(parsed, datetime(2026, 11, 10, 9, 55, 1))
    mixed = sample()
    mixed['points'][1]['observedAt'] = '2026-11-10T10:00:02.125+08:00'
    parsed, _, _ = v2_domain.parse_sample(encoded(mixed))
    observed, expiries = v2_domain.validate_times(parsed, NOW)
    assert max(observed) == datetime(2026, 11, 10, 10, 0, 2, 125000)
    assert min(expiries) == deadline and expiries[1] - expiries[0] == timedelta(milliseconds=5)


def test_migration_refuses_nonempty_or_unreadable_downgrade():
    import importlib.util
    path = Path(__file__).resolve().parents[1] / 'alembic/versions/20261110_2000_2c4e6a8b0d12_add_plc_facts_v2.py'
    spec = importlib.util.spec_from_file_location('be012_migration_source', path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    class Result:
        def __init__(self, value): self.value = value
        def first(self): return self.value
    class Operation:
        def __init__(self, failure): self.failure, self.calls, self.dropped = failure, 0, []
        def get_bind(self): return self
        def execute(self, _statement):
            self.calls += 1
            if self.failure == 'unreadable': raise RuntimeError('synthetic database failure')
            return Result((1,) if self.calls == 2 else None)
        def drop_table(self, name): self.dropped.append(name)
    for failure in ('nonempty', 'unreadable'):
        operation = Operation(failure)
        migration.op = operation
        with pytest.raises(RuntimeError): migration.downgrade()
        assert operation.dropped == []


def test_identity_limits_and_profile_source_binding():
    value = v2_config.parse_profile(profile())
    parsed, _, _ = v2_domain.parse_sample(encoded(sample()))
    v2_config.admit_source(value, parsed)
    with pytest.raises(v2_domain.V2Error) as wrong:
        v2_config.admit_source(value, parsed.model_copy(update={'instance_id': 'different'}))
    assert wrong.value.status == 403
    document = profile()
    document['credentials'] = [{'instanceId': 'daa-a', 'tokenSha256': 'a' * 64}]
    assert v2_config.parse_profile(document) == value
    document = profile()
    document['target']['serverUuid'] = []
    with pytest.raises(ValueError):
        v2_config.parse_profile(document)
    assert len(v2_domain.identifier('温' * 42).encode()) == 126
    with pytest.raises(v2_domain.V2Error):
        v2_domain.identifier('温' * 43)


@pytest.mark.asyncio
async def test_success_ack_occurs_after_commit_and_unknown_is_not_success(monkeypatch):
    install_registry_fixture(monkeypatch, v2_config.parse_profile(profile()))
    parsed, document, digest = v2_domain.parse_sample(encoded(sample()))
    events = []
    async def now(*_): return NOW
    async def put(*_): events.append('history')
    async def advance(*_): events.append('latest')
    monkeypatch.setattr(async_v2, 'target_now', now)
    monkeypatch.setattr(async_v2, 'insert_sample', put)
    monkeypatch.setattr(async_v2, 'advance_latest', advance)
    class Session:
        async def commit(self): events.append('commit')
        async def rollback(self): events.append('rollback')
    boundary = {}
    result = await service.write_sample(Session(), v2_config.parse_profile(profile()), parsed, document, digest, boundary)
    assert events == ['history', 'latest', 'commit']
    assert boundary['committed'] and result['data']['outcome'] == 'created'
    class Lost(Session):
        async def commit(self): raise OSError('synthetic lost ACK')
    with pytest.raises(v2_domain.V2Error) as error:
        await service.write_sample(Lost(), v2_config.parse_profile(profile()), parsed, document, digest, {})
    assert error.value.key == 'plc_facts_v2.commit_outcome_unknown'


@pytest.mark.asyncio
async def test_unique_conflict_reopens_transaction_for_duplicate_or_conflict(monkeypatch):
    install_registry_fixture(monkeypatch, v2_config.parse_profile(profile()))
    parsed, document, digest = v2_domain.parse_sample(encoded(sample()))
    async def now(*_): return NOW
    async def collision(*_): raise IntegrityError('synthetic', {}, Exception('duplicate'))
    row = SimpleNamespace(instance_id=b'daa-a', sample_id=b'sample-102-db21', content_hash=digest)
    async def identities(*_): return [row]
    monkeypatch.setattr(async_v2, 'target_now', now)
    monkeypatch.setattr(async_v2, 'insert_sample', collision)
    monkeypatch.setattr(async_v2, 'identities', identities)
    class Session:
        async def rollback(self): pass
    result = await service.write_sample(Session(), v2_config.parse_profile(profile()), parsed, document, digest, {})
    assert result['data']['outcome'] == 'duplicate'
    row.content_hash = b'x' * 32
    with pytest.raises(v2_domain.V2Error) as error:
        await service.write_sample(Session(), v2_config.parse_profile(profile()), parsed, document, digest, {})
    assert error.value.status == 409


@pytest.mark.asyncio
async def test_duplicate_and_new_sample_recheck_clock_after_wait(monkeypatch):
    install_registry_fixture(monkeypatch, v2_config.parse_profile(profile()))
    parsed, document, digest = v2_domain.parse_sample(encoded(sample()))
    before = datetime(2027, 2, 9, 10, 0, 2, 119999)
    cutoff = before + timedelta(microseconds=1)
    async def collision(*_): raise IntegrityError('synthetic', {}, Exception('duplicate'))
    row = SimpleNamespace(instance_id=b'daa-a', sample_id=b'sample-102-db21', content_hash=digest)
    async def identities(*_): return [row]
    class Session:
        commits = 0
        async def rollback(self): pass
        async def commit(self): self.commits += 1
    db = Session()
    readings = iter((before, before, cutoff))
    async def now(*_): return next(readings)
    monkeypatch.setattr(async_v2, 'target_now', now)
    monkeypatch.setattr(async_v2, 'insert_sample', collision)
    monkeypatch.setattr(async_v2, 'identities', identities)
    with pytest.raises(v2_domain.V2Error) as expired:
        await service.write_sample(db, v2_config.parse_profile(profile()), parsed, document, digest, {})
    assert expired.value.status == 410 and db.commits == 0
    readings = iter((before, cutoff))
    async def insert(*_): pass
    async def advance(*_): pass
    monkeypatch.setattr(async_v2, 'insert_sample', insert)
    monkeypatch.setattr(async_v2, 'advance_latest', advance)
    with pytest.raises(v2_domain.V2Error) as expired:
        await service.write_sample(db, v2_config.parse_profile(profile()), parsed, document, digest, {})
    assert expired.value.status == 410 and db.commits == 0


@pytest.mark.asyncio
async def test_target_checks_uuid_schema_revision_version_and_db_clock():
    target = profile()['target']
    target['schemaRevision'] = v2_config.REVISION
    class Result:
        def __init__(self, value): self.value = value
        def one(self): return self.value
        def scalars(self): return iter(self.value)
    class Session:
        def __init__(self):
            self.row = (target['serverUuid'], target['schema'], '8.4.6', NOW, 28800)
            self.revisions = [v2_config.REVISION]
        def get_bind(self): return SimpleNamespace(dialect=SimpleNamespace(name='mysql'))
        async def execute(self, statement):
            return Result(self.revisions if 'alembic_version' in str(statement) else self.row)
    db = Session()
    assert await async_v2.target_now(db, target) == NOW
    for row, revisions in [
        (('wrong-uuid', target['schema'], '8.4.6', NOW, 28800), db.revisions),
        ((target['serverUuid'], 'wrong-schema', '8.4.6', NOW, 28800), db.revisions),
        ((target['serverUuid'], target['schema'], '8.0.0', NOW, 28800), db.revisions),
        ((target['serverUuid'], target['schema'], '8.4.6', NOW, 0), db.revisions),
        (db.row, ['1b3d5f7a9c20']),
        (db.row, ['2c4e6a8b0d12', '3d5f7a9c1e23']),
    ]:
        db.row, db.revisions = row, revisions
        with pytest.raises(v2_domain.V2Error) as error:
            await async_v2.target_now(db, target)
        assert error.value.key == 'plc_facts_v2.not_ready'


@pytest.mark.asyncio
async def test_history_detail_independent_from_current_registration(monkeypatch):
    document = profile()
    document['sources'][0]['dbNumbers'] = []
    value = v2_config.parse_profile(document)
    install_registry_fixture(monkeypatch, value)
    calls = []
    async def now(*_): return NOW
    async def latest(*args): calls.append(args); return []
    async def detail(*_):
        return SimpleNamespace(id=1, instance_id=b'old', sample_id=b'sample', plc_id=b'PLC-Z',
            db_number=21, group_id=None, config_revision=None, source_type=None,
            source_generation=b'old-gen', source_seq=1, sampled_at=NOW, stored_at=NOW, points_json=[])
    monkeypatch.setattr(async_v2, 'target_now', now)
    monkeypatch.setattr(async_v2, 'latest', latest)
    monkeypatch.setattr(async_v2, 'detail', detail)
    assert await service.latest(object(), value, 'PLC-A', 21) == {'items': []}
    assert len(calls) == 1
    assert (await service.detail(object(), value, 1))['plcId'] == 'PLC-Z'
    with pytest.raises(v2_domain.V2Error) as denied:
        await service.latest(object(), value, 'PLC-Z', 21)
    assert denied.value.status == 403


@pytest.mark.parametrize('negative', [False, True])
@pytest.mark.parametrize('token, accepted', [
    (str(v2_domain.REAL_OVERFLOW_MIDPOINT - 1), True),
    (str(v2_domain.REAL_OVERFLOW_MIDPOINT), False),
    (str(v2_domain.REAL_OVERFLOW_MIDPOINT + 1), False),
    (str(v2_domain.REAL_OVERFLOW_MIDPOINT - 1) + '.' + '9' * 40, True),
    (str(v2_domain.REAL_OVERFLOW_MIDPOINT) + '.0', False),
    (str(v2_domain.REAL_OVERFLOW_MIDPOINT) + '.' + '0' * 39 + '1', False),
    (str(v2_domain.REAL_OVERFLOW_MIDPOINT * 10 - 1) + 'e-1', True),
    (str(v2_domain.REAL_OVERFLOW_MIDPOINT * 10) + 'e-1', False),
    (str(v2_domain.REAL_OVERFLOW_MIDPOINT * 10 + 1) + 'e-1', False),
])
def test_real_binary32_overflow_midpoint(token, accepted, negative):
    token = ('-' if negative else '') + token
    document = sample(1)
    document['points'][0].update(dataType='REAL', value=0)
    raw = encoded(document).replace(b'"value":0', b'"value":' + token.encode())
    if accepted:
        parsed, stored, _ = v2_domain.parse_sample(raw)
        assert str(parsed.points[0].value) == token
        assert v2_domain.stored_points(stored['points'])[0]['value'] == token
        assert v2_domain.json_bytes(v2_domain.real_number(token)) == token.encode()
    else:
        with pytest.raises(v2_domain.V2Error) as request:
            v2_domain.parse_sample(raw)
        assert request.value.status == 422
        with pytest.raises(v2_domain.V2Error) as storage:
            v2_domain.real_number(token)
        assert storage.value.status == 503


@pytest.mark.asyncio
async def test_real_numeric_tokens_roundtrip_storage_and_http(monkeypatch):
    document = sample(4)
    tokens = ('1.234567890123456789', '9007199254740993', '-0', '1e-1000000')
    for point in document['points']:
        point.update(dataType='REAL', value=0)
    raw = encoded(document)
    for token in tokens:
        raw = raw.replace(b'"value":0', b'"value":' + token.encode(), 1)
    parsed, payload, _ = v2_domain.parse_sample(raw)
    assert [str(point.value) for point in parsed.points] == list(tokens)
    stored = v2_domain.stored_points(payload['points'])
    assert [point['value'] for point in stored] == list(tokens)
    assert [v2_domain.stored_value(point) for point in parsed.points] == list(tokens)
    class Capture:
        def __init__(self): self.rows, self.statements = [], []
        def add(self, row): self.rows.append(row)
        async def flush(self): pass
        async def execute(self, statement): self.statements.append(statement)
    capture = Capture()
    observed, expiries = v2_domain.validate_times(parsed, NOW)
    await async_v2.insert_sample(capture, parsed, payload, b'x' * 32, observed, expiries, NOW, 'daa')
    await async_v2.advance_latest(capture, parsed, observed, expiries)
    assert [point['value'] for point in capture.rows[0].points_json] == list(tokens)
    bound = capture.statements[0].compile(dialect=dialect()).params
    assert set(tokens) <= {str(value) for key, value in bound.items() if key.startswith('value_json')}
    with pytest.raises(v2_domain.V2Error):
        v2_domain.real_number('0,"injected":true')
    bad = sample(1)
    bad['points'][0].update(dataType='STRING[20]', value=0)
    with pytest.raises(v2_domain.V2Error):
        v2_domain.parse_sample(encoded(bad).replace(b'"value":0', b'"value":1.25'))
    profile_value = v2_config.parse_profile(profile())
    install_registry_fixture(monkeypatch, profile_value)
    row = SimpleNamespace(id=1, instance_id=b'daa-a', sample_id=b'sample-102-db21', plc_id=b'PLC-A',
                          db_number=21, group_id=b'temperature', config_revision=b'rev-12', source_type='daa',
                          source_generation=b'gen-a', source_seq=102, sampled_at=NOW, stored_at=NOW,
                          points_json=stored)
    latest_rows = [SimpleNamespace(point_id=point['pointId'].encode(), point_name=None, data_type='REAL',
                                   value_json=point['value'], quality='good', reason=None, observed_at=NOW,
                                   instance_id=b'daa-a', source_generation=b'gen-a', source_seq=102,
                                   sample_id=b'sample-102-db21') for point in stored]
    async def now(*_): return NOW
    async def latest(*_): return latest_rows
    async def detail(*_): return row
    class Session:
        async def close(self): pass
    async def get_session(): return Session()
    received = []
    async def write(_db, _profile, body, _document, _digest, _boundary):
        received.extend(str(point.value) for point in body.points)
        return service.receipt(body, 'created')
    monkeypatch.setattr(api, 'get_profile', lambda: profile_value)
    monkeypatch.setattr(api, 'get_db_session', get_session)
    monkeypatch.setattr(service, 'write_sample', write)
    monkeypatch.setattr(async_v2, 'target_now', now)
    monkeypatch.setattr(async_v2, 'latest', latest)
    monkeypatch.setattr(async_v2, 'detail', detail)
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture', trust_env=False) as client:
        post = await client.post('/api/v1/integration/plc-facts/samples', content=raw,
                                 headers={'Content-Type': 'application/json'})
        assert post.status_code == 200 and received == list(tokens)
        for path in ('/api/v1/acquisition-data/latest?plcId=PLC-A&dbNumber=21', '/api/v1/acquisition-data/history/1'):
            response = await client.get(path)
            assert response.status_code == 200
            for token in tokens:
                assert b'"value":' + token.encode() in response.content
            data = json.loads(response.content, parse_float=Decimal, parse_int=Decimal)
            items = data['data'].get('items', data['data'].get('points'))
            assert items[0]['value'] == Decimal(tokens[0])
            assert items[1]['value'] == Decimal(tokens[1])
            assert items[2]['value'].is_signed()
            assert items[3]['value'] == Decimal(tokens[3])


@pytest.mark.asyncio
async def test_duplicate_query_parameters_without_authentication():
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    path = '/api/v1/acquisition-data/latest?plcId=PLC-A&plcId=PLC-A&dbNumber=21'
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture', trust_env=False) as client:
        assert (await client.get(path)).status_code == 422
        assert (await client.get(path, headers={'Authorization': 'Bearer invalid'})).status_code == 422
        machine = '/api/v1/integration/plc-facts/samples?x=1&x=1'
        assert (await client.post(machine, json=sample())).status_code == 422


@pytest.mark.asyncio
async def test_upsert_uses_ordering_fields_last():
    parsed, _, _ = v2_domain.parse_sample(encoded(sample()))
    statements = []
    class Session:
        async def execute(self, statement): statements.append(statement)
    observed, expires = v2_domain.validate_times(parsed, NOW)
    await async_v2.advance_latest(Session(), parsed, observed, expires)
    sql = str(statements[0].compile(dialect=dialect()))
    update = sql.split('ON DUPLICATE KEY UPDATE', 1)[1]
    assert update.index('point_name =') < update.index('source_seq =') < update.index('source_generation =') < update.index('instance_id =')
    assert 'CASE WHEN' in update


def test_mixed_cleanup_candidates_are_bounded():
    stamp = datetime(2026, 11, 10, 10)
    samples = [SimpleNamespace(id=index, expires_at=stamp, size=1) for index in range(1, 201)]
    points = [SimpleNamespace(plc_id=b'plc', db_number=1, point_id=str(index).encode(), expires_at=stamp,
                              instance_id=b'daa', source_generation=b'gen', source_seq=1, size=1)
              for index in range(200)]
    class Session:
        calls = 0
        def execute(self, _statement):
            self.calls += 1
            return samples if self.calls == 1 else points
    rows = sync_v2_maintenance.candidates(Session(), stamp, 200, True)
    assert len(rows) == 200


def test_cleanup_tick_never_exceeds_2000(monkeypatch):
    events = []
    setup = []
    def target(*_):
        setup.append('target')
        return NOW
    monkeypatch.setattr(maintenance.crud, 'target_now', target)
    monkeypatch.setattr(maintenance.crud, 'candidates', lambda _db, _now, limit, _lock, _deadline:
                        [(NOW, index % 2, (index,), 1) for index in range(limit)])
    monkeypatch.setattr(maintenance.crud, 'clear', lambda _db, row, _now: events.append(row) or 1)
    monkeypatch.setattr(maintenance.crud, 'oldest', lambda *_: None)
    monkeypatch.setattr(maintenance.crud, 'database_time', lambda *_: NOW)
    class Session:
        def execute(self, statement): setup.append(str(statement))
        def commit(self): pass
        def rollback(self): pass
    result = maintenance.run(Session(), {}, True)
    assert result['rows'] == len(events) == 2000
    assert setup.count('target') == 10
    for index, value in enumerate(setup):
        if value == 'target':
            assert setup[index - 3:index] == ['SET SESSION innodb_lock_wait_timeout = 1',
                                              'SET SESSION lock_wait_timeout = 1',
                                              'SET SESSION max_execution_time = 1000']


def test_cleanup_deadline_after_target_prevents_lock_and_report_probe(monkeypatch):
    clock = SimpleNamespace(value=0.0)
    events = []
    monkeypatch.setattr(maintenance, 'time', SimpleNamespace(monotonic=lambda: clock.value))
    def target(*_):
        events.append('target')
        clock.value = 2.001
        return NOW
    monkeypatch.setattr(maintenance.crud, 'target_now', target)
    monkeypatch.setattr(maintenance.crud, 'candidates', lambda *_: pytest.fail('late lock query'))
    monkeypatch.setattr(maintenance.crud, 'oldest', lambda *_: pytest.fail('late backlog query'))
    monkeypatch.setattr(maintenance.crud, 'database_time', lambda *_: NOW)
    class Session:
        def execute(self, statement): events.append(str(statement))
        def commit(self): events.append('commit')
        def rollback(self): events.append('rollback')
    result = maintenance.run(Session(), {}, True)
    assert events[:3] == ['SET SESSION innodb_lock_wait_timeout = 1', 'SET SESSION lock_wait_timeout = 1',
                          'SET SESSION max_execution_time = 1000']
    assert events.count('target') == 1 and result['rows'] == 0 and not result['oldestKnown']


def test_cleanup_deadline_between_candidate_queries(monkeypatch):
    clock = SimpleNamespace(value=0.0)
    monkeypatch.setattr(sync_v2_maintenance, 'time', SimpleNamespace(monotonic=lambda: clock.value))
    class Session:
        calls = 0
        def execute(self, _statement):
            self.calls += 1
            clock.value = 2.001
            return []
    db = Session()
    assert sync_v2_maintenance.candidates(db, NOW, 200, True, 2.0) == []
    assert db.calls == 1


def test_cleanup_deadline_after_settings_never_takes_target_lock(monkeypatch):
    clock = SimpleNamespace(value=0.0)
    monkeypatch.setattr(maintenance, 'time', SimpleNamespace(monotonic=lambda: clock.value))
    monkeypatch.setattr(maintenance.crud, 'target_now', lambda *_: pytest.fail('late target lock'))
    class Session:
        calls = 0
        def execute(self, _statement):
            self.calls += 1
            if self.calls == 3: clock.value = 2.001
        def rollback(self): pass
    with pytest.raises(TimeoutError):
        maintenance.run(Session(), {}, True)


def test_cleanup_cli_requires_nonblank_approval_before_database(capsys):
    entry = Path(__file__).resolve().parents[1] / 'scripts/plc_facts_maintenance/main.py'
    module = runpy.run_path(str(entry), run_name='be012_cli_test')
    args = ['cleanup-v2', '--plan', '--target-alias', 'fixture', '--schema', 'fixture_schema',
            '--expected-server-uuid', '00000000-0000-4000-8000-000000000001',
            '--expected-schema-revision', '3d5f7a9c1e23', '--operation-approval', ' ', '--confirmed-by', 'fixture']
    assert module['main'](args) == 1
    assert 'maintenance_failed' in capsys.readouterr().out


@pytest.mark.skip(reason='BE012 B runner is executed only from its preserved pre-retirement candidate')
def test_b_fixture_size_date_and_paired_ports(monkeypatch, tmp_path):
    import asyncio
    import importlib.util
    target = {'ARCH_BE012_B_OPERATION_APPROVAL': 'synthetic', 'ARCH_BE012_B_TARGET_ALIAS': 'arch-be012-r4-dev',
              'ARCH_BE012_B_SCHEMA': 'arch_be012_r4_dev_fresh',
              'ARCH_BE012_B_SERVER_UUID': '00000000-0000-4000-8000-000000000001',
              'ARCH_BE012_B_MYSQL_PORT': '13392', 'ARCH_BE012_B_HTTP_PORT': '18392',
              'ARCH_BE012_B_TOKEN': TOKEN, 'PLC_FACTS_V2_PROFILE_FILE': '/private/tmp/synthetic-profile',
              'MYSQL_HOST': '127.0.0.1', 'MYSQL_PORT': '13392', 'MYSQL_USER': 'fixture',
              'MYSQL_DATABASE': 'different', 'TEST_MYSQL_DATABASE': 'arch_be012_r4_dev_fresh', 'TESTING': 'True'}
    target['ARCH_BE012_B_CONFIRM'] = ':'.join(('RUN', target['ARCH_BE012_B_TARGET_ALIAS'], target['ARCH_BE012_B_SCHEMA'],
                                                target['ARCH_BE012_B_SERVER_UUID'], '13392', '18392'))
    for key, value in target.items():
        monkeypatch.setenv(key, value)
    path = Path(__file__).resolve().parents[1] / 'tests_mysql/test_plc_facts_v2.py'
    def module():
        spec = importlib.util.spec_from_file_location('be012_b_fixture_source', path)
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result
    fixture = module()
    backend = path.parents[1]
    fixture.require_copy_imports(backend)
    original_find_spec = importlib.util.find_spec
    with monkeypatch.context() as guarded:
        guarded.setattr(importlib.util, 'find_spec', lambda name: SimpleNamespace(origin='/private/tmp/other/settings.py')
                        if name == 'settings' else original_find_spec(name))
        with pytest.raises(RuntimeError, match='isolated source'):
            fixture.require_copy_imports(backend)
    with monkeypatch.context() as guarded:
        guarded.chdir(tmp_path)
        with pytest.raises(RuntimeError, match='working directory'):
            fixture.require_copy_imports(backend)
    batches = []
    class Session:
        def execute(self, _statement, rows): batches.append(rows)
        def commit(self): pass
        def close(self): pass
    monkeypatch.setattr(fixture, 'create_sync_session', Session)
    fixture.seed_expired_fixture(NOW)
    assert sum(len(batch) for batch in batches) == 10000
    first = batches[0][0]
    assert len(encoded({'points': first['points_json']})) <= 16 * 1024
    assert NOW - timedelta(hours=24) < first['expires_at'] <= NOW
    clock = SimpleNamespace(value=0.0)
    async def sleep(seconds):
        clock.value += seconds
    async def to_thread(function, *args):
        return function(*args)
    monkeypatch.setattr(fixture, 'root', tmp_path / 'source')
    monkeypatch.setattr(fixture, 'time', SimpleNamespace(monotonic=lambda: clock.value))
    monkeypatch.setattr(fixture, 'asyncio', SimpleNamespace(sleep=sleep, to_thread=to_thread, TaskGroup=asyncio.TaskGroup))
    monkeypatch.setattr(fixture, 'run_cleanup_once', lambda: {
        'completedAt': NOW.isoformat(), 'oldestExpiredAt': None, 'oldestKnown': True, 'rows': 0, 'bytes': 0})
    monkeypatch.setattr(fixture, 'expired_fixture_count', lambda _now: 0)
    evidence = tmp_path / 'evidence/cleanup-ticks.jsonl'
    monkeypatch.setenv('ARCH_BE012_B_TICK_EVIDENCE', str(evidence))
    assert asyncio.run(fixture.cleanup_for_load({'now': NOW}, 0)) == 0
    ticks = [json.loads(line) for line in evidence.read_text().splitlines()]
    assert len(ticks) == 30 and [tick['tick'] for tick in ticks] == list(range(1, 31))
    assert ticks[-1]['elapsedSeconds'] == 1740 and all(tick['remainingFixtureRows'] == 0 for tick in ticks)

    monkeypatch.setenv('ARCH_BE012_B_RUN_LOAD', 'True')
    monkeypatch.setattr(fixture, 'LOAD_SAMPLES_PER_PLC', 2)
    monkeypatch.setattr(fixture, 'seed_expired_fixture', lambda _now: None)
    monkeypatch.setattr(fixture, 'seed_unexpired_sentinel', lambda _now: None)
    monkeypatch.setattr(fixture, 'assert_unexpired_sentinel', lambda _now: None)
    monkeypatch.setattr(fixture, 'expired_fixture_count', lambda _now: 10000)
    async def cleanup(_target, _started, aggregate):
        aggregate.update(ticks=30, rows=10000, bytes=123, remainingFixtureRows=0, clearedSeconds=10)
        return 10
    monkeypatch.setattr(fixture, 'cleanup_for_load', cleanup)
    class Client:
        def __init__(self, **_kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *_args): pass
    class FinishedSession:
        def get(self, *_args): return SimpleNamespace(source_seq=100000, value_json=None, expires_at=None)
        def rollback(self): pass
        def close(self): pass
    monkeypatch.setattr(fixture, 'AsyncClient', Client)
    monkeypatch.setattr(fixture, 'create_sync_session', FinishedSession)
    target_state = lambda: {'now': NOW, 'sequence': 0}
    monkeypatch.setenv('ARCH_BE012_B_LOAD_EVIDENCE', str(tmp_path / 'wrong.json'))
    with pytest.raises(RuntimeError, match='round-owned'):
        asyncio.run(fixture.test_steady_load_and_cleanup_capacity(target_state()))
    monkeypatch.setattr(fixture, 'root', tmp_path / 'failure/source')
    failure_path = tmp_path / 'failure/evidence/load-summary.json'
    monkeypatch.setenv('ARCH_BE012_B_LOAD_EVIDENCE', str(failure_path))
    async def failed_send(_client, _raw): return SimpleNamespace(status_code=503)
    monkeypatch.setattr(fixture, 'send', failed_send)
    with pytest.raises(ExceptionGroup):
        asyncio.run(fixture.test_steady_load_and_cleanup_capacity(target_state()))
    failure = json.loads(failure_path.read_text())
    assert failure['status'] == 'failed' and failure['failed'] > 0
    assert failure['attempted'] == failure['success'] + failure['failed']
    monkeypatch.setattr(fixture, 'root', tmp_path / 'success/source')
    success_path = tmp_path / 'success/evidence/load-summary.json'
    monkeypatch.setenv('ARCH_BE012_B_LOAD_EVIDENCE', str(success_path))
    async def successful_send(_client, _raw): return SimpleNamespace(status_code=200)
    monkeypatch.setattr(fixture, 'send', successful_send)
    asyncio.run(fixture.test_steady_load_and_cleanup_capacity(target_state()))
    saved = success_path.read_text()
    result = json.loads(saved)
    assert result['status'] == 'passed' and (result['attempted'], result['success'], result['failed']) == (4, 4, 0)
    assert result['p95Ms'] == 0 and result['cleanup']['ticks'] == 30
    for plc in ('PLC-A', 'PLC-B'):
        counts = result['plcs'][plc]
        assert counts['pointCounts'] == {'64': 2} and counts['pointsTotal'] == 128
        assert counts['bodyBytesMin'] > 0 and counts['bodyBytesMax'] >= counts['bodyBytesMin']
    assert TOKEN not in saved and 'Authorization' not in saved and len(saved) <= 8192
    monkeypatch.setenv('ARCH_BE012_B_HTTP_PORT', '18393')
    with pytest.raises(RuntimeError, match='target guard'):
        module()


def test_business_runner_accepts_only_guarded_previous_and_successor(monkeypatch, tmp_path):
    import importlib.util
    path = Path(__file__).resolve().parents[1] / 'tests_mysql/test_business_integration.py'
    spec = importlib.util.spec_from_file_location('be012_business_runner_source', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    backend = path.parents[1]
    module.require_copy_imports(backend)
    original_find_spec = importlib.util.find_spec
    with monkeypatch.context() as guarded:
        guarded.setattr(importlib.util, 'find_spec', lambda name: SimpleNamespace(origin='/private/tmp/other/database.py')
                        if name == 'database' else original_find_spec(name))
        with pytest.raises(RuntimeError, match='isolated source'):
            module.require_copy_imports(backend)
    with monkeypatch.context() as guarded:
        guarded.chdir(tmp_path)
        with pytest.raises(RuntimeError, match='working directory'):
            module.require_copy_imports(backend)
    schema = 'arch_be012_r4_dev_upgrade'
    server = '00000000-0000-4000-8000-000000000001'
    values = {'BE010_SUCCESSOR_ACK': 'ARCH-BE-012-r4-successor', 'ARCH_BE012_B_SERVER_UUID': server,
              'MYSQL_PORT': '13392', 'ARCH_BE012_B_HTTP_PORT': '18392', 'ARCH_BE012_B_TARGET_ALIAS': 'arch-be012-r4-dev',
              'TEST_MYSQL_DATABASE': schema, 'MYSQL_DATABASE': 'different', 'MYSQL_HOST': '127.0.0.1',
              'MYSQL_USER': 'fixture', 'TESTING': 'True', 'BE010_MYSQL_EXECUTION_ACK': 'ARCH-BE-010-r2-B',
              'BE010_MYSQL_SCHEMA_ACK': schema, 'BE010_MYSQL_ENDPOINT_ACK': '127.0.0.1:13392',
              'ARCH_BE012_B_CONFIRM': ':'.join(('RUN', 'arch-be012-r4-dev', schema, server, '13392', '18392'))}
    for key, value in values.items(): monkeypatch.setenv(key, value)
    profile_data = {'profile': 'BE010-r2-B', 'expected_table_count': 75, 'target_revision': '1b3d5f7a9c20'}
    for phase, revision in (('previous', '1b3d5f7a9c20'), ('successor', '2c4e6a8b0d12')):
        monkeypatch.setenv('BE010_R4_PHASE', phase)
        monkeypatch.setenv('BE010_SUCCESSOR_REVISION', revision)
        assert module.guard_configuration(tmp_path, profile_data) == (phase, revision)
    monkeypatch.setenv('ARCH_BE012_B_HTTP_PORT', '18393')
    with pytest.raises(AssertionError):
        module.guard_configuration(tmp_path, profile_data)


@pytest.mark.asyncio
async def test_b_http_clients_ignore_proxy_environment(monkeypatch):
    import ast
    import httpx
    monkeypatch.setenv('HTTP_PROXY', 'http://192.0.2.1:9999')
    monkeypatch.setenv('NO_PROXY', '')
    source = Path(__file__).resolve().parents[1] / 'tests_mysql/test_plc_facts_v2.py'
    tree = ast.parse(source.read_text())
    clients = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
               and isinstance(node.func, ast.Name) and node.func.id == 'AsyncClient']
    assert clients
    assert all(any(keyword.arg == 'trust_env' and isinstance(keyword.value, ast.Constant)
                   and keyword.value.value is False for keyword in node.keywords) for node in clients)
    async with httpx.AsyncClient(base_url='http://127.0.0.1:18392', trust_env=False) as client:
        assert not client._mounts


@pytest.mark.asyncio
async def test_http_source_scope_body_limit_and_detail_path(monkeypatch):
    profile_value = v2_config.parse_profile(profile())
    monkeypatch.setattr(api, 'get_profile', lambda: profile_value)
    class Session:
        async def close(self): pass
    async def session(): return Session()
    async def write(_db, _profile, body, _document, _digest, _boundary):
        v2_config.admit_source(profile_value, body)
        return service.receipt(body, 'created')
    monkeypatch.setattr(service, 'write_sample', write)
    async def no_session(): raise AssertionError('bad request must not obtain a session')
    monkeypatch.setattr(api, 'get_db_session', session)
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    specification = app.openapi()
    assert '/api/v1/acquisition-data/history/{id}' in specification['paths']
    post = specification['paths']['/api/v1/integration/plc-facts/samples']['post']
    assert post['requestBody']['content']['application/json']['schema']['$ref'].endswith('/SampleV2In')
    assert not specification['components'].get('securitySchemes')
    for path in specification['paths'].values():
        for operation in path.values():
            assert not operation.get('security') and '401' not in operation['responses']
    assert set(post['responses']) == {'200', '403', '409', '410', '413', '415', '422', '503'}
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture') as client:
        wrong_source = dict(sample(), instanceId='unregistered')
        response = await client.post('/api/v1/integration/plc-facts/samples', json=wrong_source)
        assert response.status_code == 403
        assert response.json()['errorCode'] == 'plc_facts_v2.scope_rejected'
        monkeypatch.setattr(api, 'get_db_session', no_session)
        response = await client.post('/api/v1/integration/plc-facts/samples', content=b' ' * 524289,
                                     headers={'Content-Type': 'application/json'})
        assert response.status_code == 413
        assert response.json()['data'] is None
        malformed = sample()
        malformed['dbNumber'] = True
        response = await client.post('/api/v1/integration/plc-facts/samples', json=malformed)
        assert response.status_code == 422
        assert response.json()['errorCode'] == 'plc_facts_v2.invalid_request'
        monkeypatch.setattr(api, 'get_profile', lambda: (_ for _ in ()).throw(v2_domain.V2Error('not_ready', 503)))
        response = await client.post('/api/v1/integration/plc-facts/samples', json=sample())
        assert response.status_code == 503
        assert response.json()['errorCode'] == 'plc_facts_v2.not_ready'


@pytest.mark.asyncio
async def test_http_success_uses_frozen_body_and_reports_close_failure(monkeypatch):
    profile_value = v2_config.parse_profile(profile())
    monkeypatch.setattr(api, 'get_profile', lambda: profile_value)
    seen = []
    class Session:
        fail_close = False
        async def close(self):
            if self.fail_close:
                raise OSError('synthetic close failure')
    session = Session()
    async def get_session(): return session
    async def write(_db, _profile, parsed, _document, digest, boundary):
        seen.append(digest)
        boundary['commit_attempted'] = True
        boundary['committed'] = True
        return service.receipt(parsed, 'created')
    monkeypatch.setattr(api, 'get_db_session', get_session)
    monkeypatch.setattr(service, 'write_sample', write)
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    raw = encoded(sample()) + b' '
    headers = {'Content-Type': 'application/json'}
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture') as client:
        response = await client.post('/api/v1/integration/plc-facts/samples', content=raw, headers=headers)
        assert response.status_code == 200 and response.json()['data']['outcome'] == 'created'
        assert seen == [hashlib.sha256(raw).digest()]
        session.fail_close = True
        response = await client.post('/api/v1/integration/plc-facts/samples', content=raw, headers=headers)
        assert response.status_code == 503
        assert response.json()['errorCode'] == 'plc_facts_v2.commit_outcome_unknown'


def test_normal_app_registers_acquisition_without_authentication():
    import sys
    import app as app_package
    from core.registrar import create_app
    previous = sys.modules.pop('app.router', None)
    old_attribute = getattr(app_package, 'router', None)
    try:
        app = create_app(testing=True)
        paths = {getattr(route, 'path', None) for route in app.routes}
        assert {'/api/v1/integration/plc-facts/batches', '/api/v1/integration/plc-facts/latest',
                '/api/v1/integration/plc-facts/history'}.isdisjoint(paths)
        assert '/api/v1/integration/plc-facts/samples' in paths
        assert '/api/v1/acquisition-data/history/{id}' in paths
        operations = app.openapi()['paths']
        assert not operations['/api/v1/acquisition-data/history/{id}']['get'].get('security')
        assert operations['/api/v1/auth/me']['get']['security'] == [{'HTTPBearer': []}]
    finally:
        sys.modules.pop('app.router', None)
        if previous is not None:
            sys.modules['app.router'] = previous
        if old_attribute is None:
            if hasattr(app_package, 'router'):
                delattr(app_package, 'router')
        else:
            app_package.router = old_attribute


def test_published_contract_matches_runtime_models():
    from app.plc_facts.schemas.v2 import SampleV2In
    contract = Path(__file__).resolve().parents[2] / 'contracts/published/http-api/plc-facts-v2'
    app = FastAPI(title='PLC Facts v2', version='2')
    app.include_router(api.router, prefix='/api/v1')
    assert json.loads((contract / 'openapi-acquisition-dev-r4.json').read_text()) == app.openapi()
    expected = SampleV2In.model_json_schema(by_alias=True)
    published = json.loads((contract / 'schema-acquisition-r2.json').read_text())
    published.pop('$schema')
    published.pop('description')
    assert published == expected
    vectors = json.loads((contract / 'vectors-acquisition-r2.json').read_text())
    assert v2_domain.parse_sample(encoded(vectors['sample']))[0].sample_id == vectors['created']['data']['sampleId']
    assert vectors['duplicate']['data']['outcome'] == 'duplicate'
