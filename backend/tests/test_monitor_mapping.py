"""曲线来源日与设备查询输入无DB边界。"""
import pytest
from pydantic import ValidationError
from app.monitor.schemas.process_curve_query import ProcessCurveQuery
pytestmark=pytest.mark.no_db
@pytest.mark.parametrize('date',['20261016','2026-02-30','2026-10-16T00:00:00Z',123,None])
def test_curve_day_is_exact_calendar_date(date):
    with pytest.raises(ValidationError):ProcessCurveQuery.model_validate({'equipmentId':'line-A','date':date})
