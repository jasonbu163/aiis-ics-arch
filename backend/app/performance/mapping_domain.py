"""HTTP映射纯规则：精确身份、UTC毫秒、存储数值及存在集合；无DB/HTTP依赖。"""
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import re
import struct
import unicodedata

_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.(\d+))?(?:Z|[+-]\d{2}:\d{2})$")

def identifier(value, maximum=128):
    if not isinstance(value, str) or not 1 <= len(value) <= maximum or value != value.strip():
        raise ValueError("invalid identifier")
    if any(unicodedata.category(c).startswith("C") for c in value):
        raise ValueError("invalid identifier")
    return value

def source_time(value):
    if not isinstance(value, str):
        raise ValueError("source ISO time required")
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

def utc_time(value):
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.isoformat(timespec="milliseconds") + "Z"

def decimal_number(value, precision, scale, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("JSON number required")
    number = Decimal(str(value))
    if not number.is_finite() or abs(number) >= Decimal(10) ** (precision-scale) or (nonnegative and number < 0):
        raise ValueError("number outside storage domain")
    _, digits, exponent = number.as_tuple()
    digits = list(digits)
    while digits and digits[-1] == 0:
        digits.pop(); exponent += 1
    if digits and exponent < -scale:
        raise ValueError("number exceeds storage scale")
    if number != number.to_integral_value() and Decimal(str(float(number))) != number:
        raise ValueError("number cannot round trip as JSON")
    return Decimal(0) if number == 0 else number

def float_number(value, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("JSON number required")
    number = Decimal(str(value))
    if not number.is_finite() or abs(number) > Decimal("3.4028234663852886e38") or (nonnegative and number < 0):
        raise ValueError("number outside FLOAT domain")
    try:
        stored = struct.unpack("!f", struct.pack("!f", float(number)))[0]
    except (OverflowError, struct.error):
        raise ValueError("number outside FLOAT domain") from None
    difference = abs(Decimal(str(stored)) - number)
    if (number != 0 and (stored == 0 or difference > abs(number)*Decimal("0.000001"))) or difference > max(Decimal("0.000001"), abs(number)*Decimal("0.000001")):
        raise ValueError("FLOAT cannot preserve measurement")
    return 0.0 if stored == 0 else stored

def integer_number(value, low=-2147483648, high=2147483647):
    number = decimal_number(value, 20, 0)
    if not low <= number <= high:
        raise ValueError("integer outside storage domain")
    return int(number)

def canonical(value):
    if isinstance(value, datetime):
        return utc_time(value)
    if isinstance(value, Decimal):
        text = format(value, "f")
        return "0" if value == 0 else text.rstrip("0").rstrip(".") if "." in text else text
    return value

def fingerprint(sample, stream, **keys):
    fields = {key: canonical(getattr(sample, key)) for key in sorted(sample.model_fields_set) if key != "sample_id"}
    fields.update(stream=stream, **keys)
    return hashlib.sha256(json.dumps(fields, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def json_number(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    return value


def observation_text(value, maximum):
    """普通观测文案仅限长度与非空白，保留来源空格，不套用设备身份规则。"""
    if not isinstance(value,str) or not 1 <= len(value) <= maximum or not value.strip():
        raise ValueError("invalid observation text")
    try:
        value.encode("utf-8")
    except UnicodeError:
        raise ValueError("invalid observation text") from None
    return value
