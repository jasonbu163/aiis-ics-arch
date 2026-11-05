"""原子接收事务owner：可靠回执、有限证明、逐点顺序与全局发布序。"""
import json
import copy
import hashlib
import hmac
from uuid import uuid4
from sqlalchemy.exc import DBAPIError
from common.log import log_event
from ..crud import async_ingest as crud
from ..models import BatchReceipt,SampleReceipt,RawSample,Cycle,LatestPoint
from ..canonical import canonical,binary,text_digest,strict_json,digest
from ..retention import instant,Instant,expiry,proof_expiry
from ..source import definition_digest
from ..error_codes import FactsError


def emit(event,**fields):
    try: log_event('INFO',event,**fields)
    except Exception: pass

def member_set(prepared):
    return sorted([dict(sampleId=p.wire.sample_id,part=p.wire.part,contentDigest=p.wire.content_digest,
        sourceSha256=p.wire.source_sha256,cycleId=p.wire.cycle_id,cycleDigest=prepared.cycles[p.wire.cycle_id].digest) for p in prepared.parts],key=lambda p:(p['sampleId'].encode(),p['part']))

def position(row): return dict(commitSerial=str(row.commit_serial),ordinal=row.ordinal)
def bounds(p,months):
    times=[instant(x.observed_at) for x in p.payload.points.values()]
    return min(times),max(times),min(t.months(months) for t in times)

def source_eligible(binding,p):
    payload=p.payload
    if (binding.instance_id,binding.source_generation,binding.definition_set_digest)==(crud.key(payload.instance_id),crud.key(payload.source_generation),binary(p.definition_set_digest)) and binding.seq_from<=int(payload.source_seq)<=binding.seq_through:
        return True
    windows=json.loads(binding.raw_only_windows)
    for w in windows:
        if (w['instanceId'],w['sourceGeneration'],w['definitionSetDigest'])==(payload.instance_id,payload.source_generation,p.definition_set_digest) and w['seqFrom']<=int(payload.source_seq)<=w['seqThrough']:
            return False
    raise FactsError('source_rejected',403)

def restore(row,now):
    if now.wall>=row.proof_expires_at: raise FactsError('proof_expired',410)
    result=strict_json(row.result)
    if row.terminal=='rejected': raise FactsError(result['errorCode'].split('.')[-1],row.http_status,result['data'])
    data=result['data']; data.update(outcome='duplicate',newFactsCommitted=False)
    for item in data['results']:
        readable=instant(item['expiresAt'])>now
        item.update(outcome='duplicate',confirmation='duplicate' if readable else 'historical_committed',valueReadable=readable)
    return result

async def parent_depth(db,prepared,now):
    b=prepared.wire
    if b.parent is None: return 0
    p=await crud.batch(db,b.instance_id,b.parent.batch_id)
    if p is None or p.terminal!='rejected' or now.wall>=p.proof_expires_at: raise FactsError('parent_proof_expired',410)
    if p.request_digest!=binary(b.parent.request_digest) or p.rejection_token_sha is None or not hmac.compare_digest(hashlib.sha256(b.parent.rejection_token.encode()).digest(),p.rejection_token_sha): raise FactsError('invalid_request')
    if b.parent.batch_id==b.batch_id or p.parent_depth>=8: raise FactsError('invalid_request')
    previous=json.loads(p.members)
    if not all(m in previous for m in member_set(prepared)): raise FactsError('invalid_request')
    return p.parent_depth+1

