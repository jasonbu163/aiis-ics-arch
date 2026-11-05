"""严格原材料/数据类型/完整固定片验证，无DB。"""
from decimal import Decimal
import copy
import pytest
from app.plc_facts.source import prepare,validate,value_check,context_definitions
from app.plc_facts.schemas.source import PointFact
from app.plc_facts.canonical import strict_json
from app.plc_facts.error_codes import FactsError
from test_plc_facts_contract import sample,vectors
pytestmark=pytest.mark.no_db

@pytest.mark.parametrize('body,status',[(b'{"a":1,"a":2}',422),(b'{"a":NaN}',422),(b'{"a":Infinity}',422),(b'\xef\xbb\xbf{}',422),(b'{"x":"\\ud800"}',422),(b'\xff',422),(b'[]',422),(b'{"x":'+b'['*20+b'0'+b']'*20+b'}',413)])
def test_strict_json(body,status):
    with pytest.raises(FactsError) as exc: strict_json(body)
    assert exc.value.code==status

@pytest.mark.parametrize('name',('twoPlcsSameDb','onePlcTwoDbsTwoGroups','fragmented','partialFragment'))
def test_independently_frozen_shapes(name):
    p=prepare(vectors()['fixtures'][name])
    assert p.parts
    if name=='twoPlcsSameDb': assert len({x.payload.plc_id for x in p.parts})==2
    if name=='onePlcTwoDbsTwoGroups': assert {x.payload.db_number for x in p.parts}=={1,2}
    if name=='fragmented': assert len(p.parts)>1
    if name=='partialFragment': assert len(p.parts)==1 and len(next(iter(p.cycles.values())).expected)>1

@pytest.mark.parametrize('field,value', [('extra',1),('batch_id','snake'),('sourceProfile','v3'),('parent',{}),('batchCreatedAt','2026-11-04T10:00:00'),('batchCreatedAt','2026-11-04T10:00:00.0000000001+08:00')])
def test_outer_invalid(field,value):
    b=sample();b[field]=value
    with pytest.raises(FactsError): prepare(b)

@pytest.mark.parametrize('kind,value,ok',[
('BOOL',True,True),('BOOL',1,False),('INT',-32768,True),('INT',32768,False),('INT',True,False),('BYTE',255,True),('BYTE',-1,False),('UINT',65535,True),('UINT',65536,False),('DINT',-2147483648,True),('UDINT',4294967295,True),('UDINT',4294967296,False),('REAL',Decimal('1.00000000000000001'),True),('REAL',Decimal('1e-46'),False),('REAL',Decimal('4e38'),False),('CHAR','\x00',True),('CHAR','中',False),('STRING[3]','   ',True),('STRING[3]','four',False),('UNKNOWN',1,False)])
def test_values(kind,value,ok):
    fact=strict_json(sample()['samples'][0]['payloadUtf8'])['points']['point_x']
    fact['definition']['dataType']=kind;fact['value']=value
    if kind=='BOOL': fact['definition']['address']['bit']=0
    point=validate(PointFact,fact)
    if ok: value_check(point)
    else:
        with pytest.raises(FactsError): value_check(point)

@pytest.mark.parametrize('value,reason,typ,ok',[(None,'read_failed','INT',True),(0,'read_failed','INT',False),(None,None,'INT',False),(None,'unsupported_type','X',True),(None,'read_failed','X',False)])
def test_bad_has_no_value(value,reason,typ,ok):
    fact=strict_json(sample()['samples'][0]['payloadUtf8'])['points']['point_x'];fact.update(value=value,reason=reason,quality='bad');fact['definition']['dataType']=typ
    p=validate(PointFact,fact)
    if ok:value_check(p)
    else:
        with pytest.raises(FactsError):value_check(p)

def test_original_whitespace_cannot_keep_source_hash():
    b=sample();b['samples'][0]['payloadUtf8']=' '+b['samples'][0]['payloadUtf8']
    with pytest.raises(FactsError) as exc:prepare(b)
    assert exc.value.error_code.value=='plc_facts.digest_mismatch'


@pytest.mark.parametrize('precision',[7,28,100])
@pytest.mark.parametrize('text,accepted',[
    ('3.4028234663852886e38',True),('-3.4028234663852886e38',True),
    ('3.402823466385288599999999999999999999999e38',True),('-3.402823466385288599999999999999999999999e38',True),
    ('3.402823466385288600000000000000000000001e38',False),('-3.402823466385288600000000000000000000001e38',False),
    ('1.401298464324817e-45',True),('-1.401298464324817e-45',True),
    ('1.401298464324817000000000000000000000001e-45',True),('-1.401298464324817000000000000000000000001e-45',True),
    ('1.401298464324816999999999999999999999999e-45',False),('-1.401298464324816999999999999999999999999e-45',False),
    ('0',True),('-0.0',True),
])
def test_real_limits_are_exact_under_each_decimal_context(precision,text,accepted):
    from decimal import localcontext
    from app.plc_facts.canonical import canonical
    fact=strict_json(sample()['samples'][0]['payloadUtf8'])['points']['point_x']
    fact['definition']['dataType']='REAL'
    fact['value']=strict_json('{"number":'+text+'}')['number']
    # Compare independently without rounding or arithmetic under the tested context.
    magnitude=Decimal(text).copy_abs()
    assert accepted==(magnitude==0 or Decimal('1.401298464324817e-45')<=magnitude<=Decimal('3.4028234663852886e38'))
    with localcontext() as context:
        context.prec=precision
        point=validate(PointFact,fact)
        if accepted:value_check(point)
        else:
            with pytest.raises(FactsError) as exc:value_check(point)
            assert exc.value.error_code.value=='plc_facts.invalid_request' and exc.value.code==422
        encoded=canonical({'value':point.value})
        assert strict_json(encoded)['value']==Decimal(text)
        assert canonical({'number':Decimal('1.0000000000000000000000000000000000001')})==b'{"number":1.0000000000000000000000000000000000001}'
