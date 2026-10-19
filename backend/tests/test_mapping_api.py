"""真实ASGI局部HTTP、路由次序、权限/scope与依赖退出；不打开listener。"""
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from fastapi import FastAPI
from httpx import ASGITransport,AsyncClient
from sqlalchemy.exc import DBAPIError
from core.deps import get_current_user
from database import get_db
from tests.test_mapping_service import MemoryTransactions,identity
from app.equipment.api.mapping_samples import router as equipment_router
from app.performance.api.mapping_observations import router as production_router
from app.performance.api.process_samples import router as process_router
from app.performance.api.routes import router as legacy_router
from app.monitor.api.process_curve_samples import router as monitor_router
from app.equipment.mapping_config import MappingConfig as EquipmentConfig,get_mapping_config as equipment_config
from app.performance.mapping_config import MappingConfig as PerformanceConfig,get_mapping_config as performance_config
from app.monitor.mapping_config import MappingConfig as MonitorConfig,get_mapping_config as monitor_config
from app.performance.services import async_mapping_query
pytestmark=pytest.mark.no_db

@pytest.fixture
def harness(monkeypatch):
    db=MemoryTransactions();db.install(monkeypatch)
    app=FastAPI(debug=True)
    for router in (equipment_router,production_router,process_router,legacy_router,monitor_router):app.include_router(router,prefix='/api/v1')
    actor=SimpleNamespace(id=1,role='admin',is_active=True)
    app.state.role_api_permissions={'supervisor':(),'operator':()}
    app.state.performance_mapping_config=PerformanceConfig(PERFORMANCE_MAPPING_INGEST_ID='line-A',_env_file=None)
    app.dependency_overrides[get_current_user]=lambda:actor
    app.dependency_overrides[get_db]=lambda:db
    app.dependency_overrides[equipment_config]=lambda:EquipmentConfig(EQUIPMENT_MAPPING_INGEST_ID='line-A',_env_file=None)
    app.dependency_overrides[performance_config]=lambda:PerformanceConfig(PERFORMANCE_MAPPING_INGEST_ID='line-A',_env_file=None)
    app.dependency_overrides[monitor_config]=lambda:MonitorConfig(MONITOR_MAPPING_INGEST_ID='line-A',_env_file=None)
    monkeypatch.setattr(async_mapping_query,'read_records',AsyncMock(return_value=dict(items=[],total=0,page=1,page_size=20)))
    return app,db,actor

async def request(app,path,method='POST',payload=None,raw=None,headers=None):
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://fixture') as client:
        return await client.request(method,'/api/v1'+path,content=raw if raw is not None else json.dumps(payload) if payload is not None else None,
            headers=headers if headers is not None else {'Authorization':'Bearer synthetic-override','Content-Type':'application/json'})

@pytest.mark.asyncio
async def test_real_route_dispatch_static_before_dynamic(harness):
    response=await request(harness[0],'/performances/mapping-records?equipmentId=line-A','GET')
    assert response.status_code==200 and response.json()['data']['items']==[]

@pytest.mark.asyncio
@pytest.mark.parametrize('path,payload',[
 ('/equipment/drive-samples',identity(tv=0)),('/equipment/production-parameter-samples',identity(coilNo='A',width=0)),
 ('/performances/production-observations',identity(coilNo='A',observationStatus='in_production',weight=0)),
 ('/monitor/process-curve-samples',identity(z1TempAct=0))])
async def test_write_camelcase_and_identity(harness,path,payload):
    response=await request(harness[0],path,payload=payload)
    assert response.status_code==200,response.text
    first=response.json()['data'];assert first['recordId'] and first['equipmentId']=='line-A' and first['sampledAt'].endswith('.123Z')
    response=await request(harness[0],path,payload=payload)
    assert response.json()['data']['outcome']=='duplicate'

@pytest.mark.asyncio
@pytest.mark.parametrize('path,raw',[
 ('/equipment/drive-samples',json.dumps(identity(tv=0)).replace('"tv": 0','"tv": 0, "tv": 1')),
 ('/equipment/drive-samples',json.dumps(identity(tv=True))),
 ('/equipment/drive-samples',json.dumps(identity(tv=None))),
 ('/equipment/drive-samples',json.dumps(identity(tv=0,tv_set=1))),
 ('/monitor/process-curve-samples',json.dumps(identity(z1TempSet=1.1))),
 ('/performances/production-observations',json.dumps(identity(observationStatus='unknown',weight=0)))])
async def test_raw_strict_rejection(harness,path,raw):
    response=await request(harness[0],path,raw=raw)
    assert response.status_code==422 and response.json()['code']==422 and response.json()['data'] is None
    assert not harness[1].receipts

@pytest.mark.asyncio
@pytest.mark.parametrize('path,payload',[
 ('/equipment/drive-samples',identity(tv=0)),('/performances/production-observations',identity(observationStatus='unknown')),
 ('/monitor/process-curve-samples',identity(z1TempAct=0))])
