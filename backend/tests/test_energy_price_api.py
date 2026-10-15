"""真实 ASGI 路由、共享信封与权限矩阵；无网络或数据库写入。"""
from dataclasses import replace
from datetime import datetime, timezone, date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from fastapi import APIRouter, FastAPI
from httpx import ASGITransport, AsyncClient
from app.energy.manifest import manifest
from app.energy.schemas.energy_price import HourlyPriceRecord, PricePage
from app.energy.services import async_energy_price as service
from app.module_registry import include_module_routers
from core.deps import get_current_user
from core.registrar import create_app
from core.role_permissions import build_role_api_permissions
from database import get_db

pytestmark = pytest.mark.no_db


def snapshot():
    return HourlyPriceRecord(observed_at=datetime(2026,10,13),hour_start=datetime(2026,10,13),id=4,electric_price=Decimal(0),hydrogen_price=Decimal("1.2345"),argon_price=Decimal("999999.9999"),electric_remark="电",hydrogen_remark=None,argon_remark="气",remark="  snapshot  ",operator="actor",created_at=datetime(2026,10,13),updated_at=datetime(2026,10,13))


def app_for(monkeypatch, role="admin", grants=()):
    app=create_app(testing=True)
    app.state.role_api_permissions=build_role_api_permissions(list_json(grants),list_json(grants),[manifest],warn=lambda **fields: None)
    app.dependency_overrides[get_current_user]=lambda: SimpleNamespace(role=role,username="actor")
    app.dependency_overrides[get_db]=lambda: None
    monkeypatch.setattr(service,"current_price",AsyncMock(return_value=None))
    monkeypatch.setattr(service,"price_history",AsyncMock(side_effect=lambda db,page,page_size,day=None: PricePage(items=[],total=0,page=page,page_size=page_size)))
    monkeypatch.setattr(service,"save_price",AsyncMock(return_value=snapshot()))
    return app


def list_json(grants):
    import json
    return json.dumps(list(grants))


@pytest.mark.asyncio
async def test_asgi_wire_contract_and_pagination(monkeypatch):
    app=app_for(monkeypatch)
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        current=await client.get("/api/v1/energy/current")
        assert current.status_code==200 and current.json()["data"] is None
        assert current.json()["code"]==200 and current.json()["message"]=="success"
        empty=await client.get("/api/v1/energy")
        assert empty.json()["data"]==dict(items=[],total=0,page=1,pageSize=20)
        saved=await client.post("/api/v1/energy",json=dict(electricPrice=0,hydrogenPrice="1.2345",argonPrice="999999.9999",remark="  snapshot  "))
        assert saved.status_code==200
        row=saved.json()["data"]
        assert set(row)=={"id","electricPrice","hydrogenPrice","argonPrice","electricRemark","hydrogenRemark","argonRemark","remark","operator","createdAt","updatedAt","observedAt","hourStart"}
        assert row["electricPrice"]==0 and row["operator"]=="actor" and row["remark"]=="  snapshot  "
        assert all(isinstance(row[key],(int,float)) for key in ("electricPrice","hydrogenPrice","argonPrice"))
        service.save_price.assert_awaited_once()
        assert service.save_price.call_args.args[2]=="actor"
        service.current_price.return_value=snapshot()
        assert (await client.get("/api/v1/energy/current")).json()["data"]==row
        service.price_history.side_effect=lambda db,page,page_size,day=None: PricePage(items=[snapshot()] if page==1 else [],total=1,page=page,page_size=page_size)
        assert (await client.get("/api/v1/energy?pageSize=100")).json()["data"]["items"]==[row]
        assert (await client.get("/api/v1/energy?page=99&pageSize=1")).json()["data"]==dict(items=[],total=1,page=99,pageSize=1)
        for query in ("page=0","page=-1","pageSize=0","pageSize=101","page=x"):
            assert (await client.get("/api/v1/energy?"+query)).status_code==422
        for key in ("id","operator","createdAt","updatedAt"):
            assert (await client.post("/api/v1/energy",json=dict(electricPrice=0,hydrogenPrice=1,argonPrice=2,**{key:"forged"}))).status_code==422
        for literal in ("NaN", "Infinity", "-Infinity"):
            response = await client.post("/api/v1/energy", content='{"electricPrice":'+literal+',"hydrogenPrice":1,"argonPrice":2}', headers={"Content-Type":"application/json"})
            assert response.status_code == 422
        for value in (True,None,"","NaN","Infinity",-1,"0.00001","1000000"):
            assert (await client.post("/api/v1/energy",json=dict(electricPrice=value,hydrogenPrice=1,argonPrice=2))).status_code==422


