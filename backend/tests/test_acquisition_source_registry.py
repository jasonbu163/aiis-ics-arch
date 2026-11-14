"""来源管理输入、权限与已提交响应的隔离测试。"""
from types import SimpleNamespace
import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy.dialects.mysql import dialect
from sqlalchemy.exc import OperationalError
from sqlalchemy.schema import CreateTable

from app.plc_facts.api import source_registry as api
from app.plc_facts.crud import async_source_registry as crud
from app.plc_facts.models.source_registry import SourceInitialization
from app.plc_facts.schemas.source_registry import RegistrationIn, UpdateIn
from app.plc_facts.services import async_source_registry as service
from app.plc_facts.services.sync_source_registry_import import restore_generations
from app.plc_facts.v2_config import parse_profile
from app.plc_facts.v2_domain import V2Error, identifier
from core.deps import get_current_active_admin, get_current_user

pytestmark = pytest.mark.no_db


def test_management_openapi_matches_source_and_requires_bearer():
    app = FastAPI(title='AIIS Acquisition Sources Management', version='2')
    app.include_router(api.router, prefix='/api/v1')
    contract = Path(__file__).resolve().parents[2] / 'contracts/published/http-api/plc-facts-v2/openapi-acquisition-sources-r4.json'
    spec = app.openapi()
    assert json.loads(contract.read_text()) == spec
    assert 'HTTPBearer' in spec['components']['securitySchemes']
    assert set(spec['paths']['/api/v1/admin/acquisition-sources']) == {'get', 'post', 'patch'}
    assert all(operation.get('security') for operation in spec['paths']['/api/v1/admin/acquisition-sources'].values())


def source():
    return {'sourceType': 'daa', 'instanceId': 'inst', 'plcId': 'plc/中文',
            'sourceGeneration': 'gen-1', 'registrationRevision': 'revision',
            'createdAt': '2026-11-13T12:00:00.000000+08:00',
            'updatedAt': '2026-11-13T12:00:00.000000+08:00'}


def test_mysql_initialization_ddl_uses_a_fixed_singleton_key():
    ddl = str(CreateTable(SourceInitialization.__table__).compile(dialect=dialect()))
    assert 'AUTO_INCREMENT' not in ddl
    assert 'CHECK (id = 1)' in ddl


