"""真实ASGI原始JSON、现有JWT依赖及局部HTTP脱敏矩阵；不连接DB。"""
from datetime import timedelta
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from app.equipment.api.temperature_samples import router
from app.equipment.config import TemperatureConfig, get_temperature_config
from app.equipment.services import async_temperature_sample as service
from core.deps import get_current_user
from core.jwt import create_access_token, create_refresh_token
from database import get_db
from tests.test_equipment_temperature_service import MemoryTransactions, payload

pytestmark=pytest.mark.no_db


@pytest.fixture
def harness(monkeypatch):
    db=MemoryTransactions();db.install(monkeypatch)
    app=FastAPI(debug=True); app.include_router(router,prefix="/api/v1")
    app.state.role_api_permissions={"supervisor":(),"operator":()}
    actor=SimpleNamespace(id=1,role="admin",is_active=True)
    app.dependency_overrides[get_current_user]=lambda:actor
    app.dependency_overrides[get_db]=lambda:db
    app.dependency_overrides[get_temperature_config]=lambda:TemperatureConfig(EQUIPMENT_TEMPERATURE_PILOT_ID="temperature-pilot-01",_env_file=None)
    return app,db,actor


async def request(app,method="POST",raw=None,query="",headers=None):
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://fixture") as client:
        return await client.request(method,"/api/v1/equipment/temperature-samples"+query,
            content=raw if raw is not None else (json.dumps(payload()) if method=="POST" else None),headers=headers if headers is not None else {"Content-Type":"application/json","Authorization":"Bearer synthetic-override"})


def error(response,status,key):
    assert response.status_code==status
    assert response.json()==dict(code=status,message="equipment.temperature_"+key,data=None,errorCode="equipment.temperature_"+key)


@pytest.mark.asyncio
async def test_real_post_get_camelcase_zero_milliseconds(harness):
    app,db,actor=harness
    response=await request(app);assert response.status_code==200
    first=response.json()["data"]
    assert first==dict(recordId=1,equipmentId="temperature-pilot-01",sampleId="sample-A",sampledAt="2026-10-16T10:00:00.123Z",outcome="created")
    response=await request(app,"GET",query="?recordId=1&limit=1")
    item=response.json()["data"]["items"][0]
    assert item["zone1Set"]==0 and item["zone5Act"]==5.5 and item["sampledAt"].endswith(".123Z")
    assert not {"sampleId","actorUserId","fingerprint"}&item.keys()
    assert len([key for key in item if key.startswith("zone")])==10
    duplicate=await request(app);assert duplicate.json()["data"]["outcome"]=="duplicate"
    response=await request(app,raw=json.dumps(payload(zone1Set=1)));error(response,409,"sample_id_conflict")
    response=await request(app,raw=json.dumps(payload(sampleId="other",zone1Set=1)));error(response,409,"sample_time_conflict")


INVALID=[{"zone1Set":None},{"zone1Set":True},{"zone1Set":"1"},{"quality":"bad"},{"zone1Set":1e20},
 {"zone1Set":1e-11},{"sampleId":" x"},{"sampleId":"x\n"},{"sampleId":""},{"equipmentId":"other"},
 {"sampledAt":"2026-10-16T10:00:00+00:60"},{"sampledAt":"2026-10-16T10:00:00+01:99"},{"sampledAt":"2026-10-16T10:00:00+24:00"},{"sampledAt":"2026-10-16T10:00:00"},{"sampledAt":"2026-10-16T10:00:00.1231Z"},
 {"sampledAt":"0999-12-31T23:00:00Z"},{"sampledAt":"1000-01-01T00:00:00+01:00"},
 {"sampledAt":"9999-12-31T23:59:59-01:00"},{"extra":1},{"zone1_set":0}]
@pytest.mark.asyncio
@pytest.mark.parametrize("changes",INVALID)
async def test_raw_invalid_samples(harness,changes):
    app,db,_=harness;response=await request(app,raw=json.dumps(payload(**changes)))
    error(response,403 if changes.get("equipmentId")=="other" else 422,"forbidden" if changes.get("equipmentId")=="other" else "invalid_sample")
    assert not db.samples and not db.receipts and db.commits==0