@pytest.mark.asyncio
@pytest.mark.parametrize("role",["admin","supervisor","operator","unknown"])
@pytest.mark.parametrize("grants",[(),("energy-price-read",),("energy-price-manage",),("energy-price-read","energy-price-manage"),("auxiliary",)])
async def test_independent_permission_matrix(monkeypatch,role,grants):
    app=app_for(monkeypatch,role,grants)
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        for method,path,permission in (("GET","/api/v1/energy/current","energy-price-read"),("GET","/api/v1/energy","energy-price-read"),("POST","/api/v1/energy","energy-price-manage")):
            response=await client.request(method,path,**({"json":dict(electricPrice=0,hydrogenPrice=1,argonPrice=2)} if method=="POST" else {}))
            allowed=role=="admin" or (role in {"supervisor","operator"} and permission in grants)
            assert response.status_code==(200 if allowed else 403)


@pytest.mark.asyncio
async def test_unauthenticated_and_disabled_routes(monkeypatch):
    app=app_for(monkeypatch)
    app.dependency_overrides.pop(get_current_user)
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        for path in ("/api/v1/energy/current","/api/v1/energy"):
            assert (await client.get(path)).status_code in {401,403}
        assert (await client.post("/api/v1/energy",json=dict(electricPrice=0,hydrogenPrice=1,argonPrice=2))).status_code in {401,403}
    # Real registry assembly with a disabled manifest has no route/OpenAPI surface for any actor.
    app=FastAPI(); router=APIRouter()
    include_module_routers(router,[replace(manifest,enabled=False)])
    app.include_router(router,prefix="/api/v1")
    assert not app.openapi()["paths"]
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
        assert (await client.get("/api/v1/energy/current")).status_code==404
        assert (await client.get("/api/v1/energy")).status_code==404
        assert (await client.post("/api/v1/energy")).status_code==404


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["electricPrice", "hydrogenPrice", "argonPrice"])
@pytest.mark.parametrize("literal", [
    "1.23450000000000001", "999999.99990000001", "0.000100000000000000001",
    "0.00001", "1000000", "1e-5", "1e999", "-0.0001",
])
async def test_raw_json_number_precision_rejects_before_save(monkeypatch, field, literal):
    app = app_for(monkeypatch)
    values = {"electricPrice": "0", "hydrogenPrice": "1", "argonPrice": "2"}
    values[field] = literal
    raw = "{" + ",".join('"' + key + '":' + value for key, value in values.items()) + "}"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/energy", content=raw,
                                     headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    service.save_price.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("literal", [
    "0", "0.0000000000000000", "0.0001", "1.2345", "999999.9999",
    "1.2345000000000000000000000000000000", "999999.99990000", "1e-4",
])
async def test_raw_json_number_accepts_exact_boundary_and_trailing_zeros(monkeypatch, literal):
    app = app_for(monkeypatch)
    raw = '{"electricPrice":' + literal + ',"hydrogenPrice":1,"argonPrice":2}'
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/energy", content=raw,
                                     headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    service.save_price.assert_awaited_once()
    assert service.save_price.call_args.args[1].electric_price == Decimal(literal)


@pytest.mark.asyncio
@pytest.mark.parametrize("raw", [
    '{"electricPrice":0,"hydrogenPrice":1,"argonPrice":2,"remark":1.23}',
    '{"electricPrice":0,"hydrogenPrice":1,"argonPrice":2,"id":1e999}',
    '{"electricPrice":0,"hydrogenPrice":1,"argonPrice":2,"remark":NaN}',
    '{"electricPrice":0.1,',
])
async def test_exact_json_parser_preserves_other_validation_failures(monkeypatch, raw):
    app = app_for(monkeypatch)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/energy", content=raw,
                                     headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    service.save_price.assert_not_awaited()


