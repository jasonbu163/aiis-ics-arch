"""完整温控样本的纯规范化规则；不依赖HTTP或数据库Session。"""
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import re
import unicodedata

TEMPERATURE_FIELDS = tuple(f"zone{zone}_{kind}" for zone in range(1, 6) for kind in ("set", "act"))
_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.(\d+))?(?:Z|[+-]\d{2}:\d{2})$")


def validate_identifier(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 128 or value != value.strip():
        raise ValueError("invalid identifier")
    if not value.strip() or any(unicodedata.category(c).startswith("C") for c in value):
        raise ValueError("invalid identifier")
    return value


def normalize_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("JSON number required")
    number = Decimal(str(value))
    if not number.is_finite() or number.copy_abs() >= Decimal("1e20"):
        raise ValueError("number outside storage domain")
    # 使用tuple检查小数尾数，避免Decimal默认context对大数normalize舍入。
    _, digits, exponent = number.as_tuple()
    trimmed = list(digits)
    while trimmed and trimmed[-1] == 0:
        trimmed.pop(); exponent += 1
    if trimmed and exponent < -10:
        raise ValueError("number exceeds storage scale")
    if number != number.to_integral_value() and Decimal(str(float(number))) != number:
        raise ValueError("number cannot round trip as JSON number")
    return Decimal(0) if number == 0 else number


def normalize_sampled_at(value):
    if not isinstance(value, str):
        raise ValueError("ISO8601 string required")
    match = _TIME.fullmatch(value)
    if not match or (match[1] and any(c != "0" for c in match[1][3:])):
        raise ValueError("timezone and exact milliseconds required")
    if not value.endswith("Z") and (int(value[-5:-3]) > 23 or int(value[-2:]) > 59):
        raise ValueError("invalid timezone offset")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise ValueError("invalid source time") from None
    if not 1000 <= result.year <= 9999:
        raise ValueError("time outside storage domain")
    return result.replace(tzinfo=None)


def utc_milliseconds(value):
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.isoformat(timespec="milliseconds") + "Z"


def canonical_number(value):
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if value == 0 else text


def fingerprint(sample):
    data = {"equipmentId": sample.equipment_id, "sampledAt": utc_milliseconds(sample.sampled_at),
            "quality": sample.quality, **{key: canonical_number(getattr(sample, key)) for key in TEMPERATURE_FIELDS}}
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def json_number(value):
    return int(value) if value == value.to_integral_value() else float(value)