@pytest.mark.asyncio
@pytest.mark.parametrize("raw",['{}','null','[]','{','{"zone1Set":NaN}','{"zone1Set":Infinity}',json.dumps(payload()).replace('"zone1Set": 0','"zone1Set": 0, "zone1Set": 1'),json.dumps(payload()).replace('"zone1Set": 0,',''),json.dumps(payload()).replace('"zone1Set": 0','"zone1Set": 9007199254740991.0000000001')])
async def test_raw_missing_duplicate_nonfinite_and_lossy_number(harness,raw):
    app,db,_=harness;error(await request(app,raw=raw),422,"invalid_sample");assert not db.samples


@pytest.mark.asyncio
@pytest.mark.parametrize("role,grants,read,write",[("admin",(),200,200),("supervisor",("equipment-temperature-read",),200,403),("operator",("equipment-temperature-read",),200,403),("supervisor",("equipment-temperature-ingest",),403,403),("operator",("equipment", "mapping-manage", "control-agent-read"),403,403),("unknown",("equipment-temperature-read",),403,403)])
async def test_independent_role_permission_matrix(harness,role,grants,read,write):
    app,db,actor=harness;actor.role=role;app.state.role_api_permissions[role]=grants
    response=await request(app,"GET");assert response.status_code==read
    response=await request(app);assert response.status_code==write
    if write==403:assert not db.samples


@pytest.mark.asyncio
@pytest.mark.parametrize("method",["GET","POST"])
async def test_empty_scope_and_cross_scope_refused_before_queries(harness,method):
    app,db,_=harness
    app.dependency_overrides[get_temperature_config]=lambda:TemperatureConfig(_env_file=None,EQUIPMENT_TEMPERATURE_PILOT_ID="")
    error(await request(app,method),403,"forbidden")
    assert not db.samples and not db.receipts


@pytest.mark.asyncio
@pytest.mark.parametrize("query",["?limit=0","?limit=1001","?limit=x","?recordId=0","?extra=1","?equipment_id=temperature-pilot-01"])
async def test_query_validation(harness,query):
    error(await request(harness[0],"GET",query=query),422,"invalid_sample")


@pytest.mark.asyncio
async def test_debug_system_failures_are_local_sanitized_http(harness,monkeypatch):
    app,db,_=harness
    monkeypatch.setattr(service,"read_samples",AsyncMock(side_effect=RuntimeError("password=mysql://private SQL")))
    error(await request(app,"GET"),500,"internal_error")
    db.failure="commit"
    error(await request(app),503,"unavailable")


@pytest.mark.asyncio
@pytest.mark.parametrize("kind",["missing","basic","bad","expired","refresh","revoked","inactive"])
@pytest.mark.parametrize("method",["GET","POST"])
async def test_existing_auth_dependency_is_401(harness,monkeypatch,kind,method):
    app,db,actor=harness;app.dependency_overrides.pop(get_current_user)
    from app.user.services.async_token_blacklist import TokenBlacklistService
    monkeypatch.setattr(TokenBlacklistService,"is_blacklisted",AsyncMock(return_value=kind=="revoked"))
    class Result:
        def scalar_one_or_none(self):return actor
    db.execute=AsyncMock(return_value=Result())
    actor.is_active=kind!="inactive"
    token=create_access_token({"sub":"fixture"})
    if kind=="bad":token="invalid"
    if kind=="expired":token=create_access_token({"sub":"fixture"},timedelta(seconds=-1))
    if kind=="refresh":token=create_refresh_token({"sub":"fixture"})
    headers={"Content-Type":"application/json"}
    if kind!="missing":headers["Authorization"]=("Basic " if kind=="basic" else "Bearer ")+token
    response=await request(app,method,headers=headers)
    error(response,401,"unauthenticated");assert response.headers["www-authenticate"]=="Bearer"
    assert not db.samples


