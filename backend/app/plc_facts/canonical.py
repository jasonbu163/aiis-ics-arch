"""pf-json/v1严格UTF-8解析与Decimal规范字节；不使用binary float。"""
from decimal import Decimal
import hashlib
import json
from .error_codes import FactsError

MAX_BODY = 4 * 1024 * 1024

def strict_json(body, maximum=MAX_BODY):
    if isinstance(body,str):
        try: body=body.encode('utf-8')
        except UnicodeError: raise FactsError('invalid_request') from None
    if len(body)>maximum: raise FactsError('payload_too_large',413)
    depth=0; quoted=False; escaped=False
    for ch in body:
        if quoted:
            if escaped: escaped=False
            elif ch==92: escaped=True
            elif ch==34: quoted=False
        elif ch==34: quoted=True
        elif ch in (91,123):
            depth+=1
            if depth>20: raise FactsError('payload_too_large',413)
        elif ch in (93,125): depth-=1
    def pairs(items):
        result={}
        for key,value in items:
            if key in result: raise ValueError()
            result[key]=value
        return result
    def number(token):
        n=Decimal(token)
        if not n.is_finite() or len(n.as_tuple().digits)>256 or abs(n.as_tuple().exponent)>1000: raise ValueError()
        return n
    def reject(_): raise ValueError()
    def scalar(value):
        if isinstance(value,str): value.encode('utf-8')
        elif isinstance(value,dict):
            for k,v in value.items(): scalar(k); scalar(v)
        elif isinstance(value,list):
            for v in value: scalar(v)
    try:
        result=json.loads(body.decode('utf-8'),parse_int=int,parse_float=number,
                          object_pairs_hook=pairs,parse_constant=reject)
        scalar(result)
        if not isinstance(result,dict): raise ValueError()
        return result
    except (ValueError,UnicodeError,RecursionError): raise FactsError('invalid_request') from None

def canonical(value):
    if hasattr(value,'model_dump'): value=value.model_dump(by_alias=True,exclude_unset=False)
    if value is None: return b'null'
    if value is True: return b'true'
    if value is False: return b'false'
    if isinstance(value,(int,Decimal)):
        d=Decimal(value)
        if not d.is_finite(): raise FactsError('invalid_request')
        if not d: return b'0'
        s=format(d,'f')
        if '.' in s: s=s.rstrip('0').rstrip('.')
        return s.encode('ascii')
    if isinstance(value,float): raise TypeError('pf-json forbids binary float')
    if isinstance(value,str):
        # JSON minimal escapes use lowercase unicode for all control characters.
        s='"'
        for c in value:
            if c in ('"','\\'): s+='\\'+c
            elif ord(c)<32: s+='\\u%04x'%ord(c)
            else: s+=c
        return (s+'"').encode('utf-8')
    if isinstance(value,list) or isinstance(value,tuple): return b'['+b','.join(canonical(v) for v in value)+b']'
    if isinstance(value,dict): return b'{'+b','.join(canonical(k)+b':'+canonical(value[k]) for k in sorted(value,key=lambda x:x.encode('utf-8')))+b'}'
    raise TypeError('unsupported canonical value')

def sha(value): return 'sha256:'+hashlib.sha256(value).hexdigest()
def digest(domain,value): return sha(b'plc-facts/v1\0'+domain.encode()+b'\0'+canonical(value))
def binary(value): return bytes.fromhex(value.removeprefix('sha256:'))
def text_digest(value): return 'sha256:'+value.hex()
def unpack(value): return strict_json(value)
