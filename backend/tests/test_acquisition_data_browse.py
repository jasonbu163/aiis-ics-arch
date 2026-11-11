"""采集数据 r2 来源准入、授权交集、字面搜索与分页合同。"""
from copy import deepcopy
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.mysql import dialect

from app.plc_facts import v2_config, v2_domain
from app.plc_facts.api import v2 as api
from app.plc_facts.crud import async_v2 as crud
from app.plc_facts.services import async_v2 as service
from tests.test_plc_facts_v2 import TOKEN, encoded, profile, sample

pytestmark = pytest.mark.no_db
NOW = datetime(2026, 11, 10, 10, 0, 3)


def mixed_profile():
    doc = profile()
    doc['instances'].append({'instanceId': 'external-b', 'sourceType': 'external'})
    doc['sources'].append({'plcId': 'PLC-B', 'instanceId': 'external-b',
                           'sourceGeneration': 'gen-b', 'dbNumbers': [22, 23]})
    doc['readScopes']['admin'] = [{'plcId': 'PLC-A', 'dbNumbers': [21, 22]},
                                  {'plcId': 'PLC-B', 'dbNumbers': [22, 23]}]
    doc['readScopes']['supervisor'] = [{'plcId': 'PLC-A', 'dbNumbers': [21]},
                                       {'plcId': 'PLC-B', 'dbNumbers': [23]}]
    doc['readScopes']['empty'] = []
    return doc


@pytest.mark.parametrize('case', ['missing', 'duplicate', 'unknown_kind', 'trailing_space_kind', 'nul_kind',
                                  'unregistered_credential', 'unregistered_source'])
def test_profile_rejects_unregistered_or_invalid_instances(case):
    doc = mixed_profile()
    if case == 'missing': doc.pop('instances')
    elif case == 'duplicate': doc['instances'].append(deepcopy(doc['instances'][0]))
    elif case == 'unknown_kind': doc['instances'][0]['sourceType'] = 'DAA'
    elif case == 'trailing_space_kind': doc['instances'][1]['sourceType'] = 'external '
    elif case == 'nul_kind': doc['instances'][0]['sourceType'] = 'daa\x00'
    elif case == 'unregistered_credential': doc['credentials'][0]['instanceId'] = 'other'
    else: doc['sources'][0]['instanceId'] = 'other'
    with pytest.raises((ValueError, v2_domain.V2Error)):
        v2_config.parse_profile(doc)


@pytest.mark.parametrize('field', ['groupId', 'configRevision'])
@pytest.mark.parametrize('form', ['omitted', 'null'])
def test_metadata_depends_on_registered_source_and_raw_body(field, form):
    doc = mixed_profile()
    registered = v2_config.parse_profile(doc)
    body = sample(1)
    if form == 'omitted': body.pop(field)
    else: body[field] = None
    parsed, _, digest = v2_domain.parse_sample(encoded(body))
    with pytest.raises(v2_domain.V2Error) as error:
        v2_config.admit_source(registered, 'daa-a', parsed)
    assert error.value.status == 422
    body.update(instanceId='external-b', plcId='PLC-B', dbNumber=22, sourceGeneration='gen-b')
    parsed, _, _ = v2_domain.parse_sample(encoded(body))
    v2_config.admit_source(registered, 'external-b', parsed)
    alternate = dict(body)
    if field in alternate: alternate.pop(field)
    else: alternate[field] = None
    assert v2_domain.parse_sample(encoded(alternate))[2] != v2_domain.parse_sample(encoded(body))[2]
    body[field] = ''
    with pytest.raises(v2_domain.V2Error): v2_domain.parse_sample(encoded(body))
    assert len(digest) == 32


def test_source_type_is_not_a_caller_controlled_field():
    body = sample(1)
    body['sourceType'] = 'external'
    with pytest.raises(v2_domain.V2Error) as error:
        v2_domain.parse_sample(encoded(body))
    assert error.value.status == 422


