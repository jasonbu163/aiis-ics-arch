"""r8 版本守卫、列配置与来源锁的无库回归。"""
from datetime import datetime
from types import SimpleNamespace

import pytest
import httpx
from fastapi import FastAPI
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects import mysql

from app.equipment_observation.domain import ObservationError
from app.equipment_observation.schemas import SlotPatch
from app.equipment_observation.services.configuration import update_binding
from app.equipment_observation.services.reads import sample_data
from app.equipment_observation.services import reads
from app.equipment_observation.models import LatestSnapshot
from app.plc_facts.services.observation_evidence import _source
from app.plc_facts.v2_config import load_profile
from app.plc_facts.v2_domain import V2Error
from app.equipment_observation.api import routes
from core.deps import get_current_user
from database import get_db

pytestmark = pytest.mark.no_db


@pytest.mark.asyncio
async def test_column_selection_does_not_change_write_enabled_or_old_value_binding():
    row = SimpleNamespace(target='history', group_key='temperature', slot_no=7, metric_key='actual',
                          enabled=False, list_visible=False, list_order=None, first_used_at=None)

    class DB:
        async def get(self, model, key):
            assert key == ('history', 'temperature', 7)
            return row

        async def commit(self):
            pass

    result = await update_binding(DB(), 'history', 'temperature', 7,
                                  SlotPatch.model_validate({'listVisible': True, 'listOrder': 10}))
    assert result['enabled'] is False and result['listVisible'] is True and result['listOrder'] == 10
    assert result['metricKey'] == 'actual' and result['slotNo'] == 7
    await update_binding(DB(), 'history', 'temperature', 7, SlotPatch.model_validate({'enabled': True}))
    assert row.enabled is True and row.list_visible is True and row.list_order == 10
    await update_binding(DB(), 'history', 'temperature', 7, SlotPatch.model_validate({'listOrder': None}))
    assert row.list_order is None
    with pytest.raises(ObservationError):
        await update_binding(DB(), 'history', 'temperature', 7, SlotPatch.model_validate({'listVisible': None}))
    for value in ({'listOrder': -1}, {'listVisible': 1}, {'unexpected': True}):
        with pytest.raises(ValidationError):
            SlotPatch.model_validate(value)


@pytest.mark.asyncio
async def test_list_decodes_each_group_and_keeps_false_zero_and_empty_values():
    def metric(key):
        return SimpleNamespace(metric_key=key, name_zh=key, name_en=key, value_type='string', unit=None, decimals=None)
    now = datetime(2026, 11, 16, 10)
    row = SimpleNamespace(id=1, equipment_id='line', task_no='000042', observed_at=now,
                          quality='good', local_values={'temperature': {'01': 0, '02': False, '03': ''}, 'drive': {'01': 2.5}}, remark=None,
                          created_at=now, updated_at=now)
    maps = {('temperature', '01'): metric('temperatureActual'), ('drive', '01'): metric('driveSpeed'),
            ('temperature', '02'): metric('ready'), ('temperature', '03'): metric('coil')}
    result = await sample_data(None, row, 'latest', maps)
    values = {item['metricKey']: item['value'] for item in result['values']}
    assert values == {'temperatureActual': 0, 'ready': False, 'coil': '', 'driveSpeed': 2.5}


@pytest.mark.asyncio
async def test_source_registry_identity_is_locked_and_has_no_legacy_db_list():
    class Result:
        def scalar_one_or_none(self):
            return SimpleNamespace(instance_id=b'instance', source_generation=b'generation')

    class DB:
        async def execute(self, statement):
            assert statement._for_update_arg is not None and statement._for_update_arg.read is True
            return Result()

    assert await _source(DB(), {'plcId': 'plc', 'dbNumber': 21}) == ('instance', 'generation')