@pytest.mark.asyncio
async def test_module_disabled_removes_old_and_new_routes(monkeypatch):
    from dataclasses import replace
    import importlib
    import app.equipment.manifest as declaration
    import app.router as routes
    from core.registrar import create_app
    monkeypatch.setattr(declaration,"manifest",replace(declaration.manifest,enabled=False))
    try:
        importlib.reload(routes)
        app=create_app(testing=True)
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://fixture") as client:
            for path in ("temperature-samples","temperature-control","drive","production-parameters"):
                assert (await client.get("/api/v1/equipment/"+path)).status_code==404
            assert (await client.post("/api/v1/equipment/temperature-samples")).status_code==404
    finally:
        monkeypatch.undo();importlib.reload(routes)


@pytest.mark.asyncio
async def test_failed_log_sink_never_leaks_debug_traceback(harness,monkeypatch):
    import app.equipment.api.temperature_http as adapter
    app,db,_=harness
    def failed(*args,**kwargs):raise RuntimeError("private password SQL")
    monkeypatch.setattr(service,"log_event",failed)
    monkeypatch.setattr(adapter,"log_event",failed)
    error(await request(app),500,"internal_error")
    assert len(db.saved_samples)==len(db.saved_receipts)==1


@pytest.mark.asyncio
async def test_unauthenticated_invalid_json_is_401_before_body(harness):
    error(await request(harness[0],raw="{",headers={"Content-Type":"application/json"}),401,"unauthenticated")


@pytest.mark.asyncio
@pytest.mark.parametrize("raw",[b"\xff",json.dumps(payload()).replace('"zone1Set": 0','"zone1Set": 1e9999')])
async def test_invalid_utf8_and_numeric_overflow_are_controlled_422(harness,raw):
    error(await request(harness[0],raw=raw),422,"invalid_sample")


@pytest.mark.asyncio
@pytest.mark.parametrize("number",["-0","1.0000000000","0.0000000001","99999999999999999999","-99999999999999999999"])
async def test_exact_numeric_storage_boundary_acceptance(harness,number):
    raw=json.dumps(payload()).replace('"zone1Set": 0','"zone1Set": '+number)
    response=await request(harness[0],raw=raw);assert response.status_code==200
    response=await request(harness[0],"GET",query="?recordId=1")
    from decimal import Decimal
    assert Decimal(str(response.json()["data"]["items"][0]["zone1Set"]))==Decimal(number)


@pytest.mark.asyncio
async def test_json_lines_have_controlled_object_context_and_no_payload(harness):
    import io
    from common.log import logger
    stream=io.StringIO();sink=logger.add(stream,serialize=True)
    try:
        await request(harness[0])
        await request(harness[0],raw=json.dumps(payload(zone1Set=1)))
        await request(harness[0],raw=json.dumps(payload(equipmentId="other")))
    finally:logger.remove(sink)
    events=[json.loads(line)["record"]["extra"] for line in stream.getvalue().splitlines()]
    success=next(e for e in events if e.get("event")=="temperature_sample_received")
    assert success["actor_user_id"]==1 and success["equipment_id"]=="temperature-pilot-01" and success["sample_id"]=="sample-A"
    conflict=next(e for e in events if e.get("event")=="temperature_sample_conflict")
    assert conflict["sample_id"]=="sample-A" and conflict["actor_user_id"]==1
    scope=next(e for e in events if e.get("error_code")=="equipment.temperature_forbidden")
    assert scope["actor_user_id"]==1 and scope["equipment_id"]=="other"
    for event in events:
        assert not {"token","authorization","zone1Set","zone1_set","payload","sql"}&event.keys()


@pytest.mark.asyncio
@pytest.mark.parametrize("status,key",[(500,"internal_error"),(503,"unavailable"),(422,"invalid_sample")])
async def test_dependency_http_errors_preserve_safe_status(harness,status,key):
    from fastapi import HTTPException
    def failure():raise HTTPException(status,detail="private SQL password")
    harness[0].dependency_overrides[get_db]=failure
    error(await request(harness[0],"GET"),status,key)


@pytest.mark.asyncio
async def test_unexpected_business_or_output_schema_errors_are_internal(harness,monkeypatch):
    from common.exceptions import BusinessException
    from common.error_codes import ErrorCode
    from app.equipment.schemas.temperature_sample_out import TemperatureSampleOut
    for failure in (BusinessException(ErrorCode.USER_NOT_FOUND),None):
        async def fail(*args,**kwargs):
            if failure:raise failure
            return TemperatureSampleOut.model_validate({})
        monkeypatch.setattr(service,"read_samples",fail)
        error(await request(harness[0],"GET"),500,"internal_error")
    from fastapi import HTTPException
    def permission_failure():raise HTTPException(403,detail={"secret":"private"})
    harness[0].dependency_overrides[get_db]=permission_failure
    error(await request(harness[0],"GET"),403,"forbidden")


