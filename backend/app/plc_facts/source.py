"""原文关联、定义和值、固定贪心分片；全部在数据库锁外验证。"""
from dataclasses import dataclass
from decimal import Decimal
import re
from pydantic import ValidationError
from .canonical import strict_json,canonical,digest,sha
from .error_codes import FactsError
from .retention import instant
from .schemas.source import Payload,CycleManifest,Definition
from .schemas.batch_in import BatchIn


def validate(model,value):
    try: return model.model_validate(value)
    except (ValidationError,ValueError,TypeError): raise FactsError('invalid_request') from None


def ordered(values): return sorted(values,key=lambda x:x.encode('utf-8'))
def unique(values):
    if len(values)!=len(set(values)): raise FactsError('invalid_request')
    return values


def definition_object(definition):
    d=definition.model_dump(by_alias=True) if isinstance(definition,Definition) else dict(definition)
    result={k:d.get(k) for k in ('id','plcId','dbId','sourcePath','name','nameMode','dataType','enabled','groupId')}
    a=d.get('address')
    result['address']=None if a is None else {k:a[k] for k in ('offset','bit','confirmed')}
    return result


def definition_digest(definition): return digest('definition',definition_object(definition))


def context_definitions(context,plc_id):
    """上下文扩展仅保留原证据，解释有限归属结构，不执行任何内容。"""
    if type(context.get('schemaVersion')) is not int or context.get('schemaVersion')!=1: raise FactsError('invalid_request')
    maps={}
    for key in ('plcs','dbs','groups','points'):
        rows=context.get(key)
        if not isinstance(rows,list): raise FactsError('invalid_request')
        if len(rows)>4096: raise FactsError('payload_too_large',413)
        if any(not isinstance(r,dict) or not isinstance(r.get('id'),str) for r in rows): raise FactsError('invalid_request')
        unique([r['id'] for r in rows]); maps[key]={r['id']:r for r in rows}
    plc=maps['plcs'].get(plc_id)
    if not plc or type(plc.get('enabled')) is not bool: raise FactsError('invalid_request')
    definitions={}; entries=[]
    for p in maps['points'].values():
        if p.get('plcId')!=plc_id: continue
        d=validate(Definition,p); db=maps['dbs'].get(d.db_id); group=maps['groups'].get(d.group_id)
        if not db or db.get('plcId')!=plc_id or type(db.get('number')) is not int or not 1<=db['number']<=65535: raise FactsError('invalid_request')
        if group and (group.get('plcId')!=plc_id or type(group.get('enabled')) is not bool): raise FactsError('invalid_request')
        definitions[d.id]=(d,db['number'],bool(group and group['enabled']))
        entries.append(dict(pointId=d.id,dbNumber=db['number'],groupEnabled=bool(group and group['enabled']),definitionDigest=definition_digest(d)))
    entries.sort(key=lambda e:e['pointId'].encode('utf-8'))
    return definitions,digest('definition-set',dict(plcId=plc_id,plcEnabled=plc['enabled'],points=entries)),plc['enabled']


def value_check(point):
    d=point.definition; typ=d.data_type; v=point.value; a=d.address
    for text,max_bytes in ((d.source_path,2048),(d.name,512),(d.comment,4096)):
        if len(text.encode('utf-8'))>max_bytes: raise FactsError('payload_too_large',413)
    widths={'BOOL':1,'BYTE':1,'USINT':1,'CHAR':1,'INT':2,'UINT':2,'WORD':2,'DINT':4,'UDINT':4,'DWORD':4,'REAL':4}
    string=re.fullmatch(r'STRING\[([1-9][0-9]{0,2})\]',typ)
    if string and not 1<=int(string[1])<=254: string=None
    known=typ in widths or string is not None
    width=widths.get(typ,int(string[1])+2 if string else 1)
    if a and (a.offset+width>65536 or (typ=='BOOL' and a.bit is None) or (typ!='BOOL' and a.bit is not None)): raise FactsError('invalid_request')
    if point.quality=='bad':
        if v is not None or not point.reason or len(point.reason.encode('utf-8'))>128 or (not known and point.reason!='unsupported_type'): raise FactsError('invalid_request')
        return
    if v is None or point.reason is not None or not a or not a.confirmed or not known: raise FactsError('invalid_request')
    if typ=='BOOL': ok=type(v) is bool
    elif typ in ('BYTE','USINT','INT','UINT','WORD','DINT','UDINT','DWORD'):
        bounds={'BYTE':(0,255),'USINT':(0,255),'INT':(-32768,32767),'UINT':(0,65535),'WORD':(0,65535),'DINT':(-2147483648,2147483647),'UDINT':(0,4294967295),'DWORD':(0,4294967295)}
        ok=type(v) is int and bounds[typ][0]<=v<=bounds[typ][1]
    elif typ=='REAL':
        # copy_abs与Decimal(int)精确复制，不受调用方Decimal context精度舍入。
        magnitude=Decimal(v).copy_abs() if type(v) in (int,Decimal) else None
        ok=magnitude is not None and magnitude<=Decimal('3.4028234663852886e38') and (magnitude==0 or magnitude>=Decimal('1.401298464324817e-45'))
    else:
        ok=isinstance(v,str) and all(ord(c)<128 for c in v) and (len(v)==1 if typ=='CHAR' else len(v)<=int(string[1]))
    if not ok: raise FactsError('invalid_request')