def test_authorized_scope_intersection_does_not_create_cross_product():
    value = v2_config.parse_profile(mixed_profile())
    assert service.matching_scope(value, 'supervisor', None, None) == {'PLC-A': {21}, 'PLC-B': {23}}
    assert service.matching_scope(value, 'supervisor', None, 23) == {'PLC-B': {23}}
    assert service.matching_scope(value, 'supervisor', 'PLC-A', None) == {'PLC-A': {21}}
    assert service.matching_scope(value, 'empty', None, None) == {}
    with pytest.raises(v2_domain.V2Error) as denied:
        service.matching_scope(value, 'supervisor', 'PLC-A', 23)
    assert denied.value.status == 403
    with pytest.raises(v2_domain.V2Error):
        service.matching_scope(value, 'empty', None, 21)


class QueryResult:
    def __init__(self, total=0): self.total = total
    def scalar_one(self): return self.total
    def scalars(self): return iter([])
    def all(self): return []


class SQLCapture:
    def __init__(self, total=0): self.statements, self.total = [], total
    async def execute(self, statement):
        self.statements.append(statement)
        return QueryResult(self.total)


@pytest.mark.asyncio
async def test_sql_scope_current_source_order_and_literal_search():
    value = v2_config.parse_profile(mixed_profile())
    scope = service.matching_scope(value, 'supervisor', None, None)
    session = SQLCapture(total=25)
    total, rows = await crud.browse_latest(session, scope, value['sources'], r'_%\\Temp', 2, 10, NOW)
    assert total == 25 and rows == [] and len(session.statements) == 2
    count_sql = str(session.statements[0].compile(dialect=dialect()))
    page = session.statements[1].compile(dialect=dialect())
    page_sql = str(page)
    assert 'plc_facts_latest.instance_id' in count_sql and 'plc_facts_latest.source_generation' in count_sql
    assert 'plc_facts_latest.expires_at >' in count_sql and ' OR ' in count_sql
    assert 'ORDER BY plc_facts_latest.plc_id, plc_facts_latest.db_number, plc_facts_latest.point_id' in page_sql
    assert r'%\_\%\\\\Temp%' in page.params.values()
    assert list(page.params.values()).count(10) >= 2
    history = SQLCapture()
    await crud.history(history, scope, NOW.replace(hour=9), NOW, 1, 50, NOW)
    hsql = str(history.statements[0].compile(dialect=dialect()))
    assert 'plc_facts_history.plc_id' in hsql and 'plc_facts_history.db_number' in hsql and ' OR ' in hsql


@pytest.mark.asyncio
async def test_revocation_preserves_readable_source_and_exact_point(monkeypatch):
    doc = mixed_profile()
    doc['credentials'] = []
    value = v2_config.parse_profile(doc)
    row = SimpleNamespace(point_id=b'point-0', point_name=None, data_type='BOOL', value_json=False,
                          quality='good', reason=None, observed_at=NOW, instance_id=b'daa-a',
                          source_generation=b'gen-a', source_seq=1, sample_id=b's1')
    calls = []
    async def now(*_): return NOW
    async def latest(_db, plc, number, source, _now, point_id):
        calls.append((plc, number, source, point_id))
        return [row] if point_id == 'point-0' else []
    monkeypatch.setattr(crud, 'target_now', now)
    monkeypatch.setattr(crud, 'latest', latest)
    with pytest.raises(v2_domain.V2Error) as invalid:
        v2_config.authenticate(value, 'Bearer ' + TOKEN)
    assert invalid.value.status == 401
    actual = await service.latest(object(), value, 'admin', 'PLC-A', 21, 'point-0')
    assert actual['items'][0]['sourceType'] == 'daa'
    assert (await service.latest(object(), value, 'admin', 'PLC-A', 21, 'POINT-0'))['items'] == []
    assert calls[0][3] == 'point-0'


