"""指标接入与展示使用的纯校验和事件身份规则。"""
from datetime import datetime
from common.integration.envelope import BUSINESS_TIMEZONE, identifier as core_identifier
import hashlib
import json
import math
import re

IDENTIFIER = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
TASK = re.compile(r"^[A-Z0-9_.-]{1,50}$")
SHANGHAI = BUSINESS_TIMEZONE


class ObservationError(Exception):
    def __init__(self, status, reason):
        self.status = status
        self.reason = reason
        super().__init__(reason)


def reject(reason="invalid_request", status=422):
    raise ObservationError(status, reason)


def identifier(value, limit=64):
    try:
        return core_identifier(value, limit)
    except (ValueError, TypeError, UnicodeError):
        reject()


def task_no(value):
    if not isinstance(value, str) or not value.isascii():
        reject("invalid_task")
    value = value.strip().upper()
    if not TASK.fullmatch(value):
        reject("invalid_task")
    return value


def sampled_time(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})", value
    ):
        reject("invalid_sampled_at")
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            reject("invalid_sampled_at")
        return stamp.astimezone(SHANGHAI).replace(tzinfo=None)
    except (ValueError, OverflowError):
        reject("invalid_sampled_at")


def wire_time(value):
    if value is None:
        return None
    return value.replace(tzinfo=SHANGHAI).isoformat(timespec="microseconds")


def scalar(value, kind):
    if kind == "number" and type(value) in (int, float):
        try:
            if math.isfinite(value) and (type(value) is not int or -(1 << 63) <= value < (1 << 64)):
                return value
        except OverflowError:
            pass
    if kind == "boolean" and type(value) is bool:
        return value
    if kind == "string" and isinstance(value, str) and len(value) <= 4096:
        return value
    reject("metric_type")


def canonical(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError):
        reject()


def digest(value):
    return hashlib.sha256(canonical(value)).digest()


def response(data):
    return {"code": 200, "message": "success", "data": data}
