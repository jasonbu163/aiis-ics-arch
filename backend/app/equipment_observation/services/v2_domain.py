"""来源无关的设备整包与能耗样本：严格时间、标量和原请求摘要。"""
from datetime import datetime
from decimal import Decimal
import hashlib
import math
import re

from common.integration.canonical import canonical_bytes
from ..domain import SHANGHAI, identifier, reject, task_no

_TIME = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})$")
_OUTER = {"contractVersion", "producerId", "eventId", "mappingId", "mappingRevision", "sourceRefs", "data"}


def observed_time(value):
    match = _TIME.fullmatch(value) if isinstance(value, str) else None
    if not match or match.group(2) and any(char != "0" for char in match.group(2)[6:]):
        reject("invalid_observed_at")
    fraction = (match.group(2) or "")[:6]
    text = match.group(1) + ("." + fraction if fraction else "") + match.group(3).replace("Z", "+00:00")
    try:
        value = datetime.fromisoformat(text).astimezone(SHANGHAI).replace(tzinfo=None)
        if value.year < 1000:
            reject("invalid_observed_at")
        return value
    except (ValueError, OverflowError):
        reject("invalid_observed_at")


def scalar(value, kind):
    if kind == "number" and type(value) in (int, float, Decimal):
        try:
            number = value if isinstance(value, Decimal) else Decimal(str(value))
            if not number.is_finite():
                reject("metric_type")
            if number == number.to_integral_value() and -(1 << 63) <= number < (1 << 64):
                return int(number)
            converted = float(number)
            if math.isfinite(converted) and Decimal(str(converted)) == number:
                return converted
        except (ValueError, OverflowError):
            pass
    elif kind == "boolean" and type(value) is bool:
        return value
    elif kind == "string" and isinstance(value, str) and len(value) <= 4096:
        return value
    reject("metric_type")


def _object(value, required, allowed):
    if not isinstance(value, dict) or not required.issubset(value) or not set(value).issubset(allowed):
        reject()


def _envelope(document, producer):
    _object(document, {"eventId", "data"}, _OUTER)
    if document.get("contractVersion", "aiis.metric-ingest/v2") != "aiis.metric-ingest/v2":
        reject("contract_version", 409)
    if document.get("producerId", producer["producerId"]) != producer["producerId"]:
        reject("forbidden", 403)
    event_id = identifier(document["eventId"], 128)
    if ("mappingId" in document) != ("mappingRevision" in document):
        reject()
    if "mappingId" in document:
        identifier(document["mappingId"])
        identifier(document["mappingRevision"], 32)
    if "sourceRefs" in document:
        refs = document["sourceRefs"]
        if not isinstance(refs, list) or len(refs) > 128 or any(not isinstance(ref, dict) for ref in refs):
            reject("source_refs")
        for ref in refs:
            if not isinstance(ref.get("kind"), str) or not ref["kind"] or len(ref["kind"]) > 128:
                reject("source_refs")
    try:
        request_digest = hashlib.sha256(canonical_bytes(document)).digest()
    except (ValueError, TypeError, UnicodeError):
        reject()
    return event_id, request_digest


def _quality(data, target):
    quality = data.get("quality")
    if quality is None and target != "history":
        quality = "unknown"
    if quality not in ("good", "bad", "unknown") or target == "history" and quality != "good":
        reject("quality")
    return quality


def device_event(document, producer, target):
    event_id, request_digest = _envelope(document, producer)
    data = document["data"]
    _object(data, {"equipmentId", "taskNo", "observedAt", "groups"},
            {"equipmentId", "taskNo", "observedAt", "groups", "quality"})
    equipment, task = identifier(data["equipmentId"]), task_no(data["taskNo"])
    observed = observed_time(data["observedAt"])
    groups = data["groups"]
    if not isinstance(groups, dict):
        reject("values")
    for group, values in groups.items():
        identifier(group)
        if not isinstance(values, dict) or len(values) > 100:
            reject("values")
        for key, value in values.items():
            identifier(key)
            if value is None or isinstance(value, (dict, list)):
                reject("values")
    return {"eventId": event_id, "requestDigest": request_digest, "equipmentId": equipment,
            "taskNo": task, "observedAt": observed, "quality": _quality(data, target), "groups": groups}


def energy_event(document, producer):
    event_id, request_digest = _envelope(document, producer)
    data = document["data"]
    _object(data, {"meterId", "groupKey", "observedAt", "values"},
            {"meterId", "groupKey", "observedAt", "values", "quality", "intervalStartAt", "intervalEndAt"})
    meter, group = identifier(data["meterId"]), identifier(data["groupKey"])
    values = data["values"]
    if not isinstance(values, dict) or not 1 <= len(values) <= 100:
        reject("values")
    for key, value in values.items():
        identifier(key)
        if value is None or isinstance(value, (dict, list)):
            reject("values")
    start = observed_time(data["intervalStartAt"]) if "intervalStartAt" in data else None
    end = observed_time(data["intervalEndAt"]) if "intervalEndAt" in data else None
    if (start is None) != (end is None) or start is not None and start >= end:
        reject("invalid_time_range")
    return {"eventId": event_id, "requestDigest": request_digest, "meterId": meter, "groupKey": group,
            "observedAt": observed_time(data["observedAt"]), "intervalStartAt": start, "intervalEndAt": end,
            "quality": _quality(data, "energy"), "values": values}
