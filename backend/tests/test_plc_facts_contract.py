"""独立固定向量与公开合同检查；no_db，无共享清库fixture。"""
import copy
import hashlib
import json
from pathlib import Path
from decimal import Decimal
import pytest
import app.plc_facts
from app.plc_facts.canonical import canonical,digest,strict_json
from app.plc_facts.source import prepare,definition_digest
from app.plc_facts.schemas.batch_in import BatchIn
from app.plc_facts.schemas.receipt_out import ReceiptOut,FailureOut

pytestmark=pytest.mark.no_db
ROOT=Path(app.plc_facts.__file__).resolve().parents[3]
CONTRACT=ROOT/'contracts/published/http-api/plc-facts-v1'
def vectors(): return json.loads((CONTRACT/'vectors.json').read_text(),parse_float=Decimal)
def sample(): return copy.deepcopy(vectors()['request'])

@pytest.mark.parametrize('name',('sourceSha256','manifestSha256','contextSha256','contentDigest','requestDigest'))
def test_fixed_request_digests(name):
    v=vectors();p=prepare(v['request'])
    actual=getattr(p.wire,{'sourceSha256':'source_sha256'}.get(name,name),None)
    if name=='requestDigest': actual=p.wire.request_digest
    elif name in ('sourceSha256','contentDigest'): actual=getattr(p.parts[0].wire,{'sourceSha256':'source_sha256','contentDigest':'content_digest'}[name])
    else: actual=getattr(p.cycles['cycle-demo'].wire,{'manifestSha256':'manifest_sha256','contextSha256':'context_sha256'}[name])
    assert actual==v['expected'][name]

def test_independent_full_projection_definition_vectors():
    v=vectors();p=prepare(v['request']);part=p.parts[0]
    assert p.cycles['cycle-demo'].digest==v['expected']['cycleDigest']
    assert definition_digest(part.payload.points['point_x'].definition)==v['expected']['definitionDigest']
    assert part.definition_set_digest==v['expected']['definitionSetDigest']
    assert digest('batch',strict_json(v['canonicalRequestUtf8']))==v['expected']['requestDigest']
    for row in v['basics']: assert hashlib.sha256(row['bytes'].encode()).hexdigest()==row['sha256']

@pytest.mark.parametrize('domain,expected',[
('sample-part','2c28257e2df4234ce62fd9deb1fd7d2a948ad95742224f91c5b3fad081ceb4ca'),
('cycle','1f49907793e5bc4fabb661186cd3c158986d5bc6b760d87c8cd652da38b52ace'),
('batch','e0f1dedaff692e2ce5dedb0dedd6997bdb963732fb910ec0a62b3824c3bceeb3'),
('query-projection','6f195650e8e74f2327437afbc08c6051b0cf4d001d07c2ed73d02e90574f5285'),
('definition','339b46388541dabcf9c099b1c290596cde85578cf61434a1bee20b354de7202b'),
('definition-set','42b6200b76449af730f97b714c0a72add947a9cc75577d83e6ade84da5c65d3b')])
def test_domain_vectors(domain,expected): assert digest(domain,{})=='sha256:'+expected

@pytest.mark.parametrize('number',('1','1.0','1e0','1.00000'))
def test_decimal_number_semantics(number): assert canonical({'n':Decimal(number),'z':Decimal('-0')})==b'{"n":1,"z":0}'

def test_minimal_control_unicode_and_case():
    assert canonical({'x_y':'\n\t/中','A':True,'a':False})=='{"A":true,"a":false,"x_y":"\\u000a\\u0009/中"}'.encode()

def test_machine_ref_closure_and_only_three_routes():
    op=json.loads((CONTRACT/'openapi.json').read_text());schema=json.loads((CONTRACT/'schema.json').read_text())
    assert len(op['paths'])==3
    assert set(op['paths'])=={'/api/v1/integration/plc-facts/'+s for s in ('batches','latest','history')}
    def walk(v):
        if isinstance(v,dict):
            if '$ref' in v:
                assert v['$ref'].split('/')[-1] in schema['$defs']
            if v.get('type')=='number': assert 'anyOf' not in v
            for item in v.values():walk(item)
        elif isinstance(v,list):
            for item in v:walk(item)
    walk(schema)
    for path,value in op['paths'].items():
        method='post' if path.endswith('batches') else 'get'
        assert not value[method].get('security')
        assert set(value[method]['responses'])=={'200','403','409','410','413','415','422','429','503','500'}

def independent_freeze(batch):
    """Test fixture authoring uses stdlib, separately from the provider encoder."""
    from datetime import datetime,timezone,timedelta
    def encode(v):
        return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    def sha(s):return 'sha256:'+hashlib.sha256(s.encode()).hexdigest()
    def domain(name,v):return 'sha256:'+hashlib.sha256(('plc-facts/v1\0'+name+'\0'+encode(v)).encode()).hexdigest()
    def t9(s):
        dt=datetime.fromisoformat(s).astimezone(timezone(timedelta(hours=8)))
        return dt.strftime('%Y-%m-%dT%H:%M:%S')+'.%06d000+08:00'%dt.microsecond
    b=copy.deepcopy(batch)
    for s in b['samples']:
        p=json.loads(s['payloadUtf8']);s['sourceSha256']=sha(s['payloadUtf8'])
        pr={k:v for k,v in p.items() if k not in ('schemaVersion','revision')};pr['configRevision']=p['revision']
        pr.update(sourceSha256=s['sourceSha256'],part=s['part'],parts=s['parts']);pr['points']={k:pr['points'][k] for k in s['pointIds']}
        for k in ('startedAt','finishedAt','savedAt'):pr[k]=t9(pr[k])
        for v in pr['points'].values():v['observedAt']=t9(v['observedAt'])
        s['contentDigest']=domain('sample-part',pr)
    for c in b['cycles']:
        manifest=json.loads(c['manifestUtf8'])
        for t in c['transportManifest']:
            for s in b['samples']:
                if s['sampleId']!=t['sampleId']:continue
                t['sourceSha256']=s['sourceSha256']
                for part in t['parts']:
                    if part['part']==s['part']:part['contentDigest']=s['contentDigest']
                for original in manifest['samples']:
                    if original['sampleId']==s['sampleId']:original['sha256']=s['sourceSha256'][7:]
        c['manifestUtf8']=encode(manifest);c['manifestSha256']=sha(c['manifestUtf8']);c['contextSha256']=sha(c['contextUtf8'])
    outer=copy.deepcopy(b);outer.pop('requestDigest',None);outer['batchCreatedAt']=t9(outer['batchCreatedAt'])
    outer['cycles'].sort(key=lambda c:c['cycleId']);outer['samples'].sort(key=lambda s:(s['sampleId'],s['part']))
    b['requestDigest']=domain('batch',outer)
    return b