async def record_rejection(db,state,prepared,now,key,status,suffix,diagnostics,depth):
    """门闩内只记录无值终结证明；容量耗尽不伪造可靠拒绝。"""
    b=prepared.wire; expires=proof_expiry(now); members=member_set(prepared); receipt=str(uuid4())
    token_body=canonical(dict(instanceId=b.instance_id,batchId=b.batch_id,requestDigest=b.request_digest,
        members=members,reason=suffix,proofExpiresAt=expires.wire()))
    from ..cursors import b64
    token=b64(token_body)+'.'+b64(hmac.new(bytes.fromhex(key),token_body,hashlib.sha256).digest())
    data=dict(contractVersion='plc-facts/v1',instanceId=b.instance_id,batchId=b.batch_id,requestDigest=b.request_digest,
        receiptId=receipt,recordedAt=now.wire(),persistence='rejection_recorded',newFactsCommitted=False,retryable=False,
        retirementAllowed=True,rejectionToken=token,rejectionExpiresAt=expires.wire(),diagnostics=diagnostics)
    result=dict(code=status,message='plc_facts.'+suffix,errorCode='plc_facts.'+suffix,data=data)
    crud.reserve(state,proof_delta=1)
    db.add(BatchReceipt(instance_id=crud.key(b.instance_id),batch_id=crud.key(b.batch_id),request_digest=binary(b.request_digest),
        receipt_id=receipt,terminal='rejected',http_status=status,result=canonical(result),members=canonical(members),
        parent_batch_id=crud.key(b.parent.batch_id) if b.parent else None,parent_depth=depth,rejection_token=token.encode(),
        rejection_token_sha=hashlib.sha256(token.encode()).digest(),recorded_at=now.wall,proof_expires_at=expires.wall,**crud.timestamps(now)))
    state.last_db_time=now.wall; state.updated_at=now.wall
    return result

async def ingest(db,prepared,settings,boundary=None):
    """仅此Service commit；发送前依赖退出失败由API标unknown。"""
    boundary=boundary if boundary is not None else {}
    boundary['transactionStarted']=True
    try:
        state=await crud.state_row(db,lock=True)
        await crud.adopted(db,state)
        now=await crud.clock(db,state)
        old=await crud.batch(db,prepared.wire.instance_id,prepared.wire.batch_id)
        if old:
            if old.request_digest!=binary(prepared.wire.request_digest): raise FactsError('batch_content_conflict',409)
            result=restore(old,now)
            await db.rollback() # read-only original outcome; release gate before response
            boundary['known']=True
            emit('plc_facts_batch_replayed',instance_id=prepared.wire.instance_id,batch_id=prepared.wire.batch_id,digest=prepared.wire.request_digest)
            return result
        depth=await parent_depth(db,prepared,now)
        diagnostics=[]; errors=[]; existing={}; bindings={}; eligible={}; cycle_rows={}
        for cid,c in prepared.cycles.items():
            row=await crud.cycle(db,prepared.wire.instance_id,cid)
            seq=await crud.cycle_sequence(db,c.manifest.plc_id,c.manifest.source_generation,int(c.manifest.source_seq))
            if row and row.cycle_digest!=binary(c.digest) or seq and (seq.instance_id,seq.cycle_id)!=(crud.key(prepared.wire.instance_id),crud.key(cid)):
                errors.append((409,'cycle_content_conflict'))
            cycle_rows[cid]=row
        for p in prepared.parts:
            w=p.wire; payload=p.payload
            old=await crud.receipt(db,payload.instance_id,w.sample_id,w.part); existing[(w.sample_id,w.part)]=old
            raw=await crud.raw(db,payload.instance_id,w.sample_id)
            diagnosis='eligible'; proof=None
            if old and (old.content_digest!=binary(w.content_digest) or old.source_sha!=binary(w.source_sha256)) or raw and (raw.source_sha!=binary(w.source_sha256) or raw.cycle_id!=crud.key(w.cycle_id)):
                errors.append((409,'sample_content_conflict')); diagnosis='conflict'
            elif old and old.proof_expires_at>now.wall:
                diagnosis='duplicate_proven'; proof=dict(sampleId=w.sample_id,part=w.part,contentDigest=w.content_digest,sourceSha256=w.source_sha256,position=position(old),proofExpiresAt=Instant(old.proof_expires_at).wire())
            else:
                if old is not None:
                    errors.append((410,'proof_expired')); diagnosis='expired_unproven'
                if payload.plc_id not in bindings: bindings[payload.plc_id]=await crud.binding(db,payload.plc_id)
                binding=bindings[payload.plc_id]
                if binding is None: raise FactsError('not_ready',503)
                try: eligible[(w.sample_id,w.part)]=source_eligible(binding,p)
                except FactsError:
                    errors.append((403,'source_rejected')); diagnosis='source_rejected'
                low,high,expires=bounds(p,state.retention_months)
                if expires<=now:
                    errors.append((410,'sample_expired'))
                    if diagnosis=='eligible': diagnosis='expired_unproven'
                if any(instant(t)>now.seconds(300) for t in (payload.started_at,payload.finished_at,payload.saved_at,*[v.observed_at for v in payload.points.values()])):
                    errors.append((422,'invalid_request'))
                # Equal sequence of the same point cannot change any fact.
                if eligible.get((w.sample_id,w.part)):
                    for pid,fact in p.projection['points'].items():
                        current=await crud.latest(db,payload.plc_id,pid)
                        if current and current.source_epoch==binding.source_epoch and current.source_seq==int(payload.source_seq) and current.point_fact!=canonical(fact):
                            errors.append((409,'sample_content_conflict')); diagnosis='conflict'
            diagnostics.append(dict(sampleId=w.sample_id,part=w.part,diagnosis=diagnosis,historicalProof=proof))
        created=instant(prepared.wire.batch_created_at)
        if created>now.seconds(300): errors.append((422,'invalid_request'))
        if created<now.seconds(-86400): errors.append((410,'batch_admission_expired'))
        if errors:
            # Stable priority: identity > source > expiry > remaining input errors.
            priority={409:0,403:1,410:2,422:3}
            status,suffix=min(errors,key=lambda e:priority[e[0]])
            result=await record_rejection(db,state,prepared,now,settings.PLC_FACTS_CURSOR_HMAC_KEY,status,suffix,diagnostics,depth)
        else:
            result=await persist(db,state,prepared,now,existing,bindings,eligible,cycle_rows,depth)
        await db.flush()
        boundary['commitAttempted']=True
        await db.commit()
        boundary['committed']=True; boundary['known']=True
        emit('plc_facts_batch_committed' if result['code']==200 else 'plc_facts_batch_rejected',instance_id=prepared.wire.instance_id,batch_id=prepared.wire.batch_id,digest=prepared.wire.request_digest,status=result['code'],parts=len(prepared.parts))
        if result['code']!=200: raise FactsError(result['errorCode'].split('.')[-1],result['code'],result['data'])
        return result
    except FactsError:
        if not boundary.get('commitAttempted'):
            try: await db.rollback(); boundary['known']=True
            except Exception: raise unknown(prepared) from None
        raise
    except Exception as exc:
        unknown_commit=boundary.get('commitAttempted',False)
        try: await db.rollback(); boundary['known']=not unknown_commit
        except Exception: unknown_commit=True
        if unknown_commit: raise unknown(prepared) from None
        if isinstance(exc,DBAPIError) and getattr(exc.orig,'args',(None,))[0] in (1205,1213,3572): raise FactsError('busy',429) from None
        raise FactsError('unavailable',503) from None