def fixed_parts(points):
    result=[]; current={}
    for key in ordered(points):
        candidate={**current,key:points[key]}
        if len(candidate)>512 or len(canonical(candidate))>128*1024:
            if not current: raise FactsError('payload_too_large',413)
            result.append(list(current)); current={key:points[key]}
            if len(canonical(current))>128*1024: raise FactsError('payload_too_large',413)
        else: current=candidate
    if current: result.append(list(current))
    return result


def projection(payload,part,parts,point_ids,source_sha):
    p=payload.model_dump(by_alias=True)
    p.pop('schemaVersion'); p['configRevision']=p.pop('revision')
    # Legacy omission is preserved in content projection; definition digest normalizes it independently.
    for key,point in payload.points.items():
        if 'name_mode' not in point.definition.model_fields_set: p['points'][key]['definition'].pop('nameMode',None)
    p.update(sourceSha256=source_sha,part=part,parts=parts)
    p['points']={key:p['points'][key] for key in point_ids}
    return p

@dataclass
class PreparedPart:
    wire: object
    payload: Payload
    projection: dict
    definition_set_digest: str
    definitions: dict
    current_enabled: bool

@dataclass
class PreparedCycle:
    wire: object
    manifest: CycleManifest
    context: dict
    digest: str
    expected: dict

@dataclass
class PreparedBatch:
    wire: BatchIn
    parts: list[PreparedPart]
    cycles: dict[str,PreparedCycle]


