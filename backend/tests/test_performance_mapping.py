"""HTTP人工重量与生产时间有效值边界；保持原人工权限入口。"""
from types import SimpleNamespace
from datetime import datetime
from decimal import Decimal
import pytest
from common.exceptions import BusinessException
from app.performance.services.async_performance import PerformanceService
from app.performance.services.async_production_observation import apply_duration
pytestmark=pytest.mark.no_db

@pytest.mark.asyncio
@pytest.mark.parametrize('payload',[{}, {'weight':None},{'weight':True},{'weight':'1'},{'weight':1,'grade':'A'},{'weight':Decimal('1.00001')},{'weight':-1}])
async def test_manual_http_weight_raw_validation_precedes_sql(payload):
    class NoSQL:
        async def execute(self,*args):raise AssertionError('validation must precede SQL')
    with pytest.raises(BusinessException) as error:await PerformanceService.update_mapping_weight(NoSQL(),1,'line-A',payload,1)
    assert error.value.code==422

def test_negative_reported_pair_rejected_even_with_valid_manual_pair():
    row=SimpleNamespace(start_time=datetime(2026,1,1),end_time=datetime(2026,1,2),reported_start_time=datetime(2026,2,2),reported_end_time=datetime(2026,2,1),first_observed_at=None,last_observed_at=None)
    with pytest.raises(BusinessException) as error:apply_duration(row)
    assert error.value.code==422
