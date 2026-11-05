"""一致性snapshot查询owner；逻辑expiry优先于物理清理，分页不越过发布位置。"""
from ..crud import async_ingest as crud,async_query as query_crud
from ..canonical import canonical,digest,strict_json,text_digest
from ..retention import Instant,instant
from ..cursors import issue,consume,filter_hash
from ..error_codes import FactsError

MAX_RESPONSE=2*1024*1024

def pos(value): return dict(commitSerial=str(value[0]),ordinal=value[1])
def expired(row,now): return Instant(row.expires_at,row.expires_ns)<=now

def matches(row,q):
    return row.plc_id==crud.key(q.plc_id) and all(value is None or actual==value for value,actual in (
        (q.instance_id,crud.decoded(row.instance_id)),(q.source_generation,crud.decoded(row.source_generation)),
        (q.db_number,row.db_number),(q.group_id,crud.decoded(row.group_id))))

def cycle_out(row):
    return dict(cycleId=crud.decoded(row.cycle_id),cycleDigest=text_digest(row.cycle_digest),complete=row.complete,qualityGood=row.quality_good,
        receivedParts=len(strict_json(row.received_parts)['items']),expectedParts=len(strict_json(row.expected_parts)['items']))

def gap(row,reason):
    return dict(kind='gap',position=pos([row.commit_serial,row.ordinal]),reason=reason,instanceId=crud.decoded(row.instance_id),plcId=crud.decoded(row.plc_id),
        sourceGeneration=crud.decoded(row.source_generation),sourceSeq=str(row.source_seq),cycleId=crud.decoded(row.cycle_id),sampleId=crud.decoded(row.sample_id),part=row.part,
        pointIds=strict_json(row.point_ids)['items'],sourceSha256=text_digest(row.source_sha),contentDigest=text_digest(row.content_digest),
        observedFrom=Instant(row.observed_from,row.observed_from_ns).wire(),observedTo=Instant(row.observed_to,row.observed_to_ns).wire(),expiredAt=Instant(row.raw_expires_at,row.raw_expires_ns).wire())

async def read(db,q,settings):
    try:
        state=await crud.state_row(db)
        await crud.adopted(db,state)
        now=await crud.clock(db,state)
        mode=getattr(q,'mode','latest')
        if mode=='latest': data=await latest(db,q,state,now,settings.PLC_FACTS_CURSOR_HMAC_KEY)
        else: data=await history(db,q,state,now,settings.PLC_FACTS_CURSOR_HMAC_KEY)
        await db.rollback() # read transaction fully exits before any bytes are sent
        return dict(code=200,message='success',data=data)
    except Exception:
        await db.rollback()
        raise

def base(state,now,mode):
    return dict(contractVersion='plc-facts/v1',digestProfile='pf-json/v1',asOf=now.wire(),mode=mode,items=[],hasMore=False,
        coverage=dict(complete=False,meaning='receipt_feed_only_not_source_completeness',unknownBeforeSerial=str(state.proof_floor_serial)))

async def latest(db,q,state,now,key):
    binding=await crud.binding(db,q.plc_id)
    if binding is None: raise FactsError('not_ready',503)
    fhash=filter_hash(q); after=None
    if q.page_cursor:
        p=consume(q.page_cursor,key,'latest',state.storage_epoch,fhash,now)
        if p.get('bindingRevision')!=binding.binding_revision: raise FactsError('binding_conflict',409)
        after=p.get('lastPoint')
    data=base(state,now,'latest'); data.update(bindingRevision=str(binding.binding_revision),nextPageCursor=None)
    rows=await query_crud.latest_points(db,q.plc_id,binding.source_epoch,after,q,2001)
    count=0; groups={}; last=after; byte_count=len(canonical(data))
    for row in rows[:2000]:
        if expired(row,now): last=[row.db_number,crud.decoded(row.point_id)]; continue
        if count>=q.limit: data['hasMore']=True; break
        point=strict_json(row.point_fact)
        point.update(expiresAt=Instant(row.expires_at,row.expires_ns).wire(),source=dict(instanceId=crud.decoded(row.instance_id),sourceGeneration=crud.decoded(row.source_generation),sourceSeq=str(row.source_seq),configRevision=crud.decoded(row.config_revision),definitionDigest=text_digest(row.definition_digest),sampleId=crud.decoded(row.sample_id),part=row.part,cycleId=crud.decoded(row.cycle_id),groupId=crud.decoded(row.group_id)))
        size=len(canonical(point))+len(row.point_id)+128
        if byte_count+size>MAX_RESPONSE-16384: data['hasMore']=True; break
        last=[row.db_number,crud.decoded(row.point_id)]; count+=1; byte_count+=size
        group=groups.setdefault(row.db_number,dict(plcId=q.plc_id,dbNumber=row.db_number,points={}))
        group['points'][crud.decoded(row.point_id)]=point
    if len(rows)>2000: data['hasMore']=True
    data['items']=list(groups.values())
    if data['hasMore']:
        data['nextPageCursor']=issue(key,'latest',state.storage_epoch,fhash,[0,0],now,bindingRevision=binding.binding_revision,lastPoint=last)
    return data

