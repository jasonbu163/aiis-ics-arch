"""一次性维护事务owner；显式采用/CAS与有界清理，不创建调度器。"""
import json
from dataclasses import dataclass
from datetime import timedelta
import time
from uuid import uuid4,UUID
from database import get_sync_db_context
from ..crud import sync_maintenance as crud
from ..crud.async_ingest import key,decoded,payload_size,reserve,timestamps
from ..models import StreamState,SourceBinding,LatestPoint,RawSample,Cycle,BatchReceipt,SampleReceipt
from ..canonical import canonical,binary,strict_json,text_digest,sha
from ..source import context_definitions,definition_digest
from ..retention import Instant
from ..error_codes import FactsError
from .async_ingest import emit

@dataclass
class MaintenanceOptions:
    action: str
    apply: bool
    target_alias: str
    schema: str
    expected_schema_revision: str
    expected_storage_epoch: str
    operation_approval: str
    confirmed_by: str
    expected_adoption_id: str|None=None
    revalidate_schema_only: bool=False
    plc_id: str|None=None
    instance_id: str|None=None
    source_generation: str|None=None
    config_revision: str|None=None
    context_utf8: str|None=None
    context_sha256: str|None=None
    expected_binding_revision: int|None=None
    seq_from: int|None=None
    old_seq_through: int|None=None
    retention_months: int=3
    max_value_bytes: int=1073741824
    max_proof_rows: int=1000000


def target(db,o):
    if not all((o.target_alias,o.schema,o.operation_approval,o.confirmed_by,o.expected_schema_revision,o.expected_storage_epoch)): raise FactsError('not_ready',503)
    try: UUID(o.expected_storage_epoch)
    except ValueError: raise FactsError('invalid_request') from None
    if db.connection().engine.url.database!=o.schema: raise FactsError('not_ready',503)
    profile=crud.verify_profile(db.connection())
    if profile['revision']!=o.expected_schema_revision: raise FactsError('not_ready',503)
    return profile


def adoption_evidence(o,profile,now,old=None):
    return canonical(dict(version='plc-facts-adoption/v1',targetAlias=o.target_alias,schema=o.schema,schemaProfile=profile['schemaProfile'],verifiedSchemaRevision=profile['revision'],fingerprint=profile['fingerprint'],dbNow=now.wire(),utcOffsetSeconds=28800,storageEpoch=o.expected_storage_epoch,retentionMonths=o.retention_months,confirmedBy=o.confirmed_by,operationApproval=o.operation_approval,previousAdoptionId=old,bindingSummary=None if o.revalidate_schema_only else dict(plcId=o.plc_id,instanceId=o.instance_id,sourceGeneration=o.source_generation,configRevision=o.config_revision,contextSha256=o.context_sha256,expectedBindingRevision=o.expected_binding_revision,seqFrom=o.seq_from,oldSeqThrough=o.old_seq_through)))