def test_facts_profile_preserves_legacy_diagnostic_revision(tmp_path):
    import json
    path = tmp_path / 'facts-profile.json'
    settings = SimpleNamespace(PLC_FACTS_V2_PROFILE_FILE=str(path))
    target = {'alias': 'fixture', 'serverUuid': '00000000-0000-4000-8000-000000000001', 'schema': 'fixture'}
    for revision in ('7b9d1f3a5c7e', '8c0e2a4d6f18', '9d1f3a5c7e20'):
        path.write_text(json.dumps({'target': {**target, 'schemaRevision': revision}}))
        assert load_profile(settings)['target']['schemaRevision'] == revision
    path.write_text(json.dumps({'target': {**target, 'schemaRevision': 'unknown'}}))
    with pytest.raises(V2Error):
        load_profile(settings)


@pytest.mark.asyncio
async def test_admin_list_column_http_contract_and_role_restriction(monkeypatch):
    row = SimpleNamespace(target='history', group_key='temperature', slot_no=7, metric_key='actual',
                          enabled=False, list_visible=False, list_order=None, first_used_at=None)
    class DB:
        async def get(self, model, key): return row
        async def commit(self): pass

    async def no_probe(db, target): return None
    async def column_data(db, target): return {'target': target, 'items': []}
    monkeypatch.setattr(routes, 'get_profile', lambda: {'readScopes': {'admin': ['line']}, 'target': {}})
    monkeypatch.setattr(routes, 'probe_target', no_probe)
    monkeypatch.setattr(routes.configuration, 'list_columns', column_data)
    app = FastAPI()
    app.include_router(routes.router, prefix='/api/v1')
    app.dependency_overrides[get_db] = lambda: DB()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role='admin')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
        response = await client.get('/api/v1/equipment/observation-list-columns', params={'target': 'history'})
        assert response.status_code == 200 and response.json()['data'] == {'target': 'history', 'items': []}
        path = '/api/v1/equipment/metric-slot-bindings/history/temperature/7'
        response = await client.patch(path, json={'listVisible': True, 'listOrder': 10})
        assert response.status_code == 200 and response.json()['data']['enabled'] is False
        assert response.json()['data']['listVisible'] is True and response.json()['data']['listOrder'] == 10
        assert (await client.patch(path, json={'listOrder': -1})).status_code == 422
        assert (await client.patch(path, json={'listVisible': None})).status_code == 422
        assert (await client.patch(path, json={'enabled': False, 'unknown': 1})).status_code == 422
        monkeypatch.setattr(routes, 'get_profile', lambda: {'readScopes': {'admin': []}, 'target': {}})
        assert (await client.get('/api/v1/equipment/observation-list-columns', params={'target': 'history'})).status_code == 200
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role='operator')
        assert (await client.get('/api/v1/equipment/observation-list-columns', params={'target': 'history'})).status_code == 403
        assert (await client.patch(path, json={'listVisible': False})).status_code == 403


@pytest.mark.asyncio
async def test_empty_and_scoped_admin_record_queries_are_fail_closed(monkeypatch):
    user = SimpleNamespace(role='admin')
    empty = {'readScopes': {'admin': []}, 'devices': {}}
    conditions = await reads._conditions(None, empty, user, LatestSnapshot)
    sql = str(select(LatestSnapshot.id).where(*conditions).compile(dialect=mysql.dialect(), compile_kwargs={'literal_binds': True}))
    assert 'IN (NULL) AND (1 != 1)' in sql
    scoped = {'readScopes': {'admin': ['line-1']}, 'devices': {'line-1': {'equipmentId': 'line-1'}}, 'target': {}}
    with pytest.raises(ObservationError) as error:
        await reads._conditions(None, scoped, user, LatestSnapshot, equipment='line-2')
    assert error.value.status == 403
    async def no_probe(db, target): return None
    monkeypatch.setattr(reads, 'probe_target', no_probe)
    class Result:
        def scalar_one_or_none(self): return None
    class DB:
        async def execute(self, statement):
            params = statement.compile(dialect=mysql.dialect()).params
            assert ['line-1'] in params.values()
            return Result()
    with pytest.raises(ObservationError) as error:
        await reads.detail(DB(), scoped, user, 'latest', 9)
    assert error.value.status == 404
