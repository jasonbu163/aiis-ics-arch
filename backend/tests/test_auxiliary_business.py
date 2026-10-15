"""辅助GET零写、合法规则null、现有显式写事务和稳定错误。"""
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from httpx import ASGITransport, AsyncClient
from app.auxiliary.services.async_auxiliary import AuxiliaryService
from common.exceptions import BusinessException
from core.registrar import create_app
from core.deps import get_current_user
from database import get_db

pytestmark = pytest.mark.no_db


@pytest.mark.asyncio
async def test_read_only_empty_shift_and_rule_do_not_seed_or_commit():
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    service = AuxiliaryService(db)
    service.crud = SimpleNamespace(list_shifts=AsyncMock(return_value=([], 0)), get_active_shift_rule=AsyncMock(return_value=None))
    assert await service.list_shifts(1, 20, None, '2026-10-01', '2026-10-31') == ([], 0)
    assert await service.get_shift_rule() is None
    db.commit.assert_not_awaited(); db.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_asgi_rule_null_is_shared_success_envelope(monkeypatch):
    monkeypatch.setattr(AuxiliaryService, 'get_shift_rule', AsyncMock(return_value=None))
    app = create_app(testing=True)
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role='admin', username='fixture')
    app.dependency_overrides[get_db] = lambda: None
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture') as client:
        response = await client.get('/api/v1/shift-rules')
    assert response.status_code == 200
    assert response.json()['data'] is None
    assert response.json()['code'] == 200 and response.json()['message'] == 'success'


@pytest.mark.asyncio
async def test_explicit_write_commits_and_failure_rolls_back():
    from app.auxiliary.schemas.auxiliary_in import ShiftTeamCreate
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    service = AuxiliaryService(db)
    service.crud = SimpleNamespace(create_shift_team=AsyncMock(return_value=SimpleNamespace(id=1)))
    assert (await service.create_shift_team(ShiftTeamCreate(team_name='fixture'))).id == 1
    db.commit.assert_awaited_once()
    service.crud.create_shift_team.side_effect = RuntimeError('fixture failure')
    with pytest.raises(RuntimeError):
        await service.create_shift_team(ShiftTeamCreate(team_name='fixture'))
    db.rollback.assert_awaited_once()
