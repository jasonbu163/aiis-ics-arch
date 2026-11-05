"""真实Service的内存仓储替身：事务边界/回执/逐点顺序；不冒充MySQL证明。"""
import copy,json
from types import SimpleNamespace
import pytest
from app.plc_facts.services import async_ingest as service
from app.plc_facts.crud import async_ingest as crud
from app.plc_facts.models import StreamState,SourceBinding,BatchReceipt,SampleReceipt,RawSample,Cycle,LatestPoint
from app.plc_facts.source import prepare
from app.plc_facts.canonical import canonical,binary,strict_json
from app.plc_facts.retention import instant
from app.plc_facts.schemas.receipt_out import ReceiptOut,FailureOut
from app.plc_facts.error_codes import FactsError
from test_plc_facts_contract import sample,independent_freeze,vectors
pytestmark=pytest.mark.no_db
NOW=instant('2026-11-04T10:00:01+08:00')
SETTINGS=SimpleNamespace(PLC_FACTS_CURSOR_HMAC_KEY='ab'*32)

class MemoryDb:
    def __init__(self,p):
        self.state=StreamState(id=1,storage_epoch='epoch',retention_months=3,high_serial=0,proof_floor_serial=0,proof_floor_ordinal=0,last_db_time=NOW.wall,value_bytes=0,proof_rows=0,max_value_bytes=1073741824,max_proof_rows=1000000)
        self.rows=[];self.commits=0;self.rollbacks=0;self.fail_commit=False;self.fail_rollback=False;self.bindings={}
        for part in p.parts:
            self.bindings[part.payload.plc_id]=SourceBinding(plc_id=crud.key(part.payload.plc_id),instance_id=crud.key(part.payload.instance_id),source_generation=crud.key(part.payload.source_generation),definition_set_digest=binary(part.definition_set_digest),source_epoch=1,binding_revision=1,seq_from=1,seq_through=9223372036854775806,raw_only_windows=b'[]')
    def add(self,row):self.rows.append(row)
    async def flush(self):pass
    async def commit(self):
        self.commits+=1
        if self.fail_commit:raise RuntimeError('secret mysql DSN must not escape')
    async def rollback(self):
        self.rollbacks+=1
        if self.fail_rollback:raise RuntimeError('secret rollback failure')
    def find(self,model,**filters):return next((r for r in self.rows if isinstance(r,model) and all(getattr(r,k)==v for k,v in filters.items())),None)

def install(monkeypatch,db):
    async def state_row(_,lock=False):assert lock;return db.state
    async def adopted(*_):pass
    async def clock(*_):return NOW
    async def batch(_,instance,batch_id):return db.find(BatchReceipt,instance_id=crud.key(instance),batch_id=crud.key(batch_id))
    async def receipt(_,instance,sample,part):return db.find(SampleReceipt,instance_id=crud.key(instance),sample_id=crud.key(sample),part=part)
    async def raw(_,instance,sample):return db.find(RawSample,instance_id=crud.key(instance),sample_id=crud.key(sample))
    async def cycle(_,instance,cycle_id):return db.find(Cycle,instance_id=crud.key(instance),cycle_id=crud.key(cycle_id))
    async def seq(_,plc,generation,number):return db.find(Cycle,plc_id=crud.key(plc),source_generation=crud.key(generation),source_seq=number)
    async def binding(_,plc):return db.bindings.get(plc)
    async def latest(_,plc,point):return db.find(LatestPoint,plc_id=crud.key(plc),point_id=crud.key(point))
    async def receipts(_,instance,sample):return [r for r in db.rows if isinstance(r,SampleReceipt) and r.instance_id==crud.key(instance) and r.sample_id==crud.key(sample)]
    for name,fn in dict(state_row=state_row,adopted=adopted,clock=clock,batch=batch,receipt=receipt,raw=raw,cycle=cycle,cycle_sequence=seq,binding=binding,latest=latest,sample_receipts=receipts).items():monkeypatch.setattr(crud,name,fn)
    return db

