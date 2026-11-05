"""BE009-B专用MySQL矩阵源码；A不执行，缺精确可丢弃目标批准即拒绝收集。"""
import asyncio
import copy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
import pytest
import pytest_asyncio
pytestmark=pytest.mark.mysql

_REQUIRED=('PLC_FACTS_B_OPERATION_APPROVAL','PLC_FACTS_B_TARGET_ALIAS','PLC_FACTS_B_SCHEMA','PLC_FACTS_B_EXPECTED_REVISION','PLC_FACTS_B_STORAGE_EPOCH')
if any(not os.environ.get(k) for k in _REQUIRED):
    pytest.skip('BE009-B requires separate exact disposable MySQL target approval',allow_module_level=True)
if os.environ['PLC_FACTS_B_EXPECTED_REVISION']!='0a2c4e6f8b10':
    raise RuntimeError('BE009 standalone B may only target explicit 0a2; joint 1b3 is a separate BE010 gate')
if os.environ.get('PLC_FACTS_B_CONFIRM')!='RUN:'+os.environ['PLC_FACTS_B_TARGET_ALIAS']+':'+os.environ['PLC_FACTS_B_SCHEMA']+':'+os.environ['PLC_FACTS_B_STORAGE_EPOCH']:
    raise RuntimeError('BE009-B exact target confirmation missing')
if os.environ.get('PROJECTION_RUNNER_ENABLED','False').lower()!='false' or os.environ.get('BACKEND_MOCK_ENABLED','False').lower()!='false':
    raise RuntimeError('B requires real owner Service with Projection runner and business mocks disabled')

from sqlalchemy import select,func,text
from database import get_sync_db_context,get_db_session
from app.plc_facts.models import StreamState,SourceBinding,RawSample,SampleReceipt,BatchReceipt,Cycle,LatestPoint
from app.plc_facts.crud.sync_maintenance import verify_profile,clock,blob_bytes,proof_rows
from app.plc_facts.crud import async_ingest as crud
from app.plc_facts.services.async_ingest import ingest
from app.plc_facts.services.async_query import read
from app.plc_facts.source import prepare
from app.plc_facts.canonical import canonical,sha,digest,binary,strict_json
from app.plc_facts.retention import Instant
from app.plc_facts.schemas.query import LatestQuery,HistoryQuery
from app.plc_facts.error_codes import FactsError

SETTINGS=SimpleNamespace(PLC_FACTS_CURSOR_HMAC_KEY=os.environ.get('PLC_FACTS_CURSOR_HMAC_KEY',''))
if len(SETTINGS.PLC_FACTS_CURSOR_HMAC_KEY)!=64:raise RuntimeError('explicit synthetic cursor key required')
ROOT=Path(__file__).resolve().parents[2]
SPEC_VECTOR=json.loads((ROOT/'contracts/published/http-api/plc-facts-v1/vectors.json').read_text())['request']

@pytest_asyncio.fixture(scope='module',loop_scope='module',autouse=True)
async def dispose_async_pool():
    """同模块用同一loop；真实异步连接池必须在其loop关闭前释放。"""
    yield
    from database import async_engine
    await async_engine.dispose()

@pytest.fixture(scope='module')
def target():
    """外层先显式upgrade 0a2并以批准CLI adopt；本入口不建库/DDL/清库。"""
    with get_sync_db_context() as db:
        assert db.connection().engine.url.database==os.environ['PLC_FACTS_B_SCHEMA']
        assert db.execute(text('SELECT VERSION()')).scalar_one().split('-')[0]=='8.4.6'
        profile=verify_profile(db.connection());assert profile['revision']=='0a2c4e6f8b10' and profile['applicationTables']==71
        state=db.get(StreamState,1);assert state and state.storage_epoch==os.environ['PLC_FACTS_B_STORAGE_EPOCH']
        now=clock(db,state);binding=db.get(SourceBinding,b'plc-demo');assert binding
        assert binding.instance_id==b'daa-demo' and binding.source_generation==b'generation-demo'
        assert (state.value_bytes,state.proof_rows)==(blob_bytes(db),proof_rows(db))
        # 首次默认空夹具；重跑须外层明确固定本次已知水位/证明数及源序号，不暗中清库。
        assert state.high_serial==int(os.environ.get('PLC_FACTS_B_EXPECTED_HIGH_SERIAL','0'))
        assert state.proof_rows==int(os.environ.get('PLC_FACTS_B_EXPECTED_PROOF_ROWS','0'))
        db.rollback()
    return dict(now=now,seq=int(os.environ.get('PLC_FACTS_B_SOURCE_SEQ_START','0')))


