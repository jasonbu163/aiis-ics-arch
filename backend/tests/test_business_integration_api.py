"""A0 八路拒绝、旧认证、模块关闭及依赖退出的真实 ASGI 内存测试。"""
from copy import deepcopy
from dataclasses import replace
import importlib
import json

import pytest
from fastapi import APIRouter, Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from common.integration.canonical import canonical_bytes
from common.integration.receipt import IntegrationReceipt, receipt_response
from starlette.responses import Response
from tests.test_business_integration_contract import example, REQUESTS, RESOURCES

pytestmark = pytest.mark.no_db
PATHS = ("equipment/temperature-samples", "equipment/drive-samples", "equipment/production-parameter-samples",
         "performances/production-observations", "performances/101/process-temperature-samples",
         "performances/101/process-tension-samples", "performances/101/process-speed-samples", "monitor/process-curve-samples")
OWNERS = ("equipment",) * 3 + ("performance",) * 4 + ("monitor",)


def composed_router():
    from app.module_registry import include_module_routers
    router = APIRouter()
    include_module_routers(router)
    return router


def local_app(owner, enabled=False, devices='["line-demo"]', producers='["sma-demo"]', profile="unadopted"):
    api = importlib.import_module(f"app.{owner}.api.integration")
    app = FastAPI(debug=True)
    app.include_router(api.router, prefix="/api/v1")
    prefix = owner.upper() + "_INTEGRATION_"
    config = api.IntegrationConfig(_env_file=None, **{prefix+"ENABLED":enabled,
        prefix+"EQUIPMENT_IDS_JSON":devices, prefix+"PRODUCER_IDS_JSON":producers, prefix+"STORAGE_PROFILE":profile})
    app.dependency_overrides[api.get_integration_config] = lambda: config
    return app


@pytest.mark.parametrize("index", range(8))
@pytest.mark.parametrize("enabled,devices,producers,profile,status,suffix", [
    (False,'["line-demo"]','["sma-demo"]',"unadopted",403,"scope_rejected"),
    (True,'[]','["sma-demo"]',"unadopted",403,"scope_rejected"),
    (True,'["LINE-DEMO"]','["sma-demo"]',"unadopted",403,"scope_rejected"),
    (True,'["line-demo"]','["other"]',"unadopted",403,"scope_rejected"),
    (True,'["line-demo"]','["sma-demo"]',"unadopted",503,"not_ready"),
    (True,'["line-demo"]','["sma-demo"]',"pretend-adopted",503,"not_ready"),
])
async def test_eight_routes_fail_closed_without_credentials_or_db(index, enabled, devices, producers, profile, status, suffix, monkeypatch):
    app = local_app(OWNERS[index], enabled, devices, producers, profile)
    from database import get_db
    def db_denied(): raise AssertionError("database dependency entered")
    app.dependency_overrides[get_db] = db_denied
    async def session_denied(): raise AssertionError("new session factory entered")
    monkeypatch.setattr(importlib.import_module(f"app.{OWNERS[index]}.api.integration"),"get_db_session",session_denied)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://fixture") as client:
        response = await client.post("/api/v1/integration/"+PATHS[index], content=canonical_bytes(example(index)), headers={"content-type":"application/json"})
    error = OWNERS[index]+".integration_"+suffix
    assert response.status_code == status
    assert response.json() == {"code":status,"message":error,"data":None,"errorCode":error}


