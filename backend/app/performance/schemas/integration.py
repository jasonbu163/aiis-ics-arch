"""匿名集成 typed data；来源时间为上海毫秒，省略和零严格区分。"""
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BeforeValidator, ConfigDict, model_validator
from common.schema_base import to_camel
from common.integration.envelope import IntegrationSchema, IntegrationEnvelope
from app.performance.integration_domain import identifier, source_time, decimal_number, integer_number, observation_text
from common.integration.receipt import IntegrationReceipt


Identifier = Annotated[str, BeforeValidator(identifier)]


BusinessKey = Annotated[str, BeforeValidator(lambda v: identifier(v, 50))]


SourceTime = Annotated[datetime, BeforeValidator(source_time)]


class SampleIdentity(IntegrationSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Identifier
    quality: Literal["good"]


class ProductionObservationData(SampleIdentity):
    sampled_at: SourceTime
    observation_status: Literal["in_production", "not_in_production", "unknown"]
    coil_no: BusinessKey | None = None
    grade: Annotated[str, BeforeValidator(lambda v: observation_text(v, 20))] = None
    weight: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 10, 4, True))] = None
    total_length: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 10, 2, True))] = None
    diameter: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 8, 2, True))] = None
    density: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 5, 3, True))] = None
    spec: Annotated[str, BeforeValidator(lambda v: observation_text(v, 50))] = None
    start_time: SourceTime = None
    end_time: SourceTime = None
    output_quantity: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 10, 4, True))] = None
    qualified_quantity: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 10, 4, True))] = None
    efficiency_rate: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 5, 2, True))] = None
    quality_score: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 5, 2, True))] = None
    remark: Annotated[str, BeforeValidator(lambda v: observation_text(v, 500))] = None

    @model_validator(mode="after")
    def production_fields(self):
        if self.observation_status == "in_production":
            if self.coil_no is None:
                raise ValueError("coilNo required")
        elif self.coil_no is not None or self.model_fields_set.intersection(('grade', 'weight', 'total_length', 'diameter', 'density', 'spec', 'start_time', 'end_time', 'output_quantity', 'qualified_quantity', 'efficiency_rate', 'quality_score', 'remark')):
            raise ValueError("inactive observation cannot carry production values")
        if self.start_time is not None and self.end_time is not None and not 0 <= (self.end_time - self.start_time).total_seconds() <= 2147483647:
            raise ValueError("negative production duration")
        return self


class ProcessIdentity(SampleIdentity):
    record_time: SourceTime
    coil_no: BusinessKey
    zone: BusinessKey


class ProcessTemperatureData(ProcessIdentity):
    set_temp: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 8, 2, False))] = None
    max_temp: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 8, 2, False))] = None
    min_temp: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 8, 2, False))] = None
    avg_temp: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 8, 2, False))] = None
    duration: Annotated[int, BeforeValidator(lambda v: integer_number(v, 0, 9999999999))] = None

    @model_validator(mode="after")
    def measurements(self):
        if not self.model_fields_set.intersection(('set_temp', 'max_temp', 'min_temp', 'avg_temp', 'duration')):
            raise ValueError("at least one observation required")
        if self.min_temp is not None and self.avg_temp is not None and self.min_temp > self.avg_temp:
            raise ValueError("measurement order invalid")
        if self.avg_temp is not None and self.max_temp is not None and self.avg_temp > self.max_temp:
            raise ValueError("measurement order invalid")
        if self.min_temp is not None and self.max_temp is not None and self.min_temp > self.max_temp:
            raise ValueError("measurement order invalid")
        return self


class ProcessTensionData(ProcessIdentity):
    set_tension: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 10, 2, True))] = None
    avg_tension: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 10, 2, True))] = None
    max_tension: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 10, 2, True))] = None
    min_tension: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 10, 2, True))] = None

    @model_validator(mode="after")
    def measurements(self):
        if not self.model_fields_set.intersection(('set_tension', 'avg_tension', 'max_tension', 'min_tension')):
            raise ValueError("at least one observation required")
        if self.min_tension is not None and self.avg_tension is not None and self.min_tension > self.avg_tension:
            raise ValueError("measurement order invalid")
        if self.avg_tension is not None and self.max_tension is not None and self.avg_tension > self.max_tension:
            raise ValueError("measurement order invalid")
        if self.min_tension is not None and self.max_tension is not None and self.min_tension > self.max_tension:
            raise ValueError("measurement order invalid")
        return self


class ProcessSpeedData(ProcessIdentity):
    set_speed: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 10, 2, True))] = None
    avg_speed: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 10, 2, True))] = None
    max_speed: Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 10, 2, True))] = None

    @model_validator(mode="after")
    def measurements(self):
        if not self.model_fields_set.intersection(('set_speed', 'avg_speed', 'max_speed')):
            raise ValueError("at least one observation required")
        if self.avg_speed is not None and self.max_speed is not None and self.avg_speed > self.max_speed:
            raise ValueError("measurement order invalid")
        return self


ProductionObservationRequest = IntegrationEnvelope[ProductionObservationData]


