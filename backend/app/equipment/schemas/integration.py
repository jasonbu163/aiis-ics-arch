"""匿名集成 typed data；来源时间为上海毫秒，省略和零严格区分。"""
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BeforeValidator, ConfigDict
from common.schema_base import to_camel
from common.integration.envelope import IntegrationSchema, IntegrationEnvelope
from app.equipment.integration_domain import decimal_number, source_time, identifier
from pydantic import BeforeValidator, ConfigDict, model_validator
from app.equipment.integration_domain import identifier, source_time, float_number
from app.equipment.integration_domain import identifier, source_time, float_number, observation_text
from common.integration.receipt import IntegrationReceipt


TemperatureNumber = Annotated[Decimal, BeforeValidator(lambda v: decimal_number(v, 30, 10))]


Identifier = Annotated[str, BeforeValidator(identifier)]


SourceTime = Annotated[datetime, BeforeValidator(source_time)]


class TemperatureData(IntegrationSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Identifier
    sampled_at: SourceTime
    quality: Literal["good"]
    zone1_set: TemperatureNumber
    zone1_act: TemperatureNumber
    zone2_set: TemperatureNumber
    zone2_act: TemperatureNumber
    zone3_set: TemperatureNumber
    zone3_act: TemperatureNumber
    zone4_set: TemperatureNumber
    zone4_act: TemperatureNumber
    zone5_set: TemperatureNumber
    zone5_act: TemperatureNumber


Measurement = Annotated[Decimal, BeforeValidator(float_number)]


class DriveData(IntegrationSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Identifier
    sampled_at: SourceTime
    quality: Literal["good"]
    tv: Measurement = None
    km: Measurement = None
    dew_point_set: Measurement = None
    dew_point_actual: Measurement = None
    oxygen: Measurement = None
    muffle_pressure: Measurement = None
    nh3_flow_set: Measurement = None
    nh3_flow_actual: Measurement = None
    ng_flow_set: Measurement = None
    ng_flow_actual: Measurement = None
    uncoiler_set: Measurement = None
    uncoiler_actual: Measurement = None
    entry_looper_set: Measurement = None
    entry_looper_actual: Measurement = None
    furnace_set: Measurement = None
    furnace_actual: Measurement = None
    exit_looper_set: Measurement = None
    exit_looper_actual: Measurement = None
    recoiler_set: Measurement = None
    recoiler_actual: Measurement = None

    @model_validator(mode="after")
    def observed_fields(self):
        if not self.model_fields_set.intersection(('tv', 'km', 'dew_point_set', 'dew_point_actual', 'oxygen', 'muffle_pressure', 'nh3_flow_set', 'nh3_flow_actual', 'ng_flow_set', 'ng_flow_actual', 'uncoiler_set', 'uncoiler_actual', 'entry_looper_set', 'entry_looper_actual', 'furnace_set', 'furnace_actual', 'exit_looper_set', 'exit_looper_actual', 'recoiler_set', 'recoiler_actual')):
            raise ValueError("at least one observation required")
        return self


class ProductionParameterData(IntegrationSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Identifier
    sampled_at: SourceTime
    quality: Literal["good"]
    coil_no: Annotated[str, BeforeValidator(lambda v: identifier(v, 50))]
    grade: Annotated[str, BeforeValidator(lambda v: observation_text(v, 50))] = None
    entry_time: SourceTime = None
    thickness: Annotated[Decimal, BeforeValidator(lambda v: float_number(v, nonnegative=True))] = None
    width: Annotated[Decimal, BeforeValidator(lambda v: float_number(v, nonnegative=True))] = None
    total_time: Annotated[Decimal, BeforeValidator(lambda v: float_number(v, nonnegative=True))] = None
    weight: Annotated[Decimal, BeforeValidator(lambda v: float_number(v, nonnegative=True))] = None
    speed: Annotated[Decimal, BeforeValidator(lambda v: float_number(v, nonnegative=True))] = None

    @model_validator(mode="after")
    def observed_fields(self):
        if not self.model_fields_set.intersection(('grade', 'entry_time', 'thickness', 'width', 'total_time', 'weight', 'speed')):
            raise ValueError("at least one observation required")
        return self


TemperatureRequest = IntegrationEnvelope[TemperatureData]


DriveRequest = IntegrationEnvelope[DriveData]


ProductionParameterRequest = IntegrationEnvelope[ProductionParameterData]



class TemperatureReceipt(IntegrationReceipt):
    resource: Literal["temperature"] = "temperature"
    changed_fields: list[Literal['equipmentId', 'sampledAt', 'quality', 'zone1Set', 'zone1Act', 'zone2Set', 'zone2Act', 'zone3Set', 'zone3Act', 'zone4Set', 'zone4Act', 'zone5Set', 'zone5Act']]


class DriveReceipt(IntegrationReceipt):
    resource: Literal["drive"] = "drive"
    changed_fields: list[Literal['equipmentId', 'sampledAt', 'quality', 'tv', 'km', 'dewPointSet', 'dewPointActual', 'oxygen', 'mufflePressure', 'nh3FlowSet', 'nh3FlowActual', 'ngFlowSet', 'ngFlowActual', 'uncoilerSet', 'uncoilerActual', 'entryLooperSet', 'entryLooperActual', 'furnaceSet', 'furnaceActual', 'exitLooperSet', 'exitLooperActual', 'recoilerSet', 'recoilerActual']]


class ProductionParameterReceipt(IntegrationReceipt):
    resource: Literal["production_parameters"] = "production_parameters"
    changed_fields: list[Literal['equipmentId', 'sampledAt', 'quality', 'coilNo', 'grade', 'entryTime', 'thickness', 'width', 'totalTime', 'weight', 'speed']]


# 每个operation的typed200及模块局部错误壳，不发布框架HTTPValidationError。
from pydantic import create_model
from common.integration.receipt import IntegrationSuccess

TemperatureSuccess = IntegrationSuccess[TemperatureReceipt]

DriveSuccess = IntegrationSuccess[DriveReceipt]

ProductionParameterSuccess = IntegrationSuccess[ProductionParameterReceipt]
Error403 = create_model("EquipmentIntegrationError403", __base__=IntegrationSchema, code=(Literal[403], ...), message=(Literal['equipment.integration_scope_rejected'], ...), data=(type(None), ...), error_code=(Literal['equipment.integration_scope_rejected'], ...))
Error409 = create_model("EquipmentIntegrationError409", __base__=IntegrationSchema, code=(Literal[409], ...), message=(Literal['equipment.integration_event_conflict', 'equipment.integration_value_conflict'], ...), data=(type(None), ...), error_code=(Literal['equipment.integration_event_conflict', 'equipment.integration_value_conflict'], ...))
Error413 = create_model("EquipmentIntegrationError413", __base__=IntegrationSchema, code=(Literal[413], ...), message=(Literal['equipment.integration_payload_too_large'], ...), data=(type(None), ...), error_code=(Literal['equipment.integration_payload_too_large'], ...))
Error415 = create_model("EquipmentIntegrationError415", __base__=IntegrationSchema, code=(Literal[415], ...), message=(Literal['equipment.integration_media_type'], ...), data=(type(None), ...), error_code=(Literal['equipment.integration_media_type'], ...))
Error422 = create_model("EquipmentIntegrationError422", __base__=IntegrationSchema, code=(Literal[422], ...), message=(Literal['equipment.integration_invalid_request'], ...), data=(type(None), ...), error_code=(Literal['equipment.integration_invalid_request'], ...))
Error503 = create_model("EquipmentIntegrationError503", __base__=IntegrationSchema, code=(Literal[503], ...), message=(Literal['equipment.integration_not_ready', 'equipment.integration_unavailable', 'equipment.integration_commit_unknown'], ...), data=(type(None), ...), error_code=(Literal['equipment.integration_not_ready', 'equipment.integration_unavailable', 'equipment.integration_commit_unknown'], ...))
Error500 = create_model("EquipmentIntegrationError500", __base__=IntegrationSchema, code=(Literal[500], ...), message=(Literal['equipment.integration_internal_error'], ...), data=(type(None), ...), error_code=(Literal['equipment.integration_internal_error'], ...))

def error_responses(resource):
    responses = {403:{"model":Error403}, 409:{"model":Error409}, 413:{"model":Error413}, 415:{"model":Error415}, 422:{"model":Error422}, 503:{"model":Error503}, 500:{"model":Error500}}
    return responses

DriveData.model_config["json_schema_extra"] = {"anyOf":[{"required":[to_camel(field)]} for field in ('tv', 'km', 'dew_point_set', 'dew_point_actual', 'oxygen', 'muffle_pressure', 'nh3_flow_set', 'nh3_flow_actual', 'ng_flow_set', 'ng_flow_actual', 'uncoiler_set', 'uncoiler_actual', 'entry_looper_set', 'entry_looper_actual', 'furnace_set', 'furnace_actual', 'exit_looper_set', 'exit_looper_actual', 'recoiler_set', 'recoiler_actual')], "x-missing-measurement":"omit; explicit null rejected; persisted SQL NULL", "x-post-merge-range":"validate complete min/avg/max ordering before any mutation"}

ProductionParameterData.model_config["json_schema_extra"] = {"anyOf":[{"required":[to_camel(field)]} for field in ('grade', 'entry_time', 'thickness', 'width', 'total_time', 'weight', 'speed')], "x-missing-measurement":"omit; explicit null rejected; persisted SQL NULL", "x-post-merge-range":"validate complete min/avg/max ordering before any mutation"}


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

_NUMERIC_PROFILES={'TemperatureData': {'decimal': {'precision': 30, 'scale': 10, 'nonnegative': False, 'fields': ['zone1Set', 'zone1Act', 'zone2Set', 'zone2Act', 'zone3Set', 'zone3Act', 'zone4Set', 'zone4Act', 'zone5Set', 'zone5Act']}, 'float': []}, 'DriveData': {'float': 'all-measurements'}, 'ProductionParameterData': {'float': ['thickness', 'width', 'totalTime', 'weight', 'speed'], 'nonnegative': True}}
def _numeric_callback(previous,profile):
    def update(schema):bounded_numeric_schema(schema,previous,profile)
    return update

for _name,_profile in _NUMERIC_PROFILES.items():
    _class=globals()[_name]
    _previous=_class.model_config.get("json_schema_extra")
    _class.model_config["json_schema_extra"]=_numeric_callback(_previous,_profile)
