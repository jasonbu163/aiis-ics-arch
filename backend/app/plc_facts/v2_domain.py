"""v2 样本、时间和值域纯规则，不访问数据库或 HTTP。"""
import calendar
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum
import hashlib
import json
import re

from pydantic import ValidationError

from .schemas.v2 import SampleV2In

MAX_BODY = 512 * 1024
MAX_SEQUENCE = 9223372036854775806
REAL_OVERFLOW_MIDPOINT = (1 << 128) - (1 << 103)
TIME_PATTERN = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?\+08:00\Z')
STRING_PATTERN = re.compile(r'STRING\[([1-9][0-9]{0,2})\]\Z')
INTEGER_LIMITS = {
    'BYTE': (0, 255), 'USINT': (0, 255), 'INT': (-32768, 32767),
    'WORD': (0, 65535), 'UINT': (0, 65535),
    'DINT': (-2147483648, 2147483647),
    'DWORD': (0, 4294967295), 'UDINT': (0, 4294967295),
}
JSON_NUMBER = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z')


@dataclass(frozen=True)
class RealNumber:
    """保留 JSON 数字 token，避免浮点舍入和指数展开。"""
    token: str

    def __str__(self):
        return self.token


class V2ErrorCode(StrEnum):
    INVALID_CREDENTIAL = 'plc_facts.v2.invalid_credential'
    SCOPE_REJECTED = 'plc_facts.v2.scope_rejected'
    SAMPLE_CONTENT_CONFLICT = 'plc_facts.v2.sample_content_conflict'
    EXPIRED_UNCONFIRMED = 'plc_facts.v2.expired_unconfirmed'
    PAYLOAD_TOO_LARGE = 'plc_facts.v2.payload_too_large'
    MEDIA_TYPE = 'plc_facts.v2.media_type'
    INVALID_REQUEST = 'plc_facts.v2.invalid_request'
    NOT_READY = 'plc_facts.v2.not_ready'
    COMMIT_OUTCOME_UNKNOWN = 'plc_facts.v2.commit_outcome_unknown'
    NOT_FOUND = 'plc_facts.v2.not_found'


class V2Error(Exception):
    def __init__(self, key, status):
        self.internal_code = V2ErrorCode('plc_facts.v2.' + key)
        self.key = self.internal_code.value.replace('plc_facts.v2.', 'plc_facts_v2.', 1)
        self.status = status
        super().__init__(self.key)


def invalid():
    return V2Error('invalid_request', 422)


def identifier(value):
    if not isinstance(value, str) or not value or value.strip() != value:
        raise invalid()
    try:
        encoded = value.encode('utf-8')
    except UnicodeError:
        raise invalid() from None
    if len(encoded) > 128 or any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise invalid()
    return value


def text_field(value, limit, *, nonempty=False):
    if not isinstance(value, str):
        raise invalid()
    try:
        size = len(value.encode('utf-8'))
    except UnicodeError:
        raise invalid() from None
    if size > limit or (nonempty and not size):
        raise invalid()
    return value


def parse_time(value):
    if not isinstance(value, str) or not TIME_PATTERN.fullmatch(value):
        raise invalid()
    try:
        result = datetime.fromisoformat(value).replace(tzinfo=None)
        if result.year < 1000:
            raise ValueError()
        return result
    except (ValueError, OverflowError):
        raise invalid() from None


def expiry(observed):
    month = observed.month + 3
    year = observed.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    try:
        day = min(observed.day, calendar.monthrange(year, month)[1])
        return observed.replace(year=year, month=month, day=day) - timedelta(hours=24)
    except (ValueError, OverflowError):
        raise invalid() from None


def wire_time(value):
    return value.isoformat(timespec='microseconds') + '+08:00'


def finite_binary32(value):
    """按最近值舍入判断溢出，避免 binary64 二次舍入改变边界。"""
    if type(value) is int:
        return -REAL_OVERFLOW_MIDPOINT < value < REAL_OVERFLOW_MIDPOINT
    token = str(value)
    try:
        approximate = abs(float(token))
        if approximate != REAL_OVERFLOW_MIDPOINT:
            return approximate < REAL_OVERFLOW_MIDPOINT
        return Decimal(token).copy_abs() < REAL_OVERFLOW_MIDPOINT
    except (OverflowError, ValueError):
        return False


