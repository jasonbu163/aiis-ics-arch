"""BE006严格原始数值/存在集合/时间合同，SQL无DB检查。"""
from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.performance.schemas.production_observation_in import ProductionObservationIn
from app.performance.schemas.process_sample_in import ProcessTemperatureIn,ProcessTensionIn,ProcessSpeedIn
from tests.mapping_fixtures import identity
pytestmark=pytest.mark.no_db

@pytest.mark.parametrize("cls,values",[(ProcessTemperatureIn,dict(minTemp=2,avgTemp=1)),(ProcessTensionIn,dict(minTension=1,maxTension=0)),(ProcessSpeedIn,dict(avgSpeed=2,maxSpeed=1)),(ProcessTemperatureIn,dict(duration=Decimal("1.1")))])
def test_process_ranges_and_integer_duration(cls,values):
    p=dict(equipmentId="line-A",sampleId="x",quality="good",recordTime="2026-10-16T10:00:00Z",coilNo="0",zone="Z",**values)
    with pytest.raises(ValidationError):cls.model_validate(p)