def batch(target,*,value=202,observed=None):
    """合成材料只使用公开文档；身份从新UUID冻结一次，时间来自已采用DB。"""
    target['seq']+=1;seq=str(target['seq']);identity=str(uuid4());b=copy.deepcopy(SPEC_VECTOR)
    with get_sync_db_context() as db:now=clock(db,db.get(StreamState,1));db.rollback()
    observed=observed or now.seconds(-2);p=json.loads(b['samples'][0]['payloadUtf8']);m=json.loads(b['cycles'][0]['manifestUtf8'])
    for doc in (p,m):
        doc.update(cycleId='cycle-'+identity,sourceSeq=seq,startedAt=observed.wire(),finishedAt=observed.wire(),savedAt=observed.wire())
    p['sampleId']='sample-'+identity;p['points']['point_x'].update(value=value,observedAt=observed.wire())
    source=canonical(p).decode();source_sha=sha(source.encode());m['samples'][0].update(sampleId=p['sampleId'],sha256=source_sha[7:])
    for r in m['reads']:r.update(startedAt=observed.wire(),finishedAt=observed.wire())
    s=b['samples'][0];s.update(sampleId=p['sampleId'],cycleId=p['cycleId'],payloadUtf8=source,sourceSha256=source_sha)
    projection={k:v for k,v in p.items() if k not in ('schemaVersion','revision')};projection.update(configRevision=p['revision'],sourceSha256=source_sha,part=1,parts=1)
    s['contentDigest']=digest('sample-part',projection)
    c=b['cycles'][0];c.update(cycleId=p['cycleId'],manifestUtf8=canonical(m).decode());c['manifestSha256']=sha(c['manifestUtf8'].encode())
    t=c['transportManifest'][0];t.update(sampleId=p['sampleId'],sourceSha256=source_sha);t['parts'][0]['contentDigest']=s['contentDigest']
    b.update(batchId='batch-'+identity,batchCreatedAt=now.wire());outer={k:v for k,v in b.items() if k!='requestDigest'};b['requestDigest']=digest('batch',outer)
    return prepare(b)

async def submit(p,session=None):
    if session is not None:return await ingest(session,p,SETTINGS,{})
    db=await get_db_session()
    async with db:return await ingest(db,p,SETTINGS,{})
async def query(q):
    db=await get_db_session()
    async with db:return await read(db,q,SETTINGS)

def counts():
    with get_sync_db_context() as db:
        values=tuple(db.execute(select(func.count()).select_from(m)).scalar_one() for m in (RawSample,SampleReceipt,BatchReceipt,Cycle,LatestPoint))
        state=db.get(StreamState,1);assert (state.value_bytes,state.proof_rows)==(blob_bytes(db),proof_rows(db));db.rollback();return values

@pytest.mark.asyncio(loop_scope='module')
async def test_01_ingest_latest_history_replay_and_exact_side_effects(target):
    p=batch(target);before=counts();first=await submit(p)
    assert first['code']==200 and first['data']['newFactsCommitted'];after=counts();assert after[:4]==tuple(n+1 for n in before[:4])
    latest=await query(LatestQuery(plcId='plc-demo'));assert latest['data']['items'][0]['points']['point_x']['value']==202
    history=await query(HistoryQuery(mode='changes',plcId='plc-demo',start='earliest'))
    assert any(i['contentDigest']==p.parts[0].wire.content_digest for i in history['data']['items'] if i['kind']=='fact')
    replay=await submit(p);assert replay['data']['receiptId']==first['data']['receiptId'] and replay['data']['outcome']=='duplicate';assert counts()==after

@pytest.mark.asyncio(loop_scope='module')
async def test_02_concurrent_same_batch_and_identity_conflict(target):
    p=batch(target,value=203);responses=await asyncio.gather(submit(p),submit(p),return_exceptions=True)
    # NOWAIT contention may return busy; retry the identical original after the first releases.
    if any(isinstance(x,FactsError) for x in responses):responses=[await submit(p),await submit(p)]
    assert responses[0]['data']['receiptId']==responses[1]['data']['receiptId']
    changed=copy.deepcopy(p);changed.wire.request_digest='sha256:'+'00'*32
    before=counts()
    with pytest.raises(FactsError) as exc:await submit(changed)
    assert exc.value.code==409 and counts()==before

