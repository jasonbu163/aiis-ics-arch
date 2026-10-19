"""设备HTTP域精确查询；设备必填且SQL实际限制。"""
from typing import Annotated
from pydantic import ConfigDict, BeforeValidator, Field
from common.schema_base import ApiSchema, to_camel
from app.equipment.mapping_domain import identifier
class MappingSampleQuery(ApiSchema):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True, validate_by_name=False, extra="forbid")
    equipment_id: Annotated[str, BeforeValidator(identifier)]
    record_id: int | None = Field(None, gt=0)
    limit: int = Field(100, ge=1, le=1000)
