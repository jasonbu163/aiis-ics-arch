"""安全发布位置和签名/过滤/epoch/TTL边界，独立推演不替代B并发。"""
import pytest
from app.plc_facts.retention import instant
from app.plc_facts.cursors import issue,consume
from app.plc_facts.error_codes import FactsError
pytestmark=pytest.mark.no_db
NOW=instant('2026-11-04T10:00:00+08:00');KEY='ab'*32
@pytest.mark.parametrize('mode,ttl',[('changes',86400),('range',900),('latest',30)])
def test_ttl_and_binding(mode,ttl):
    token=issue(KEY,mode,'epoch','filter',[1,2],NOW)
    assert consume(token,KEY,mode,'epoch','filter',NOW.seconds(ttl-1))['after']==[1,2]
    with pytest.raises(FactsError) as exc:consume(token,KEY,mode,'epoch','filter',NOW.seconds(ttl))
    assert exc.value.code==410

@pytest.mark.parametrize('key,mode,epoch,filters',[('bc'*32,'changes','e','f'),(KEY,'range','e','f'),(KEY,'changes','other','f'),(KEY,'changes','e','other')])
def test_rebinding_and_rotation(key,mode,epoch,filters):
    token=issue(KEY,'changes','e','f',[5,2],NOW)
    with pytest.raises(FactsError) as exc:consume(token,key,mode,epoch,filters,NOW)
    assert exc.value.code==422

def test_floor_compares_ordinal_not_only_serial():
    token=issue(KEY,'changes','e','f',[5,2],NOW)
    assert consume(token,KEY,'changes','e','f',NOW,(5,2))
    with pytest.raises(FactsError) as exc:consume(token,KEY,'changes','e','f',NOW,(5,3))
    assert exc.value.error_code.value=='plc_facts.cursor_gap'

def test_independent_serial_gate_invariant():
    # raw IDs allocated outside the gate cannot determine the committed prefix.
    raw_ids={'T1':1,'T2':2};high=0;gate='T1'
    proposed={'T1':high+1};assert gate=='T1' and 'T2' not in proposed
    # rollback: uncommitted position can be reused; commit: all parts visible with H.
    gate=None;proposed.pop('T1');gate='T2';proposed['T2']=high+1
    assert proposed['T2']==1 and raw_ids['T2']==2
    high=proposed['T2'];published={(high,1),(high,2)}
    assert all(serial<=high for serial,_ in published)
