"""通用任务字段、任务号、类型化值及时间的纯规则。"""
from datetime import datetime
from decimal import Context, Decimal, InvalidOperation
import re
from app.task.errors import TaskError, TaskErrorCode
from common.integration.envelope import BUSINESS_TIMEZONE

IDENT = re.compile(r'^[A-Za-z0-9._-]{1,64}$')
TASK_NO = re.compile(r'^[A-Z0-9._-]{1,50}$')
FIELD_NAME = re.compile(r'^[a-z][A-Za-z0-9_]{0,63}$')


def invalid(field=None, reason='invalid_value'):
    raise TaskError(TaskErrorCode.INVALID_REQUEST, 422, field=field, reason=reason)


def task_number(value):
    if not isinstance(value, str) or not value.strip().isascii():
        invalid('taskNo', 'invalid_identifier')
    result = value.strip().upper()
    if not TASK_NO.fullmatch(result):
        invalid('taskNo', 'invalid_identifier')
    return result


def identifier(value, field=None):
    if not isinstance(value, str) or not IDENT.fullmatch(value):
        invalid(field, 'invalid_identifier')
    return value


def local_time(value, field=None):
    if value is None:
        return None
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        invalid(field, 'invalid_time')
    try:
        result = value.astimezone(BUSINESS_TIMEZONE).replace(tzinfo=None)
    except (OverflowError, ValueError):
        invalid(field, 'invalid_time')
    if result.year < 1000:
        invalid(field, 'time_out_of_range')
    return result


def wire_time(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=BUSINESS_TIMEZONE)
    return value.astimezone(BUSINESS_TIMEZONE).isoformat()


def encode_value(definition, value, path=None):
    if value is None:
        if not definition.is_nullable:
            invalid(path, 'null_not_allowed')
        return None
    kind = definition.value_type
    if kind == 'string':
        if not isinstance(value, str):
            invalid(path, 'type_mismatch')
        if len(value) > 255:
            invalid(path, 'length_limit')
        try:
            value.encode('utf-8')
        except UnicodeEncodeError:
            invalid(path, 'invalid_unicode')
        return value
    if kind == 'boolean':
        if type(value) is not bool:
            invalid(path, 'type_mismatch')
        return 'true' if value else 'false'
    if kind == 'number':
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            invalid(path, 'type_mismatch')
        try:
            number = Decimal(str(value)) if isinstance(value, float) else Decimal(value)
            if not number.is_finite():
                invalid(path, 'number_out_of_range')
            if not number:
                return '0'
            if not -4 <= number.adjusted() <= 9:
                invalid(path, 'number_out_of_range')
            exact = number.quantize(Decimal('0.0001'), context=Context(prec=15))
            if exact != number:
                invalid(path, 'number_out_of_range')
            return format(exact, 'f').rstrip('0').rstrip('.')
        except (InvalidOperation, ValueError):
            invalid(path, 'number_out_of_range')
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


def item_patch(fields, incoming, module, writer):
    lookup = {field.name: field for field in fields if field.scope in ('shared_sync', module + '_local')}
    shared, local = {}, {}
    for name, value in (incoming or {}).items():
        if not FIELD_NAME.fullmatch(name):
            invalid('items', 'invalid_field_name')
        field = lookup.get(name)
        path = f'items.{name}'
        if field is None:
            invalid(path, 'unknown_field')
        if not field.enabled:
            invalid(path, 'disabled_field')
        if module == 'plan':
            allowed = writer == 'integration' or field.plan_editable
        elif writer == 'integration':
            allowed = field.performance_owner == 'automated'
        else:
            allowed = field.performance_owner == 'manual' and field.performance_editable
        if not allowed:
            raise TaskError(TaskErrorCode.FORBIDDEN, 403, field=path, reason='field_owner')
        patch = shared if field.scope == 'shared_sync' else local
        patch[slot_key(field.slot_no)] = encode_value(field, value, path)
    return shared, local


def merge_values(current, changes):
    result = dict(current or {})
    for slot, value in changes.items():
        if value is None:
            result.pop(slot, None)
        else:
            result[slot] = value
    return result


def record_items(fields, row, module):
    result = {}
    for field in fields:
        if not field.enabled or field.scope not in ('shared_sync', module + '_local'):
            continue
        values = row.sync_values if field.scope == 'shared_sync' else row.local_values
        value = (values or {}).get(slot_key(field.slot_no))
        result[field.name] = None if value is None else decode_value(field, value)
    return result


def business_now():
    return datetime.now(BUSINESS_TIMEZONE).replace(tzinfo=None)


def matching_target(payload, row, other, *, inherit=False):
    requested = payload.get('targetKey')
    if requested is not None:
        identifier(requested, 'targetKey')
    if payload.get('producerId') is not None:
        identifier(payload['producerId'], 'producerId')
    here = row.target_key if row is not None else None
    there = other.target_key if other is not None else None
    if len({value for value in (here, there, requested) if value is not None}) > 1:
        raise TaskError(TaskErrorCode.TARGET_CONFLICT, 409, field='targetKey', reason='known_target_mismatch')
    if row is None and inherit and requested is None:
        return there
    return here if requested is None else requested


def apply_changes(row, patch, now):
    changed = False
    for name, value in patch.items():
        if getattr(row, name) != value:
            setattr(row, name, value)
            changed = True
    if changed:
        row.updated_at = now
    return changed


def base_wire(row, items):
    return {'id': str(row.id), 'taskNo': row.task_no, 'targetKey': row.target_key,
            'productionStatus': row.production_status, 'remark': row.remark,
            'createdAt': wire_time(row.created_at), 'updatedAt': wire_time(row.updated_at),
            'items': items}
