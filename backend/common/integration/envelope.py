"""严格信封、来源引用与上海时间规范化；纯函数，无数据库当前时间读取。"""
from datetime import datetime, timedelta, timezone
import re
import unicodedata
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator
from common.schema_base import to_camel
from common.integration.canonical import canonical_bytes

CONTRACT_VERSION = "aiis.business-integration/v1"
# 本合同固定东八区，不将历史 Shanghai DST/LMT 引入业务墙上时间。
BUSINESS_TIMEZONE = timezone(timedelta(hours=8), name="Asia/Shanghai")
_TIME = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})$")


def identifier(value, maximum=128):
    if not isinstance(value, str) or not 1 <= len(value) <= maximum or value.strip() != value:
        raise ValueError("invalid identifier")
    if any(unicodedata.category(c).startswith("C") for c in value):
        raise ValueError("invalid identifier")
    value.encode("utf-8", errors="strict")
    return value


def _time_parts(value):
    match = _TIME.fullmatch(value) if isinstance(value, str) else None
    if not match:
        raise ValueError("offset timestamp required")
    base, fraction, offset = match.groups()
    if offset != "Z" and (int(offset[1:3]) > 23 or int(offset[4:6]) > 59):
        raise ValueError("invalid offset")
    try:
        local = datetime.fromisoformat(base + offset.replace("Z", "+00:00")).astimezone(BUSINESS_TIMEZONE)
    except (ValueError, OverflowError):
        raise ValueError("invalid timestamp") from None
    if local.year < 1000:
        raise ValueError("timestamp outside storage domain")
    return local, fraction or ""


def source_time(value):
    local, fraction = _time_parts(value)
    if any(c != "0" for c in fraction[3:]):
        raise ValueError("nonzero submillisecond timestamp")
    return local.replace(microsecond=int((fraction + "000")[:3]) * 1000)


def shanghai_time(value):
    if value.tzinfo is None or value.utcoffset() is None or value.microsecond % 1000:
        raise ValueError("aware millisecond timestamp required")
    return value.astimezone(BUSINESS_TIMEZONE).isoformat(timespec="milliseconds")


def fact_time(value):
    """来源引用保留任意有效小数精度，不经 datetime 微秒截断。"""
    local, fraction = _time_parts(value)
    fraction = fraction.rstrip("0")
    return local.strftime("%Y-%m-%dT%H:%M:%S") + ("." + fraction if fraction else "") + "+08:00"


def validate_source_clock(value, database_now):
    """未来 Service 注入已确认的 DB 上海时钟；本函数不接数据库。"""
    shanghai_time(database_now)
    if value > database_now + timedelta(minutes=5):
        raise ValueError("source timestamp is too far in future")
    return value


class IntegrationSchema(BaseModel):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        schema = handler(core_schema)
        def strict_numbers(node):
            if isinstance(node, dict):
                alternatives = node.get("anyOf", [])
                if any(item.get("type") == "number" for item in alternatives) and any(item.get("type") == "string" for item in alternatives):
                    number = next(item for item in alternatives if item.get("type") == "number")
                    node.pop("anyOf")
                    node.update(number)
                if node.get("default", False) is None:
                    node.pop("default")
                for child in node.values():
                    strict_numbers(child)
            elif isinstance(node, list):
                for child in node:
                    strict_numbers(child)
        strict_numbers(schema)
        return schema

    model_config = ConfigDict(alias_generator=to_camel, validate_by_alias=True,
                             validate_by_name=False, extra="forbid")


Identifier = Annotated[str, BeforeValidator(identifier)]
SourceTime = Annotated[datetime, BeforeValidator(source_time)]
FactTime = Annotated[str, BeforeValidator(fact_time)]


class PlcFactRef(IntegrationSchema):
    kind: Literal["plc_fact"]
    instance_id: Identifier
    plc_id: Identifier
    sample_id: Identifier
    point_id: Identifier
    source_generation: Identifier = None
    config_revision: Identifier = None
    observed_at: FactTime = None


class ExternalEventRef(IntegrationSchema):
    kind: Literal["external_event"]
    source_id: Identifier
    source_event_id: Identifier
    observed_at: FactTime = None


DataT = TypeVar("DataT", bound=IntegrationSchema)


class IntegrationEnvelope(IntegrationSchema, Generic[DataT]):
    contract_version: Literal["aiis.business-integration/v1"]
    producer_id: Identifier
    event_id: Identifier
    mapping_id: Identifier
    mapping_revision: Identifier
    source_refs: list[Annotated[PlcFactRef | ExternalEventRef, Field(discriminator="kind")]] = Field(min_length=1, max_length=128)
    data: DataT

    @model_validator(mode="after")
    def unique_references(self):
        refs = [canonical_bytes(ref.model_dump(by_alias=True, exclude_unset=True)) for ref in self.source_refs]
        if len(set(refs)) != len(refs):
            raise ValueError("duplicate source reference")
        return self
