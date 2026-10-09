"""No-DB 回归：原始等级、有效策略与现有 permission guard。"""
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from starlette.requests import Request

from core.deps import get_role_permissions, require_permissions
from core.role_permissions import build_role_api_permissions, parse_permission_array
from app.module_registry import ModuleManifest

pytestmark = pytest.mark.no_db


def request_with_policy(policy=None):
    app = FastAPI()
    if policy is not None:
        app.state.role_api_permissions = policy
    return Request({"type": "http", "app": app})


@pytest.mark.parametrize("raw", ['not-json', '', '{}', 'null', '"monitor"', '[1]', '[null]', '[""]', '["  "]'])
def test_invalid_array_fails_without_echoing_raw(raw):
    with pytest.raises(ValueError, match="SUPERVISOR_API_PERMISSIONS_JSON"):
        parse_permission_array(raw, "SUPERVISOR_API_PERMISSIONS_JSON")


def test_exact_keys_and_duplicates():
    assert parse_permission_array('["monitor","monitor","Monitor"," monitor"]', 'KEY') == {
        'monitor', 'Monitor', ' monitor',
    }


@pytest.mark.parametrize('key', ['monitor', 'unknown', 'aiis_demo'])
def test_original_operator_subset_checked_before_filter(key):
    warnings = []
    with pytest.raises(ValueError, match='OPERATOR_API_PERMISSIONS_JSON.*absent from SUPERVISOR'):
        build_role_api_permissions('[]', f'["{key}"]', [], warn=lambda **w: warnings.append(w))
    assert warnings == []


def test_shared_owners_explicit_boundaries_and_filtered_grants():
    manifests = [
        ModuleManifest(name='disabled', enabled=False, permissions=('shared', 'off')),
        ModuleManifest(name='enabled', permissions=('shared',)),
    ]
    warnings = []
    policy = build_role_api_permissions(
        '["shared","off","missing","*","system","control-agent","control-agent-read"]',
        '["shared","off"]', manifests, warn=lambda **w: warnings.append(w),
    )
    assert policy['supervisor'] == {'shared', 'system', 'control-agent', 'control-agent-read'}
    assert policy['operator'] == {'shared'}
    assert {w['reason'] for w in warnings} == {'unknown_permission', 'disabled_module'}
    assert next(w for w in warnings if w['permission'] == 'off')['modules'] == ['disabled']
    assert len(warnings) == 4
    with pytest.raises(TypeError):
        policy['operator'] = frozenset({'off'})
    request = request_with_policy(policy)
    for _ in range(3):
        assert get_role_permissions('operator', request) == ['shared']
        assert get_role_permissions('unknown', request) == []
    assert len(warnings) == 4


@pytest.mark.asyncio
async def test_permission_guard_admin_bypass_and_nonadmin_fail_closed():
    policy = build_role_api_permissions('["system"]', '[]', [], warn=lambda **w: None)
    request = request_with_policy(policy)
    guard = require_permissions('system')
    for role in ['admin', 'supervisor']:
        actor = SimpleNamespace(role=role)
        assert await guard(request=request, current_user=actor) is actor
    for role in ['operator', 'unknown']:
        with pytest.raises(HTTPException) as exc:
            await guard(request=request, current_user=SimpleNamespace(role=role))
        assert exc.value.status_code == 403
    assert get_role_permissions('supervisor') == []
    assert get_role_permissions('supervisor', request_with_policy()) == []
    with pytest.raises(HTTPException):
        await guard(request=request_with_policy(), current_user=SimpleNamespace(role='supervisor'))
    admin = SimpleNamespace(role='admin')
    assert await guard(request=request_with_policy(), current_user=admin) is admin


@pytest.mark.asyncio
async def test_guard_grants_do_not_bypass_independent_business_constraints():
    from app.user.services.async_user import UserService
    from app.control_agent.services.async_authorization import ControlAgentAuthorizationService
    from common.exceptions import BusinessException

    policy = build_role_api_permissions('["system","control-agent"]', '[]', [], warn=lambda **w: None)
    request = request_with_policy(policy)
    admin = SimpleNamespace(role='admin')
    supervisor = SimpleNamespace(role='supervisor')
    assert await require_permissions('system')(request=request, current_user=admin) is admin
    with pytest.raises(BusinessException):
        UserService._ensure_can_manage_target(admin, admin)
    assert await require_permissions('control-agent')(request=request, current_user=supervisor) is supervisor
    with pytest.raises(PermissionError, match='requires_admin'):
        ControlAgentAuthorizationService()._ensure_highest_privilege_user(supervisor)
