"""异步事实持久访问；所有写者先锁单例，本层不提交或回滚。"""
from sqlalchemy import select,text,or_
from ..models import StreamState,SourceBinding,BatchReceipt,SampleReceipt,RawSample,Cycle,LatestPoint
from ..canonical import canonical,binary,text_digest,strict_json
from ..retention import db_instant,Instant
from ..error_codes import FactsError


def key(s): return s.encode('utf-8')
def decoded(b): return b.decode('utf-8')
def timestamps(now): return dict(created_at=now.wall,updated_at=now.wall)

async def clock(db,state=None):
    row=(await db.execute(text('SELECT CURRENT_TIMESTAMP(6), TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))'))).one()
    now=db_instant(row[0])
    if row[1]!=28800 or (state is not None and now.wall<state.last_db_time): raise FactsError('clock_invalid',503)
    return now

async def state_row(db,lock=False):
    stmt=select(StreamState).where(StreamState.id==1)
    if lock: stmt=stmt.with_for_update(nowait=True)
    state=(await db.execute(stmt.execution_options(populate_existing=True))).scalar_one_or_none()
    if state is None: raise FactsError('not_ready',503)
    return state

async def adopted(db,state):
    from .sync_maintenance import verify_profile
    profile=await db.run_sync(lambda session:verify_profile(session.connection()))
    if state.storage_profile!='mysql84_shanghai_v1' or (state.schema_profile,state.verified_schema_revision,state.schema_fingerprint)!=(profile['schemaProfile'],profile['revision'],binary(profile['fingerprint'])):
        raise FactsError('not_ready',503)

async def batch(db,instance,batch_id): return await db.get(BatchReceipt,(key(instance),key(batch_id)),populate_existing=True)
async def receipt(db,instance,sample,part):
    return (await db.execute(select(SampleReceipt).where(SampleReceipt.instance_id==key(instance),SampleReceipt.sample_id==key(sample),SampleReceipt.part==part))).scalar_one_or_none()
async def raw(db,instance,sample):
    return (await db.execute(select(RawSample).where(RawSample.instance_id==key(instance),RawSample.sample_id==key(sample)))).scalar_one_or_none()
async def cycle(db,instance,cycle_id): return await db.get(Cycle,(key(instance),key(cycle_id)))
async def cycle_sequence(db,plc,generation,seq):
    return (await db.execute(select(Cycle).where(Cycle.plc_id==key(plc),Cycle.source_generation==key(generation),Cycle.source_seq==seq))).scalar_one_or_none()
async def binding(db,plc): return await db.get(SourceBinding,key(plc),populate_existing=True)
async def latest(db,plc,point): return await db.get(LatestPoint,(key(plc),key(point)),populate_existing=True)

async def sample_receipts(db,instance,sample):
    return list((await db.execute(select(SampleReceipt).where(SampleReceipt.instance_id==key(instance),SampleReceipt.sample_id==key(sample)))).scalars())

def payload_size(row):
    fields={RawSample:('payload_utf8','projections'),Cycle:('manifest_utf8','context_utf8','transport_manifest'),LatestPoint:('point_fact',)}
    return sum(len(getattr(row,c) or b'') for c in fields.get(type(row),()))

def reserve(state,value_delta=0,proof_delta=0):
    values=state.value_bytes+value_delta; proofs=state.proof_rows+proof_delta
    if values<0 or proofs<0: raise FactsError('not_ready',503)
    if values>state.max_value_bytes or proofs>state.max_proof_rows: raise FactsError('capacity_exceeded',503)
    state.value_bytes=values; state.proof_rows=proofs

async def flush(db): await db.flush()
