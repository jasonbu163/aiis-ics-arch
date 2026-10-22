"""无隐式转换的有限YAML配置；所有外部地址须显式提供。"""
from __future__ import annotations
from dataclasses import dataclass, fields, asdict
import ipaddress
from pathlib import Path
from urllib.parse import urlsplit
import yaml
from field_flow.domain import Failure, integer, require, valid_id, Resource


@dataclass(frozen=True)
class Plc:
    id: str
    host: str
    port: int
    rack: int
    slot: int
    connect_timeout_ms: int
    io_timeout_ms: int
    queue_capacity: int
    queue_wait_ms: int
    ready_wait_ms: int


@dataclass(frozen=True)
class Target:
    plc_id: str
    db_number: int
    db_size_bytes: int
    byte_offset: int
    type: str


@dataclass(frozen=True)
class Flow:
    id: str
    kind: str
    business_name: str
    interval_ms: int
    source_id: str
    get_url: str
    target: Target
    input_max_age_ms: int


@dataclass(frozen=True)
class Http:
    connect_timeout_ms: int
    total_timeout_ms: int
    pool_wait_ms: int
    max_connections: int
    max_body_bytes: int


@dataclass(frozen=True)
class Config:
    schema_version: int
    instance_id: str
    plcs: tuple[Plc, ...]
    flows: tuple[Flow, ...]
    http: Http
    shutdown_timeout_ms: int


def typed(cls, data):
    require(type(data) is dict and set(data) == {f.name for f in fields(cls)}, "config_schema")
    result = cls(**data)
    for f in fields(cls):
        if f.type == "int":
            require(type(getattr(result, f.name)) is int, "config_schema")
        if f.type == "str":
            require(type(getattr(result, f.name)) is str, "config_schema")
    return result


def parse(data):
    require(type(data) is dict, "config_schema")
    data = dict(data)
    require(type(data.get("plcs")) is list and type(data.get("flows")) is list, "config_schema")
    data["plcs"] = tuple(typed(Plc, p) for p in data["plcs"])
    require(all(type(f) is dict for f in data["flows"]), "config_schema")
    data["flows"] = tuple(typed(Flow, {**f, "target": typed(Target, f.get("target"))}) for f in data["flows"] if type(f) is dict)
    data["http"] = typed(Http, data.get("http"))
    c = typed(Config, data)
    require(c.schema_version == 1 and valid_id(c.instance_id) and 1 <= len(c.plcs) <= 4 and 1 <= len(c.flows) <= 8, "config_schema")
    ids, endpoints = set(), set()
    limits = {"connect_timeout_ms": (500, 3000), "io_timeout_ms": (500, 5000), "queue_capacity": (1, 16), "queue_wait_ms": (100, 5000), "ready_wait_ms": (100, 5000)}
    for p in c.plcs:
        require(valid_id(p.id) and p.id not in ids and (p.host, p.port) not in endpoints, "config_plc")
        try:
            require(str(ipaddress.IPv4Address(p.host)) == p.host, "config_plc")
        except ipaddress.AddressValueError:
            raise Failure("config_plc") from None
        ids.add(p.id); endpoints.add((p.host, p.port))
        for k, (low, high) in {**limits, "port": (1, 65535), "rack": (0, 7), "slot": (0, 31)}.items():
            integer(getattr(p, k), low, high, "config_range")
    ids, resources = set(), []
    for f in c.flows:
        require(valid_id(f.id) and f.id not in ids and valid_id(f.source_id) and valid_id(f.business_name) and f.kind == "demo01", "config_flow")
        ids.add(f.id)
        integer(f.interval_ms, 100, 10000, "config_range")
        integer(f.input_max_age_ms, 1, 60000, "config_range")
        url = urlsplit(f.get_url)
        require(url.scheme in ("http", "https") and url.hostname and not url.username and not url.password and not url.fragment, "config_url")
        p = next((p for p in c.plcs if p.id == f.target.plc_id), None)
        require(p is not None, "config_target")
        t = f.target
        integer(t.db_number, 1, 65535, "config_target"); integer(t.db_size_bytes, 2, 65536, "config_target"); integer(t.byte_offset, 0, 65534, "config_target")
        require(t.type == "INT" and t.byte_offset + 2 <= t.db_size_bytes, "config_target")
        r = Resource(p.host, p.port, p.rack, p.slot, t.db_number, t.byte_offset)
        require(not any(r.overlaps(old) for old in resources), "config_overlap"); resources.append(r)
    for k, (low, high) in {"connect_timeout_ms": (100, 1500), "total_timeout_ms": (100, 5000), "pool_wait_ms": (100, 1500), "max_connections": (1, 8), "max_body_bytes": (1, 4096)}.items():
        integer(getattr(c.http, k), low, high, "config_range")
    require(max(c.http.connect_timeout_ms, c.http.pool_wait_ms) <= c.http.total_timeout_ms, "config_http")
    integer(c.shutdown_timeout_ms, 5000, 20000, "config_range")
    require(c.shutdown_timeout_ms >= max([c.http.total_timeout_ms] + [max(p.connect_timeout_ms, p.io_timeout_ms) for p in c.plcs]) + 5500, "config_shutdown")
    return c


def load(path):
    try:
        raw = Path(path).read_bytes()
        require(len(raw) <= 65536, "config_size")
        return parse(yaml.safe_load(raw))
    except (OSError, yaml.YAMLError, TypeError, ValueError, AttributeError):
        raise Failure("config_schema") from None