@pytest.mark.asyncio
async def test_real_service_create_replay_bad_latest(monkeypatch):
    p=prepare(sample());db=install(monkeypatch,MemoryDb(p));boundary={}
    first=await service.ingest(db,p,SETTINGS,boundary)
    ReceiptOut.model_validate(first)
    assert boundary['committed'] and db.commits==1 and db.state.high_serial==1
    assert first['data']['results'][0]['latestAdvancedPointIds']==['point_x']
    old_rows=len(db.rows);proof_rows=db.state.proof_rows;bytes_before=db.state.value_bytes
    replay=await service.ingest(db,p,SETTINGS,{})
    assert replay['data']['outcome']=='duplicate' and len(db.rows)==old_rows and db.commits==1
    assert db.state.proof_rows==proof_rows and db.state.value_bytes==bytes_before
    b=sample();b['batchId']='batch-2';s=b['samples'][0];s['sampleId']='sample-2';s['cycleId']='cycle-2';payload=json.loads(s['payloadUtf8']);payload.update(sampleId='sample-2',cycleId='cycle-2',sourceSeq='2');payload['points']['point_x'].update(value=None,quality='bad',reason='read_failed');s['payloadUtf8']=json.dumps(payload)
    c=b['cycles'][0];c['cycleId']='cycle-2';m=json.loads(c['manifestUtf8']);m.update(cycleId='cycle-2',sourceSeq='2');m['samples'][0]['sampleId']='sample-2';c['manifestUtf8']=json.dumps(m);c['transportManifest'][0]['sampleId']='sample-2'
    second=await service.ingest(db,prepare(independent_freeze(b)),SETTINGS,{})
    row=db.find(LatestPoint,plc_id=b'plc-demo',point_id=b'point_x')
    assert strict_json(row.point_fact)['value'] is None and row.source_seq==2
    assert second['data']['commitSerial']=='2'

@pytest.mark.asyncio
async def test_partial_sample_cycle_not_false_complete(monkeypatch):
    p=prepare(vectors()['fixtures']['partialFragment']);db=install(monkeypatch,MemoryDb(p))
    r=await service.ingest(db,p,SETTINGS,{})
    assert not r['data']['cycles'][0]['complete'] and not r['data']['results'][0]['sourceSampleComplete']
    assert r['data']['cycles'][0]['expectedParts']>r['data']['cycles'][0]['receivedParts']

@pytest.mark.asyncio
async def test_commit_failure_is_unknown_and_not_raw_exception(monkeypatch):
    p=prepare(sample());db=install(monkeypatch,MemoryDb(p));db.fail_commit=True
    with pytest.raises(FactsError) as exc:await service.ingest(db,p,SETTINGS,{})
    assert exc.value.data['persistence']=='unknown' and exc.value.data['newFactsCommitted'] is None
    assert 'secret' not in str(exc.value)

@pytest.mark.asyncio
async def test_content_conflict_precedes_source_and_records_only_rejection(monkeypatch):
    p=prepare(sample());db=install(monkeypatch,MemoryDb(p));await service.ingest(db,p,SETTINGS,{})
    b=sample();b['batchId']='different-batch';payload=json.loads(b['samples'][0]['payloadUtf8']);payload['points']['point_x']['value']=203;b['samples'][0]['payloadUtf8']=json.dumps(payload)
    candidate=prepare(independent_freeze(b));before=len([r for r in db.rows if isinstance(r,RawSample)])
    with pytest.raises(FactsError) as exc:await service.ingest(db,candidate,SETTINGS,{})
    assert exc.value.code==409 and exc.value.data['persistence']=='rejection_recorded'
    assert len([r for r in db.rows if isinstance(r,RawSample)])==before
    token=exc.value.data['rejectionToken']
    # Replay under a different signing key returns the persisted original token.
    with pytest.raises(FactsError) as replay:await service.ingest(db,candidate,SimpleNamespace(PLC_FACTS_CURSOR_HMAC_KEY='cd'*32),{})
    assert replay.value.data['rejectionToken']==token

@pytest.mark.asyncio
async def test_scope_current_source_epoch_isolation(monkeypatch):
    p=prepare(sample());db=install(monkeypatch,MemoryDb(p));binding=db.bindings['plc-demo'];binding.instance_id=b'another'
    with pytest.raises(FactsError) as exc:await service.ingest(db,p,SETTINGS,{})
    assert exc.value.code==403 and exc.value.data['persistence']=='rejection_recorded'
    assert not any(isinstance(r,RawSample) for r in db.rows)