@pytest.mark.parametrize("index", range(8))
@pytest.mark.parametrize("case,status,suffix", [
    ("128", 503, "not_ready"),
    ("129", 413, "payload_too_large"),
    ("unknown_field", 422, "invalid_request"),
    ("wrong_type", 422, "invalid_request"),
    ("identifier_too_long", 422, "invalid_request"),
])
async def test_source_reference_limit_in_normal_composition(index, case, status, suffix, monkeypatch):
    from core.registrar import create_app
    from database import get_db
    prefix = OWNERS[index].upper() + "_INTEGRATION_"
    monkeypatch.setenv(prefix + "ENABLED", "True")
    monkeypatch.setenv(prefix + "EQUIPMENT_IDS_JSON", '["line-demo"]')
    monkeypatch.setenv(prefix + "PRODUCER_IDS_JSON", '["sma-demo"]')
    monkeypatch.setenv(prefix + "STORAGE_PROFILE", "unadopted")
    app = create_app(testing=True)
    def db_denied():
        raise AssertionError("database dependency entered")
    app.dependency_overrides[get_db] = db_denied
    async def session_denied(): raise AssertionError("new session factory entered")
    monkeypatch.setattr(importlib.import_module(f"app.{OWNERS[index]}.api.integration"),"get_db_session",session_denied)
    payload = example(index)
    payload["sourceRefs"] = [{"kind": "external_event", "sourceId": "source", "sourceEventId": str(i)}
                             for i in range(129 if case == "129" else 128)]
    if case == "unknown_field":
        payload["sourceRefs"][0]["unknown"] = "invalid"
    elif case == "wrong_type":
        payload["sourceRefs"] = {"kind": "external_event"}
    elif case == "identifier_too_long":
        payload["sourceRefs"][0]["sourceId"] = "s" * 129
    body = canonical_bytes(payload)
    assert len(body) < 65536
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://fixture") as client:
        response = await client.post("/api/v1/integration/" + PATHS[index], content=body,
                                     headers={"content-type": "application/json"})
    error = OWNERS[index] + ".integration_" + suffix
    assert response.status_code == status
    assert response.json() == {"code": status, "message": error, "data": None, "errorCode": error}


@pytest.mark.parametrize("body,headers,status,suffix", [
    (b'{"a":1,"a":2}', {"content-type":"application/json"},422,"invalid_request"),
    (b'{"data":{"tv":1,"tv":2}}', {"content-type":"application/json"},422,"invalid_request"),
    (b'{"data":{"tv":NaN}}', {"content-type":"application/json"},422,"invalid_request"),
    (b'{"data":"\xff"}', {"content-type":"application/json"},422,"invalid_request"),
    (b'{}', {"content-type":"text/plain"},415,"media_type"),
    (b'{}', {"content-type":"application/json; charset=latin1"},415,"media_type"),
    (b'{}', {"content-type":"application/json; charset = latin1"},415,"media_type"),
    (b'{}', {"content-type":"application/json", "content-encoding":"gzip"},415,"media_type"),
    (b' ' * 65537, {"content-type":"application/json"},413,"payload_too_large"),
    (b'{"a":'+b'['*12+b'0'+b']'*12+b'}', {"content-type":"application/json"},413,"payload_too_large"),
])
async def test_raw_http_status_and_error_shell(body, headers, status, suffix):
    async with AsyncClient(transport=ASGITransport(app=local_app("equipment",True)), base_url="http://fixture") as client:
        response = await client.post("/api/v1/integration/equipment/drive-samples", content=body, headers=headers)
    assert response.status_code == status
    assert response.json()["code"] == status and response.json()["data"] is None
    assert response.json()["errorCode"] == "equipment.integration_"+suffix


@pytest.mark.parametrize("database_failure", [False, True])
async def test_complete_yield_dependency_exit_precedes_success_and_debug_is_sanitized(database_failure):
    from app.equipment.api.integration import ModuleIntegrationRoute
    app = FastAPI(debug=True)
    app.router.route_class = ModuleIntegrationRoute
    async def late_failure():
        yield
        if database_failure:
            from sqlalchemy.exc import DBAPIError
            raise DBAPIError("SECRET SQL DSN body", {}, Exception("SECRET"))
        raise RuntimeError("SECRET SQL DSN body")
    @app.post("/exit", dependencies=[Depends(late_failure)])
    async def endpoint(): return {"code":200, "data":{"committed":True}}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://fixture") as client:
        response = await client.post("/exit", json={})
    assert response.status_code == (503 if database_failure else 500)
    assert response.json()["errorCode"] == ("equipment.integration_unavailable" if database_failure else "equipment.integration_internal_error")
    assert "SECRET" not in response.text and "committed" not in response.text


@pytest.mark.parametrize("owner", ["equipment","performance","monitor"])
async def test_registry_disables_new_and_old_whole_group(owner, monkeypatch):
    module = importlib.import_module(f"app.{owner}.manifest")
    monkeypatch.setattr(module, "manifest", replace(module.manifest, enabled=False))
    app = FastAPI()
    app.include_router(composed_router(), prefix="/api/v1")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://fixture") as client:
        for index, route_owner in enumerate(OWNERS):
            if route_owner == owner:
                for path in ("integration/"+PATHS[index], PATHS[index]):
                    response = await client.post("/api/v1/"+path, json={})
                    assert response.status_code == 404


