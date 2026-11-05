"""稳定回执 DTO 与重放输出；只描述已提交事实，不把解析或 flush 当作提交。"""
from typing import Annotated, Literal, Generic, TypeVar
from pydantic import Field, field_serializer, model_validator
from common.integration.envelope import IntegrationSchema, Identifier, SourceTime, CONTRACT_VERSION, shanghai_time
from common.integration.canonical import DIGEST_PROFILE, canonical_bytes

Digest = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
PositiveId = Annotated[int, Field(strict=True, gt=0)]


class IntegrationReceipt(IntegrationSchema):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema=super().__get_pydantic_json_schema__(core_schema,handler)
        schema["required"]=list(schema.get("properties",{}))
        for field in ("sourceTime","committedAt"):
            schema["properties"][field]["pattern"]=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+08:00$"
        return schema

    contract_version: Literal["aiis.business-integration/v1"] = CONTRACT_VERSION
    digest_profile: Literal["bi-json/v1"] = DIGEST_PROFILE
    producer_id: Identifier
    event_id: Identifier
    resource: Literal["temperature", "drive", "production_parameters", "production_observation",
                      "process_temperature", "process_tension", "process_speed", "process_curve"]
    equipment_id: Identifier
    mapping_id: Identifier
    mapping_revision: Identifier
    request_digest: Digest
    business_digest: Digest
    receipt_id: PositiveId
    record_id: PositiveId | None
    performance_id: PositiveId | None
    affected_record_ids: list[PositiveId]
    source_time: SourceTime
    committed_at: SourceTime
    status: Literal["committed"] = "committed"
    confirmation: Literal["business_committed", "decision_only"]
    applied: bool = Field(strict=True)
    outcome: Literal["created", "updated", "duplicate", "stale"]
    original_outcome: Literal["created", "updated", "duplicate", "stale"]
    changed_fields: list[str]
    business_retention: Literal["no_auto_ttl"] = "no_auto_ttl"

    @field_serializer("source_time", "committed_at")
    def format_time(self, value):
        return shanghai_time(value)

    @model_validator(mode="after")
    def decision_facts(self):
        if self.original_outcome == "stale" and (self.applied or self.record_id is not None or
                self.confirmation != "decision_only" or self.affected_record_ids):
            raise ValueError("stale is decision only")
        if self.original_outcome != "stale" and self.confirmation != "business_committed":
            raise ValueError("business receipt requires business confirmation")
        return self


def receipt_response(receipt, replay=False):
    """显式 JSON 键原样输出，不经全局 camelize；重放只改变 outcome。"""
    data = receipt.model_dump(by_alias=True)
    if replay:
        data["outcome"] = "duplicate"
    return canonical_bytes({"code": 200, "message": "success", "data": data})


ReceiptT = TypeVar("ReceiptT", bound=IntegrationReceipt)


class IntegrationSuccess(IntegrationSchema, Generic[ReceiptT]):
    code: Literal[200]
    message: Literal["success"]
    data: ReceiptT