ProcessTemperatureRequest = IntegrationEnvelope[ProcessTemperatureData]


ProcessTensionRequest = IntegrationEnvelope[ProcessTensionData]


ProcessSpeedRequest = IntegrationEnvelope[ProcessSpeedData]



class ProductionObservationReceipt(IntegrationReceipt):
    resource: Literal["production_observation"] = "production_observation"
    changed_fields: list[Literal['sampledAt', 'observationStatus', 'coilNo', 'grade', 'weight', 'totalLength', 'diameter', 'density', 'spec', 'startTime', 'endTime', 'outputQuantity', 'qualifiedQuantity', 'efficiencyRate', 'qualityScore', 'remark']]


class ProcessTemperatureReceipt(IntegrationReceipt):
    resource: Literal["process_temperature"] = "process_temperature"
    changed_fields: list[Literal['setTemp', 'maxTemp', 'minTemp', 'avgTemp', 'duration']]


class ProcessTensionReceipt(IntegrationReceipt):
    resource: Literal["process_tension"] = "process_tension"
    changed_fields: list[Literal['setTension', 'avgTension', 'maxTension', 'minTension']]


class ProcessSpeedReceipt(IntegrationReceipt):
    resource: Literal["process_speed"] = "process_speed"
    changed_fields: list[Literal['setSpeed', 'avgSpeed', 'maxSpeed']]


# 每个operation的typed200及模块局部错误壳，不发布框架HTTPValidationError。
from pydantic import create_model
from common.integration.receipt import IntegrationSuccess

ProductionObservationSuccess = IntegrationSuccess[ProductionObservationReceipt]

ProcessTemperatureSuccess = IntegrationSuccess[ProcessTemperatureReceipt]

ProcessTensionSuccess = IntegrationSuccess[ProcessTensionReceipt]

ProcessSpeedSuccess = IntegrationSuccess[ProcessSpeedReceipt]
Error403 = create_model("PerformanceIntegrationError403", __base__=IntegrationSchema, code=(Literal[403], ...), message=(Literal['performance.integration_scope_rejected'], ...), data=(type(None), ...), error_code=(Literal['performance.integration_scope_rejected'], ...))
Error409 = create_model("PerformanceIntegrationError409", __base__=IntegrationSchema, code=(Literal[409], ...), message=(Literal["performance.integration_event_conflict", "performance.integration_value_conflict"], ...), data=(type(None), ...), error_code=(Literal["performance.integration_event_conflict", "performance.integration_value_conflict"], ...))
Error409Observation = create_model("PerformanceIntegrationError409Observation", __base__=IntegrationSchema, code=(Literal[409], ...), message=(Literal["performance.integration_event_conflict", "performance.integration_value_conflict", "performance.integration_observation_time_conflict"], ...), data=(type(None), ...), error_code=(Literal["performance.integration_event_conflict", "performance.integration_value_conflict", "performance.integration_observation_time_conflict"], ...))
Error409Process = create_model("PerformanceIntegrationError409Process", __base__=IntegrationSchema, code=(Literal[409], ...), message=(Literal["performance.integration_event_conflict", "performance.integration_value_conflict", "performance.integration_parent_mismatch"], ...), data=(type(None), ...), error_code=(Literal["performance.integration_event_conflict", "performance.integration_value_conflict", "performance.integration_parent_mismatch"], ...))
Error413 = create_model("PerformanceIntegrationError413", __base__=IntegrationSchema, code=(Literal[413], ...), message=(Literal['performance.integration_payload_too_large'], ...), data=(type(None), ...), error_code=(Literal['performance.integration_payload_too_large'], ...))
Error415 = create_model("PerformanceIntegrationError415", __base__=IntegrationSchema, code=(Literal[415], ...), message=(Literal['performance.integration_media_type'], ...), data=(type(None), ...), error_code=(Literal['performance.integration_media_type'], ...))
Error422 = create_model("PerformanceIntegrationError422", __base__=IntegrationSchema, code=(Literal[422], ...), message=(Literal['performance.integration_invalid_request'], ...), data=(type(None), ...), error_code=(Literal['performance.integration_invalid_request'], ...))
Error503 = create_model("PerformanceIntegrationError503", __base__=IntegrationSchema, code=(Literal[503], ...), message=(Literal['performance.integration_not_ready', 'performance.integration_unavailable', 'performance.integration_commit_unknown'], ...), data=(type(None), ...), error_code=(Literal['performance.integration_not_ready', 'performance.integration_unavailable', 'performance.integration_commit_unknown'], ...))
Error500 = create_model("PerformanceIntegrationError500", __base__=IntegrationSchema, code=(Literal[500], ...), message=(Literal['performance.integration_internal_error'], ...), data=(type(None), ...), error_code=(Literal['performance.integration_internal_error'], ...))
Error404 = create_model("PerformanceIntegrationError404", __base__=IntegrationSchema, code=(Literal[404], ...), message=(Literal["performance.integration_parent_not_found"], ...), data=(type(None), ...), error_code=(Literal["performance.integration_parent_not_found"], ...))