@pytest.mark.asyncio
@pytest.mark.parametrize("number",["1e99999999999999999999999999999999999999999999999999","1e-99999999999999999999999999999999999999999999999999"])
async def test_decimal_parser_exponent_domain_errors_are_422(harness,number):
    raw=json.dumps(payload()).replace('"zone1Set": 0','"zone1Set": '+number)
    error(await request(harness[0],raw=raw),422,"invalid_sample")


@pytest.mark.asyncio
async def test_json_parser_recursion_failure_is_422(harness):
    raw="["*1100+"0"+"]"*1100
    error(await request(harness[0],raw=raw),422,"invalid_sample")


class ExitStore:
    """仅Python对象模拟已提交数据；不连接或创建任何数据库。"""
    def __init__(self):
        self.samples=[]
        self.receipts=[]


class ExitSession:
    """真实CRUD/Service/get_db使用的无DB Session，故障精确区分业务和依赖退出。"""
    def __init__(self,store,method,fault=None):
        self.store,self.method,self.fault=store,method,fault
        self.samples,self.receipts=list(store.samples),list(store.receipts)
        self.commits=self.rollbacks=self.closes=self.flushes=0
        self.order=[]

    async def __aenter__(self):return self
    async def __aexit__(self,*args):self.order.append("context_exit")

    async def execute(self,statement):
        from app.equipment.models.temperature_sample import EquipmentTemperatureSample as Sample
        entity=statement.column_descriptions[0]["entity"]
        rows=list(self.samples if entity is Sample else self.receipts)
        for clause in statement._where_criteria:
            rows=[row for row in rows if getattr(row,clause.left.key)==clause.right.value]
        if statement._order_by_clauses:
            rows.sort(key=lambda row:(row.sampled_at,row.id),reverse=True)
        if statement._limit_clause is not None:rows=rows[:statement._limit_clause.value]
        class Result:
            def scalar_one_or_none(self):
                assert len(rows)<=1
                return rows[0] if rows else None
            def scalars(self):return self
            def all(self):return rows
        return Result()

    def add(self,row):
        from app.equipment.models.temperature_sample import EquipmentTemperatureSample as Sample
        (self.samples if isinstance(row,Sample) else self.receipts).append(row)

    async def flush(self):
        from datetime import datetime
        self.flushes+=1
        if self.fault=="business_flush" and self.flushes==1:raise RuntimeError("PRIVATE business flush")
        if self.fault=="receipt_flush" and self.flushes==2:raise RuntimeError("PRIVATE receipt flush")
        for rows in (self.samples,self.receipts):
            for index,row in enumerate(rows,1):
                if row.id is None:row.id=index
                if row.created_at is None:row.created_at=datetime(2026,10,16)
                if row.updated_at is None:row.updated_at=datetime(2026,10,16)

    async def commit(self):
        from sqlalchemy.exc import OperationalError
        self.commits+=1;self.order.append("commit_"+str(self.commits))
        boundary=1 if self.method=="GET" or self.fault=="service_commit" else 2
        if self.fault in {"commit","rollback","service_commit"} and self.commits==boundary:
            raise OperationalError("PRIVATE SQL",{},Exception("PRIVATE DSN"))
        self.store.samples,self.store.receipts=list(self.samples),list(self.receipts)

    async def rollback(self):
        self.rollbacks+=1;self.order.append("rollback")
        if self.fault=="rollback":raise RuntimeError("PRIVATE rollback")
        self.samples,self.receipts=list(self.store.samples),list(self.store.receipts)

    async def close(self):
        self.closes+=1;self.order.append("close")
        if self.fault=="close":raise RuntimeError("PRIVATE close")