@pytest.mark.asyncio
async def test_http_default_optional_filters_limits_and_nullable_history(monkeypatch):
    value = v2_config.parse_profile(mixed_profile())
    monkeypatch.setattr(api, 'get_profile', lambda: value)
    calls = []
    class Session:
        async def close(self): pass
    async def session(): return Session()
    async def now(*_): return NOW
    async def browse(_db, scope, _sources, search, page, page_size, _now):
        calls.append((scope, search, page, page_size))
        return 0, []
    old = SimpleNamespace(id=1, instance_id=b'old', sample_id=b's1', plc_id=b'PLC-A', db_number=21,
                          group_id=None, config_revision=None, source_type=None, source_generation=b'g',
                          source_seq=1, sampled_at=NOW, stored_at=NOW)
    async def history(_db, scope, *_):
        calls.append(scope)
        return 1, [(old, 1)]
    monkeypatch.setattr(api, 'get_db_session', session)
    monkeypatch.setattr(crud, 'target_now', now)
    monkeypatch.setattr(crud, 'browse_latest', browse)
    monkeypatch.setattr(crud, 'history', history)
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    app.dependency_overrides[api.reader] = lambda: SimpleNamespace(role='supervisor')
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture', trust_env=False) as client:
        path = '/api/v1/acquisition-data/latest/browse'
        result = await client.get(path)
        assert result.status_code == 200 and result.json()['data']['pageSize'] == 50
        assert calls[-1] == ({'PLC-A': {21}, 'PLC-B': {23}}, '', 1, 50)
        result = await client.get(path, params={'dbNumber': 23, 'pointSearch': '  %_  ', 'page': 2, 'pageSize': 10})
        assert result.status_code == 200 and calls[-1] == ({'PLC-B': {23}}, '%_', 2, 10)
        assert (await client.get(path, params={'plcId': 'PLC-A', 'dbNumber': 23})).status_code == 403
        assert (await client.get(path, params={'pointSearch': 'a' * 129})).status_code == 422
        assert (await client.get(path, params={'pageSize': 101})).status_code == 422
        history_path = '/api/v1/acquisition-data/history'
        params = {'from': '2026-11-09T10:00:03+08:00', 'to': '2026-11-10T10:00:03+08:00'}
        result = await client.get(history_path, params=params)
        assert result.status_code == 200
        item = result.json()['data']['items'][0]
        assert item['groupId'] is None and item['configRevision'] is None and item['sourceType'] is None
        assert calls[-1] == {'PLC-A': {21}, 'PLC-B': {23}}
        params['from'] = '2026-11-02T10:00:03+08:00'
        assert (await client.get(history_path, params=params)).status_code == 422


@pytest.mark.asyncio
async def test_http_machine_sources_auth_and_raw_body_policy(monkeypatch):
    import hashlib
    doc = mixed_profile()
    external_token = 'fixture-external-token-with-32-bytes'
    doc['credentials'].append({'instanceId': 'external-b',
                               'tokenSha256': hashlib.sha256(external_token.encode()).hexdigest()})
    value = v2_config.parse_profile(doc)
    monkeypatch.setattr(api, 'get_profile', lambda: value)
    digests = []
    class Session:
        async def close(self): pass
    async def session(): return Session()
    async def write(_db, _profile, body, _document, digest, _boundary):
        digests.append((body.instance_id, body.group_id, body.config_revision, digest))
        return service.receipt(body, 'created')
    monkeypatch.setattr(api, 'get_db_session', session)
    monkeypatch.setattr(service, 'write_sample', write)
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    path = '/api/v1/integration/plc-facts/samples'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN}
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture', trust_env=False) as client:
        daa = sample(1)
        assert (await client.post(path, content=encoded(daa), headers=headers)).status_code == 200
        for field in ('groupId', 'configRevision'):
            invalid = dict(daa)
            invalid.pop(field)
            assert (await client.post(path, content=encoded(invalid), headers=headers)).status_code == 422
            invalid[field] = None
            assert (await client.post(path, content=encoded(invalid), headers=headers)).status_code == 422
        assert (await client.post(path, content=encoded(daa), headers={**headers, 'Authorization': 'Bearer wrong'})).status_code == 401
        assert (await client.post(path, content=encoded(daa), headers={**headers, 'Authorization': 'Bearer ' + external_token})).status_code == 403
        external = dict(daa, instanceId='external-b', plcId='PLC-B', dbNumber=22, sourceGeneration='gen-b')
        external.pop('groupId')
        external.pop('configRevision')
        ext_headers = {**headers, 'Authorization': 'Bearer ' + external_token}
        assert (await client.post(path, content=encoded(external), headers=ext_headers)).status_code == 200
        external['groupId'] = None
        assert (await client.post(path, content=encoded(external), headers=ext_headers)).status_code == 200
        assert digests[-1][3] != digests[-2][3]
        external['sourceType'] = 'daa'
        assert (await client.post(path, content=encoded(external), headers=ext_headers)).status_code == 422


