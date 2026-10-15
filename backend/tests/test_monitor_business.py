"""监控历史查询mock-off零写，业务读取与事实权限完全独立。"""
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from httpx import ASGITransport, AsyncClient
from app.monitor.services import async_temperature, async_energy
from core.registrar import create_app
from core.deps import get_current_user
from database import get_db
from core.role_permissions import build_role_api_permissions
from app.module_registry import get_module_manifests
import json

pytestmark = pytest.mark.no_db


@pytest.mark.asyncio
async def test_empty_history_queries_never_add_flush_commit(monkeypatch):
    db = SimpleNamespace(add=lambda *a: pytest.fail('GET added data'), flush=AsyncMock(side_effect=AssertionError('GET flushed')), commit=AsyncMock(side_effect=AssertionError('GET committed')))
    monkeypatch.setattr(async_temperature.temperature_crud, 'list_curves_by_date', AsyncMock(return_value=[]))
    monkeypatch.setattr(async_energy.energy_crud, 'get_day_totals', AsyncMock(return_value=(None,None)))
    monkeypatch.setattr(async_energy.energy_crud, 'get_month_totals', AsyncMock(return_value=(None,None)))
    monkeypatch.setattr(async_energy.energy_crud, 'list_latest_process_curves', AsyncMock(return_value=[]))
    assert await async_temperature.get_curve_dashboard_data(db,'all','2026-10-14') == {'trends': [], 'latest': {}}
    assert (await async_energy.get_energy_summary_data(db,'realtime'))['trends'] == []
    db.flush.assert_not_awaited(); db.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize('grants,business,fact', [([],403,403),(['monitor'],403,200),(['monitor-business-read'],200,403)])
async def test_monitor_fact_and_business_grants_are_independent(monkeypatch,grants,business,fact):
    from app.monitor.api import temperature, collector
    monkeypatch.setattr(temperature,'get_curve_dashboard_data',AsyncMock(return_value={'trends':[],'latest':{}}))
    monkeypatch.setattr(collector,'get_collector_status_data',AsyncMock(return_value={'items':[]}))
    app=create_app(testing=True)
    app.state.role_api_permissions=build_role_api_permissions(json.dumps(grants),'[]',get_module_manifests(),warn=lambda **kw:None)
    app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(role='supervisor',username='fixture')
    app.dependency_overrides[get_db]=lambda:None
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://fixture') as client:
        assert (await client.get('/api/v1/monitor/temperature?date=2026-10-14')).status_code==business
        assert (await client.get('/api/v1/monitor/collector/status')).status_code==fact