@pytest.mark.asyncio(loop_scope='module')
async def test_03_real_commit_then_lost_ack_recovers_original_receipt(target):
    p=batch(target,value=204);db=await get_db_session();original=db.commit
    async def lost_ack():await original();raise ConnectionError('controlled loss after real commit')
    db.commit=lost_ack
    async with db:
        with pytest.raises(FactsError) as exc:await submit(p,db)
    assert exc.value.data['persistence']=='unknown'
    before=counts();recovered=await submit(p)
    assert recovered['data']['outcome']=='duplicate' and recovered['data']['persistence']=='committed' and counts()==before

@pytest.mark.asyncio(loop_scope='module')
async def test_04_gate_blocks_later_publication_and_late_observation_has_new_position(target):
    p1=batch(target,value=205);p2=batch(target,value=206,observed=target['now'].seconds(-60))
    db=await get_db_session();original=db.commit;ready=asyncio.Event();release=asyncio.Event()
    async def delayed():ready.set();await release.wait();await original()
    db.commit=delayed
    async with db:
        task=asyncio.create_task(submit(p1,db));await asyncio.wait_for(ready.wait(),5)
        baseline=await query(HistoryQuery(mode='changes',plcId='plc-demo',start='tail'))
        with pytest.raises(FactsError) as blocked:await submit(p2)
        assert blocked.value.code==429
        release.set();one=await asyncio.wait_for(task,5)
    two=await submit(p2);assert int(two['data']['commitSerial'])==int(one['data']['commitSerial'])+1
    resumed=await query(HistoryQuery(mode='changes',plcId='plc-demo',cursor=baseline['data']['nextCursor']))
    identities={i['projection']['sampleId'] for i in resumed['data']['items'] if i['kind']=='fact'}
    assert {p1.parts[0].wire.sample_id,p2.parts[0].wire.sample_id}<=identities

@pytest.mark.asyncio(loop_scope='module')
async def test_05_expired_input_is_reliably_rejected_without_partial_values(target):
    p=batch(target,observed=target['now'].months(-4));before=counts()
    with pytest.raises(FactsError) as exc:await submit(p)
    assert exc.value.code==410 and exc.value.data['persistence']=='rejection_recorded'
    after=counts();assert after[0:2]==before[0:2] and after[2]==before[2]+1
    with pytest.raises(FactsError) as replay:await submit(p)
    assert replay.value.data['rejectionToken']==exc.value.data['rejectionToken'] and counts()==after


def test_06_cleanup_and_proof_boundaries_require_outer_approved_time_fixture(target):
    """外层approved合成积压/time fixture准备后，显式tick并核精确配额/非owner指纹。"""
    if os.environ.get('PLC_FACTS_B_CLEANUP_FIXTURE_READY')!='True':pytest.skip('outer approved expiry/proof/cleanup fixture not yet prepared')
    from app.plc_facts.services.sync_maintenance import MaintenanceOptions,execute
    options=MaintenanceOptions(action='cleanup',apply=True,target_alias=os.environ['PLC_FACTS_B_TARGET_ALIAS'],schema=os.environ['PLC_FACTS_B_SCHEMA'],expected_schema_revision='0a2c4e6f8b10',expected_storage_epoch=os.environ['PLC_FACTS_B_STORAGE_EPOCH'],operation_approval=os.environ['PLC_FACTS_B_OPERATION_APPROVAL'],confirmed_by='approved-b-fixture')
    before=counts();r=execute(options);after=counts()
    assert r['totals']['rows']<=2000 and r['totals']['valueBytes']<=20*1024*1024 and r['totals']['transactions']<=10
    assert all(a<=b for a,b in zip(after,before))
    with get_sync_db_context() as db:
        state=db.get(StreamState,1);assert state.cleanup_last_success is not None;assert (state.value_bytes,state.proof_rows)==(blob_bytes(db),proof_rows(db));db.rollback()

