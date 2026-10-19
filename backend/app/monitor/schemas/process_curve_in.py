"""逐样本曲线严格输入；十二INTEGER温度和二十一FLOAT观测。"""
from datetime import datetime
from typing import Annotated, Literal
from pydantic import BeforeValidator, ConfigDict, model_validator
from common.schema_base import ApiSchema, to_camel
from app.monitor.mapping_domain import identifier, source_time, float_number, integer_number
class ProcessCurveIn(ApiSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Annotated[str, BeforeValidator(identifier)]
    sample_id: Annotated[str, BeforeValidator(identifier)]
    sampled_at: Annotated[datetime, BeforeValidator(source_time)]
    quality: Literal["good"]
    coil_number: Annotated[str, BeforeValidator(lambda v: identifier(v, 50))] = None
    line_speed_set: Annotated[float, BeforeValidator(float_number)] = None
    line_speed_act: Annotated[float, BeforeValidator(float_number)] = None
    unc_set_tension_p: Annotated[float, BeforeValidator(float_number)] = None
    unc_act_tension_p: Annotated[float, BeforeValidator(float_number)] = None
    rec_set_tension_p: Annotated[float, BeforeValidator(float_number)] = None
    rec_act_tension_p: Annotated[float, BeforeValidator(float_number)] = None
    unc_set_tension_kg: Annotated[float, BeforeValidator(float_number)] = None
    rec_set_tension_kg: Annotated[float, BeforeValidator(float_number)] = None
    furn_set_tension_kg: Annotated[float, BeforeValidator(float_number)] = None
    furn_act_tension_kg: Annotated[float, BeforeValidator(float_number)] = None
    cool_fan1_set_fre: Annotated[float, BeforeValidator(float_number)] = None
    cool_fan1_act_fre: Annotated[float, BeforeValidator(float_number)] = None
    cool_fan2_set_fre: Annotated[float, BeforeValidator(float_number)] = None
    cool_fan2_act_fre: Annotated[float, BeforeValidator(float_number)] = None
    n2_total: Annotated[float, BeforeValidator(float_number)] = None
    elect_consum: Annotated[float, BeforeValidator(float_number)] = None
    h2_flow: Annotated[float, BeforeValidator(float_number)] = None
    n2_flow: Annotated[float, BeforeValidator(float_number)] = None
    oxygen_content: Annotated[float, BeforeValidator(float_number)] = None
    dew_point: Annotated[float, BeforeValidator(float_number)] = None
    muffle_pressure: Annotated[float, BeforeValidator(float_number)] = None
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
