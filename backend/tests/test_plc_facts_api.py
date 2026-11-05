"""三路ASGI进程内HTTP合同、默认关闭/noDB和依赖退出故障。"""
from contextlib import asynccontextmanager
from types import SimpleNamespace
import pytest
from fastapi import FastAPI,Depends,Request
from httpx import ASGITransport,AsyncClient
from app.plc_facts.api.routes import router
from app.plc_facts.api.http import FactsRoute,success
from app.plc_facts.api import dependencies as deps
from app.plc_facts.config import FactsSettings
from app.plc_facts.source import prepare
from app.plc_facts.services import async_ingest as service
from test_plc_facts_contract import sample
from test_plc_facts_ordering import MemoryDb,install,SETTINGS
pytestmark=pytest.mark.no_db

def app():
    a=FastAPI();a.include_router(router,prefix='/api/v1');return a

def settings(enabled=False,scope='[]',profile='unadopted',key=''):
    return FactsSettings(_env_file=None,PLC_FACTS_ENABLED=enabled,PLC_FACTS_PLC_IDS_JSON=scope,PLC_FACTS_STORAGE_PROFILE=profile,PLC_FACTS_CURSOR_HMAC_KEY=key)

@pytest.mark.asyncio
@pytest.mark.parametrize('method,path,body,expected',[('POST','batches',sample,403),('GET','latest?plcId=plc-demo',None,403),('GET','history?mode=changes&plcId=plc-demo&start=earliest',None,403),('GET','latest?plcId=plc-demo&unknown=x',None,422),('GET','latest?plcId=a&plcId=b',None,422),('GET','history?mode=changes&plcId=plc-demo',None,422)])
async def test_default_or_invalid_never_reaches_database(monkeypatch,method,path,body,expected):
    monkeypatch.setattr(deps,'get_settings',lambda:settings())
    async def denied():raise AssertionError('database dependency must not execute')
    monkeypatch.setattr(deps,'get_db_session',denied)
    async with AsyncClient(transport=ASGITransport(app=app()),base_url='http://fixture') as client:
        kwargs={'json':body()} if body else {}
        r=await client.request(method,'/api/v1/integration/plc-facts/'+path,**kwargs)
    assert r.status_code==expected,r.text
    assert r.headers['content-type']=='application/json'
    assert r.json()['code']==expected and r.json()['data']['persistence']=='none'

@pytest.mark.asyncio
@pytest.mark.parametrize('content_type,encoding,body,status',[('text/plain','identity',b'{}',415),('application/json;charset=ascii','identity',b'{}',415),('application/json','gzip',b'{}',415),('application/json','identity',b'{"x":1,"x":2}',422),('application/json','identity',b'x'*(4*1024*1024+1),413)])
async def test_media_size_and_parser(content_type,encoding,body,status):
    async with AsyncClient(transport=ASGITransport(app=app()),base_url='http://fixture') as client:
        r=await client.post('/api/v1/integration/plc-facts/batches',content=body,headers={'Content-Type':content_type,'Content-Encoding':encoding})
    assert r.status_code==status and r.json()['data']['persistence']=='none'

@pytest.mark.asyncio
async def test_eligible_unadopted_profile_rejects_before_session(monkeypatch):
    monkeypatch.setattr(deps,'get_settings',lambda:settings(True,'["plc-demo"]','arbitrary','ab'*32))
    async def denied():raise AssertionError('must not connect')
    monkeypatch.setattr(deps,'get_db_session',denied)
    async with AsyncClient(transport=ASGITransport(app=app()),base_url='http://fixture') as client:
        r=await client.post('/api/v1/integration/plc-facts/batches',json=sample())
    assert r.status_code==503 and r.json()['errorCode']=='plc_facts.not_ready'

@pytest.mark.asyncio
async def test_real_service_commit_then_complete_dependency_close_before_send(monkeypatch):
    db=install(monkeypatch,MemoryDb(prepare(sample())));events=[]
    async def close():events.append('close')
    db.close=close
    original=db.commit
    async def commit():await original();events.append('commit')
    db.commit=commit
    monkeypatch.setattr(deps,'get_settings',lambda:settings(True,'["plc-demo"]','mysql84_shanghai_v1','ab'*32))
    async def session():return db
    monkeypatch.setattr(deps,'get_db_session',session)
    application=app()
    async def wrapped(scope,receive,send):
        async def observed(message):
            if message['type']=='http.response.start':events.append('send')
            await send(message)
        await application(scope,receive,observed)
    async with AsyncClient(transport=ASGITransport(app=wrapped),base_url='http://fixture') as client:
        r=await client.post('/api/v1/integration/plc-facts/batches',json=sample())
    assert r.status_code==200,r.text
    assert events==['commit','close','send']
    assert r.json()['data']['results'][0]['latestAdvancedPointIds']==['point_x']

@pytest.mark.asyncio
async def test_close_after_commit_is_unknown_and_response_does_not_echo_exception(monkeypatch):
    db=install(monkeypatch,MemoryDb(prepare(sample())))
    async def close():raise RuntimeError('password://secret?token=private')
    db.close=close
    monkeypatch.setattr(deps,'get_settings',lambda:settings(True,'["plc-demo"]','mysql84_shanghai_v1','ab'*32))
    async def session():return db
    monkeypatch.setattr(deps,'get_db_session',session)
    async with AsyncClient(transport=ASGITransport(app=app()),base_url='http://fixture') as client:
        r=await client.post('/api/v1/integration/plc-facts/batches',json=sample())
    assert r.status_code==503 and r.json()['data']['persistence']=='unknown'
    assert 'password' not in r.text and 'private' not in r.text
    assert deps._inflight==0

@pytest.mark.asyncio
async def test_conflict_error_also_closes_session_before_response(monkeypatch):
    db=install(monkeypatch,MemoryDb(prepare(sample())));await service.ingest(db,prepare(sample()),SETTINGS,{})
    events=[]
    async def close():events.append('close')
    db.close=close
    monkeypatch.setattr(deps,'get_settings',lambda:settings(True,'["plc-demo"]','mysql84_shanghai_v1','ab'*32))
    async def session():return db
    monkeypatch.setattr(deps,'get_db_session',session)
    b=sample();b['requestDigest']='sha256:'+'00'*32
    # Trigger a Service-level error through the existing durable original identity.
    from app.plc_facts.api import batches
    from app.plc_facts.error_codes import FactsError
    async def rejected(*args,**kwargs):raise FactsError('batch_content_conflict',409)
    monkeypatch.setattr(batches,'ingest',rejected)
    async with AsyncClient(transport=ASGITransport(app=app()),base_url='http://fixture') as client:
        r=await client.post('/api/v1/integration/plc-facts/batches',json=sample())
    assert r.status_code==409 and events==['close'] and deps._inflight==0
