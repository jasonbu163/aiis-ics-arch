"""采集消费者标识、错误、摘要及租约请求头的稳定规则。"""
from dataclasses import dataclass
from hashlib import sha256
import json
import re
from uuid import NAMESPACE_URL, UUID, uuid5

from .v2_domain import MAX_SEQUENCE, V2Error, identifier

LEASE_ID_HEADER = 'X-Consumer-Lease-Id'
LEASE_GENERATION_HEADER = 'X-Consumer-Lease-Generation'
CONSUMER_ID_HEADER = 'X-Consumer-Id'
DELIVERY_ID_HEADER = 'X-Delivery-Id'


class ConsumerError(Exception):
    def __init__(self, key, status, data=None):
        self.status = status
        self.key = f'acquisition_consumer.{key}'
        self.data = data
        super().__init__(self.key)


def require_identifier(value):
    try:
        return identifier(value)
    except V2Error:
        raise ConsumerError('invalid_request', 422) from None


def consumer_uuid(value):
    if not isinstance(value, str) or len(value) != 36:
        raise ConsumerError('invalid_request', 422)
    try:
        if str(UUID(value)) == value:
            return value
    except ValueError:
        pass
    raise ConsumerError('invalid_request', 422)


def sequence(value):
    if not isinstance(value, str) or not re.fullmatch(r'[1-9][0-9]{0,18}', value):
        raise ConsumerError('invalid_request', 422)
    number = int(value)
    if number > MAX_SEQUENCE:
        raise ConsumerError('invalid_request', 422)
    return number


def delivery_id(consumer_id, event_seq):
    return str(uuid5(NAMESPACE_URL, f'aiis:acq-consumer:v1:{consumer_id}:{event_seq}'))


def fingerprint(operation, body):
    return sha256(json.dumps([operation, body.model_dump(by_alias=True)], sort_keys=True,
                             ensure_ascii=False, separators=(',', ':')).encode('utf-8')).digest()


@dataclass(frozen=True)
class Lease:
    identity: str | None
    generation: str | None

    def parsed(self):
        if self.identity is None or self.generation is None:
            raise ConsumerError('lease_required', 409)
        return consumer_uuid(self.identity), sequence(self.generation)


@dataclass(frozen=True)
class TargetWrite:
    authorization: str | None
    consumer_id: str | None
    delivery_id: str | None
    lease: Lease
    duplicate_headers: bool
