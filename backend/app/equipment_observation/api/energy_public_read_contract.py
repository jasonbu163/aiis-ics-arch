"""公有能耗 GET 的 OpenAPI 回包。"""

_SAMPLE = {
    "type": "object", "additionalProperties": False,
    "required": ["meterId", "groupKey", "observedAt", "quality", "values"],
    "dependentRequired": {"intervalStartAt": ["intervalEndAt"], "intervalEndAt": ["intervalStartAt"]},
    "properties": {
        "meterId": {"type": "string"},
        "groupKey": {"type": "string"},
        "observedAt": {"type": "string", "format": "date-time"},
        "quality": {"enum": ["good", "bad", "unknown"]},
        "intervalStartAt": {"type": "string", "format": "date-time"},
        "intervalEndAt": {"type": "string", "format": "date-time"},
        "values": {"type": "object", "additionalProperties": {"type": "number"}},
    },
}


def _response(status, description, payload):
    data_key = "data" if status == 200 else "errorCode"
    fields = {"code": {"const": status}, "message": {"type": "string"}, "data": {"type": "null"}}
    fields[data_key] = payload
    return {"description": description, "content": {"application/json": {"schema": {
        "type": "object", "additionalProperties": False, "required": list(fields), "properties": fields,
    }}}}


def _contract(description, **paging):
    fields = {"items": {"type": "array", "items": _SAMPLE}, **paging}
    return {
        "200": _response(200, description, {"type": "object", "additionalProperties": False,
                                           "required": list(fields), "properties": fields}),
        "422": _response(422, "Invalid sample query", {"type": "string"}),
        "503": _response(503, "Energy data unavailable", {"const": "equipment_observation.not_ready"}),
    }


LATEST_ENERGY_READ = _contract("Latest stored sample for each matching meter and group")
ENERGY_HISTORY_READ = _contract(
    "Stored samples and pagination metadata",
    total={"type": "integer", "minimum": 0},
    page={"type": "integer", "minimum": 1},
    pageSize={"type": "integer", "minimum": 1, "maximum": 100},
    totalPages={"type": "integer", "minimum": 0},
)
