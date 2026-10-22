"""严格INT命令、物理资源身份、来源时效和稳定错误。"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json
import re
import time
import uuid


class Failure(Exception):
    """业务/集成稳定key；不带原报文、地址或凭据。"""


def require(condition, key):
    if not condition:
        raise Failure(key)


def now_ms():
    return time.time_ns() // 1_000_000


def identity():
    return uuid.uuid4().hex


def valid_id(value):
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,64}", value) is not None


def integer(value, low, high, key="input_schema"):
    require(type(value) is int and low <= value <= high, key)
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


@dataclass(frozen=True)
class Resource:
    host: str
    port: int
    rack: int
    slot: int
    db: int
    offset: int
    length: int = 2

    def overlaps(self, other):
        return ((self.host, self.port, self.rack, self.slot, self.db) ==
                (other.host, other.port, other.rack, other.slot, other.db) and
                self.offset < other.offset + other.length and other.offset < self.offset + self.length)


@dataclass(frozen=True)
class Intent:
    source_id: str
    command_id: str
    flow_id: str
    target: Resource
    config_identity_hash: str
    value: int
    issued_at_ms: int
    expires_at_ms: int
    input_max_age_ms: int

    def validate_time(self, wall=None):
        wall = now_ms() if wall is None else wall
        require(0 < self.expires_at_ms - self.issued_at_ms <= 60000 and
                self.issued_at_ms <= wall + 1000 and wall < self.expires_at_ms and
                wall - self.issued_at_ms <= self.input_max_age_ms, "input_stale")

    def deadline(self):
        return time.monotonic() + max(0, self.expires_at_ms - now_ms()) / 1000


class Clock:
    def __init__(self):
        self.wall, self.mono, self.invalid = now_ms(), time.monotonic(), False

    def check(self, wall=None):
        wall = now_ms() if wall is None else wall
        self.invalid |= abs(wall - self.wall - (time.monotonic() - self.mono) * 1000) > 1000
        require(not self.invalid, "clock_invalid")


def parse_input(body, flow, plc):
    fields = {"schema_version", "source_id", "ready", "command_id", "value", "issued_at_ms", "expires_at_ms"}
    require(type(body) is dict and set(body) == fields, "input_schema")
    require(type(body["schema_version"]) is int and body["schema_version"] == 1 and
            body["source_id"] == flow.source_id and type(body["ready"]) is bool, "input_schema")
    if not body["ready"]:
        require(all(body[k] is None for k in ("command_id", "value", "issued_at_ms", "expires_at_ms")), "input_schema")
        return None
    require(valid_id(body["command_id"]), "input_schema")
    integer(body["value"], -32768, 32767)
    for key in ("issued_at_ms", "expires_at_ms"):
        integer(body[key], -(2**63), 2**63-1)
    target = Resource(plc.host, plc.port, plc.rack, plc.slot, flow.target.db_number, flow.target.byte_offset)
    intent = Intent(body["source_id"], body["command_id"], flow.id, target,
                    digest({"flow": asdict(flow), "endpoint": asdict(target)}), body["value"],
                    body["issued_at_ms"], body["expires_at_ms"], flow.input_max_age_ms)
    intent.validate_time()
    return intent