def unknown(prepared):
    b=prepared.wire
    emit('plc_facts_batch_commit_unknown',instance_id=b.instance_id,batch_id=b.batch_id,digest=b.request_digest)
    return FactsError('commit_outcome_unknown',503,dict(contractVersion='plc-facts/v1',instanceId=b.instance_id,batchId=b.batch_id,requestDigest=b.request_digest,
        persistence='unknown',newFactsCommitted=None,retryable=True,retirementAllowed=False,diagnostics=[],rejectionToken=None))

async def persist(db,state,prepared,now,existing,bindings,eligible,cycle_rows,depth):
    b=prepared.wire; expires_proof=proof_expiry(now)
    new=[p for p in prepared.parts if existing[(p.wire.sample_id,p.wire.part)] is None]
    serial=state.high_serial+1 if new else None
    new.sort(key=lambda p:(p.payload.instance_id.encode(),p.wire.sample_id.encode(),p.wire.part))
    # Cycle proof and complete expected set are durable before any ACK is built.
    for cid,c in prepared.cycles.items():
        row=cycle_rows[cid]
        if row is None:
            expiry_cycle=expiry(c.manifest.started_at,state.retention_months)
            expected=[dict(sampleId=sid,part=part,contentDigest=content) for (sid,part),content in sorted(c.expected.items())]
            row=Cycle(instance_id=crud.key(b.instance_id),cycle_id=crud.key(cid),plc_id=crud.key(c.manifest.plc_id),source_generation=crud.key(c.manifest.source_generation),source_seq=int(c.manifest.source_seq),cycle_digest=binary(c.digest),manifest_sha=binary(c.wire.manifest_sha256),context_sha=binary(c.wire.context_sha256),
                manifest_utf8=c.wire.manifest_utf8.encode() if expiry_cycle>now else None,context_utf8=c.wire.context_utf8.encode() if expiry_cycle>now else None,
                transport_manifest=canonical([t.model_dump(by_alias=True) for t in c.wire.transport_manifest]) if expiry_cycle>now else None,
                expected_parts=canonical({'items':expected}),received_parts=canonical({'items':[]}),complete=False,quality_good=True,
                expires_at=expiry_cycle.wall,expires_ns=expiry_cycle.ns,proof_expires_at=expires_proof.wall,**crud.timestamps(now))
            crud.reserve(state,crud.payload_size(row),1); db.add(row); cycle_rows[cid]=row
    results=[]
    for ordinal,p in enumerate(new,1):
        w=p.wire; payload=p.payload; low,high,raw_expiry=bounds(p,state.retention_months)
        raw=await crud.raw(db,b.instance_id,w.sample_id)
        if raw is None:
            raw=RawSample(instance_id=crud.key(b.instance_id),sample_id=crud.key(w.sample_id),cycle_id=crud.key(w.cycle_id),plc_id=crud.key(payload.plc_id),source_generation=crud.key(payload.source_generation),source_seq=int(payload.source_seq),db_number=payload.db_number,source_sha=binary(w.source_sha256),payload_utf8=w.payload_utf8.encode(),projections=canonical({'parts':{}}),observed_from=low.wall,observed_from_ns=low.ns,observed_to=high.wall,observed_to_ns=high.ns,expires_at=raw_expiry.wall,expires_ns=raw_expiry.ns,**crud.timestamps(now))
            crud.reserve(state,crud.payload_size(raw)); db.add(raw)
        original_size=crud.payload_size(raw); projections=strict_json(raw.projections); projections['parts'][str(w.part)]=p.projection
        raw.projections=canonical(projections); raw.updated_at=now.wall; crud.reserve(state,crud.payload_size(raw)-original_size)
        advanced=[]; binding=bindings[payload.plc_id]
        if eligible[(w.sample_id,w.part)] and p.current_enabled:
            for pid,fact in p.projection['points'].items():
                definition=p.payload.points[pid].definition
                if not definition.enabled or not p.definitions[pid][2]: continue
                observation=instant(fact['observedAt']); expiration=observation.months(state.retention_months)
                if expiration<=now: continue
                old=await crud.latest(db,payload.plc_id,pid)
                if old and old.source_epoch==binding.source_epoch and old.source_seq>=int(payload.source_seq): continue
                data=dict(source_epoch=binding.source_epoch,definition_digest=binary(definition_digest(definition)),instance_id=crud.key(payload.instance_id),source_generation=crud.key(payload.source_generation),source_seq=int(payload.source_seq),config_revision=crud.key(payload.revision),sample_id=crud.key(w.sample_id),part=w.part,cycle_id=crud.key(w.cycle_id),db_number=payload.db_number,group_id=crud.key(payload.group_id),point_fact=canonical(fact),observed_at=observation.wall,observed_ns=observation.ns,expires_at=expiration.wall,expires_ns=expiration.ns,updated_at=now.wall)
                before=crud.payload_size(old) if old else 0
                if old:
                    for k,v in data.items(): setattr(old,k,v)
                else:
                    old=LatestPoint(plc_id=crud.key(payload.plc_id),point_id=crud.key(pid),created_at=now.wall,**data); db.add(old)
                crud.reserve(state,crud.payload_size(old)-before); advanced.append(pid)
        cycle=cycle_rows[w.cycle_id]; received=strict_json(cycle.received_parts)['items']
        marker=dict(sampleId=w.sample_id,part=w.part,contentDigest=w.content_digest)
        if marker not in received: received.append(marker)
        cycle.received_parts=canonical({'items':received}); cycle.complete=len(received)==len(strict_json(cycle.expected_parts)['items'])
        cycle.quality_good=cycle.quality_good and all(x.quality=='good' for x in p.payload.points.values()); cycle.updated_at=now.wall
        receipt=SampleReceipt(instance_id=crud.key(b.instance_id),sample_id=crud.key(w.sample_id),part=w.part,parts=w.parts,cycle_id=crud.key(w.cycle_id),plc_id=crud.key(payload.plc_id),source_generation=crud.key(payload.source_generation),source_seq=int(payload.source_seq),db_number=payload.db_number,group_id=crud.key(payload.group_id),source_sha=binary(w.source_sha256),content_digest=binary(w.content_digest),point_ids=canonical({'items':w.point_ids}),commit_serial=serial,ordinal=ordinal,observed_from=low.wall,observed_from_ns=low.ns,observed_to=high.wall,observed_to_ns=high.ns,raw_expires_at=raw_expiry.wall,raw_expires_ns=raw_expiry.ns,first_result=b'{}',proof_expires_at=expires_proof.wall,**crud.timestamps(now))
        db.add(receipt); crud.reserve(state,proof_delta=1); existing[(w.sample_id,w.part)]=receipt
        # Flush keeps subsequent parts of the same sample visible with autoflush disabled.
        await db.flush()
        received_sample=await crud.sample_receipts(db,b.instance_id,w.sample_id)
        result=dict(sampleId=w.sample_id,part=w.part,parts=w.parts,sourceSha256=w.source_sha256,contentDigest=w.content_digest,outcome='created',originalOutcome='created',confirmation='created',sourceSampleComplete=len(received_sample)==w.parts,position=position(receipt),latestAdvancedPointIds=advanced,expiresAt=raw_expiry.wire(),valueReadable=True)
        receipt.first_result=canonical(result)
    for p in prepared.parts:
        row=existing[(p.wire.sample_id,p.wire.part)]; result=strict_json(row.first_result)
        if p not in new:
            readable=Instant(row.raw_expires_at,row.raw_expires_ns)>now
            result.update(outcome='duplicate',confirmation='duplicate' if readable else 'historical_committed',valueReadable=readable)
        else:
            # All parts received in this transaction share the final completeness state.
            sample_rows=await crud.sample_receipts(db,b.instance_id,p.wire.sample_id)
            result['sourceSampleComplete']=len(sample_rows)==p.wire.parts; row.first_result=canonical(result)
        results.append(result)
    cycle_outputs=[]
    for cid,row in cycle_rows.items():
        cycle_outputs.append(dict(cycleId=cid,cycleDigest=text_digest(row.cycle_digest),complete=row.complete,qualityGood=row.quality_good,receivedParts=len(strict_json(row.received_parts)['items']),expectedParts=len(strict_json(row.expected_parts)['items'])))
    data=dict(contractVersion='plc-facts/v1',digestProfile='pf-json/v1',instanceId=b.instance_id,batchId=b.batch_id,requestDigest=b.request_digest,receiptId=str(uuid4()),status='committed',persistence='committed',newFactsCommitted=bool(new),outcome='created' if new else 'duplicate',originalOutcome='created' if new else 'duplicate',confirmation='facts_committed',commitSerial=str(serial) if serial else None,committedAt=now.wire(),proofExpiresAt=expires_proof.wire(),results=results,cycles=cycle_outputs)
    result=dict(code=200,message='success',data=data)
    crud.reserve(state,proof_delta=1)
    db.add(BatchReceipt(instance_id=crud.key(b.instance_id),batch_id=crud.key(b.batch_id),request_digest=binary(b.request_digest),receipt_id=data['receiptId'],terminal='committed',http_status=200,result=canonical(result),members=canonical({'items':member_set(prepared)}),parent_batch_id=crud.key(b.parent.batch_id) if b.parent else None,parent_depth=depth,rejection_token=None,rejection_token_sha=None,recorded_at=now.wall,proof_expires_at=expires_proof.wall,**crud.timestamps(now)))
    if serial: state.high_serial=serial
    state.last_db_time=now.wall; state.updated_at=now.wall
    return result
