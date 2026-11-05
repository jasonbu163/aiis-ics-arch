"""匿名集成 typed data；来源时间为上海毫秒，省略和零严格区分。"""
from decimal import Decimal
from datetime import datetime
from typing import Annotated, Literal
from pydantic import BeforeValidator, ConfigDict, model_validator
from common.schema_base import to_camel
from common.integration.envelope import IntegrationSchema, IntegrationEnvelope
from app.monitor.integration_domain import identifier, source_time, float_number, integer_number
from common.integration.receipt import IntegrationReceipt


class ProcessCurveData(IntegrationSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Annotated[str, BeforeValidator(identifier)]
    sampled_at: Annotated[datetime, BeforeValidator(source_time)]
    quality: Literal["good"]
    coil_number: Annotated[str, BeforeValidator(lambda v: identifier(v, 50))] = None
    line_speed_set: Annotated[Decimal, BeforeValidator(float_number)] = None
    line_speed_act: Annotated[Decimal, BeforeValidator(float_number)] = None
    unc_set_tension_p: Annotated[Decimal, BeforeValidator(float_number)] = None
    unc_act_tension_p: Annotated[Decimal, BeforeValidator(float_number)] = None
    rec_set_tension_p: Annotated[Decimal, BeforeValidator(float_number)] = None
    rec_act_tension_p: Annotated[Decimal, BeforeValidator(float_number)] = None
    unc_set_tension_kg: Annotated[Decimal, BeforeValidator(float_number)] = None
    rec_set_tension_kg: Annotated[Decimal, BeforeValidator(float_number)] = None
    furn_set_tension_kg: Annotated[Decimal, BeforeValidator(float_number)] = None
    furn_act_tension_kg: Annotated[Decimal, BeforeValidator(float_number)] = None
    cool_fan1_set_fre: Annotated[Decimal, BeforeValidator(float_number)] = None
    cool_fan1_act_fre: Annotated[Decimal, BeforeValidator(float_number)] = None
    cool_fan2_set_fre: Annotated[Decimal, BeforeValidator(float_number)] = None
    cool_fan2_act_fre: Annotated[Decimal, BeforeValidator(float_number)] = None
    n2_total: Annotated[Decimal, BeforeValidator(float_number)] = None
    elect_consum: Annotated[Decimal, BeforeValidator(float_number)] = None
    h2_flow: Annotated[Decimal, BeforeValidator(float_number)] = None
    n2_flow: Annotated[Decimal, BeforeValidator(float_number)] = None
    oxygen_content: Annotated[Decimal, BeforeValidator(float_number)] = None
    dew_point: Annotated[Decimal, BeforeValidator(float_number)] = None
    muffle_pressure: Annotated[Decimal, BeforeValidator(float_number)] = None
    z1_temp_set: Annotated[int, BeforeValidator(integer_number)] = None
    z1_temp_act: Annotated[int, BeforeValidator(integer_number)] = None
    z2_temp_set: Annotated[int, BeforeValidator(integer_number)] = None
    z2_temp_act: Annotated[int, BeforeValidator(integer_number)] = None
    z3_temp_set: Annotated[int, BeforeValidator(integer_number)] = None
    z3_temp_act: Annotated[int, BeforeValidator(integer_number)] = None
    z4_temp_set: Annotated[int, BeforeValidator(integer_number)] = None
    z4_temp_act: Annotated[int, BeforeValidator(integer_number)] = None
    z5_temp_set: Annotated[int, BeforeValidator(integer_number)] = None
    z5_temp_act: Annotated[int, BeforeValidator(integer_number)] = None
    z6_temp_set: Annotated[int, BeforeValidator(integer_number)] = None
    z6_temp_act: Annotated[int, BeforeValidator(integer_number)] = None

    @model_validator(mode="after")
    def measurements(self):
        if not self.model_fields_set.intersection(('line_speed_set', 'line_speed_act', 'unc_set_tension_p', 'unc_act_tension_p', 'rec_set_tension_p', 'rec_act_tension_p', 'unc_set_tension_kg', 'rec_set_tension_kg', 'furn_set_tension_kg', 'furn_act_tension_kg', 'cool_fan1_set_fre', 'cool_fan1_act_fre', 'cool_fan2_set_fre', 'cool_fan2_act_fre', 'n2_total', 'elect_consum', 'h2_flow', 'n2_flow', 'oxygen_content', 'dew_point', 'muffle_pressure', 'z1_temp_set', 'z1_temp_act', 'z2_temp_set', 'z2_temp_act', 'z3_temp_set', 'z3_temp_act', 'z4_temp_set', 'z4_temp_act', 'z5_temp_set', 'z5_temp_act', 'z6_temp_set', 'z6_temp_act')):
            raise ValueError("at least one measurement required")
        return self


ProcessCurveRequest = IntegrationEnvelope[ProcessCurveData]



class ProcessCurveReceipt(IntegrationReceipt):
    resource: Literal["process_curve"] = "process_curve"
    changed_fields: list[Literal['equipmentId', 'sampledAt', 'quality', 'coilNumber', 'lineSpeedSet', 'lineSpeedAct', 'uncSetTensionP', 'uncActTensionP', 'recSetTensionP', 'recActTensionP', 'uncSetTensionKg', 'recSetTensionKg', 'furnSetTensionKg', 'furnActTensionKg', 'coolFan1SetFre', 'coolFan1ActFre', 'coolFan2SetFre', 'coolFan2ActFre', 'n2Total', 'electConsum', 'h2Flow', 'n2Flow', 'oxygenContent', 'dewPoint', 'mufflePressure', 'z1TempSet', 'z1TempAct', 'z2TempSet', 'z2TempAct', 'z3TempSet', 'z3TempAct', 'z4TempSet', 'z4TempAct', 'z5TempSet', 'z5TempAct', 'z6TempSet', 'z6TempAct']]


# 每个operation的typed200及模块局部错误壳，不发布框架HTTPValidationError。
from pydantic import create_model
from common.integration.receipt import IntegrationSuccess

ProcessCurveSuccess = IntegrationSuccess[ProcessCurveReceipt]
Error403 = create_model("MonitorIntegrationError403", __base__=IntegrationSchema, code=(Literal[403], ...), message=(Literal['monitor.integration_scope_rejected'], ...), data=(type(None), ...), error_code=(Literal['monitor.integration_scope_rejected'], ...))
Error409 = create_model("MonitorIntegrationError409", __base__=IntegrationSchema, code=(Literal[409], ...), message=(Literal['monitor.integration_event_conflict', 'monitor.integration_value_conflict'], ...), data=(type(None), ...), error_code=(Literal['monitor.integration_event_conflict', 'monitor.integration_value_conflict'], ...))
Error413 = create_model("MonitorIntegrationError413", __base__=IntegrationSchema, code=(Literal[413], ...), message=(Literal['monitor.integration_payload_too_large'], ...), data=(type(None), ...), error_code=(Literal['monitor.integration_payload_too_large'], ...))
Error415 = create_model("MonitorIntegrationError415", __base__=IntegrationSchema, code=(Literal[415], ...), message=(Literal['monitor.integration_media_type'], ...), data=(type(None), ...), error_code=(Literal['monitor.integration_media_type'], ...))
Error422 = create_model("MonitorIntegrationError422", __base__=IntegrationSchema, code=(Literal[422], ...), message=(Literal['monitor.integration_invalid_request'], ...), data=(type(None), ...), error_code=(Literal['monitor.integration_invalid_request'], ...))
Error503 = create_model("MonitorIntegrationError503", __base__=IntegrationSchema, code=(Literal[503], ...), message=(Literal['monitor.integration_not_ready', 'monitor.integration_unavailable', 'monitor.integration_commit_unknown'], ...), data=(type(None), ...), error_code=(Literal['monitor.integration_not_ready', 'monitor.integration_unavailable', 'monitor.integration_commit_unknown'], ...))
Error500 = create_model("MonitorIntegrationError500", __base__=IntegrationSchema, code=(Literal[500], ...), message=(Literal['monitor.integration_internal_error'], ...), data=(type(None), ...), error_code=(Literal['monitor.integration_internal_error'], ...))

def error_responses(resource):
    responses = {403:{"model":Error403}, 409:{"model":Error409}, 413:{"model":Error413}, 415:{"model":Error415}, 422:{"model":Error422}, 503:{"model":Error503}, 500:{"model":Error500}}
    return responses

ProcessCurveData.model_config["json_schema_extra"] = {"anyOf":[{"required":[to_camel(field)]} for field in ('line_speed_set', 'line_speed_act', 'unc_set_tension_p', 'unc_act_tension_p', 'rec_set_tension_p', 'rec_act_tension_p', 'unc_set_tension_kg', 'rec_set_tension_kg', 'furn_set_tension_kg', 'furn_act_tension_kg', 'cool_fan1_set_fre', 'cool_fan1_act_fre', 'cool_fan2_set_fre', 'cool_fan2_act_fre', 'n2_total', 'elect_consum', 'h2_flow', 'n2_flow', 'oxygen_content', 'dew_point', 'muffle_pressure', 'z1_temp_set', 'z1_temp_act', 'z2_temp_set', 'z2_temp_act', 'z3_temp_set', 'z3_temp_act', 'z4_temp_set', 'z4_temp_act', 'z5_temp_set', 'z5_temp_act', 'z6_temp_set', 'z6_temp_act')], "x-missing-measurement":"omit; explicit null rejected; persisted SQL NULL", "x-post-merge-range":"validate complete min/avg/max ordering before any mutation"}


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

_NUMERIC_PROFILES={'ProcessCurveData': {'float': 'all-measurements', 'integers': {'z1TempSet': [-2147483648, 2147483647], 'z1TempAct': [-2147483648, 2147483647], 'z2TempSet': [-2147483648, 2147483647], 'z2TempAct': [-2147483648, 2147483647], 'z3TempSet': [-2147483648, 2147483647], 'z3TempAct': [-2147483648, 2147483647], 'z4TempSet': [-2147483648, 2147483647], 'z4TempAct': [-2147483648, 2147483647], 'z5TempSet': [-2147483648, 2147483647], 'z5TempAct': [-2147483648, 2147483647], 'z6TempSet': [-2147483648, 2147483647], 'z6TempAct': [-2147483648, 2147483647]}}}
def _numeric_callback(previous,profile):
    def update(schema):bounded_numeric_schema(schema,previous,profile)
    return update

for _name,_profile in _NUMERIC_PROFILES.items():
    _class=globals()[_name]
    _previous=_class.model_config.get("json_schema_extra")
    _class.model_config["json_schema_extra"]=_numeric_callback(_previous,_profile)
