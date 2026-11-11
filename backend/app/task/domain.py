"""通用任务字段、任务号、类型化值及时间的纯规则。"""
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
from zoneinfo import ZoneInfo
from app.task.errors import TaskError, TaskErrorCode

SHANGHAI = ZoneInfo('Asia/Shanghai')
IDENT = re.compile(r'^[A-Za-z0-9._-]{1,64}$')
TASK_NO = re.compile(r'^[A-Z0-9._-]{1,50}$')
FIELD_NAME = re.compile(r'^[a-z][A-Za-z0-9_]{0,63}$')


def invalid():
    raise TaskError(TaskErrorCode.INVALID_REQUEST, 422)


def task_number(value):
    if not isinstance(value, str) or not value.strip().isascii():
        invalid()
    result = value.strip().upper()
    if not TASK_NO.fullmatch(result):
        invalid()
    return result


def identifier(value):
    if not isinstance(value, str) or not IDENT.fullmatch(value):
        invalid()
    return value


def local_time(value):
    if value is None:
        return None
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        invalid()
    return value.astimezone(SHANGHAI).replace(tzinfo=None)


def wire_time(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=SHANGHAI)
    return value.astimezone(SHANGHAI).isoformat()


def encode_value(definition, value):
    if value is None:
        if not definition.is_nullable:
            invalid()
        return None
    kind = definition.value_type
    if kind == 'string':
        if not isinstance(value, str) or len(value) > 255:
            invalid()
        try:
            value.encode('utf-8')
        except UnicodeEncodeError:
            invalid()
        return value
    if kind == 'boolean':
        if type(value) is not bool:
            invalid()
        return 'true' if value else 'false'
    if kind == 'number':
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            invalid()
        try:
            number = Decimal(str(value))
            if not number.is_finite():
                invalid()
            text = format(number, 'f')
            whole, _, fraction = text.lstrip('-').partition('.')
            fraction = fraction.rstrip('0')
            if len(whole.lstrip('0') or '0') > 10 or len(fraction) > 4:
                invalid()
            result = (('-' if number < 0 else '') + (whole.lstrip('0') or '0') + ('.' + fraction if fraction else ''))
            return result
        except (InvalidOperation, ValueError):
            invalid()
    invalid()


def decode_value(definition, value):
    if definition.value_type == 'boolean':
        return value == 'true'
    if definition.value_type == 'number':
        number = Decimal(value)
        return int(number) if number == number.to_integral_value() else float(number)
    return value


def slot_key(number):
    return f'{number:02d}'


def value_patch(fields, incoming, scope, owner):
    if not isinstance(incoming, dict):
        invalid()
    lookup = {field.name: field for field in fields if field.scope == scope and field.enabled}
    result = {}
    for name, value in incoming.items():
        field = lookup.get(name)
        if field is None:
            invalid()
        allowed = ((owner == 'plan' and field.plan_editable and not field.sync_enabled)
                   or (owner == 'automated' and field.performance_owner == 'automated')
                   or (owner == 'manual' and field.performance_owner == 'manual' and field.performance_editable))
        if not allowed:
            raise TaskError(TaskErrorCode.FORBIDDEN, 403)
        result[slot_key(field.slot_no)] = encode_value(field, value)
    return result


def merge_values(current, changes):
    result = dict(current or {})
    for slot, value in changes.items():
        if value is None:
            result.pop(slot, None)
        else:
            result[slot] = value
    return result


def decode_values(fields, values, scope, visible=None):
    result = {}
    for field in fields:
        slot = slot_key(field.slot_no)
        if (field.scope == scope and field.enabled and slot in (values or {})
                and (visible is None or getattr(field, visible))):
            result[field.name] = decode_value(field, values[slot])
    return result