def validate_value(point):
    kind, value = point.data_type, point.value
    if kind in INTEGER_LIMITS:
        low, high = INTEGER_LIMITS[kind]
        valid = type(value) is int and low <= value <= high
    elif kind == 'BOOL':
        valid = type(value) is bool
    elif kind == 'REAL':
        valid = (type(value) is int or isinstance(value, RealNumber)) and finite_binary32(value)
    elif kind == 'CHAR':
        valid = isinstance(value, str) and len(value) == 1 and value.isascii()
    else:
        match = STRING_PATTERN.fullmatch(kind)
        valid = bool(match and int(match.group(1)) <= 254 and isinstance(value, str)
                     and value.isascii() and len(value) <= int(match.group(1)))
    if not valid:
        raise invalid()


def parse_sample(body):
    if len(body) > MAX_BODY:
        raise V2Error('payload_too_large', 413)
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result
    def reject_constant(_):
        raise ValueError('non-finite number')
    def integer(token):
        return RealNumber('-0') if token == '-0' else int(token)
    try:
        data = json.loads(body.decode('utf-8'), object_pairs_hook=unique_pairs, parse_constant=reject_constant,
                          parse_float=RealNumber, parse_int=integer)
        if isinstance(data, dict):
            if isinstance(data.get('dbNumber'), RealNumber) and data['dbNumber'].token == '-0':
                data['dbNumber'] = 0
            if isinstance(data.get('points'), list):
                for point in data['points']:
                    if (isinstance(point, dict) and isinstance(point.get('value'), RealNumber)
                            and point['value'].token == '-0' and point.get('dataType') != 'REAL'):
                        point['value'] = 0
        sample = SampleV2In.model_validate(data)
        for field in ('instance_id', 'sample_id', 'plc_id', 'source_generation'):
            identifier(getattr(sample, field))
        for field in ('group_id', 'config_revision'):
            if getattr(sample, field) is not None:
                identifier(getattr(sample, field))
        if not re.fullmatch(r'[1-9][0-9]*', sample.source_seq) or int(sample.source_seq) > MAX_SEQUENCE:
            raise invalid()
        seen = set()
        for raw, point in zip(data['points'], sample.points):
            identifier(point.point_id)
            if point.point_id in seen:
                raise invalid()
            seen.add(point.point_id)
            if 'name' in raw:
                text_field(point.name, 100)
            if point.quality == 'good':
                if point.reason is not None:
                    raise invalid()
                validate_value(point)
            else:
                if point.value is not None:
                    raise invalid()
                text_field(point.reason, 128, nonempty=True)
                # The type remains part of the fact even when the value is unavailable.
                probe = point.model_copy(update={'value': False if point.data_type == 'BOOL' else 0})
                if point.data_type == 'CHAR':
                    probe.value = 'x'
                elif STRING_PATTERN.fullmatch(point.data_type):
                    probe.value = ''
                validate_value(probe)
            expiry(parse_time(point.observed_at))
        return sample, data, hashlib.sha256(body).digest()
    except V2Error:
        raise
    except (ValueError, TypeError, UnicodeError, RecursionError, ValidationError, OverflowError):
        raise invalid() from None


def validate_times(sample, now):
    observed = [parse_time(point.observed_at) for point in sample.points]
    if any(value > now + timedelta(minutes=5) for value in observed):
        raise invalid()
    expires = [expiry(value) for value in observed]
    if min(expires) <= now:
        raise V2Error('expired_unconfirmed', 410)
    return observed, expires


def real_number(value):
    """校验内部数值文本，原样恢复 JSON number。"""
    if type(value) in (int, float, str, RealNumber):
        token = str(value)
    else:
        raise V2Error('not_ready', 503)
    if not JSON_NUMBER.fullmatch(token):
        raise V2Error('not_ready', 503)
    if not finite_binary32(value):
        raise V2Error('not_ready', 503)
    return RealNumber(token)


def stored_value(point):
    if point.data_type == 'REAL' and point.quality == 'good':
        return str(real_number(point.value))
    return point.value


def stored_points(points):
    result = []
    for point in points:
        item = dict(point)
        if item['dataType'] == 'REAL' and item['quality'] == 'good':
            item['value'] = str(real_number(item['value']))
        result.append(item)
    return result


def public_points(points):
    result = []
    for point in points:
        item = dict(point)
        if item.get('dataType') == 'REAL' and item.get('quality') == 'good':
            item['value'] = real_number(item.get('value'))
        result.append(item)
    return result


def json_bytes(value):
    """编码受控响应，REAL 用校验过的数字 token 输出。"""
    if isinstance(value, RealNumber):
        return str(real_number(value)).encode('ascii')
    if isinstance(value, dict):
        return b'{' + b','.join(json_bytes(key) + b':' + json_bytes(item) for key, item in value.items()) + b'}'
    if isinstance(value, (list, tuple)):
        return b'[' + b','.join(json_bytes(item) for item in value) + b']'
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')
