"""三类父实绩过程输入，禁止自动创建父及NULL测量。"""
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BeforeValidator, ConfigDict, model_validator
from common.schema_base import ApiSchema, to_camel
from app.performance.mapping_domain import identifier, source_time, decimal_number, integer_number
Identifier = Annotated[str, BeforeValidator(identifier)]
BusinessKey = Annotated[str, BeforeValidator(lambda v: identifier(v, 50))]
SourceTime = Annotated[datetime, BeforeValidator(source_time)]
class SampleIdentity(ApiSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Identifier
    sample_id: Identifier
    quality: Literal["good"]

class ProcessIdentity(SampleIdentity):
    record_time: SourceTime
    coil_no: BusinessKey
    zone: BusinessKey

class ProcessTemperatureIn(ProcessIdentity):
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

class ProcessTensionIn(ProcessIdentity):
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

class ProcessSpeedIn(ProcessIdentity):
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