@pytest.mark.asyncio
@pytest.mark.parametrize(('total', 'page', 'page_size', 'keys'), [
    (0, 1, 50, []), (3, 1, 2, [b'plc/a', b'plc/b']), (3, 2, 2, [b'plc/c']),
    (3, 3, 2, []), (3, 9223372036854775807, 50, []),
    (3, 1000000000000000000000000, 50, []),
])
async def test_source_list_pagination_skips_out_of_range_mysql_offsets(monkeypatch, total, page, page_size, keys):
    statements = []
    class Result:
        def scalar_one(self): return total
        def scalars(self): return keys
    class Session:
        async def execute(self, statement):
            statements.append(statement)
            return Result()
    mocked_source = AsyncMock(side_effect=lambda db, plc: {'plcId': plc})
    monkeypatch.setattr(crud, 'source', mocked_source)
    result = await crud.page(Session(), page, page_size)
    assert result == {'items': [{'plcId': key.decode()} for key in keys], 'total': total,
                      'page': page, 'pageSize': page_size,
                      'totalPages': (total + page_size - 1) // page_size}
    assert len(statements) == (2 if (page - 1) * page_size < total else 1)
    assert mocked_source.await_count == len(keys)


def test_restore_material_preserves_retired_generations_and_rejects_conflicts():
    legacy = {'target':{'alias':'restore','schema':'fixture','serverUuid':'00000000-0000-4000-8000-000000000001',
                        'schemaRevision':'5f7a9c1e3b25'},
              'instances':[{'instanceId':'old','sourceType':'external'}, {'instanceId':'new','sourceType':'daa'}],
              'sources':[{'plcId':'plc/x','instanceId':'new','sourceGeneration':'g2','dbNumbers':[21]}],
              'readScopes':{'restore':[{'plcId':'plc/x','dbNumbers':[21,22]}]}}
    exported = {'formatVersion':1, 'legacyProfile':legacy, 'generations':[
        {'plcId':'plc/x','instanceId':'old','sourceGeneration':'g1','createdAt':'2026-11-13T10:00:00.000000+08:00'},
        {'plcId':'plc/x','instanceId':'new','sourceGeneration':'g2','createdAt':'2026-11-13T11:00:00.000000+08:00'}]}
    restored = restore_generations(parse_profile(legacy), exported)
    assert restored[('plc/x','g1')][0] == 'old' and restored[('plc/x','g2')][0] == 'new'
    assert parse_profile(legacy)['readScope']['plc/x'] == {21,22}
    with pytest.raises(ValueError):
        restore_generations(parse_profile(legacy), {**exported, 'generations':exported['generations'] * 2})
    with pytest.raises(ValueError):
        restore_generations(parse_profile(legacy), {**exported, 'generations':[{**exported['generations'][1], 'instanceId':'old'}]})


def test_registration_and_patch_input_validate_exact_values():
    body = {'sourceType': 'daa', 'instanceId': 'inst', 'plcId': 'plc/中文',
            'sourceGeneration': 'gen-1'}
    assert RegistrationIn.model_validate(body).plc_id == 'plc/中文'
    for update in ({'dbNumbers': [21]}, {'readDbNumbers': [21]}, {'plcId': ' leading'}):
        with pytest.raises(ValidationError):
            RegistrationIn.model_validate({**body, **update})
    expected = {'instanceId': 'inst', 'sourceGeneration': 'gen-1', 'registrationRevision': 'revision'}
    request = {'action': 'takeover', 'plcId': 'plc/中文', 'expected': expected,
               'replacement': {'sourceType': 'external', 'instanceId': 'new', 'sourceGeneration': 'gen-2'},
               'confirmTakeover': True}
    assert UpdateIn.model_validate(request).replacement.instance_id == 'new'
    for invalid in ({'confirmTakeover': False}, {'replacement': None}, {'extra': 1}):
        with pytest.raises(ValidationError):
            UpdateIn.model_validate({**request, **invalid})


def test_identifier_unicode_whitespace_utf8_and_byte_bounds():
    for value in ['\ufeffPLC', 'PLC\ufeff', 'PLC\u0085middle', '😀' * 32]:
        assert identifier(value) == value
        assert RegistrationIn.model_validate({'sourceType': 'external', 'instanceId': 'inst',
            'plcId': value, 'sourceGeneration': 'gen'}).plc_id == value
    for value in ['\u0085PLC', 'PLC\u0085', '\u00a0PLC', 'PLC\u2003', '\ud800PLC',
                  'PLC\udc00', '😀' * 33, 'a\x7fb']:
        with pytest.raises(V2Error):
            identifier(value)


@pytest.mark.asyncio
async def test_admission_locks_and_matches_three_ids_without_db():
    statements = []
    class Result:
        def scalar_one_or_none(self): return 'daa'
    class Session:
        async def execute(self, statement):
            statements.append(str(statement.compile(dialect=dialect())))
            return Result()
    sample = SimpleNamespace(plc_id='plc', instance_id='inst', source_generation='gen', db_number=22)
    assert await crud.admit(Session(), sample) == 'daa'
    assert 'LOCK IN SHARE MODE' in statements[0]
    assert all(field in statements[0] for field in ('plc_id', 'instance_id', 'source_generation'))
    assert 'db_number' not in statements[0]


@pytest.mark.asyncio
async def test_takeover_checks_revision_and_commits_one_new_generation(monkeypatch):
    events = []
    binding = SimpleNamespace(instance_id=b'inst', source_generation=b'gen-1',
                              registration_revision='revision', source_type='daa', retired_generations=[])
    async def ready(*args): events.append('ready')
    async def locked(*args): events.append('locked'); return binding
    async def exists(*args): events.append('generation'); return False
    async def replace(*args): events.append('replace')
    async def result(*args): return source()
    for name, value in {'binding_for_update': locked, 'generation_exists': exists,
                        'update_binding': replace, 'source': result}.items():
        monkeypatch.setattr(crud, name, value)
    monkeypatch.setattr(service, 'ensure_ready', ready)
    class Session:
        async def commit(self): events.append('commit')
        async def rollback(self): events.append('rollback')
    body = UpdateIn.model_validate({'action': 'takeover', 'plcId': 'plc/中文',
        'expected': {'instanceId': 'inst', 'sourceGeneration': 'gen-1', 'registrationRevision': 'revision'},
        'replacement': {'sourceType': 'external', 'instanceId': 'new', 'sourceGeneration': 'gen-2'},
        'confirmTakeover': True})
    outcome, _, previous = await service.update(Session(), {}, body)
    assert outcome == 'replaced' and previous['sourceType'] == 'daa'
    assert events == ['ready', 'locked', 'generation', 'replace', 'commit']
    events.clear()
    binding.registration_revision = 'other'
    with pytest.raises(service.RegistryError) as conflict:
        await service.update(Session(), {}, body)
    assert conflict.value.key == 'acquisition_sources.revision_conflict'
    assert events == ['ready', 'locked', 'rollback']


@pytest.mark.asyncio
async def test_confirmed_delete_checks_revision_and_returns_deleted_snapshot(monkeypatch):
    binding = SimpleNamespace(instance_id=b'inst', source_generation=b'gen-1',
                              registration_revision='revision', source_type='daa')
    monkeypatch.setattr(service, 'ensure_ready', AsyncMock())
    monkeypatch.setattr(crud, 'binding_for_update', AsyncMock(return_value=binding))
    deleted = AsyncMock()
    monkeypatch.setattr(crud, 'delete_binding', deleted)
    monkeypatch.setattr(crud, 'source', AsyncMock(return_value=source()))
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    raw = {'action': 'delete', 'plcId': 'plc/中文', 'expected': {
        'instanceId': 'inst', 'sourceGeneration': 'gen-1', 'registrationRevision': 'revision'},
        'confirmDelete': True}
    with pytest.raises(ValidationError):
        UpdateIn.model_validate({**raw, 'confirmDelete': False})
    outcome, result, previous = await service.update(db, {}, UpdateIn.model_validate(raw))
    assert outcome == 'deleted' and result == previous == source()
    deleted.assert_awaited_once_with(db, binding)
    db.commit.assert_awaited_once()
    binding.registration_revision = 'changed'
    with pytest.raises(service.RegistryError) as conflict:
        await service.update(db, {}, UpdateIn.model_validate(raw))
    assert conflict.value.status == 409
    assert deleted.await_count == 1


@pytest.mark.asyncio
async def test_admin_routes_and_response_envelopes(monkeypatch):
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    app.dependency_overrides[get_current_active_admin] = lambda: SimpleNamespace(id=4, role='admin')
    monkeypatch.setattr(api, 'get_profile', lambda: {'target': {}})
    class Session:
        async def close(self): pass
    async def session(): return Session()
    async def listing(*args):
        return {'items': [source()], 'total': 1, 'page': 1, 'pageSize': 50, 'totalPages': 1}
    async def register(*args): return 'created', source()
    monkeypatch.setattr(api, 'get_db_session', session)
    monkeypatch.setattr(service, 'list_sources', listing)
    monkeypatch.setattr(service, 'register', register)
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture') as client:
        response = await client.get('/api/v1/admin/acquisition-sources')
        assert response.status_code == 200 and response.json()['data']['items'][0]['plcId'] == 'plc/中文'
        response = await client.post('/api/v1/admin/acquisition-sources', json={
            'sourceType': 'daa', 'instanceId': 'inst', 'plcId': 'plc/中文',
            'sourceGeneration': 'gen-1'})
        assert response.status_code == 200 and response.json()['data']['outcome'] == 'created'
        response = await client.patch('/api/v1/admin/acquisition-sources', json={'action': 'takeover'})
        assert response.status_code == 422 and response.json()['errorCode'] == 'acquisition_sources.invalid_request'


@pytest.mark.asyncio
async def test_duplicate_query_is_checked_after_auth_for_all_methods():
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    url = '/api/v1/admin/acquisition-sources'
    body = {'sourceType': 'external', 'instanceId': 'inst', 'plcId': 'plc',
            'sourceGeneration': 'gen', 'dbNumbers': [21]}
    patch = {'action': 'extend', 'plcId': 'plc', 'expected': {
        'instanceId': 'inst', 'sourceGeneration': 'gen', 'registrationRevision': 'rev'}}
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture') as client:
        for method, query, data in [('GET', '?page=1&page=2', None),
                                    ('POST', '?x=a&x=b', body), ('PATCH', '?x=a&x=b', patch)]:
            response = await client.request(method, url + query, json=data)
            assert response.status_code == 401
            assert response.headers['www-authenticate'] == 'Bearer'
            response = await client.request(method, url + query, json=data,
                                            headers={'Authorization': 'Bearer invalid.token.value'})
            assert response.status_code == 401
            assert response.headers['www-authenticate'] == 'Bearer'
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role='operator')
        for method, query, data in [('GET', '?page=1&page=2', None),
                                    ('POST', '?x=a&x=b', body), ('PATCH', '?x=a&x=b', patch)]:
            response = await client.request(method, url + query, json=data, headers={'Authorization': 'Bearer test'})
            assert response.status_code == 403
        app.dependency_overrides[get_current_active_admin] = lambda: SimpleNamespace(id=1, role='admin')
        for method, query, data in [('GET', '?page=1&page=2', None),
                                    ('POST', '?x=a&x=b', body), ('PATCH', '?x=a&x=b', patch)]:
            response = await client.request(method, url + query, json=data, headers={'Authorization': 'Bearer test'})
            assert response.status_code == 422
            assert response.json()['errorCode'] == 'acquisition_sources.invalid_request'


