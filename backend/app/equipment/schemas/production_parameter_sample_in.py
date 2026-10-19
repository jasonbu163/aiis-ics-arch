"""严格camelCase部分观测；省略为缺测，显式null拒绝。"""
from datetime import datetime
from typing import Annotated, Literal
from pydantic import BeforeValidator, ConfigDict, model_validator
from common.schema_base import ApiSchema, to_camel
from app.equipment.mapping_domain import identifier, source_time, float_number, observation_text

Identifier = Annotated[str, BeforeValidator(identifier)]
SourceTime = Annotated[datetime, BeforeValidator(source_time)]
Measurement = Annotated[float, BeforeValidator(float_number)]

class ProductionParameterSampleIn(ApiSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Identifier
    sample_id: Identifier
    sampled_at: SourceTime
    quality: Literal["good"]
    coil_no: Annotated[str, BeforeValidator(lambda v: identifier(v, 50))]
    grade: Annotated[str, BeforeValidator(lambda v: observation_text(v, 50))] = None
    entry_time: SourceTime = None
    thickness: Annotated[float, BeforeValidator(lambda v: float_number(v, nonnegative=True))] = None
    width: Annotated[float, BeforeValidator(lambda v: float_number(v, nonnegative=True))] = None
    total_time: Annotated[float, BeforeValidator(lambda v: float_number(v, nonnegative=True))] = None
    weight: Annotated[float, BeforeValidator(lambda v: float_number(v, nonnegative=True))] = None
    speed: Annotated[float, BeforeValidator(lambda v: float_number(v, nonnegative=True))] = None

    @model_validator(mode="after")
    def observed_fields(self):
        if not self.model_fields_set.intersection(('grade', 'entry_time', 'thickness', 'width', 'total_time', 'weight', 'speed')):
            raise ValueError("at least one observation required")
        return self