def prepare(batch):
    if not isinstance(batch,BatchIn): batch=validate(BatchIn,batch)
    if not batch.cycles or not batch.samples: raise FactsError('invalid_request')
    if len(batch.cycles)>16 or len(batch.samples)>32: raise FactsError('payload_too_large',413)
    unique([c.cycle_id for c in batch.cycles]); unique([(s.sample_id,s.part) for s in batch.samples])
    if {c.cycle_id for c in batch.cycles}!={s.cycle_id for s in batch.samples}: raise FactsError('invalid_request')
    cycles={}; parts=[]; plc_ids=set()
    for c in batch.cycles:
        if sha(c.manifest_utf8.encode('utf-8'))!=c.manifest_sha256 or sha(c.context_utf8.encode('utf-8'))!=c.context_sha256: raise FactsError('digest_mismatch')
        m=validate(CycleManifest,strict_json(c.manifest_utf8,128*1024)); context=strict_json(c.context_utf8,1024*1024)
        if m.cycle_id!=c.cycle_id or not instant(m.started_at)<=instant(m.finished_at)<=instant(m.saved_at): raise FactsError('invalid_request')
        if len(m.expected_point_ids)>4096 or len(m.samples)>128: raise FactsError('payload_too_large',413)
        unique(m.expected_point_ids); unique([s.sample_id for s in m.samples]); unique([s.db_number for s in m.samples])
        if not m.samples or not m.expected_point_ids: raise FactsError('invalid_request')
        defs,_,_=context_definitions(context,m.plc_id)
        expected_points={key for key,(d,_,enabled) in defs.items() if d.enabled and enabled and d.group_id==m.group_id}
        if set(m.expected_point_ids)!=expected_points: raise FactsError('invalid_request')
        for r in m.reads:
            if r.start+r.size>65536 or not instant(m.started_at)<=instant(r.started_at)<=instant(r.finished_at)<=instant(m.finished_at): raise FactsError('invalid_request')
        unique([s.sample_id for s in c.transport_manifest]); expected={}; covered=[]
        if len(c.transport_manifest)!=len(m.samples): raise FactsError('invalid_request')
        for t in c.transport_manifest:
            original=next((s for s in m.samples if s.sample_id==t.sample_id),None)
            if not original or original.db_number!=t.db_number or 'sha256:'+original.sha256!=t.source_sha256: raise FactsError('invalid_request')
            if not t.parts or len(t.parts)>16: raise FactsError('payload_too_large',413)
            if sorted(p.part for p in t.parts)!=list(range(1,len(t.parts)+1)): raise FactsError('invalid_request')
            for p in t.parts:
                if not p.point_ids or p.point_ids!=ordered(unique(p.point_ids)) or len(p.point_ids)>512: raise FactsError('invalid_request')
                for pid in p.point_ids:
                    if pid not in defs or defs[pid][1]!=t.db_number: raise FactsError('invalid_request')
                covered+=p.point_ids; expected[(t.sample_id,p.part)]=p.content_digest
        unique(covered)
        if set(covered)!=set(m.expected_point_ids): raise FactsError('invalid_request')
        cm=c.model_dump(by_alias=True)['transportManifest']
        for t in cm:
            t['parts'].sort(key=lambda p:p['part'])
        cm.sort(key=lambda t:t['sampleId'].encode('utf-8'))
        cd=digest('cycle',dict(manifestSha256=c.manifest_sha256,contextSha256=c.context_sha256,transportManifest=cm))
        cycles[c.cycle_id]=PreparedCycle(c,m,context,cd,expected); plc_ids.add(m.plc_id)
    unique([(c.manifest.plc_id,c.manifest.source_generation,c.manifest.source_seq) for c in cycles.values()])
    if len(plc_ids)>8: raise FactsError('payload_too_large',413)
    for s in batch.samples:
        c=cycles.get(s.cycle_id)
        if c is None: raise FactsError('invalid_request')
        if sha(s.payload_utf8.encode('utf-8'))!=s.source_sha256: raise FactsError('digest_mismatch')
        p=validate(Payload,strict_json(s.payload_utf8,512*1024))
        if (p.sample_id,p.cycle_id,p.instance_id)!=(s.sample_id,s.cycle_id,batch.instance_id): raise FactsError('invalid_request')
        m=c.manifest
        for attr in ('plc_id','source_generation','source_seq','group_id','revision','started_at','finished_at','saved_at'):
            if getattr(p,attr)!=getattr(m,attr): raise FactsError('invalid_request')
        if not p.points: raise FactsError('invalid_request')
        definitions,ds,enabled=context_definitions(c.context,p.plc_id)
        for key,point in p.points.items():
            d=point.definition
            if key!=d.id or d.plc_id!=p.plc_id or d.group_id!=p.group_id or not d.enabled: raise FactsError('invalid_request')
            expected=definitions.get(key)
            if expected is None or not expected[2] or expected[1]!=p.db_number or d.model_dump()!=expected[0].model_dump(): raise FactsError('invalid_request')
            if not instant(p.started_at)<=instant(point.observed_at)<=instant(p.finished_at): raise FactsError('invalid_request')
            value_check(point)
        all_points={key:point.model_dump(by_alias=True) for key,point in p.points.items()}
        for key,point in p.points.items():
            if 'name_mode' not in point.definition.model_fields_set: all_points[key]['definition'].pop('nameMode',None)
        grouping=fixed_parts(all_points)
        t=next((t for t in c.wire.transport_manifest if t.sample_id==s.sample_id),None)
        if t is None or t.db_number!=p.db_number or t.source_sha256!=s.source_sha256 or s.parts!=len(grouping) or len(t.parts)!=len(grouping): raise FactsError('invalid_request')
        for index,keys in enumerate(grouping,1):
            item=next(x for x in t.parts if x.part==index)
            candidate=projection(p,index,len(grouping),keys,s.source_sha256)
            if item.point_ids!=keys or digest('sample-part',candidate)!=item.content_digest: raise FactsError('digest_mismatch')
        if s.part>s.parts or s.point_ids!=grouping[s.part-1]: raise FactsError('invalid_request')
        pr=projection(p,s.part,s.parts,s.point_ids,s.source_sha256)
        if digest('sample-part',pr)!=s.content_digest or c.expected.get((s.sample_id,s.part))!=s.content_digest: raise FactsError('digest_mismatch')
        parts.append(PreparedPart(s,p,pr,ds,definitions,enabled))
    outer=batch.model_dump(by_alias=True); outer.pop('requestDigest')
    outer['cycles'].sort(key=lambda c:c['cycleId'].encode('utf-8'))
    for c in outer['cycles']:
        c['transportManifest'].sort(key=lambda t:t['sampleId'].encode('utf-8'))
        for t in c['transportManifest']: t['parts'].sort(key=lambda p:p['part'])
    outer['samples'].sort(key=lambda s:(s['sampleId'].encode('utf-8'),s['part']))
    if digest('batch',outer)!=batch.request_digest: raise FactsError('digest_mismatch')
    return PreparedBatch(batch,parts,cycles)
