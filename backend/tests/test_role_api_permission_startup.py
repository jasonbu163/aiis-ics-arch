"""
文件路径: /backend/tests/test_role_api_permission_startup.py
功能描述: 隔离公开配置下的应用组合、配置来源和维护顺序 no-DB 回归
主要功能: 校验启动阻断、非阻断 WARNING、app 策略隔离及现有安全边界
"""
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request

from core import registrar
from core.deps import get_current_user, get_role_permissions, require_permissions
from settings import Settings, settings

pytestmark = pytest.mark.no_db
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def public_grants(monkeypatch):
    monkeypatch.setattr(settings, 'SUPERVISOR_API_PERMISSIONS_JSON', '[]')
    monkeypatch.setattr(settings, 'OPERATOR_API_PERMISSIONS_JSON', '[]')
    monkeypatch.setattr(settings, 'legacy_role_api_permissions_present', False)


@pytest.mark.parametrize('line', ['ROLE_API_PERMISSIONS_JSON={}', 'ROLE_API_PERMISSIONS_JSON=', 'ROLE_API_PERMISSIONS_JSON'])
def test_legacy_dotenv_presence_even_empty_fails(tmp_path, line):
    fixture = tmp_path / '.env'
    fixture.write_text((ROOT / '.env.example').read_text() + '\n' + line + '\n')
    configuration = Settings(_env_file=fixture)
    assert configuration.legacy_role_api_permissions_present
    from core.role_permissions import build_role_api_permissions
    with pytest.raises(ValueError, match='retired.*SUPERVISOR_API_PERMISSIONS_JSON.*OPERATOR'):
        build_role_api_permissions('[]', '[]', [], legacy_present=configuration.legacy_role_api_permissions_present, warn=lambda **w: None)


def test_comment_missing_defaults_and_process_override(tmp_path, monkeypatch):
    fixture = tmp_path / '.env'
    source = (ROOT / '.env.example').read_text()
    source = '\n'.join(line for line in source.splitlines() if not line.startswith(('SUPERVISOR_API_PERMISSIONS_JSON=', 'OPERATOR_API_PERMISSIONS_JSON=')))
    fixture.write_text(source + '\n# ROLE_API_PERMISSIONS_JSON={}\n')
    configuration = Settings(_env_file=fixture)
    assert not configuration.legacy_role_api_permissions_present
    assert configuration.SUPERVISOR_API_PERMISSIONS_JSON == '[]'
    assert configuration.OPERATOR_API_PERMISSIONS_JSON == '[]'
    monkeypatch.setenv('SUPERVISOR_API_PERMISSIONS_JSON', '["monitor"]')
    assert Settings(_env_file=fixture).SUPERVISOR_API_PERMISSIONS_JSON == '["monitor"]'
    monkeypatch.setenv('ROLE_API_PERMISSIONS_JSON', '')
    assert Settings(_env_file=fixture).legacy_role_api_permissions_present


@pytest.mark.parametrize('testing', [True, False])
@pytest.mark.parametrize('attribute,value', [
    ('SUPERVISOR_API_PERMISSIONS_JSON', 'broken'),
    ('OPERATOR_API_PERMISSIONS_JSON', '["monitor"]'),
    ('legacy_role_api_permissions_present', True),
])
def test_composition_rejects_invalid_input_before_registration(monkeypatch, testing, attribute, value):
    monkeypatch.setattr(settings, attribute, value)
    called = []
    monkeypatch.setattr(registrar, 'register_routers', lambda app: called.append(app))
    with pytest.raises(ValueError):
        registrar.create_app(testing=testing)
    assert called == []


def test_warnings_once_and_apps_keep_separate_policy(monkeypatch):
    events = []
    monkeypatch.setattr(registrar, 'log_event', lambda *args, **kw: events.append((args, kw)))
    monkeypatch.setattr(settings, 'SUPERVISOR_API_PERMISSIONS_JSON', '["monitor","aiis_demo","unknown"]')
    first = registrar.create_app(testing=True)
    first_request = Request({'type': 'http', 'app': first})
    assert get_role_permissions('supervisor', first_request) == ['monitor']
    assert len(events) == 2
    assert all(args[0] == 'WARNING' for args, _ in events)
    assert {kw['reason'] for _, kw in events} == {'unknown_permission', 'disabled_module'}
    monkeypatch.setattr(settings, 'SUPERVISOR_API_PERMISSIONS_JSON', '[]')
    second = registrar.create_app(testing=True)
    assert get_role_permissions('supervisor', Request({'type': 'http', 'app': second})) == []
    monkeypatch.setattr(settings, 'OPERATOR_API_PERMISSIONS_JSON', '["monitor"]')
    with pytest.raises(ValueError):
        registrar.create_app(testing=True)
    for _ in range(3):
        assert get_role_permissions('supervisor', first_request) == ['monitor']
    assert len(events) == 2


