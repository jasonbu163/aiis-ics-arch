"""自然月、offset、纳秒及独立过期边界，无DB。"""
import pytest
from app.plc_facts.retention import instant,expiry,proof_expiry
from app.plc_facts.error_codes import FactsError
pytestmark=pytest.mark.no_db

@pytest.mark.parametrize('source,months,expected',[
('2026-11-30T23:59:59.123456789+08:00',3,'2027-02-28T23:59:59.123456789+08:00'),
('2023-11-30T10:00:00+08:00',3,'2024-02-29T10:00:00.000000000+08:00'),
('2024-01-31T10:00:00+08:00',1,'2024-02-29T10:00:00.000000000+08:00'),
('2026-11-04T02:00:00.000000001Z',3,'2027-02-04T10:00:00.000000001+08:00')])
def test_calendar_months(source,months,expected):assert expiry(source,months).wire()==expected

@pytest.mark.parametrize('invalid',['2026-01-01T00:00:00','2026-01-01T00:00:60Z','0999-01-01T00:00:00+08:00','2026-01-01T00:00:00.0000000000Z','2026-02-30T00:00:00Z'])
def test_invalid_time(invalid):
    with pytest.raises(FactsError):instant(invalid)

def test_equal_cutoff_nanoseconds_and_fixed_120_days():
    end=expiry('2026-11-04T10:00:00.123456789+08:00',3)
    assert instant('2027-02-04T10:00:00.123456788+08:00')<end
    assert not end<end
    start=instant('2026-11-04T10:00:00+08:00')
    assert (proof_expiry(start).wall-start.wall).days==120
    assert (start.months(3).wall-start.wall).days!=90