def adopt(db,o,profile,state,now):
    if o.revalidate_schema_only:
        if any(v is not None for v in (o.plc_id,o.instance_id,o.source_generation,o.config_revision,o.context_utf8,o.context_sha256,o.expected_binding_revision,o.seq_from,o.old_seq_through)): raise FactsError('invalid_request')
        if state is None or state.storage_epoch!=o.expected_storage_epoch or state.adoption_id!=o.expected_adoption_id or state.schema_fingerprint!=binary(profile['fingerprint']) or state.verified_schema_revision not in crud.PROFILES or state.schema_profile!=crud.PROFILES[state.verified_schema_revision][0]: raise FactsError('binding_conflict',409)
        changes=dict(schemaProfile=profile['schemaProfile'],verifiedSchemaRevision=profile['revision'],fingerprint=profile['fingerprint'],storageEpoch=state.storage_epoch)
        if o.apply:
            state.schema_profile=profile['schemaProfile']; state.verified_schema_revision=profile['revision']
            state.adoption_evidence=adoption_evidence(o,profile,now,state.adoption_id); state.updated_at=now.wall; state.last_db_time=now.wall
        return changes
    if not all((o.plc_id,o.instance_id,o.source_generation,o.config_revision,o.context_utf8,o.context_sha256)) or o.expected_binding_revision is None or o.seq_from is None: raise FactsError('invalid_request')
    from ..schemas.source import identifier,sequence
    for v in (o.plc_id,o.instance_id,o.source_generation,o.config_revision): identifier(v)
    sequence(str(o.seq_from))
    if sha(o.context_utf8.encode())!=o.context_sha256: raise FactsError('digest_mismatch')
    context=strict_json(o.context_utf8,1024*1024); definitions,definition_set,plc_enabled=context_definitions(context,o.plc_id)
    if o.retention_months not in (1,2,3) or not 1048576<=o.max_value_bytes<=1073741824 or not 100<=o.max_proof_rows<=1000000: raise FactsError('invalid_request')
    binding=crud.binding(db,o.plc_id)
    if (binding.binding_revision if binding else 0)!=o.expected_binding_revision: raise FactsError('binding_conflict',409)
    if state:
        if state.storage_epoch!=o.expected_storage_epoch or state.adoption_id!=o.expected_adoption_id or state.retention_months!=o.retention_months or (state.max_value_bytes,state.max_proof_rows)!=(o.max_value_bytes,o.max_proof_rows): raise FactsError('binding_conflict',409)
    elif o.expected_adoption_id is not None: raise FactsError('binding_conflict',409)
    elif not crud.unadopted_owner_empty(db): raise FactsError('not_ready',503)
    if not binding and crud.binding_count(db)>=256: raise FactsError('capacity_exceeded',503)
    source_change=bool(binding and (binding.instance_id,binding.source_generation)!=(key(o.instance_id),key(o.source_generation)))
    definition_change=bool(binding and binding.definition_set_digest!=binary(definition_set))
    windows=json.loads(binding.raw_only_windows) if binding else []
    if binding and (source_change or definition_change):
        if o.old_seq_through is None or not binding.seq_from<=o.old_seq_through<=binding.seq_through: raise FactsError('invalid_request')
        if not source_change and o.seq_from!=o.old_seq_through+1: raise FactsError('invalid_request')
        windows.append(dict(instanceId=decoded(binding.instance_id),sourceGeneration=decoded(binding.source_generation),definitionSetDigest=text_digest(binding.definition_set_digest),seqFrom=binding.seq_from,seqThrough=o.old_seq_through))
        if len(windows)>8: raise FactsError('capacity_exceeded',503)
    elif binding and o.seq_from!=binding.seq_from: raise FactsError('binding_conflict',409)
    old_points=crud.latest_rows(db,o.plc_id)
    revoke=[]
    for row in old_points:
        definition=definitions.get(decoded(row.point_id))
        if source_change or not plc_enabled or definition is None or not definition[0].enabled or not definition[2] or definition_digest(definition[0])!=text_digest(row.definition_digest): revoke.append(row)
    changes=dict(plcId=o.plc_id,bindingRevision=str(o.expected_binding_revision+1),sourceEpoch=str((binding.source_epoch+(1 if source_change else 0)) if binding else 1),definitionSetDigest=definition_set,revokedLatest=len(revoke),rawOnlyWindows=len(windows))
    if not o.apply: return changes
    if state is None:
        state=StreamState(id=1,storage_epoch=o.expected_storage_epoch,storage_profile='mysql84_shanghai_v1',adoption_id=str(uuid4()),schema_profile=profile['schemaProfile'],verified_schema_revision=profile['revision'],schema_fingerprint=binary(profile['fingerprint']),adoption_evidence=adoption_evidence(o,profile,now),retention_months=o.retention_months,high_serial=0,proof_floor_serial=0,proof_floor_ordinal=0,last_db_time=now.wall,value_bytes=0,proof_rows=0,max_value_bytes=o.max_value_bytes,max_proof_rows=o.max_proof_rows,cleanup_last_success=None,cleanup_failures=0,cleanup_oldest_expired=None,**timestamps(now))
        db.add(state)
    for row in revoke: reserve(state,-payload_size(row)); db.delete(row)
    data=dict(instance_id=key(o.instance_id),source_generation=key(o.source_generation),source_epoch=int(changes['sourceEpoch']),binding_revision=int(changes['bindingRevision']),config_revision=key(o.config_revision),context_sha=binary(o.context_sha256),definition_set_digest=binary(definition_set),seq_from=o.seq_from,seq_through=9223372036854775806,raw_only_windows=canonical(windows),updated_at=now.wall)
    if binding:
        for k,v in data.items(): setattr(binding,k,v)
    else: db.add(SourceBinding(plc_id=key(o.plc_id),created_at=now.wall,**data))
    state.last_db_time=now.wall; state.updated_at=now.wall
    changes['adoptionId']=state.adoption_id
    return changes