@pytest.mark.asyncio
async def test_mysql_authorized_ingest_browse_and_cleanup(monkeypatch):
    """仅显式授权的任务独占 schema：真实事务、授权分页及清理。"""
    import hashlib
    import os
    import re
    import uuid
    from datetime import timedelta
    from pathlib import Path
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import make_url
    from sqlalchemy.orm import Session
    from sqlalchemy.pool import NullPool
    from app.plc_facts.crud import sync_v2_maintenance as sync_crud
    from app.plc_facts.services import sync_v2_maintenance as cleanup
    from settings import settings

    if os.environ.get('ARCH_ACQ003_LIVE_READ_WRITE') != 'ACQ003-ISOLATED':
        pytest.skip('explicit isolated task fixture required')
    round_name = os.environ.get('ARCH_ACQ003_FIXTURE_ROUND')
    server_uuid = os.environ.get('ARCH_ACQ003_FIXTURE_UUID', '')
    port = os.environ.get('ARCH_ACQ003_FIXTURE_PORT')
    schema = os.environ.get('ARCH_ACQ003_SCHEMA_UPGRADE')
    schema_names = tuple(os.environ.get('ARCH_ACQ003_SCHEMA_' + suffix.upper())
                         for suffix in ('upgrade', 'renamed', 'altered', 'guard'))
    expected_schemas = tuple(f'arch_acq003_{round_name}_{suffix}'
                             for suffix in ('upgrade', 'renamed', 'altered', 'guard'))
    expected_ack = ':'.join(('ACQ003', round_name or '', server_uuid, port or '', *schema_names))
    url = make_url(settings.SYNC_DATABASE_URL)
    candidate = Path(__file__).resolve().parents[2]
    assert (candidate.is_relative_to(Path('/private/tmp')) and candidate.name.startswith('arch-acq003-r2-candidate-')
            and round_name in ('dev', 'qa') and port in ('3307', '13393', '13394')
            and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', server_uuid)
            and schema_names == expected_schemas and schema == expected_schemas[0]
            and os.environ.get('ARCH_ACQ003_FIXTURE_ACK') == expected_ack
            and settings.TESTING and url.host == '127.0.0.1' and url.port == int(port)
            and url.username == f'arch_acq003_{round_name}' and url.database == schema
            and schema != 'industrial_level_2_system')
    engine = create_engine(url, poolclass=NullPool,
                           connect_args={'connect_timeout': 3, 'read_timeout': 10, 'write_timeout': 10})
    with engine.connect() as connection:
        actual_uuid, actual_schema, version, current_user, offset, now = connection.execute(text('''
            SELECT @@server_uuid, DATABASE(), VERSION(), CURRENT_USER(),
                   TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6)), CURRENT_TIMESTAMP(6)
        ''')).one()
        assert (actual_uuid, actual_schema, version.split('-')[0], current_user.split('@', 1)[0], offset) == (
            server_uuid, schema, '8.4.6', f'arch_acq003_{round_name}', 28800)
        assert connection.execute(text('SELECT version_num FROM alembic_version')).scalar_one() == '5f7a9c1e3b25'
    unique = uuid.uuid4().hex[:12]
    # Keep a separately identified legacy fixture with unknown provenance.
    with engine.begin() as connection:
        result = connection.execute(text('''
            INSERT INTO plc_facts_history
                (instance_id, sample_id, plc_id, db_number, group_id, config_revision, source_generation,
                 source_seq, points_json, content_hash, sampled_at, stored_at, expires_at, source_type)
            SELECT instance_id, :sample, plc_id, db_number, group_id, config_revision, source_generation,
                   :seq, points_json, content_hash, sampled_at, stored_at, expires_at, NULL
            FROM plc_facts_history WHERE instance_id='fixture' AND plc_id='PLC-A' LIMIT 1
        '''), {'sample': 'legacy-null-' + unique, 'seq': int(unique[:10], 16)})
        assert result.rowcount == 1
    plc_a, plc_b = f'ACQ3-A-{unique}', f'ACQ3-B-{unique}'
    instance_daa, instance_ext = f'fixture-daa-{unique}', f'fixture-ext-{unique}'
    token_daa, token_ext = f'daa-secret-{unique}', f'external-secret-{unique}'
    doc = {'target': {'alias': 'fixture', 'serverUuid': server_uuid, 'schema': schema,
                      'schemaRevision': '5f7a9c1e3b25'},
           'instances': [{'instanceId': instance_daa, 'sourceType': 'daa'},
                         {'instanceId': instance_ext, 'sourceType': 'external'}],
           'credentials': [{'instanceId': instance_daa, 'tokenSha256': hashlib.sha256(token_daa.encode()).hexdigest()},
                           {'instanceId': instance_ext, 'tokenSha256': hashlib.sha256(token_ext.encode()).hexdigest()}],
           'sources': [{'plcId': plc_a, 'instanceId': instance_daa, 'sourceGeneration': 'gen-a', 'dbNumbers': [21, 22]},
                       {'plcId': plc_b, 'instanceId': instance_ext, 'sourceGeneration': 'gen-b', 'dbNumbers': [21, 22]}],
           'readScopes': {'admin': [{'plcId': plc_a, 'dbNumbers': [21, 22]}, {'plcId': plc_b, 'dbNumbers': [21, 22]}],
                          'supervisor': [{'plcId': plc_a, 'dbNumbers': [21]}, {'plcId': plc_b, 'dbNumbers': [22]},
                                         {'plcId': 'PLC-A', 'dbNumbers': [21]}], 'empty': []}}
    holder = {'profile': v2_config.parse_profile(doc), 'role': 'supervisor'}
    monkeypatch.setattr(api, 'get_profile', lambda: holder['profile'])
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    app.dependency_overrides[api.reader] = lambda: SimpleNamespace(role=holder['role'])
    observed = v2_domain.wire_time(now - timedelta(seconds=5))
    point_id = r'temp_%\A'
    def point(name, value, kind='BOOL'):
        return {'pointId': name, 'name': name, 'dataType': kind, 'value': value,
                'quality': 'good', 'observedAt': observed}
    def body(instance, plc, number, sequence, sample_name, points):
        result = {'contractVersion': 'plc-facts/v2', 'instanceId': instance, 'sampleId': sample_name,
                  'plcId': plc, 'dbNumber': number, 'sourceGeneration': 'gen-a' if plc == plc_a else 'gen-b',
                  'sourceSeq': str(sequence), 'points': points}
        if instance == instance_daa: result.update(groupId='group', configRevision='config')
        return result
    first = body(instance_daa, plc_a, 21, 100, 'a21-' + unique, [point(point_id, 0, 'REAL')])
    first_raw = encoded(first).replace(b'"value":0', b'"value":1.234567890123456789')
    late = body(instance_daa, plc_a, 21, 99, 'a21-late-' + unique,
                [point(point_id, 9, 'REAL'), point('retro', False)])
    other_a = body(instance_daa, plc_a, 22, 1, 'a22-' + unique, [point('a22', True)])
    ext_21 = body(instance_ext, plc_b, 21, 1, 'b21-' + unique, [point('b21', True)])
    ext_22 = body(instance_ext, plc_b, 22, 1, 'b22-' + unique, [point('b22', False)])
    start, end = v2_domain.wire_time(now - timedelta(days=2)), v2_domain.wire_time(now + timedelta(seconds=30))
    path = '/api/v1/integration/plc-facts/samples'
    def auth(token): return {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture', trust_env=False) as client:
            send = lambda raw, token: client.post(path, content=raw, headers=auth(token))
            created = await send(first_raw, token_daa)
            assert created.status_code == 200 and created.json()['data']['outcome'] == 'created'
            assert (await send(first_raw, token_daa)).json()['data']['outcome'] == 'duplicate'
            for document, token in ((late, token_daa), (other_a, token_daa), (ext_21, token_ext), (ext_22, token_ext)):
                result = await send(encoded(document), token)
                assert result.status_code == 200 and result.json()['data']['outcome'] == 'created'
            assert (await send(encoded(ext_22), token_ext)).json()['data']['outcome'] == 'duplicate'
            with_null = dict(ext_22, groupId=None)
            assert (await send(encoded(with_null), token_ext)).status_code == 409
            missing = dict(first); missing.pop('groupId')
            assert (await send(encoded(missing), token_daa)).status_code == 422
            assert (await send(encoded(dict(ext_22, sourceType='daa')), token_ext)).status_code == 422
            assert (await send(encoded(first), token_ext)).status_code == 403
            assert (await send(encoded(first), 'invalid')).status_code == 401
            latest_path = '/api/v1/acquisition-data/latest'
            exact = await client.get(latest_path, params={'plcId': plc_a, 'dbNumber': 21, 'pointId': point_id})
            assert exact.status_code == 200 and b'1.234567890123456789' in exact.content
            assert exact.json()['data']['items'][0]['sourceSeq'] == '100'
            assert exact.json()['data']['items'][0]['sourceType'] == 'daa'
            assert (await client.get(latest_path, params={'plcId': plc_a, 'dbNumber': 21, 'pointId': 'TEMP_%\\A'})).json()['data']['items'] == []
            retro = await client.get(latest_path, params={'plcId': plc_a, 'dbNumber': 21, 'pointId': 'retro'})
            assert retro.json()['data']['items'][0]['sourceSeq'] == '99'
            browse_path = '/api/v1/acquisition-data/latest/browse'
            result = await client.get(browse_path, params={'page': 1, 'pageSize': 1})
            assert result.status_code == 200 and result.json()['data']['total'] == 3
            assert len(result.json()['data']['items']) == 1
            assert (await client.get(browse_path, params={'plcId': plc_a, 'dbNumber': 22})).status_code == 403
            result = await client.get(browse_path, params={'dbNumber': 22})
            assert result.json()['data']['total'] == 1 and result.json()['data']['items'][0]['sourceType'] == 'external'
            result = await client.get(browse_path, params={'pointSearch': r'_%\a'})
            assert result.status_code == 200 and result.json()['data']['total'] == 1
            history_path = '/api/v1/acquisition-data/history'
            history_result = await client.get(history_path, params={'from': start, 'to': end})
            assert history_result.status_code == 200
            items = history_result.json()['data']['items']
            ext_history = next(item for item in items if item['sampleId'] == ext_22['sampleId'])
            assert ext_history['sourceType'] == 'external' and ext_history['groupId'] is None and ext_history['configRevision'] is None
            old = next(item for item in items if item['sampleId'] == 'legacy-null-' + unique)
            assert old['sourceType'] is None
            detail = await client.get(history_path + '/' + ext_history['id'])
            assert detail.status_code == 200 and detail.json()['data']['instanceId'] == instance_ext
            holder['role'] = 'empty'
            assert (await client.get(browse_path)).json()['data']['total'] == 0
            assert (await client.get(browse_path, params={'dbNumber': 21})).status_code == 403
            holder['role'] = 'supervisor'
            revoked = deepcopy(doc)
            revoked['credentials'] = []
            holder['profile'] = v2_config.parse_profile(revoked)
            assert (await send(first_raw, token_daa)).status_code == 401
            assert (await client.get(latest_path, params={'plcId': plc_a, 'dbNumber': 21})).status_code == 200
        # Force expiry only for this test's synthetic external sample and its one point.
        with engine.begin() as connection:
            result = connection.execute(text('''UPDATE plc_facts_history SET expires_at = :expired
                WHERE instance_id = :instance AND sample_id = :sample'''),
                {'expired': now - timedelta(seconds=1), 'instance': instance_ext, 'sample': ext_22['sampleId']})
            assert result.rowcount == 1
            result = connection.execute(text('''UPDATE plc_facts_latest SET expires_at = :expired
                WHERE plc_id = :plc AND db_number = 22 AND point_id = 'b22' '''),
                {'expired': now - timedelta(seconds=1), 'plc': plc_b})
            assert result.rowcount == 1
        target = holder['profile']['target']
        with Session(engine) as session:
            target_now = sync_crud.target_now(session, target)
            expired = sync_crud.candidates(session, target_now, 200, False)
            row = session.execute(text('''SELECT id, 74 + OCTET_LENGTH(instance_id) + OCTET_LENGTH(sample_id)
                + OCTET_LENGTH(plc_id) + COALESCE(OCTET_LENGTH(group_id), 0)
                + COALESCE(OCTET_LENGTH(config_revision), 0) + OCTET_LENGTH(source_generation)
                + OCTET_LENGTH(points_json) + OCTET_LENGTH(source_type) AS total
                FROM plc_facts_history WHERE instance_id=:instance AND sample_id=:sample'''),
                {'instance': instance_ext, 'sample': ext_22['sampleId']}).one()
            sample_candidate = next(item for item in expired if item[1] == 0 and item[2][0] == row.id)
            assert sample_candidate[3] == row.total and row.total > len('external')
            plan = cleanup.run(session, target, False)
            assert plan['rows'] >= 2 and plan['bytes'] >= sample_candidate[3]
            applied = cleanup.run(session, target, True)
            assert applied['rows'] >= 2 and applied['bytes'] >= sample_candidate[3]
            assert session.execute(text('SELECT COUNT(*) FROM plc_facts_history WHERE id=:id'), {'id': row.id}).scalar_one() == 0
            latest = session.execute(text('''SELECT source_seq, value_json, expires_at FROM plc_facts_latest
                WHERE plc_id=:plc AND db_number=22 AND point_id='b22' '''), {'plc': plc_b}).one()
            assert latest.source_seq == 1 and latest.value_json is None and latest.expires_at is None
    finally:
        engine.dispose()


@pytest.mark.parametrize('kind', ['latest', 'history'])
@pytest.mark.parametrize('page,total,queries', [(1, 0, 1), (1, 2, 2), (2, 2, 2),
                                                 (3, 2, 1), (10**24, 2, 1)])
@pytest.mark.asyncio
async def test_out_of_range_pages_skip_row_query_without_losing_count(kind, page, total, queries):
    value = v2_config.parse_profile(mixed_profile())
    scope = service.matching_scope(value, 'supervisor', None, None)
    class Counted(SQLCapture):
        async def execute(self, statement):
            self.statements.append(statement)
            return QueryResult(total)
    session = Counted()
    if kind == 'latest':
        actual, rows = await crud.browse_latest(session, scope, value['sources'], '', page, 1, NOW)
    else:
        actual, rows = await crud.history(session, scope, NOW.replace(hour=9), NOW, page, 1, NOW)
    assert actual == total and rows == []
    assert len(session.statements) == queries
    if queries == 2:
        compiled = session.statements[1].compile(dialect=dialect())
        assert ' LIMIT ' in str(compiled) and (page - 1) in compiled.params.values()


@pytest.mark.asyncio
async def test_http_huge_page_retains_count_and_page_for_both_lists(monkeypatch):
    value = v2_config.parse_profile(mixed_profile())
    monkeypatch.setattr(api, 'get_profile', lambda: value)
    sessions = []
    class Counted(SQLCapture):
        async def execute(self, statement):
            self.statements.append(statement)
            return QueryResult(2)
        async def close(self): pass
    async def get_session():
        session = Counted()
        sessions.append(session)
        return session
    async def now(*_): return NOW
    monkeypatch.setattr(api, 'get_db_session', get_session)
    monkeypatch.setattr(crud, 'target_now', now)
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    app.dependency_overrides[api.reader] = lambda: SimpleNamespace(role='supervisor')
    huge = 10**24
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture', trust_env=False) as client:
        for path, query in (
            ('/api/v1/acquisition-data/latest/browse', {}),
            ('/api/v1/acquisition-data/history', {'from': '2026-11-09T10:00:03+08:00',
                                               'to': '2026-11-10T10:00:03+08:00'}),
        ):
            response = await client.get(path, params={**query, 'page': str(huge), 'pageSize': 1})
            assert response.status_code == 200
            assert response.json()['data'] == {'items': [], 'total': 2, 'page': huge,
                                                'pageSize': 1, 'totalPages': 2}
            assert len(sessions[-1].statements) == 1