@pytest.mark.asyncio
async def test_observed_at_single_api_clock_null_offsets_and_future(monkeypatch):
    from app.energy.api import energy_price as api
    app = app_for(monkeypatch)
    clock = datetime(2026, 10, 13, 4, 0, tzinfo=timezone.utc)
    calls = []
    monkeypatch.setattr(api, "utc_now", lambda: calls.append(clock) or clock)
    base = dict(electricPrice=0, hydrogenPrice=1, argonPrice=2)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for extra in ({}, {"observedAt": None}, {"observedAt": "2026-10-13T12:00:00+08:00"}, {"observedAt": "2026-10-13T04:00:00Z"}, {"observedAt": "2026-10-13T04:00Z"}):
            calls.clear()
            response = await client.post('/api/v1/energy', json={**base, **extra})
            assert response.status_code == 200
            assert calls == [clock]
            assert service.save_price.call_args.args[3] == clock
        for value in ("", "2026-10-13T04:00:00", "2026-02-30T00:00:00Z", "no", 1, True, [], {}, "0001-01-01T00:00:00Z", "9999-12-31T23:59:59Z", "2026-10-13T04:00:01Z"):
            service.save_price.reset_mock()
            response = await client.post('/api/v1/energy', json={**base, "observedAt": value})
            assert response.status_code == 422, value
            service.save_price.assert_not_awaited()
        for key in ('hourStart', 'observed_at'):
            # snake_case remains ApiSchema-compatible for observed_at, but never for server hour.
            if key == 'observed_at': continue
            assert (await client.post('/api/v1/energy',json={**base,key:'forged'})).status_code == 422
        await client.get('/api/v1/energy/current')
        assert service.current_price.call_args.args[1] == clock
        row = snapshot().model_dump(mode='json', by_alias=True)
        for key in ('observedAt','hourStart','createdAt','updatedAt'):
            assert row[key].endswith('+08:00')


@pytest.mark.asyncio
async def test_date_validation_three_paths_and_filter_forwarding(monkeypatch):
    app = app_for(monkeypatch)
    paths = {path: set(methods) for path, methods in app.openapi()['paths'].items() if path == '/api/v1/energy' or path.startswith('/api/v1/energy/')}
    assert paths == {'/api/v1/energy': {'get','post'}, '/api/v1/energy/current': {'get'}}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for value in ('2024-02-29', '0001-01-01', '9999-12-31', '2099-01-01'):
            response = await client.get('/api/v1/energy', params={'date':value,'page':2,'pageSize':24})
            assert response.status_code == 200
            assert service.price_history.call_args.args == (None,2,24,date.fromisoformat(value))
        for query in ('date=', 'date=2026-2-01', 'date=2026-02-29', 'date=2024-02-30', 'date=2026-10-13&date=2026-10-12', 'date=no', 'date=10000-01-01'):
            service.price_history.reset_mock()
            assert (await client.get('/api/v1/energy?'+query)).status_code == 422, query
            service.price_history.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize('observed_at,expected_status', [
    ('1000-01-01T00:00:00Z', 422),
    ('1000-01-01T08:00:00+08:00', 422),
    ('1000-01-01T00:54:16.999999Z', 422),
    ('1000-01-01T00:54:17Z', 200),
    ('1000-01-01T00:54:18Z', 200),
])
async def test_real_service_asgi_checks_derived_hour_mysql_lower_bound(monkeypatch, observed_at, expected_status):
    # F-001 regression: real Router/Schema/Service, only persistence/auth are fixtures.
    from app.energy.crud import async_energy_price as crud
    app = create_app(testing=True)
    db = SimpleNamespace(commit=AsyncMock(), rollback=AsyncMock())
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role='admin', username='fixture')
    app.dependency_overrides[get_db] = lambda: db
    async def persist(_db, values, actor):
        return SimpleNamespace(**values, id=1, operator=actor,
                               created_at=datetime(2026,10,13), updated_at=datetime(2026,10,13))
    write = AsyncMock(side_effect=persist)
    monkeypatch.setattr(crud, 'upsert_price', write)
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        response = await client.post('/api/v1/energy', json=dict(
            electricPrice=0, hydrogenPrice='1.2345', argonPrice=2, observedAt=observed_at,
        ))
    assert response.status_code == expected_status
    if expected_status == 422:
        write.assert_not_awaited(); db.commit.assert_not_awaited(); db.rollback.assert_not_awaited()
    else:
        write.assert_awaited_once(); db.commit.assert_awaited_once()
        values = write.call_args.args[1]
        assert values['observed_at'] == datetime.fromisoformat(observed_at.replace('Z','+00:00')).replace(tzinfo=None)
        assert values['hour_start'] == datetime(1000,1,1,0,54,17)
        row = response.json()['data']
        assert row['electricPrice'] == 0 and row['hydrogenPrice'] == 1.2345
        assert row['hourStart'] == '1000-01-01T08:54:17+08:00'
