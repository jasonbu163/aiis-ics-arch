"""登记管理输入与匿名写入的 OpenAPI 请求形状。"""
from typing import Annotated

from pydantic import Field

from ..schemas import Input

SOURCE_PATTERN = r"^[A-Za-z0-9_.-]{1,64}$"
SourceKey = Annotated[str, Field(pattern=SOURCE_PATTERN, min_length=1, max_length=64)]
Name = Annotated[str, Field(min_length=1, max_length=128)]


class CreateWriteSource(Input):
    source_key: SourceKey
    name: Name | None = None
    enabled: bool = True


class PatchWriteSource(Input):
    name: Name | None = None
    enabled: bool | None = None


WRITE_REQUEST = {
    "requestBody": {"required": True, "content": {"application/json": {"schema": {
        "type": "object", "additionalProperties": False,
        "required": ["sourceKey", "target", "taskNo", "observedAt", "items"],
        "properties": {
            "sourceKey": {"type": "string", "pattern": SOURCE_PATTERN},
            "target": {"enum": ["latest", "history"]},
            "taskNo": {"type": "string"},
            "observedAt": {"type": "string", "format": "date-time"},
            "items": {"type": "object", "minProperties": 1, "additionalProperties": {
                "type": "object",
                "additionalProperties": {"type": ["number", "boolean", "string"]},
            }},
        },
    }}}},
}


_ENERGY_GROUP = {
    "type": "object", "required": ["values"], "additionalProperties": False,
    "properties": {
        "values": {"type": "object", "minProperties": 1, "additionalProperties": {"type": "number"}},
        "quality": {"enum": ["good", "bad", "unknown", None]},
        "intervalStartAt": {"type": "string", "format": "date-time"},
        "intervalEndAt": {"type": "string", "format": "date-time"},
    },
}

ENERGY_WRITE_REQUEST = {
    "requestBody": {"required": True, "content": {"application/json": {"schema": {
        "type": "object", "additionalProperties": False,
        "required": ["sourceKey", "target", "observedAt", "items"],
        "properties": {
            "sourceKey": {"type": "string", "pattern": SOURCE_PATTERN},
            "target": {"const": "energy"},
            "observedAt": {"type": "string", "format": "date-time"},
            "items": {"type": "object", "minProperties": 1, "additionalProperties": {
                "type": "object", "minProperties": 1, "additionalProperties": _ENERGY_GROUP,
            }},
        },
    }}}},
}

_ENERGY_RECEIPT = {
    "type": "object", "required": ["sourceKey", "target", "observedAt", "outcome", "receiptId", "records"],
    "properties": {
        "sourceKey": {"type": "string", "pattern": SOURCE_PATTERN},
        "target": {"const": "energy"}, "observedAt": {"type": "string", "format": "date-time"},
        "outcome": {"const": "stored"}, "receiptId": {"type": "string"},
        "records": {"type": "array", "minItems": 1, "items": {
            "type": "object", "required": ["meterId", "groupKey", "recordId"],
            "properties": {key: {"type": "string"} for key in ("meterId", "groupKey", "recordId")},
        }},
    },
}

ENERGY_WRITE_REQUEST["responses"] = {
    "200": {"description": "Stored or replayed batch", "content": {"application/json": {"schema": {
        "type": "object", "required": ["code", "message", "data"],
        "properties": {"code": {"const": 200}, "message": {"type": "string"}, "data": _ENERGY_RECEIPT},
    }}}},
    **{status: {"description": description, "content": {"application/json": {"schema": {
        "type": "object", "required": ["code", "message", "data", "errorCode"],
        "properties": {"code": {"const": int(status)}, "message": {"type": "string"},
                       "data": {"type": "null"}, "errorCode": {"type": "string"}},
    }}}} for status, description in (
        ("403", "Source not enabled"), ("409", "Batch identity conflict"), ("413", "Payload too large"),
        ("415", "Unsupported media type"), ("422", "Invalid batch"), ("503", "Unavailable or commit unknown"),
    )},
}