async def raw_asgi(app,method="GET",path="/api/v1/equipment/temperature-samples",data=None,order=None):
    """直接捕获ASGI发送时序；不使用listener或网络transport。"""
    order=order if order is not None else []
    body=json.dumps(data).encode() if data is not None else b""
    sent=[];used=False
    async def receive():
        nonlocal used
        if not used:
            used=True
            return {"type":"http.request","body":body,"more_body":False}
        return {"type":"http.disconnect"}
    async def send(message):
        if message["type"]=="http.response.start":order.append("response_start_"+str(message["status"]))
        if message["type"]=="http.response.body":order.append("response_body")
        sent.append(message)
    scope={"type":"http","asgi":{"version":"3.0","spec_version":"2.3"},"http_version":"1.1",
           "method":method,"scheme":"http","path":path,"raw_path":path.encode(),"query_string":b"",
           "root_path":"","headers":[(b"authorization",b"Bearer synthetic-override"),(b"content-type",b"application/json")],
           "client":("127.0.0.1",0),"server":("fixture",80)}
    await app(scope,receive,send)
    starts=[message["status"] for message in sent if message["type"]=="http.response.start"]
    result=json.loads(b"".join(message.get("body",b"") for message in sent if message["type"]=="http.response.body"))
    assert len(starts)==1
    return starts[0],result,scope


def exit_app(monkeypatch,session,debug):
    import database.session_async as sessions
    from core.registrar import register_exception_handlers
    monkeypatch.setattr(sessions,"async_session_maker",lambda:session)
    app=FastAPI(debug=debug);register_exception_handlers(app)
    app.include_router(router,prefix="/api/v1")
    app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(id=1,role="admin",is_active=True)
    app.dependency_overrides[get_temperature_config]=lambda:TemperatureConfig(EQUIPMENT_TEMPERATURE_PILOT_ID="temperature-pilot-01",_env_file=None)
    return app


@pytest.mark.asyncio
@pytest.mark.parametrize("debug",[False,True])
@pytest.mark.parametrize("method",["GET","POST"])
@pytest.mark.parametrize("fault",[None,"commit","rollback","close"])
async def test_real_get_db_exit_finishes_before_any_response_and_replay_recovers(monkeypatch,debug,method,fault):
    store=ExitStore();session=ExitSession(store,method,fault)
    app=exit_app(monkeypatch,session,debug)
    status,result,_=await raw_asgi(app,method,data=payload() if method=="POST" else None,order=session.order)
    expected=200 if fault is None else (503 if fault=="commit" else 500)
    assert status==result["code"]==expected
    if fault is not None:
        key="unavailable" if fault=="commit" else "internal_error"
        assert result==dict(code=expected,message="equipment.temperature_"+key,data=None,errorCode="equipment.temperature_"+key)
        assert "response_start_200" not in session.order
    assert session.order.index("close")<session.order.index("response_start_"+str(expected))
    assert session.order.index("context_exit")<session.order.index("response_start_"+str(expected))
    assert session.commits==(2 if method=="POST" else 1)
    assert session.closes==1
    if method=="POST":
        assert len(store.samples)==len(store.receipts)==1
        committed=store.samples[0].id
        retry=ExitSession(store,"POST")
        status,result,_=await raw_asgi(exit_app(monkeypatch,retry,debug),"POST",data=payload(),order=retry.order)
        assert status==200 and result["data"]["outcome"]=="duplicate" and result["data"]["recordId"]==committed
        assert len(store.samples)==len(store.receipts)==1
        assert retry.order.index("context_exit")<retry.order.index("response_start_200")
    else:
        assert not store.samples and not store.receipts


@pytest.mark.asyncio
@pytest.mark.parametrize("fault,expected",[("business_flush",500),("receipt_flush",500),("service_commit",503)])
async def test_real_get_db_preserves_service_atomic_failures_before_response(monkeypatch,fault,expected):
    store=ExitStore();session=ExitSession(store,"POST",fault)
    status,result,_=await raw_asgi(exit_app(monkeypatch,session,True),"POST",data=payload(),order=session.order)
    assert status==result["code"]==expected and result["data"] is None
    assert not store.samples and not store.receipts
    assert session.rollbacks>=1 and session.closes==1 and "response_start_200" not in session.order
    assert session.order.index("context_exit")<session.order.index("response_start_"+str(expected))