@pytest.mark.asyncio
async def test_requests_disabled_routes_and_authenticated_only(monkeypatch):
    monkeypatch.setattr(settings, 'SUPERVISOR_API_PERMISSIONS_JSON', '["monitor"]')
    app = registrar.create_app(testing=True)

    @app.get('/permission-probe', dependencies=[])
    async def protected(actor=Depends(require_permissions('monitor'))):
        return {'role': actor.role}

    @app.get('/login-probe')
    async def authenticated(actor=Depends(get_current_user)):
        return {'role': actor.role}

    assert not any('/aiis-demo/' in path for path in app.openapi()['paths'])
    assert '/api/v1/auth/login' in app.openapi()['paths']
    assert '/api/v1/control-agent/action-scopes' in app.openapi()['paths']
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        for role in ['admin', 'supervisor', 'operator', 'other']:
            app.dependency_overrides[get_current_user] = lambda role=role: SimpleNamespace(role=role)
            assert (await client.get('/permission-probe')).status_code == (200 if role in {'admin', 'supervisor'} else 403)
            assert (await client.get('/login-probe')).status_code == 200
            assert (await client.get('/api/v1/aiis-demo/ping')).status_code == 404


@pytest.mark.parametrize('action', ['schema', 'bootstrap-users'])
@pytest.mark.parametrize('invalid', [True, False])
def test_main_maintenance_composes_before_stub_action(monkeypatch, action, invalid):
    calls = []
    module_name, function_name = (
        ('scripts.maintenance.bootstrap_or_migrate_schema', 'bootstrap_or_migrate_schema')
        if action == 'schema' else ('scripts.maintenance.ensure_admin_user', 'ensure_admin_user')
    )
    stub = ModuleType(module_name)
    setattr(stub, function_name, lambda: calls.append(action) or 0)
    monkeypatch.setitem(sys.modules, module_name, stub)
    monkeypatch.setattr(sys, 'argv', ['main.py', '--maintenance', action])
    monkeypatch.setattr(settings, 'SUPERVISOR_API_PERMISSIONS_JSON', 'broken' if invalid else '["unknown"]')
    if invalid:
        with pytest.raises(ValueError):
            runpy.run_module('main', run_name='__main__')
        assert calls == []
    else:
        with pytest.raises(SystemExit) as exit_info:
            runpy.run_module('main', run_name='__main__')
        assert exit_info.value.code == 0
        assert calls == [action]


def test_development_handoff_uses_same_invalid_app_composition(monkeypatch):
    import run
    import uvicorn
    monkeypatch.setattr(settings, 'SUPERVISOR_API_PERMISSIONS_JSON', 'invalid')
    def compose(application, **kwargs):
        assert application == 'main:app'
        runpy.run_module('main', run_name='development_import_probe')
    monkeypatch.setattr(uvicorn, 'run', compose)
    with pytest.raises(ValueError):
        run.main()


@pytest.mark.parametrize('legacy_source', ['dotenv', 'process'])
@pytest.mark.parametrize('override_source', ['process', 'init', 'both'])
def test_legacy_presence_cannot_be_disabled_by_another_input(
    tmp_path, monkeypatch, legacy_source, override_source,
):
    fixture = tmp_path / '.env'
    source = (ROOT / '.env.example').read_text()
    if legacy_source == 'dotenv':
        source += '\nROLE_API_PERMISSIONS_JSON={}\n'
    else:
        monkeypatch.setenv('ROLE_API_PERMISSIONS_JSON', '{}')
    fixture.write_text(source)
    if override_source in {'process', 'both'}:
        monkeypatch.setenv('legacy_role_api_permissions_present', 'false')
    initial = {'legacy_role_api_permissions_present': False} if override_source in {'init', 'both'} else {}
    configuration = Settings(_env_file=fixture, **initial)
    assert configuration.legacy_role_api_permissions_present
    monkeypatch.setattr(registrar, 'settings', configuration)
    with pytest.raises(ValueError, match='ROLE_API_PERMISSIONS_JSON is retired'):
        registrar.create_app(testing=True)


def test_derived_legacy_fact_does_not_change_grant_precedence(tmp_path, monkeypatch):
    fixture = tmp_path / '.env'
    source = (ROOT / '.env.example').read_text().replace(
        "SUPERVISOR_API_PERMISSIONS_JSON='[]'", "SUPERVISOR_API_PERMISSIONS_JSON='[\"system\"]'",
    )
    fixture.write_text(source)
    monkeypatch.setenv('SUPERVISOR_API_PERMISSIONS_JSON', '["monitor"]')
    assert Settings(_env_file=fixture).SUPERVISOR_API_PERMISSIONS_JSON == '["monitor"]'
    configuration = Settings(_env_file=fixture, SUPERVISOR_API_PERMISSIONS_JSON='["control-agent-read"]')
    assert configuration.SUPERVISOR_API_PERMISSIONS_JSON == '["control-agent-read"]'
    assert not configuration.legacy_role_api_permissions_present
