"""有限游标profile、HMAC与filter/epoch/TTL绑定；错误不静默跳尾。"""
import base64
import hashlib
import hmac
from .canonical import canonical,strict_json,sha
from .error_codes import FactsError
from .retention import instant


def b64(data): return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')
def un64(value): return base64.b64decode(value+'='*((-len(value))%4),altchars=b'-_',validate=True)
def filters(query):
    return {k:v for k,v in query.model_dump(by_alias=True).items() if k not in ('cursor','pageCursor','start','limit')}
def filter_hash(query): return sha(canonical(filters(query)))
def issue(key,mode,epoch,filter_digest,after,now,**extra):
    ttl={'changes':86400,'range':900,'latest':30}[mode]
    payload=dict(profile='pf-cursor/v1',contractVersion='plc-facts/v1',mode=mode,storageEpoch=epoch,
                 filterHash=filter_digest,after=after,issuedAt=now.wire(),expiresAt=now.seconds(ttl).wire(),**extra)
    data=canonical(payload)
    return b64(data)+'.'+b64(hmac.new(bytes.fromhex(key),data,hashlib.sha256).digest())

def consume(token,key,mode,epoch,filter_digest,now,floor=(0,0)):
    try:
        if not isinstance(token,str) or len(token)>8192: raise ValueError()
        body,mac=token.split('.')
        raw=un64(body); signature=un64(mac)
        if not hmac.compare_digest(signature,hmac.new(bytes.fromhex(key),raw,hashlib.sha256).digest()): raise ValueError()
        p=strict_json(raw,8192)
    except (ValueError,TypeError,FactsError):
        raise FactsError('invalid_request',422,dict(persistence='none',newFactsCommitted=False,retryable=False,retirementAllowed=False,diagnostics=[],requiresResync=True)) from None
    for k,v in dict(profile='pf-cursor/v1',contractVersion='plc-facts/v1',mode=mode,storageEpoch=epoch,filterHash=filter_digest).items():
        if p.get(k)!=v: raise FactsError('cursor_mismatch')
    if instant(p['expiresAt'])<=now: raise FactsError('cursor_expired',410,dict(persistence='none',newFactsCommitted=False,retryable=False,retirementAllowed=False,diagnostics=[],requiresResync=True))
    after=p.get('after')
    if not isinstance(after,list) or len(after) not in (2,3) or type(after[0]) is not int or type(after[1]) is not int or min(after[:2])<0 or after[1]>32: raise FactsError('invalid_request')
    if tuple(after[:2])<floor:
        raise FactsError('cursor_gap',410,dict(persistence='none',newFactsCommitted=False,retryable=False,retirementAllowed=False,diagnostics=[],requiresResync=True,lostFrom=dict(commitSerial=str(after[0]),ordinal=after[1]),lostThrough=dict(commitSerial=str(floor[0]),ordinal=floor[1]),earliestRecoverableCursor=issue(key,mode,epoch,filter_digest,list(floor),now,**({'snapshotHighSerial':p['snapshotHighSerial']} if mode=='range' and 'snapshotHighSerial' in p else {}))))
    return p
