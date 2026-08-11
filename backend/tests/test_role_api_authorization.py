"""No-DB tests for fail-closed role permission parsing."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from core.deps import get_role_permissions, parse_role_api_permissions, require_permissions
from settings import settings


pytestmark = pytest.mark.no_db


def test_permission_json_accepts_only_role_to_string_lists():
    configured = '{"supervisor": ["system", "monitor"], "operator": ["monitor"]}'
    assert parse_role_api_permissions(configured) == {
        "supervisor": ["system", "monitor"],
        "operator": ["monitor"],
    }
    for invalid in (
        '{"supervisor": "monitor"}',
        '{"supervisor": ["monitor", 1]}',
        '{"admin": ["system"]}',
        '{"operator": ["*"]}',
        "not-json",
    ):
        assert parse_role_api_permissions(invalid) == {}


@pytest.mark.asyncio
async def test_invalid_permission_configuration_denies_non_admin_and_admin_bypasses(monkeypatch):
    monkeypatch.setattr(settings, "ROLE_API_PERMISSIONS_JSON", "not-json")
    assert get_role_permissions("supervisor") == []
    admin = SimpleNamespace(role="admin")
    supervisor = SimpleNamespace(role="supervisor")
    assert await require_permissions("system")(current_user=admin) is admin
    with pytest.raises(HTTPException) as exc_info:
        await require_permissions("system")(current_user=supervisor)
    assert exc_info.value.status_code == 403
