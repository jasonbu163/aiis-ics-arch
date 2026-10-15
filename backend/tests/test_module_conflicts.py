"""声明和最终HTTP对象冲突矩阵；静态与参数路由仍可合法共存。"""
from dataclasses import replace

import pytest
from fastapi import FastAPI
from app.module_preflight import ModulePreflightError, check_routes, validate_manifests
from app.module_registry import ModuleManifest

pytestmark = pytest.mark.no_db


@pytest.mark.parametrize("field,value", [
    ("permissions", ("probe-read",)), ("error_codes", ("probe.invalid",)),
])
def test_duplicate_functional_claim_is_blocked(field, value):
    first = ModuleManifest("probe", **{field: value})
    second = ModuleManifest("other", **{field: value})
    with pytest.raises(ModulePreflightError):
        validate_manifests([first, second])


def test_duplicate_router_declaration_is_blocked():
    manifest = ModuleManifest("probe", routers=("app.probe.api.routes:router",) * 2)
    with pytest.raises(ModulePreflightError, match="manifest-duplicate"):
        validate_manifests([manifest])


@pytest.mark.parametrize("key", ["control-agent", "control-agent-read", "system"])
def test_explicit_security_permission_owner_is_protected(key):
    with pytest.raises(ModulePreflightError, match="permission"):
        validate_manifests([ModuleManifest("probe", permissions=(key,))])


def test_same_shape_parameter_and_core_route_collision():
    app = FastAPI()
    app.get("/items/{id}")(lambda: None)
    app.get("/items/{item_id}")(lambda: None)
    with pytest.raises(ModulePreflightError, match="GET /items/{}"):
        check_routes(app)
    app = FastAPI()
    app.get("/openapi.json")(lambda: None)
    with pytest.raises(ModulePreflightError, match="openapi.json"):
        check_routes(app)


def test_static_parameter_and_distinct_methods_remain_legal():
    app = FastAPI()
    app.get("/items/current")(lambda: "current")
    app.get("/items/{id}")(lambda id: id)
    app.post("/items/{id}")(lambda id: id)
    assert ("GET", "/items/current") in check_routes(app)


@pytest.mark.asyncio
async def test_static_route_still_dispatches_before_parameter():
    from httpx import ASGITransport, AsyncClient
    app = FastAPI()
    app.get('/items/current')(lambda: 'current')
    app.get('/items/{id}')(lambda id: id)
    check_routes(app)
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture') as client:
        assert (await client.get('/items/current')).json() == 'current'
        assert (await client.get('/items/123')).json() == '123'