async def history(db,q,state,now,key):
    # Binding is an explicit adopted readiness condition even for historical reads.
    if await crud.binding(db,q.plc_id) is None: raise FactsError('not_ready',503)
    high=state.high_serial; after=[0,0]; fhash=filter_hash(q); floor=(state.proof_floor_serial,state.proof_floor_ordinal)
    token=q.cursor if q.mode=='changes' else q.page_cursor
    if token:
        p=consume(token,key,q.mode,state.storage_epoch,fhash,now,floor)
        after=p['after'][:2]
        if q.mode=='range':
            high=p.get('snapshotHighSerial')
            if type(high) is not int or high>state.high_serial: raise FactsError('cursor_mismatch')
    elif q.mode=='changes' and q.start=='tail': after=max(list(floor),await query_crud.high_position(db,high))
    else: after=list(floor)
    data=base(state,now,q.mode)
    data.update(snapshotHighSerial=str(high),scannedThrough=pos(after),scanBudgetReached=False)
    if q.mode=='changes':
        data.update(baseline='explicit_tail' if q.start=='tail' else None)
        if q.start=='tail': data['omittedThrough']=str(high)
    rows=await query_crud.feed(db,high,after,2001)
    items=[]; byte_count=len(canonical(data)); scanned=after
    for row in rows[:2000]:
        location=[row.commit_serial,row.ordinal]
        if len(items)>=q.limit: data['hasMore']=True; break
        item=None
        if matches(row,q):
            ids=strict_json(row.point_ids)['items']
            selected=q.point_id is None or q.point_id in ids
            interval= q.mode!='range' or (Instant(row.observed_from,row.observed_from_ns)<instant(q.to) and Instant(row.observed_to,row.observed_to_ns)>=instant(q.from_))
            if selected and interval:
                raw=await crud.raw(db,crud.decoded(row.instance_id),crud.decoded(row.sample_id))
                if Instant(row.raw_expires_at,row.raw_expires_ns)<=now: item=gap(row,'raw_expired')
                elif raw is None: item=gap(row,'raw_unavailable')
                elif expired(raw,now): item=gap(row,'raw_expired')
                else:
                    projection=strict_json(raw.projections)['parts'].get(str(row.part))
                    if projection is None: item=gap(row,'raw_unavailable')
                    elif q.view=='original':
                        sample_rows=await crud.sample_receipts(db,crud.decoded(row.instance_id),crud.decoded(row.sample_id))
                        all_payload=strict_json(raw.payload_utf8)
                        original_times=[instant(p['observedAt']) for p in all_payload['points'].values()]
                        if len(sample_rows)==row.parts and all(instant(q.from_)<=t<instant(q.to) for t in original_times):
                            item=dict(kind='original',position=pos(location),instanceId=crud.decoded(row.instance_id),plcId=q.plc_id,sampleId=crud.decoded(row.sample_id),sourceSha256=text_digest(row.source_sha),payloadUtf8=raw.payload_utf8.decode('utf-8'),sourceSampleComplete=True,expiresAt=Instant(raw.expires_at,raw.expires_ns).wire())
                    else:
                        projection['points']={pid:fact for pid,fact in projection['points'].items() if (q.point_id is None or pid==q.point_id) and (q.mode!='range' or instant(q.from_)<=instant(fact['observedAt'])<instant(q.to)) and instant(fact['observedAt']).months(state.retention_months)>now}
                        if projection['points']:
                            projection['expiresAt']=Instant(raw.expires_at,raw.expires_ns).wire()
                            cycle=await crud.cycle(db,crud.decoded(row.instance_id),crud.decoded(row.cycle_id))
                            if cycle is None: raise FactsError('cursor_gap',410)
                            item=dict(kind='fact',position=pos(location),sourceSha256=text_digest(row.source_sha),contentDigest=text_digest(row.content_digest),projectionDigest=digest('query-projection',projection),projection=projection,cycle=cycle_out(cycle))
        if item is not None:
            size=len(canonical(item))
            if byte_count+size>MAX_RESPONSE-16384:
                data.update(hasMore=True,scanBudgetReached=True); break
            items.append(item); byte_count+=size
        scanned=location
    else:
        if len(rows)>2000: data.update(hasMore=True,scanBudgetReached=True)
    # No feed rows means high may contain rejected/empty-free serial? Only new facts allocate serial.
    if not rows: scanned=max(after,list(floor),await query_crud.high_position(db,high))
    data.update(items=items,scannedThrough=pos(scanned))
    next_token=issue(key,q.mode,state.storage_epoch,fhash,scanned,now,**({'snapshotHighSerial':high} if q.mode=='range' else {}))
    if q.mode=='changes': data['nextCursor']=next_token
    else: data['nextPageCursor']=next_token if data['hasMore'] else None
    return data
