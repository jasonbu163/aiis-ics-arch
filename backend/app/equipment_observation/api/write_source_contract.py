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