@pytest.mark.asyncio
@pytest.mark.parametrize('method', ['POST', 'PATCH'])
async def test_malformed_json_and_utf8_never_bypass_auth(method, monkeypatch):
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    business_session = AsyncMock()
    monkeypatch.setattr(api, 'get_db_session', business_session)
    url = '/api/v1/admin/acquisition-sources'
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture') as client:
        for payload in (b'{', b'\xff', b'null'):
            for authorization in (None, 'Bearer invalid.token.value'):
                headers = {'Content-Type': 'application/json'}
                if authorization:
                    headers['Authorization'] = authorization
                response = await client.request(method, url, content=payload, headers=headers)
                assert response.status_code == 401
                assert response.headers['www-authenticate'] == 'Bearer'
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role='operator')
        for payload in (b'{', b'\xff', b'null'):
            response = await client.request(method, url, content=payload,
                headers={'Content-Type': 'application/json', 'Authorization': 'Bearer test'})
            assert response.status_code == 403
        app.dependency_overrides[get_current_active_admin] = lambda: SimpleNamespace(id=1, role='admin')
        for payload in (b'{', b'\xff', b'null'):
            response = await client.request(method, url, content=payload,
                headers={'Content-Type': 'application/json', 'Authorization': 'Bearer test'})
            assert response.status_code == 422
            assert response.json()['errorCode'] == 'acquisition_sources.invalid_request'
    business_session.assert_not_awaited()


