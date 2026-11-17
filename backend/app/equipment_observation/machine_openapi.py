"""机器写入的 v2 OpenAPI 正文描述，运行时仍以原始 JSON 严格校验。"""
from copy import deepcopy

_KEY = {"type": "string", "minLength": 1, "maxLength": 64}
_TIME = {"type": "string", "format": "date-time", "description":
         "Original observed time, explicit offset required, losslessly storable in DATETIME(6); converted to Asia/Shanghai."}
_SCALAR = {"oneOf": [{"type": "number"}, {"type": "string", "maxLength": 4096}, {"type": "boolean"}]}
_VALUES = {"type": "object", "maxProperties": 100, "additionalProperties": _SCALAR}
_ENVELOPE = {
    "contractVersion": {"type": "string", "enum": ["aiis.metric-ingest/v2"], "default": "aiis.metric-ingest/v2"},
    "producerId": _KEY, "eventId": {"type": "string", "minLength": 1, "maxLength": 128},
    "mappingId": _KEY, "mappingRevision": {"type": "string", "minLength": 1, "maxLength": 32},
    "sourceRefs": {"type": "array", "maxItems": 128, "items": {"type": "object", "required": ["kind"],
                   "properties": {"kind": {"type": "string", "minLength": 1, "maxLength": 128}},
                   "additionalProperties": True}},
}
_QUALITY = {"type": ["string", "null"], "enum": ["good", "bad", "unknown", None]}
_DEVICE = {"type": "object", "required": ["equipmentId", "taskNo", "observedAt", "groups"],
           "additionalProperties": False, "properties": {"equipmentId": _KEY,
           "taskNo": {"type": "string", "minLength": 1, "maxLength": 50}, "observedAt": _TIME,
           "quality": _QUALITY, "groups": {"type": "object", "additionalProperties": _VALUES}}}
_ENERGY = {"type": "object", "required": ["meterId", "groupKey", "observedAt", "values"],
           "additionalProperties": False, "properties": {"meterId": _KEY, "groupKey": _KEY, "observedAt": _TIME,
           "quality": _QUALITY, "intervalStartAt": _TIME, "intervalEndAt": _TIME,
           "values": {"type": "object", "minProperties": 1, "maxProperties": 100,
                      "additionalProperties": {"type": "number"}}}}


def request_schema(target):
    data = deepcopy(_ENERGY if target == "energy" else _DEVICE)
    if target == "history":
        data["required"].append("quality")
        data["properties"]["quality"] = {"type": "string", "const": "good"}
    return {"type": "object", "additionalProperties": False, "required": ["eventId", "data"],
            "dependentRequired": {"mappingId": ["mappingRevision"], "mappingRevision": ["mappingId"]},
            "properties": {**deepcopy(_ENVELOPE), "data": data}}


def request_body(target):
    return {"requestBody": {"content": {"application/json": {"schema": request_schema(target)}}}}