def error_responses(resource):
    responses = {403:{"model":Error403}, 409:{"model":Error409}, 413:{"model":Error413}, 415:{"model":Error415}, 422:{"model":Error422}, 503:{"model":Error503}, 500:{"model":Error500}}
    if resource.startswith("process_"):
        responses[404] = {"model":Error404}
        responses[409] = {"model":Error409Process}
    else:
        responses[409] = {"model":Error409Observation}
    return responses


def production_schema(schema):
    observed=("grade","weight","totalLength","diameter","density","spec","startTime","endTime","outputQuantity","qualifiedQuantity","efficiencyRate","qualityScore","remark")
    schema["oneOf"]=[
        {"properties":{"observationStatus":{"const":"in_production"},"coilNo":{"type":"string","minLength":1,"maxLength":50}},"required":["coilNo"]},
        {"properties":{"observationStatus":{"enum":["not_in_production","unknown"]},"coilNo":{"type":"null"}},
         "not":{"anyOf":[{"required":[field]} for field in observed]}}]
    schema["x-total-duration-seconds"]={"minimum":0,"maximum":2147483647,"priority":["manual_pair","reported_pair","observed_pair"]}
ProductionObservationData.model_config["json_schema_extra"]=production_schema

ProcessTemperatureData.model_config["json_schema_extra"] = {"anyOf":[{"required":[to_camel(field)]} for field in ('set_temp', 'max_temp', 'min_temp', 'avg_temp', 'duration')], "x-missing-measurement":"omit; explicit null rejected; persisted SQL NULL", "x-post-merge-range":"validate complete min/avg/max ordering before any mutation"}

ProcessTensionData.model_config["json_schema_extra"] = {"anyOf":[{"required":[to_camel(field)]} for field in ('set_tension', 'avg_tension', 'max_tension', 'min_tension')], "x-missing-measurement":"omit; explicit null rejected; persisted SQL NULL", "x-post-merge-range":"validate complete min/avg/max ordering before any mutation"}

ProcessSpeedData.model_config["json_schema_extra"] = {"anyOf":[{"required":[to_camel(field)]} for field in ('set_speed', 'avg_speed', 'max_speed')], "x-missing-measurement":"omit; explicit null rejected; persisted SQL NULL", "x-post-merge-range":"validate complete min/avg/max ordering before any mutation"}


# owner限定数值技术域；JSON number与省略缺测可被机器消费，数据库仍由Service校验实际值。
def bounded_numeric_schema(schema, previous, profile):
    if callable(previous):previous(schema)
    elif previous:schema.update(previous)
    groups=profile.get("groups",[])
    if "decimal" in profile:
        domain=profile["decimal"]
        groups=groups+[(domain["precision"],domain["scale"],domain["nonnegative"],domain["fields"])]
    properties=schema["properties"]
    for precision,scale,nonnegative,fields in groups:
        maximum=10**(precision-scale)
        for field in fields:
            prop=properties[field]
            prop.update(type="number",exclusiveMaximum=maximum,**({"minimum":0} if nonnegative else {"exclusiveMinimum":-maximum}))
            prop["x-decimal-storage"]={"precision":precision,"scale":scale,"rounding":"reject"}
    integers=profile.get("integers",{})
    for field,(low,high) in integers.items():
        properties[field].update(type="integer",minimum=low,maximum=high)
    floats=profile.get("float",[])
    if floats=="all-measurements":floats=[key for key,value in properties.items() if (value.get("type")=="number" or any(item.get("type")=="number" for item in value.get("anyOf",[]))) and key not in integers]
    for field in floats:
        properties[field].update(type="number",maximum=3.4028234663852886e38,**({"minimum":0} if profile.get("nonnegative") else {"minimum":-3.4028234663852886e38}))
        properties[field]["x-float-storage"]={"profile":"binary32","relativeTolerance":0.000001,"nonzeroUnderflow":"reject","digest":"exact decimal of normalized binary32"}

_NUMERIC_PROFILES={'ProductionObservationData': {'groups': [(10, 4, True, ['weight', 'outputQuantity', 'qualifiedQuantity']), (10, 2, True, ['totalLength']), (8, 2, True, ['diameter']), (5, 3, True, ['density']), (5, 2, True, ['efficiencyRate', 'qualityScore'])]}, 'ProcessTemperatureData': {'groups': [(8, 2, False, ['setTemp', 'maxTemp', 'minTemp', 'avgTemp'])], 'integers': {'duration': [0, 9999999999]}}, 'ProcessTensionData': {'groups': [(10, 2, True, ['setTension', 'avgTension', 'maxTension', 'minTension'])]}, 'ProcessSpeedData': {'groups': [(10, 2, True, ['setSpeed', 'avgSpeed', 'maxSpeed'])]}}
def _numeric_callback(previous,profile):
    def update(schema):bounded_numeric_schema(schema,previous,profile)
    return update

for _name,_profile in _NUMERIC_PROFILES.items():
    _class=globals()[_name]
    _previous=_class.model_config.get("json_schema_extra")
    _class.model_config["json_schema_extra"]=_numeric_callback(_previous,_profile)