@pytest.mark.asyncio
async def test_generation_checks_are_current_reads_for_all_three_tables():
    statements = []
    class Result:
        def first(self): return None
    class Session:
        async def execute(self, statement):
            statements.append(str(statement.compile(dialect=dialect())))
            return Result()
    assert not await crud.generation_exists(Session(), 'plc', 'old-gen')
    assert len(statements) == 2
    assert all('LOCK IN SHARE MODE' in statement for statement in statements)
    assert all('plc_id' in statement and 'source_generation' in statement for statement in statements)


@pytest.mark.asyncio
@pytest.mark.parametrize('hit', [0, 1])
async def test_known_generation_is_found_in_each_ledger_or_fact_table(hit):
    calls = []
    class Result:
        def __init__(self, found): self.found = found
        def first(self): return (b'plc',) if self.found else None
    class Session:
        async def execute(self, statement):
            calls.append(statement)
            return Result(len(calls) - 1 == hit)
    assert await crud.generation_exists(Session(), 'plc', 'old-gen')
    assert len(calls) == hit + 1


@pytest.mark.asyncio
async def test_initial_registration_rejects_historical_generation_but_repeat_is_idempotent(monkeypatch):
    binding = SimpleNamespace(instance_id=b'inst', source_generation=b'gen', source_type='external')
    monkeypatch.setattr(service, 'ensure_ready', AsyncMock())
    locked, exists, inserted = AsyncMock(return_value=None), AsyncMock(return_value=True), AsyncMock()
    monkeypatch.setattr(crud, 'binding_for_update', locked)
    monkeypatch.setattr(crud, 'generation_exists', exists)
    monkeypatch.setattr(crud, 'insert_binding', inserted)
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    body = RegistrationIn.model_validate({'sourceType': 'external', 'instanceId': 'inst',
        'plcId': 'plc', 'sourceGeneration': 'gen'})
    with pytest.raises(service.RegistryError) as rejected:
        await service.register(db, {}, body)
    assert rejected.value.key == 'acquisition_sources.generation_reused'
    exists.assert_awaited_once_with(db, 'plc', 'gen')
    inserted.assert_not_awaited()
    db.commit.assert_not_awaited()
    locked.return_value = binding
    monkeypatch.setattr(crud, 'source', AsyncMock(return_value=source()))
    outcome, _ = await service.register(db, {}, body)
    assert outcome == 'unchanged'
    assert exists.await_count == 1
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize('rollback_fails', [False, True])
async def test_post_commit_unknown_is_retained_if_rollback_also_fails(monkeypatch, rollback_fails):
    app = FastAPI()
    app.include_router(api.router, prefix='/api/v1')
    app.dependency_overrides[get_current_active_admin] = lambda: SimpleNamespace(id=1, role='admin')
    binding = SimpleNamespace(instance_id=b'inst', source_generation=b'gen', source_type='external')
    failure = OperationalError('COMMIT', {}, Exception(2013, 'connection lost'))
    db = SimpleNamespace(commit=AsyncMock(side_effect=failure),
        rollback=AsyncMock(side_effect=RuntimeError('rollback failed') if rollback_fails else None),
        close=AsyncMock())
    monkeypatch.setattr(api, 'get_db_session', AsyncMock(return_value=db))
    monkeypatch.setattr(api, 'get_profile', lambda: {})
    monkeypatch.setattr(service, 'ensure_ready', AsyncMock())
    monkeypatch.setattr(crud, 'binding_for_update', AsyncMock(return_value=binding))
    monkeypatch.setattr(crud, 'source', AsyncMock(return_value=source()))
    body = {'sourceType': 'external', 'instanceId': 'inst', 'plcId': 'plc', 'sourceGeneration': 'gen'}
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture') as client:
        response = await client.post('/api/v1/admin/acquisition-sources', json=body)
    assert response.status_code == 503
    assert response.json()['errorCode'] == 'acquisition_sources.commit_outcome_unknown'
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_retired_generation_is_checked_per_plc_without_querying_facts():
    binding = SimpleNamespace(source_generation=b'active', retired_generations=['retired'])
    db = SimpleNamespace(execute=AsyncMock())
    assert await crud.generation_exists(db, 'plc', 'retired', binding)
    assert await crud.generation_exists(db, 'plc', 'active', binding)
    db.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_options_query_uses_registered_plcs_and_current_latest_identity():
    from app.plc_facts.crud import async_v2
    statements = []
    class Result:
        def all(self): return [(b'PLC-A', 21), (b'PLC-A', 22)]
    class Session:
        async def execute(self, statement):
            statements.append(str(statement.compile(dialect=dialect())))
            return Result()
    rows = await async_v2.options(Session(), object())
    sql = statements[0]
    assert rows == [(b'PLC-A', 21), (b'PLC-A', 22)]
    assert 'UNION' in sql and 'plc_source_registry' in sql
    assert 'plc_facts_history.expires_at' in sql and 'plc_facts_latest.expires_at' in sql
    assert 'plc_facts_latest.instance_id = plc_source_registry.instance_id' in sql
    assert 'plc_facts_latest.source_generation = plc_source_registry.source_generation' in sql
    assert 'ORDER BY' in sql