@pytest.mark.parametrize("index",range(8))
async def test_old_posts_still_require_authentication(index):
    app = FastAPI()
    app.include_router(composed_router(), prefix="/api/v1")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://fixture") as client:
        response = await client.post("/api/v1/"+PATHS[index], content=canonical_bytes(example(index)["data"]), headers={"content-type":"application/json"})
    assert response.status_code == 401


def test_receipt_replay_preserves_original_commit_and_explicit_aliases():
    from app.equipment.schemas.integration import DriveReceipt
    from pydantic import ValidationError
    value = dict(producerId="sma-demo", eventId="event-1", equipmentId="line-demo", mappingId="map",
                 mappingRevision="r1", requestDigest="sha256:"+"a"*64, businessDigest="sha256:"+"b"*64,
                 receiptId=501, recordId=101, performanceId=None, affectedRecordIds=[101],
                 sourceTime="2026-11-04T02:00:00.123Z", committedAt="2026-11-04T10:00:01+08:00",
                 confirmation="business_committed", applied=True, outcome="updated", originalOutcome="updated",
                 changedFields=["tv"])
    receipt = DriveReceipt.model_validate(value)
    first = json.loads(receipt_response(receipt))
    replay = json.loads(receipt_response(receipt, replay=True))
    assert replay["data"].pop("outcome") == "duplicate"
    assert first["data"].pop("outcome") == "updated"
    assert first == replay
    assert first["data"]["committedAt"] == "2026-11-04T10:00:01.000+08:00"
    assert first["data"]["sourceTime"] == "2026-11-04T10:00:00.123+08:00"
    assert first["data"]["businessRetention"] == "no_auto_ttl"
    value["changedFields"] = ["arbitrary_field"]
    with pytest.raises(ValidationError): DriveReceipt.model_validate(value)
    value.update(resource="production_observation", changedFields=[], recordId=None, affectedRecordIds=[],
                 applied=False, confirmation="decision_only", outcome="stale", originalOutcome="stale")
    stale = IntegrationReceipt.model_validate(value)
    assert json.loads(receipt_response(stale, replay=True))["data"]["confirmation"] == "decision_only"
    value["applied"] = True
    with pytest.raises(ValidationError): IntegrationReceipt.model_validate(value)