# Outer operation plan (must be approved separately, never executed by this source file):
# 1. Provision two isolated MySQL 8.4.6 schema/volume rounds with synthetic credentials,
#    +08:00 session time, REPEATABLE-READ, no backend listener, no production network.
# 2. Explicitly apply legacy f6 then 0a2; preserve synthetic old-64 table ID/value/precision hashes.
#    Empty/unadopted downgrade is exercised before adoption; nonempty downgrade must refuse.
# 3. Explicit CLI adopt synthetic context/plc-demo, expectedBindingRevision=0,
#    provided storageEpoch and operation approval. First suite asserts state highSerial/proofs zero.
# 4. Run this matrix with --confcutdir pointing to this directory (no shared destructive conftest).
# 5. Separately prepared approved DB-time/expiry/proof fixtures cover exact nanosecond cutoff,
#    original earliest-member expiry, >=120-day serial-prefix cleanup and cursor_gap, failed tick
#    rollback/three failures, 24h backlog status, budgets, counters and non-owner source hashes.
#    Set CLEANUP_FIXTURE_READY only after that fixture evidence is fixed; skipped rows are not B pass.
# 6. Drive additional T1 rollback/disconnect, source/definition CAS, partial-fragment and saturation
#    scenarios using the same typed Service/session helpers; freeze their evidence before B verdict.
# 7. Stop/drop only the explicitly approved owned test resources after independent evidence capture.
# BE009 standalone stays at 0a2/71. Applying 1b3 and schema-only F7 revalidation belongs to BE010-B.

@pytest.mark.asyncio(loop_scope='module')
async def test_07_actual_asgi_api_status_content_type_and_json_roundtrip(target):
    from httpx import AsyncClient,ASGITransport
    from core.registrar import create_app
    from app.plc_facts.config import get_settings
    get_settings.cache_clear();p=batch(target,value=207)
    async with AsyncClient(transport=ASGITransport(app=create_app(testing=True)),base_url='http://synthetic-asgi') as client:
        r=await client.post('/api/v1/integration/plc-facts/batches',json=p.wire.model_dump(by_alias=True))
        assert r.status_code==200 and r.headers['content-type']=='application/json'
        body=r.json();assert body['code']==200 and body['data']['requestDigest']==p.wire.request_digest and body['data']['committedAt'].endswith('+08:00')
        latest=await client.get('/api/v1/integration/plc-facts/latest',params={'plcId':'plc-demo'})
        assert latest.status_code==200 and latest.headers['content-type']=='application/json'
        assert latest.json()['data']['items'][0]['points']['point_x']['value']==207
        history=await client.get('/api/v1/integration/plc-facts/history',params={'mode':'changes','plcId':'plc-demo','start':'earliest'})
        assert history.status_code==200 and any(i.get('contentDigest')==p.parts[0].wire.content_digest for i in history.json()['data']['items'])

@pytest.mark.asyncio(loop_scope='module')
async def test_08_expired_cursor_is_410_with_explicit_resync(target):
    from app.plc_facts.cursors import issue,filter_hash
    q=HistoryQuery(mode='changes',plcId='plc-demo',start='earliest')
    with get_sync_db_context() as db:state=db.get(StreamState,1);now=clock(db,state);epoch=state.storage_epoch;db.rollback()
    token=issue(SETTINGS.PLC_FACTS_CURSOR_HMAC_KEY,'changes',epoch,filter_hash(q),[0,0],now.seconds(-86400))
    with pytest.raises(FactsError) as exc:await query(HistoryQuery(mode='changes',plcId='plc-demo',cursor=token))
    assert exc.value.code==410 and exc.value.data['requiresResync']

@pytest.mark.asyncio(loop_scope='module')
async def test_09_outer_proof_prefix_fixture_has_gap_and_never_revives_values(target):
    file=os.environ.get('PLC_FACTS_B_HISTORICAL_BATCH_FILE')
    token=os.environ.get('PLC_FACTS_B_REMOVED_PREFIX_CURSOR')
    if not file or not token:pytest.skip('requires independently approved original batch/proof-prefix fixture')
    original=prepare(json.loads(Path(file).read_text()));before=counts()
    try:
        replay=await submit(original)
        assert all(not r['valueReadable'] and r['confirmation']=='historical_committed' for r in replay['data']['results'])
    except FactsError as exc:assert exc.code==410
    assert counts()[0]==before[0]
    with pytest.raises(FactsError) as gap:await query(HistoryQuery(mode='changes',plcId='plc-demo',cursor=token))
    assert gap.value.code==410 and gap.value.data['requiresResync']