def test_exact_quota_deltas_reject_negative_and_overflow():
    state=SimpleNamespace(value_bytes=5,proof_rows=2,max_value_bytes=10,max_proof_rows=3)
    crud.reserve(state,5,1);assert (state.value_bytes,state.proof_rows)==(10,3)
    with pytest.raises(FactsError):crud.reserve(state,1)
    with pytest.raises(FactsError):crud.reserve(state,-11)

@pytest.mark.asyncio
async def test_rejection_parent_survives_key_rotation_and_cannot_add_members(monkeypatch):
    p=prepare(sample());db=install(monkeypatch,MemoryDb(p));binding=db.bindings['plc-demo'];binding.instance_id=b'wrong'
    with pytest.raises(FactsError) as exc:await service.ingest(db,p,SETTINGS,{})
    token=exc.value.data['rejectionToken'];binding.instance_id=b'daa-demo'
    child=sample();child['batchId']='child-batch';child['parent']=dict(batchId=p.wire.batch_id,requestDigest=p.wire.request_digest,rejectionToken=token)
    child=prepare(independent_freeze(child))
    r=await service.ingest(db,child,SimpleNamespace(PLC_FACTS_CURSOR_HMAC_KEY='cd'*32),{})
    assert r['code']==200 and db.find(BatchReceipt,batch_id=b'child-batch').parent_depth==1

@pytest.mark.asyncio
async def test_queries_use_safe_positions_expiry_gaps_and_original_view(monkeypatch):
    from app.plc_facts.services import async_query as query_service
    from app.plc_facts.crud import async_query as qcrud
    from app.plc_facts.schemas.query import LatestQuery,HistoryQuery
    p=prepare(sample());db=install(monkeypatch,MemoryDb(p));await service.ingest(db,p,SETTINGS,{})
    async def state(_,lock=False):return db.state
    monkeypatch.setattr(crud,'state_row',state)
    async def feed(_,high,after,maximum=2000):return [r for r in db.rows if isinstance(r,SampleReceipt) and r.commit_serial<=high and (r.commit_serial,r.ordinal)>tuple(after)]
    async def high(_,number):return [number,max((r.ordinal for r in db.rows if isinstance(r,SampleReceipt) and r.commit_serial==number),default=0)]
    async def latest(_,plc,epoch,after,q,maximum=501):return [r for r in db.rows if isinstance(r,LatestPoint) and r.source_epoch==epoch and r.plc_id==crud.key(plc)]
    monkeypatch.setattr(qcrud,'feed',feed);monkeypatch.setattr(qcrud,'high_position',high);monkeypatch.setattr(qcrud,'latest_points',latest)
    latest_result=await query_service.read(db,LatestQuery(plcId='plc-demo'),SETTINGS)
    assert latest_result['data']['items'][0]['points']['point_x']['value']==202
    q=HistoryQuery(mode='changes',plcId='plc-demo',start='earliest')
    r=await query_service.read(db,q,SETTINGS)
    assert r['data']['scannedThrough']==dict(commitSerial='1',ordinal=1) and not r['data']['hasMore']
    assert r['data']['items'][0]['projection']['points']['point_x']['value']==202
    filtered=await query_service.read(db,HistoryQuery(mode='changes',plcId='plc-demo',pointId='missing',start='earliest'),SETTINGS)
    assert filtered['data']['items']==[] and filtered['data']['scannedThrough']==dict(commitSerial='1',ordinal=1)
    original=await query_service.read(db,HistoryQuery.model_validate({'mode':'range','plcId':'plc-demo','from':'2026-11-04T10:00:00+08:00','to':'2026-11-04T10:00:01+08:00','view':'original'}),SETTINGS)
    assert original['data']['items'][0]['payloadUtf8']==sample()['samples'][0]['payloadUtf8']
    async def expired_clock(*_):return instant('2027-02-04T10:00:00.123+08:00')
    monkeypatch.setattr(crud,'clock',expired_clock)
    expired=await query_service.read(db,q,SETTINGS)
    assert expired['data']['items'][0]['kind']=='gap' and 'value' not in canonical(expired['data']['items'][0]).decode()
    no_latest=await query_service.read(db,LatestQuery(plcId='plc-demo'),SETTINGS)
    assert no_latest['data']['items']==[]
