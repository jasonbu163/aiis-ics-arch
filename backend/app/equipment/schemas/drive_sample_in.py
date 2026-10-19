"""严格camelCase部分观测；省略为缺测，显式null拒绝。"""
from datetime import datetime
from typing import Annotated, Literal
from pydantic import BeforeValidator, ConfigDict, model_validator
from common.schema_base import ApiSchema, to_camel
from app.equipment.mapping_domain import identifier, source_time, float_number

Identifier = Annotated[str, BeforeValidator(identifier)]
SourceTime = Annotated[datetime, BeforeValidator(source_time)]
Measurement = Annotated[float, BeforeValidator(float_number)]

class DriveSampleIn(ApiSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Identifier
    sample_id: Identifier
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