def cleanup_batch(db,state,now,apply,remaining_rows=200,remaining_bytes=2*1024*1024):
    """每事务≤200行/2MiB/100ms；单条大于剩余预算时推迟，原文上限可放入2MiB。"""
    started=time.monotonic(); count=0; removed_bytes=0; proof_count=0; actions=[]
    # 留20ms给最后一次SQL/最终flush；已发出的写入耗时参与下一项预算，避免末尾集中flush回滚整批。
    def budget(size): return count<remaining_rows and removed_bytes+size<=remaining_bytes and time.monotonic()-started<0.08
    # All raw values are removed before the finite proofs. No request invokes this function.
    for model in (RawSample,LatestPoint,Cycle):
        rows=crud.expired_rows(db,model,now)
        for row in rows:
            if Instant(row.expires_at,row.expires_ns)>now: continue
            size=payload_size(row)
            if model is Cycle and size==0: continue
            clear_fields=[]
            if model is Cycle:
                size=0
                for field in ('manifest_utf8','context_utf8','transport_manifest'):
                    field_size=len(getattr(row,field) or b'')
                    if field_size and budget(size+field_size): clear_fields.append(field); size+=field_size
                if not clear_fields: break
            elif not budget(size): break
            count+=1; removed_bytes+=size; actions.append(model.__tablename__)
            if apply:
                if model is Cycle:
                    for field in clear_fields: setattr(row,field,None)
                    row.updated_at=now.wall
                else: db.delete(row)
                db.flush()
    if count==0 or time.monotonic()-started<0.1:
        for row in crud.expired_batches(db,now):
            if not budget(0): break
            count+=1; proof_count+=1; actions.append(BatchReceipt.__tablename__)
            if apply: db.delete(row); db.flush()
    # Delete only an entire serial prefix; never an arbitrary matching PLC subset.
    if time.monotonic()-started<0.1:
        rows=crud.prefix_rows(db)
        if rows:
            serial=rows[0].commit_serial
            if rows and all(r.proof_expires_at<=now.wall for r in rows) and count+len(rows)<=remaining_rows and budget(0):
                for row in rows:
                    count+=1; proof_count+=1; actions.append(SampleReceipt.__tablename__)
                    if apply: db.delete(row)
                if apply: db.flush()
                if apply: state.proof_floor_serial=serial; state.proof_floor_ordinal=rows[-1].ordinal
    if apply: db.flush()
    if time.monotonic()-started<0.1:
        for row in crud.expired_cycle_proofs(db,now):
            if not budget(0): break
            # CRUD已在LIMIT前确认无原值且没有任何receipt引用。
            count+=1; proof_count+=1; actions.append(Cycle.__tablename__)
            if apply: db.delete(row); db.flush()
    elapsed=time.monotonic()-started
    if apply:
        reserve(state,-removed_bytes,-proof_count); state.cleanup_last_success=now.wall; state.cleanup_failures=0; state.last_db_time=now.wall; state.updated_at=now.wall
    return dict(rows=count,valueBytes=removed_bytes,proofRows=proof_count,elapsedMs=int(elapsed*1000),tables=sorted(set(actions)))


def summary(db,state,now):
    oldest=[]
    for m in (RawSample,LatestPoint,Cycle):
        value=crud.oldest_expired(db,m,now)
        if value: oldest.append(value)
    age=max(0,int((now.wall-min(oldest)).total_seconds())) if oldest else 0
    degraded=state.cleanup_failures>=3 or bool(oldest) and (state.cleanup_last_success is None or (now.wall-state.cleanup_last_success).total_seconds()>=180)
    return dict(storageEpoch=state.storage_epoch,adoptionId=state.adoption_id,highSerial=str(state.high_serial),valueBytes=state.value_bytes,proofRows=state.proof_rows,cleanupDegraded=degraded,oldestExpiredAgeSeconds=age,physicalCleanupSlaViolated=age>86400)


def _execute(o):
    started=time.monotonic(); totals=dict(rows=0,valueBytes=0,proofRows=0,transactions=0)
    for tick in range(10 if o.action=='cleanup' and o.apply else 1):
        if time.monotonic()-started>=2: break
        with get_sync_db_context() as db:
            profile=target(db,o)
            state=crud.lock(db) if o.apply else crud.state_row(db)
            now=crud.clock(db,state)
            if o.action=='adopt': result=adopt(db,o,profile,state,now)
            else:
                if state is None or state.storage_epoch!=o.expected_storage_epoch or state.verified_schema_revision!=profile['revision'] or state.schema_fingerprint!=binary(profile['fingerprint']): raise FactsError('not_ready',503)
                if o.action=='status': result=summary(db,state,now)
                else:
                    result=cleanup_batch(db,state,now,o.apply,min(200,2000-totals['rows']),min(2*1024*1024,20*1024*1024-totals['valueBytes']))
                    for field in ('rows','valueBytes','proofRows'): totals[field]+=result[field]
                    totals['transactions']+=1
            if o.action=='cleanup' and o.apply:
                flush_started=time.monotonic()
                db.flush()
                if result['elapsedMs']+(time.monotonic()-flush_started)*1000>100: raise FactsError('busy',429)
            if not o.apply: db.rollback()
        if o.action!='cleanup' or not o.apply or result['rows']==0: break
    emit('plc_facts_binding_adopted' if o.action=='adopt' else 'plc_facts_cleanup_completed',action=o.action,applied=o.apply,**totals)
    return dict(action=o.action,applied=o.apply,schemaProfile=profile['schemaProfile'],schemaRevision=profile['revision'],result=result,totals=totals)


def execute(o):
    try:
        return _execute(o)
    except Exception:
        failures=None
        if o.action=='cleanup' and o.apply:
            try:
                with get_sync_db_context() as db:
                    target(db,o)
                    state=crud.lock(db)
                    now=crud.clock(db,state)
                    if state is None or state.storage_epoch!=o.expected_storage_epoch: raise FactsError('not_ready',503)
                    state.cleanup_failures+=1; state.updated_at=now.wall
                    failures=state.cleanup_failures
            except Exception:
                pass
        emit('plc_facts_cleanup_degraded' if failures is not None and failures>=3 else 'plc_facts_cleanup_failed',action=o.action,consecutive_failures=failures)
        raise