@pytest.mark.asyncio
@pytest.mark.parametrize("debug",[False,True])
@pytest.mark.parametrize("scope",["request","function"])
@pytest.mark.parametrize("failure,expected,key",[("business409",409,"sample_id_conflict"),("business503",503,"unavailable"),
    ("http401",401,"unauthenticated"),("http403",403,"forbidden"),("http422",422,"invalid_sample"),
    ("http500",500,"internal_error"),("http503",503,"unavailable"),("operational",503,"unavailable"),
    ("runtime",500,"internal_error"),("core_business",500,"internal_error")])
async def test_request_and_function_yield_typed_errors_remain_local(monkeypatch,debug,scope,failure,expected,key):
    from fastapi import APIRouter,Depends,HTTPException,Request
    from sqlalchemy.exc import OperationalError
    from app.equipment.api.temperature_http import TemperatureRoute
    from app.equipment.error_codes import TemperatureError
    from common.exceptions import BusinessException
    from common.error_codes import ErrorCode
    from core.registrar import register_exception_handlers
    events=[];local_stacks={}
    async def dependency(request: Request):
        local_stacks.update({key:request.scope[key] for key in ("fastapi_inner_astack","fastapi_function_astack")})
        events.append("enter")
        try:yield
        finally:
            events.append("exit")
            if failure=="business409":raise BusinessException(TemperatureError.SAMPLE_ID_CONFLICT,code=409,message="PRIVATE business")
            if failure=="business503":raise BusinessException(TemperatureError.UNAVAILABLE,code=503,message="PRIVATE business")
            if failure=="core_business":raise BusinessException(ErrorCode.USER_NOT_FOUND,message="PRIVATE core")
            if failure.startswith("http"):raise HTTPException(int(failure[4:]),detail="PRIVATE HTTP")
            if failure=="operational":raise OperationalError("PRIVATE SQL",{},Exception("PRIVATE DSN"))
            raise RuntimeError("PRIVATE runtime")
    app=FastAPI(debug=debug);register_exception_handlers(app)
    local=APIRouter(route_class=TemperatureRoute)
    @local.get("/typed",dependencies=[Depends(dependency,scope=scope)])
    async def typed():return {"code":200,"message":"success","data":None}
    app.include_router(local)
    status,result,returned_scope=await raw_asgi(app,path="/typed",order=events)
    assert status==expected
    assert result==dict(code=expected,message="equipment.temperature_"+key,data=None,errorCode="equipment.temperature_"+key)
    assert events.index("exit")<events.index("response_start_"+str(expected))
    assert "response_start_200" not in events
    assert "PRIVATE" not in json.dumps(result)
    # 外层原stack已还原；本地提前完成的stack不会遗留为全局request状态。
    for key,local_stack in local_stacks.items():
        assert returned_scope[key] is not local_stack
        assert not local_stack._exit_callbacks
        assert not returned_scope[key]._exit_callbacks


@pytest.mark.asyncio
@pytest.mark.parametrize("key",["fastapi_inner_astack","fastapi_function_astack"])
@pytest.mark.parametrize("kind",["missing","invalid"])
async def test_missing_or_invalid_framework_stack_is_safe_internal_failure(key,kind):
    from contextlib import AsyncExitStack
    from fastapi import Request
    from app.equipment.api.temperature_http import TemperatureRoute
    async def endpoint():return {"code":200}
    route=TemperatureRoute("/invalid-stack",endpoint=endpoint,methods=["GET"])
    stacks={"fastapi_inner_astack":AsyncExitStack(),"fastapi_function_astack":AsyncExitStack()}
    if kind=="missing":stacks.pop(key)
    else:stacks[key]=object()
    scope={"type":"http","method":"GET","path":"/invalid-stack","query_string":b"", "headers":[(b"authorization",b"Bearer synthetic-override")],**stacks}
    before=dict(stacks)
    response=await route.get_route_handler()(Request(scope))
    assert response.status_code==500
    assert json.loads(response.body)==dict(code=500,message="equipment.temperature_internal_error",data=None,errorCode="equipment.temperature_internal_error")
    for name,value in before.items():assert scope[name] is value
    if kind=="missing":assert key not in scope
