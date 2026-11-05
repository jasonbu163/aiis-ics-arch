"""bi-json/v1：精确十进制 JSON、UTF-8 排序和两层摘要；不改变旧 serializer。"""
import hashlib
import json
import math
from datetime import datetime
from decimal import Decimal


DIGEST_PROFILE = "bi-json/v1"


def canonical_bytes(value):
    """只编码已验证的数据；FLOAT 调用方须先规范 binary32。"""
    if value is None:
        result = "null"
    elif isinstance(value, bool):
        result = "true" if value else "false"
    elif isinstance(value, (int, Decimal)):
        number = Decimal(value)
        if not number.is_finite() or len(number.as_tuple().digits) > 256 or abs(number.as_tuple().exponent) > 1000:
            raise ValueError("number outside canonical domain")
        result = "0" if number == 0 else format(number, "f")
        if "." in result:
            result = result.rstrip("0").rstrip(".")
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite number")
        return canonical_bytes(Decimal.from_float(value))
    elif isinstance(value, str):
        result = json.dumps(value, ensure_ascii=False)
    elif isinstance(value, datetime):
        from common.integration.envelope import shanghai_time
        return canonical_bytes(shanghai_time(value))
    elif isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("string keys required")
        return b"{" + b",".join(canonical_bytes(key) + b":" + canonical_bytes(value[key])
                                for key in sorted(value, key=lambda key: key.encode("utf-8"))) + b"}"
    elif isinstance(value, (list, tuple)):
        return b"[" + b",".join(canonical_bytes(item) for item in value) + b"]"
    else:
        raise ValueError("unsupported canonical type")
    return result.encode("utf-8", errors="strict")


def integration_digests(envelope, resource, parent_record_id=None):
    """字段存在集合由 exclude_unset 后的 data 键集表达；父 ID 永远在摘要内。"""
    data = envelope.model_dump(by_alias=True, exclude_unset=True)
    data["sourceRefs"] = sorted(data["sourceRefs"], key=canonical_bytes)
    data.update(resource=resource, parentRecordId=parent_record_id)
    business = {"resource": resource, "parentRecordId": parent_record_id, "data": data["data"]}
    digest = lambda value: "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()
    return digest(data), digest(business)