def test_migration_fact_reconciliation_includes_schema_and_all_values():
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    migration = ScriptDirectory.from_config(Config('alembic.ini')).get_revision('7b9d1f3a5c7e').module
    class Rows:
        def __init__(self, values): self.values = values
        def __iter__(self): return iter(self.values)
        def close(self): pass
    class Session:
        def __init__(self, latest_seq=7): self.latest_seq = latest_seq
        def exec_driver_sql(self, statement): return SimpleNamespace(one=lambda: ('table', statement))
        def execute(self, statement):
            sql = str(statement)
            assert statement.get_execution_options()['stream_results'] is True
            return Rows([(b'plc', self.latest_seq)] if 'plc_facts_latest' in sql else [(b'original', 'sample')])
    first = migration.fact_snapshot(Session())
    assert first == migration.fact_snapshot(Session())
    changed = migration.fact_snapshot(Session(latest_seq=8))
    assert first['plc_facts_history'] == changed['plc_facts_history']
    assert first['plc_facts_latest']['rowCount'] == changed['plc_facts_latest']['rowCount'] == 1
    assert first['plc_facts_latest']['rowsSha256'] != changed['plc_facts_latest']['rowsSha256']


@pytest.mark.asyncio
async def test_registry_labels_are_per_plc_even_for_a_shared_instance():
    rows = [SimpleNamespace(plc_id=b'PLC-A', instance_id=b'shared', source_generation=b'gen-a', source_type='daa'),
            SimpleNamespace(plc_id=b'PLC-B', instance_id=b'shared', source_generation=b'gen-b', source_type='external')]
    class Result:
        def scalars(self): return iter(rows)
    class Session:
        async def execute(self, _statement): return Result()
    profile = await crud.read_profile(Session(), {'schema': 'fixture'})
    assert profile['sources'] == {'PLC-A': ('shared', 'gen-a'), 'PLC-B': ('shared', 'gen-b')}
    assert profile['sourceTypes'] == {'PLC-A': 'daa', 'PLC-B': 'external'}
