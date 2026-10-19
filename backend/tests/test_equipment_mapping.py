"""BE006严格原始数值/存在集合/时间合同，SQL无DB检查。"""
from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.equipment.schemas.drive_sample_in import DriveSampleIn
from app.equipment.schemas.production_parameter_sample_in import ProductionParameterSampleIn
from app.performance.schemas.production_observation_in import ProductionObservationIn
from app.performance.schemas.process_sample_in import ProcessTemperatureIn,ProcessTensionIn,ProcessSpeedIn
from app.monitor.schemas.process_curve_in import ProcessCurveIn
from app.equipment.mapping_domain import float_number,fingerprint
from tests.test_mapping_service import identity
pytestmark=pytest.mark.no_db

@pytest.mark.parametrize("value",[True,"1",None,float("inf"),float("nan"),Decimal("1e-100"),Decimal("1e-40"),Decimal("3.5e38")])
def test_float_rejects_unrepresentable_or_non_number(value):
    with pytest.raises(ValueError):float_number(value)

@pytest.mark.parametrize("value",[0,-0.0,Decimal("1.25"),Decimal("3.4028234663852886e38"),Decimal("1e-38")])
def test_float_bounded_storage(value):
    result=float_number(value)
    assert result==0 if value==0 else result!=0
    if value!=0:assert abs(Decimal(str(result))-Decimal(str(value)))<=abs(Decimal(str(value)))*Decimal("1e-6")

@pytest.mark.parametrize("change",[{"tv":None},{"tv":True},{"tv":"2"},{"tv":float("nan")},{"tv":1,"tv_set":1},{"tv":1,"sampleId":" x"},{"tv":1,"sampledAt":"2026-10-16T10:00:00.1234Z"},{"tv":1,"sampledAt":"2026-10-16T10:00:00"},{}])
def test_drive_strict_optional_observations(change):
    with pytest.raises(ValidationError):DriveSampleIn.model_validate(identity(**change))

def test_fingerprint_numeric_time_equivalence_and_presence():
    a=DriveSampleIn.model_validate(identity(tv=1));b=DriveSampleIn.model_validate(identity(tv=1.0))
    b.sampled_at=a.sampled_at
    assert fingerprint(a,"drive")==fingerprint(b,"drive")
    assert fingerprint(a,"drive")!=fingerprint(DriveSampleIn.model_validate(identity(tv=1,km=0)),"drive")

@pytest.mark.parametrize("cls,extra,bad",[
 (ProductionParameterSampleIn,dict(coilNo="A",width=0),dict(width=-1)),
 (ProductionParameterSampleIn,dict(coilNo="A",width=0),dict(processSteps=[])),
 (ProductionObservationIn,dict(coilNo="0",observationStatus="in_production"),dict(weight=Decimal("1.00001"))),
 (ProductionObservationIn,dict(coilNo="0",observationStatus="in_production"),dict(weight=1000000)),
 (ProductionObservationIn,dict(coilNo="0",observationStatus="in_production"),dict(qualityScore=1000)),
 (ProductionObservationIn,dict(observationStatus="unknown"),dict(weight=0)),
 (ProcessCurveIn,dict(z1TempSet=0),dict(z1TempSet=1.2)),
 (ProcessCurveIn,dict(z1TempSet=0),dict(z1TempSet=2147483648))])
def test_slice_storage_boundaries(cls,extra,bad):
    p=identity(**extra);cls.model_validate(p);p.update(bad)
    with pytest.raises(ValidationError):cls.model_validate(p)

@pytest.mark.parametrize("cls,values",[(ProcessTemperatureIn,dict(minTemp=2,avgTemp=1)),(ProcessTensionIn,dict(minTension=1,maxTension=0)),(ProcessSpeedIn,dict(avgSpeed=2,maxSpeed=1)),(ProcessTemperatureIn,dict(duration=Decimal("1.1")))])
def test_process_ranges_and_integer_duration(cls,values):
    p=dict(equipmentId="line-A",sampleId="x",quality="good",recordTime="2026-10-16T10:00:00Z",coilNo="0",zone="Z",**values)
    with pytest.raises(ValidationError):cls.model_validate(p)

@pytest.mark.parametrize('module,scope', [('equipment','EQUIPMENT_MAPPING_INGEST_ID'),('performance','PERFORMANCE_MAPPING_INGEST_ID'),('monitor','MONITOR_MAPPING_INGEST_ID')])
def test_local_scope_process_dotenv_and_per_application_cache(monkeypatch,tmp_path,module,scope):
    import importlib
    from types import SimpleNamespace
    from common.exceptions import BusinessException
    config=importlib.import_module('app.'+module+'.mapping_config')
    env=tmp_path/'public.env';env.write_text(scope+'=dotenv-line\n')
    monkeypatch.setattr(config,'resolve_env_file',lambda:env)
    monkeypatch.setenv(scope,'process-line')
    def request():return SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace()))
    a=request();first=config.get_mapping_config(a)
    assert first.allowed_equipment('process-line')=='process-line'
    monkeypatch.setenv(scope,'changed-line')
    assert config.get_mapping_config(a) is first
    assert config.get_mapping_config(request()).allowed_equipment('changed-line')=='changed-line'
    monkeypatch.delenv(scope)
    assert config.get_mapping_config(request()).allowed_equipment('dotenv-line')=='dotenv-line'
    empty=config.MappingConfig(**{scope:''},_env_file=None)
    with pytest.raises(BusinessException) as error:empty.allowed_equipment('dotenv-line')
    assert error.value.code==403


def test_observation_text_preserves_spaces_without_weakening_device_identity():
    p=identity(coilNo='A',grade=' Grade A ',width=0)
    assert ProductionParameterSampleIn.model_validate(p).grade==' Grade A '
    p=identity(coilNo='A',observationStatus='in_production',remark=' reported reason ')
    assert ProductionObservationIn.model_validate(p).remark==' reported reason '
    with pytest.raises(ValidationError):DriveSampleIn.model_validate(identity(equipmentId=' line-A ',tv=0))
