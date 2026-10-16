"""新温控读面查询；SQL下推limit并在recordId前约束设备。"""
from typing import Annotated
from pydantic import ConfigDict, Field
from common.schema_base import ApiSchema, to_camel
from app.equipment.schemas.temperature_sample_in import Identifier


class TemperatureSampleQuery(ApiSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Identifier | None = None
    record_id: Annotated[int | None, Field(gt=0)] = None
    limit: Annotated[int, Field(ge=1, le=1000)] = 100
