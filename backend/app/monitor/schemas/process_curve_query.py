"""上海自然日曲线查询，设备必填。"""
from datetime import date
import re
from pydantic import ConfigDict, Field, field_validator
from app.monitor.mapping_domain import identifier
from common.schema_base import ApiSchema, to_camel
class ProcessCurveQuery(ApiSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: str
    date: date
    record_id: int | None = Field(None, gt=0)
    limit: int = Field(1000, ge=1, le=1000)
    @field_validator("date", mode="before")
    @classmethod
    def day(cls, value):
        if not isinstance(value,str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}",value):
            raise ValueError("date must be YYYY-MM-DD")
        return value
    @field_validator("equipment_id")
    @classmethod
    def equipment(cls, value):
        return identifier(value)