@pytest.mark.parametrize('index', (1,3,7))
@pytest.mark.parametrize('commit_kind,exit_kind,expected_suffix,expected_status', [
    ('dbapi','none','commit_unknown',503), ('dbapi','runtime','commit_unknown',503),
    ('dbapi','dbapi','commit_unknown',503), ('value','none','commit_unknown',503),
    ('value','runtime','commit_unknown',503), ('business','dbapi','commit_unknown',503),
    ('integrity','runtime','commit_unknown',503),
    ('runtime','suppress','commit_unknown',503), ('prevalidate','none','invalid_request',422),
    ('ok','runtime','internal_error',500), ('ok','dbapi','unavailable',503),
])
async def test_real_replay_transaction_commit_phase_survives_complete_session_exit(index,commit_kind,exit_kind,expected_suffix,expected_status,monkeypatch):
    """正常composition/实际Service；仅传入session/probe/receipt替身，无DB。"""
    from types import SimpleNamespace
    from sqlalchemy.exc import DBAPIError,IntegrityError
    from core.registrar import create_app
    from common.exceptions import BusinessException
    from common.integration.canonical import integration_digests
    from common.integration.envelope import source_time
    owner=OWNERS[index]
    api=importlib.import_module(f'app.{owner}.api.integration')
    crud=importlib.import_module(f'app.{owner}.crud.async_integration')
    error=importlib.import_module(f'app.{owner}.integration_error_codes').IntegrationError
    body=example(index);request=REQUESTS[index].model_validate(body)
    request_digest,business_digest=integration_digests(request,RESOURCES[index])
    result=dict(contractVersion='aiis.business-integration/v1',digestProfile='bi-json/v1',producerId=request.producer_id,eventId=request.event_id,resource=RESOURCES[index],equipmentId=request.data.equipment_id,mappingId=request.mapping_id,mappingRevision=request.mapping_revision,requestDigest=request_digest,businessDigest=business_digest,receiptId=501,recordId=101,performanceId=101 if index==3 else None,affectedRecordIds=[101],sourceTime='2026-11-04T10:00:00.123+08:00',committedAt='2026-11-04T10:01:00.000+08:00',status='committed',confirmation='business_committed',applied=True,outcome='created',originalOutcome='created',changedFields=[],businessRetention='no_auto_ttl')
    calls=[]
    class Session:
        async def __aenter__(self):calls.append('enter');return self
        async def __aexit__(self,*args):
            calls.append('exit')
            if exit_kind=='runtime':raise RuntimeError('private exit')
            if exit_kind=='dbapi':raise DBAPIError('private SQL',{},RuntimeError('private DSN'))
            return exit_kind=='suppress'
        async def commit(self):
            calls.append('commit')
            if commit_kind=='dbapi':raise DBAPIError('private SQL',{},RuntimeError('private commit'))
            if commit_kind=='value':raise ValueError('private commit')
            if commit_kind=='runtime':raise RuntimeError('private commit')
            if commit_kind=='business':raise BusinessException(error.VALUE_CONFLICT,code=409)
            if commit_kind=='integrity':raise IntegrityError('private SQL',{},Exception(1062,"Duplicate entry 'private' for key 'uq_"+owner+"_integration_delivery'"))
        async def rollback(self):calls.append('rollback')
    async def factory():return Session()
    async def probe(*args):return source_time('2026-11-04T11:00:00.000+08:00')
    async def receipt(*args):return SimpleNamespace(request_digest=request_digest,result=result)
    monkeypatch.setattr(api,'get_db_session',factory)
    monkeypatch.setattr(crud,'probe_adoption',probe)
    monkeypatch.setattr(crud,'get_receipt',receipt)
    if commit_kind=='prevalidate':
        name='async_integration_observation'if owner=='performance'else'async_integration'
        module=importlib.import_module(f'app.{owner}.services.{name}')
        def invalid_result(*args):raise ValueError('private typed validation')
        monkeypatch.setattr(module,'receipt_response',invalid_result)
    app=create_app(testing=True)
    app.dependency_overrides[api.get_integration_config]=lambda:SimpleNamespace(require_ready=lambda *args:{'fixture':'only'})
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://fixture') as client:
        response=await client.post('/api/v1/integration/'+PATHS[index],content=canonical_bytes(body),headers={'content-type':'application/json'})
    expected=owner+'.integration_'+expected_suffix
    assert response.status_code==expected_status and response.json()==dict(code=expected_status,message=expected,data=None,errorCode=expected)
    assert calls.count('exit')==1
    if commit_kind=='prevalidate':assert calls.count('commit')==0 and calls.count('rollback')==1
    else:assert calls.count('commit')==1 and calls.index('commit')<calls.index('exit')
    assert 'private'not in response.text


@pytest.mark.parametrize('scope,cleanup',(('request','runtime'),('function','runtime'),('request','dbapi'),('function','dbapi'),('request','suppress')))
async def test_commit_unknown_retained_through_both_yield_scopes(scope,cleanup):
    from app.equipment.api.integration import ModuleIntegrationRoute
    from app.equipment.integration_error_codes import IntegrationError
    from common.exceptions import BusinessException
    from sqlalchemy.exc import DBAPIError
    app=FastAPI(debug=True);app.router.route_class=ModuleIntegrationRoute
    calls=[]
    async def failing_exit():
        try:yield
        except Exception:
            calls.append('exit')
            if cleanup=='runtime':raise RuntimeError('private cleanup') from None
            if cleanup=='dbapi':raise DBAPIError('private SQL',{},RuntimeError('private cleanup')) from None
            # Request-scope suppression must never manufacture success or erase recorded unknown.
    @app.post('/exit',dependencies=[Depends(failing_exit,scope=scope)])
    async def endpoint():raise BusinessException(IntegrationError.COMMIT_UNKNOWN,code=503)
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://fixture')as client:
        response=await client.post('/exit',json={})
    assert response.status_code==503 and response.json()['errorCode']=='equipment.integration_commit_unknown'
    assert calls==['exit']
