"""实绩HTTP域查询：设备、分页、业务状态与生产日期。"""
from datetime import date
from typing import Annotated, Literal
from pydantic import ConfigDict, BeforeValidator, Field
from common.schema_base import ApiSchema, to_camel
from app.performance.mapping_domain import identifier
class MappingQuery(ApiSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Annotated[str, BeforeValidator(identifier)]
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    coil_no: str | None = None
    grade: str | None = None
    observation_status: Literal["in_production", "not_in_production", "unknown"] | None = None
    start_date: date | None = None
    end_date: date | None = None
