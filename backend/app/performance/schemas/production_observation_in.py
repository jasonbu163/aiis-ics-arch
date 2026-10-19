"""生产观察严格输入；非在产不携带卷或观测字段。"""
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BeforeValidator, ConfigDict, model_validator
from common.schema_base import ApiSchema, to_camel
from app.performance.mapping_domain import identifier, source_time, decimal_number, integer_number, observation_text
Identifier = Annotated[str, BeforeValidator(identifier)]
BusinessKey = Annotated[str, BeforeValidator(lambda v: identifier(v, 50))]
SourceTime = Annotated[datetime, BeforeValidator(source_time)]
class SampleIdentity(ApiSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Identifier
    sample_id: Identifier
    quality: Literal["good"]

class ProductionObservationIn(SampleIdentity):
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
        if self.start_time is not None and self.end_time is not None and self.end_time < self.start_time:
            raise ValueError("negative production duration")
        return self
