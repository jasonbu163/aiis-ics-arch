"""质量结果字段规范化及校验规则。"""
from decimal import Decimal, InvalidOperation
from enum import StrEnum
import re
import unicodedata
from urllib.parse import urlsplit


class QualityErrorCode(StrEnum):
    UNAUTHENTICATED = 'quality.unauthenticated'
    FORBIDDEN = 'quality.forbidden'
    NOT_FOUND = 'quality.not_found'
    TASK_NO_CONFLICT = 'quality.task_no_conflict'
    TARGET_CONFLICT = 'quality.target_conflict'
    CONFIG_REVISION_CONFLICT = 'quality.config_revision_conflict'
    INVALID_REQUEST = 'quality.invalid_request'
    UNAVAILABLE = 'quality.unavailable'
    COMMIT_UNKNOWN = 'quality.commit_unknown'


class QualityError(Exception):
    def __init__(self, code, status, *, field=None, reason=None):
        self.code = code
        self.status = status
        self.details = {k: v for k, v in {'field': field, 'reason': reason}.items() if v is not None}
        super().__init__(code.value)


def invalid(field, reason):
    raise QualityError(QualityErrorCode.INVALID_REQUEST, 422, field=field, reason=reason)


def normalize_task_no(value):
    if not isinstance(value, str):
        raise ValueError('invalid taskNo')
    value = value.strip()
    if not re.fullmatch(r'[A-Za-z0-9._-]{1,50}', value, re.ASCII):
        raise ValueError('invalid taskNo')
    return value.upper()


def validate_link(value):
    if not isinstance(value, str) or len(value) > 2048 or not value:
        raise ValueError('invalid URL length or type')
    if any(c.isspace() or c == '\\' or unicodedata.category(c).startswith('C') for c in value):
        raise ValueError('URL contains prohibited characters')
    try:
        target = urlsplit(value)
        if (target.scheme not in {'http', 'https'} or not target.hostname
                or target.username is not None or target.password is not None
                or '%' in target.netloc or target.port == 0):
            raise ValueError('expected an HTTP(S) URL with a hostname and without credentials')
    except ValueError:
        raise ValueError('invalid HTTP(S) URL') from None
    return value


def validate_items(supplied, definitions, *, human):
    enabled = {d['name']: d for d in definitions if d['enabled']}
    validated = {}
    for name, value in supplied.items():
        definition = enabled.get(name)
        field = f'items.{name}'
        if definition is None:
            invalid(field, 'unknown_or_disabled_field')
        if human and not definition['editable']:
            raise QualityError(QualityErrorCode.FORBIDDEN, 403, field=field, reason='field_not_editable')
        validated[name] = _validate_value(definition, value, field)
    return validated


def _validate_value(definition, value, field):
    if value is None:
        if not definition['isNullable']:
            invalid(field, 'field_not_nullable')
        return None
    kind = definition['type']
    if kind == 'number':
        if type(value) not in (int, float, Decimal):
            invalid(field, 'expected_number')
        try:
            number = Decimal(str(value))
            if not number.is_finite() or abs(number) >= 10**10 or number != number.quantize(Decimal('0.0001')):
                invalid(field, 'number_out_of_range')
        except (ValueError, InvalidOperation):
            invalid(field, 'number_out_of_range')
        return int(number) if number == number.to_integral_value() else float(number)
    if kind == 'boolean':
        if type(value) is not bool:
            invalid(field, 'expected_boolean')
        return value
    if kind == 'link':
        try:
            return validate_link(value)
        except ValueError:
            invalid(field, 'invalid_url')
    if not isinstance(value, str) or len(value) > 255:
        invalid(field, 'expected_string_up_to_255')
    try:
        value.encode('utf-8')
    except UnicodeError:
        invalid(field, 'invalid_unicode')
    return value


def validate_definitions(previous, definitions):
    current = {d['name']: d for d in definitions}
    if len(current) != len(definitions):
        invalid('definitions', 'duplicate_field_name')
    for existing in previous:
        name = existing['name']
        replacement = current.get(name)
        if replacement is None:
            invalid('definitions', 'defined_fields_cannot_be_removed')
        if any(existing.get(key) != replacement.get(key) for key in ('type', 'unit')):
            invalid('definitions', 'field_type_and_unit_are_immutable')
    return sorted(definitions, key=lambda d: (d['order'], d['name']))