async def test_missing_auth_cross_scope_and_nonadmin(harness,path,payload):
    app,db,actor=harness
    response=await request(app,path,payload=payload,headers={});assert response.status_code==401
    wrong=dict(payload,equipmentId='other');response=await request(app,path,payload=wrong);assert response.status_code==403
    actor.role='supervisor';app.state.role_api_permissions['supervisor']=('equipment-mapping-ingest','performance-mapping-ingest','monitor-curve-ingest')
    response=await request(app,path,payload=payload);assert response.status_code==403 and not db.rows

@pytest.mark.asyncio
@pytest.mark.parametrize('path,payload',[
 ('/equipment/drive-samples',identity(tv=0)),('/performances/production-observations',identity(observationStatus='unknown')),
 ('/monitor/process-curve-samples',identity(z1TempAct=0))])
@pytest.mark.parametrize('failure',['system','dbapi'])
async def test_dependency_exit_before_success_and_debug_redaction(harness,path,payload,failure):
    app,db,_=harness
    async def exiting():
        yield db
        if failure=='dbapi':raise DBAPIError('private SQL',{},RuntimeError('private DSN'))
        raise RuntimeError('private secret')
    app.dependency_overrides[get_db]=exiting
    response=await request(app,path,payload=payload)
    assert response.status_code==(503 if failure=='dbapi' else 500)
    assert response.json()['code']==response.status_code and response.json()['data'] is None
    assert 'private' not in response.text
    # Business already committed: same sample retry recovers, never adds another record.
    app.dependency_overrides[get_db]=lambda:db
    retry=await request(app,path,payload=payload)
    assert retry.status_code==200 and retry.json()['data']['outcome']=='duplicate'

@pytest.mark.asyncio
async def test_http_manual_branch_is_strict_scoped_and_delete_protected(harness,monkeypatch):
    from app.performance.services.async_performance import async_performance_service
    app,db,actor=harness
    manual=AsyncMock(return_value={'record_id':7,'weight':0})
    monkeypatch.setattr(async_performance_service,'update_mapping_weight',manual)
    response=await request(app,'/performances/7?dataSource=http&equipmentId=line-A','PUT',payload={'weight':0})
    assert response.status_code==200,response.text
    assert manual.await_args.args[3]=={'weight':0}
    response=await request(app,'/performances/7?dataSource=http&equipmentId=other','PUT',payload={'weight':0})
    assert response.status_code==403 and manual.await_count==1
    monkeypatch.setattr(async_mapping_query,'read_record',AsyncMock(return_value={'record_id':7}))
    response=await request(app,'/performances/7?dataSource=http&equipmentId=line-A','DELETE')
    assert response.status_code==409 and response.json()['errorCode']=='performance.mapping_delete_forbidden'

@pytest.mark.asyncio
@pytest.mark.parametrize('path,payload',[
 ('/equipment/drive-samples',identity(tv=0)),('/performances/production-observations',identity(observationStatus='unknown')),
 ('/monitor/process-curve-samples',identity(z1TempAct=0))])
@pytest.mark.parametrize('kind',['missing','basic','bad','expired','refresh','revoked','inactive'])
async def test_real_jwt_dependency_401_for_all_new_owners(harness,monkeypatch,path,payload,kind):
    from datetime import timedelta
    from core.jwt import create_access_token,create_refresh_token
    from app.user.services.async_token_blacklist import TokenBlacklistService
    app,db,actor=harness;app.dependency_overrides.pop(get_current_user)
    monkeypatch.setattr(TokenBlacklistService,'is_blacklisted',AsyncMock(return_value=kind=='revoked'))
    class Result:
        def scalar_one_or_none(self):return actor
    db.execute=AsyncMock(return_value=Result())
    actor.is_active=kind!='inactive'
    token=create_access_token({'sub':'fixture'})
    if kind=='bad':token='invalid'
    if kind=='expired':token=create_access_token({'sub':'fixture'},timedelta(seconds=-1))
    if kind=='refresh':token=create_refresh_token({'sub':'fixture'})
    headers={'Content-Type':'application/json'}
    if kind!='missing':headers['Authorization']=('Basic ' if kind=='basic' else 'Bearer ')+token
    response=await request(app,path,payload=payload,headers=headers)
    assert response.status_code==401 and response.json()['code']==401
    assert response.headers['www-authenticate']=='Bearer' and not db.rows


@pytest.mark.asyncio
async def test_production_read_view_reset_does_not_access_expired_authenticated_user(harness,monkeypatch):
    """Unbound ORM Session expires a loaded User on rollback; no connection/DB is created."""
    from sqlalchemy import inspect
    from sqlalchemy.orm import Session,make_transient_to_detached
    from app.user.models.user import User
    app,db,_=harness
    actor=User(id=1,username='public-fixture',role='admin',is_active=True)
    make_transient_to_detached(actor)
    identity_session=Session() # Unbound identity-map behavior only, never executes SQL.
    identity_session.add(actor)
    original=db.rollback
    async def rollback():
        await original()
        identity_session.rollback()
    monkeypatch.setattr(db,'rollback',rollback)
    app.dependency_overrides[get_current_user]=lambda:actor
    try:
        response=await request(app,'/performances/production-observations',payload=identity(observationStatus='unknown'))
        assert response.status_code==200,response.text
        assert inspect(actor).expired
        assert response.json()['data']['outcome']=='updated' and db.commits==1
    finally:
        identity_session.close()
