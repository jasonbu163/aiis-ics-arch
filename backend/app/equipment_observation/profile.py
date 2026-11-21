"""独立业务机器身份及设备范围，私有 profile 默认关闭。"""
from functools import lru_cache
import hashlib
import hmac
import json
from pathlib import Path
import re
from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict
from settings import resolve_env_file
from common.integration.envelope import identifier as core_identifier
from .domain import ObservationError

WRITE_SOURCES_REVISION = "e9f3b5d7c021"
REVISIONS = (WRITE_SOURCES_REVISION,)


def valid_identifier(value, limit=64):
    try:
        core_identifier(value, limit)
        return True
    except (ValueError, TypeError, UnicodeError):
        return False



class ObservationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=resolve_env_file(), extra="ignore")
    OBSERVATION_ENABLED: bool = False
    OBSERVATION_PROFILE_FILE: str = ""


def parse_profile(document):
    required_top = {"target", "devices", "readScopes", "producers", "historyRules", "groupSettings"}
    if (not isinstance(document, dict) or not required_top.issubset(document)
            or not set(document).issubset(required_top | {"meters", "meterReadScopes"})):
        raise ValueError("invalid profile")
    target = document["target"]
    if (not isinstance(target, dict) or set(target) != {"serverUuid", "schema", "schemaRevision"}
            or target["schemaRevision"] not in REVISIONS or not isinstance(target["serverUuid"], str)
            or str(UUID(target["serverUuid"])) != target["serverUuid"]
            or not valid_identifier(target["schema"])):
        raise ValueError("invalid target")
    devices = {}
    identity = {"equipmentId", "nameZh", "nameEn"}
    legacy = {"plcId", "dbNumber", "taskPointId", "idleValue", "maxTaskAgeSeconds"}
    timings = {"staleAfterSeconds", "futureToleranceSeconds"}
    if not isinstance(document["devices"], list):
        raise ValueError("invalid devices")
    for entry in document["devices"]:
        if (not isinstance(entry, dict) or not identity.issubset(entry)
                or not set(entry).issubset(identity | legacy | timings)
                or bool(set(entry) & legacy) and not legacy.issubset(entry)
                or bool(set(entry) & timings) and not timings.issubset(entry)):
            raise ValueError("invalid device")
        if (not valid_identifier(entry["equipmentId"])
                or any(not isinstance(entry[k], str) or not 1 <= len(entry[k]) <= 128 for k in ("nameZh", "nameEn"))
                or entry["equipmentId"] in devices):
            raise ValueError("invalid device")
        if legacy.issubset(entry) and (any(not valid_identifier(entry[k], 128) for k in ("plcId", "taskPointId"))
                or type(entry["dbNumber"]) is not int or not 1 <= entry["dbNumber"] <= 65535
                or type(entry["maxTaskAgeSeconds"]) is not int or not 1 <= entry["maxTaskAgeSeconds"] <= 86400
                or not isinstance(entry["idleValue"], str)):
            raise ValueError("invalid legacy device")
        if timings.issubset(entry) and any(type(entry[k]) is not int or not 1 <= entry[k] <= 86400 for k in timings):
            raise ValueError("invalid device timing")
        if not timings.issubset(entry):
            raise ValueError("r10 device timing must be explicit")
        devices[entry["equipmentId"]] = entry
    read_scopes = document["readScopes"]
    if not isinstance(read_scopes, dict):
        raise ValueError("invalid read scopes")
    for role, allowed in read_scopes.items():
        if not isinstance(role, str) or not isinstance(allowed, list) or len(allowed) != len(set(allowed)):
            raise ValueError("invalid read scope")
        if not set(allowed).issubset(devices):
            raise ValueError("unknown scoped device")
    meters = {}
    if not isinstance(document.get("meters", []), list):
        raise ValueError("invalid meters")
    for entry in document.get("meters", []):
        if (not isinstance(entry, dict) or set(entry) != {"meterId", "nameZh", "nameEn"}
                or not valid_identifier(entry["meterId"]) or entry["meterId"] in meters
                or any(not isinstance(entry[k], str) or not 1 <= len(entry[k]) <= 128 for k in ("nameZh", "nameEn"))):
            raise ValueError("invalid meter")
        meters[entry["meterId"]] = entry
    meter_scopes = document.get("meterReadScopes", {})
    if not isinstance(meter_scopes, dict):
        raise ValueError("invalid meter scopes")
    for role, allowed in meter_scopes.items():
        if (not isinstance(role, str) or not isinstance(allowed, list) or len(allowed) != len(set(allowed))
                or not set(allowed).issubset(meters)):
            raise ValueError("invalid meter scope")
    producers = {}
    seen_hashes = set()
    required = {"producerId", "tokenSha256", "kind", "enabled", "grants"}
    optional = {"mappingId", "mappingRevision", "sourceId", "energyGrants"}
    if not isinstance(document["producers"], list):
        raise ValueError("invalid producers")
    for entry in document["producers"]:
        if not isinstance(entry, dict) or not required.issubset(entry) or not set(entry).issubset(required | optional):
            raise ValueError("invalid producer")
        if (not valid_identifier(entry["producerId"]) or entry["producerId"] in producers
                or not isinstance(entry["tokenSha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", entry["tokenSha256"])
                or entry["tokenSha256"] in seen_hashes or entry["kind"] not in ("sma", "external", "other")
                or type(entry["enabled"]) is not bool or not isinstance(entry["grants"], list)
                or ("mappingId" in entry) != ("mappingRevision" in entry)
                or "mappingId" in entry and (not valid_identifier(entry["mappingId"]) or not valid_identifier(entry["mappingRevision"], 32))
                or "sourceId" in entry and entry["sourceId"] != "" and not valid_identifier(entry["sourceId"], 128)):
            raise ValueError("invalid producer")
        seen_hashes.add(entry["tokenSha256"])
        pairs = set()
        for grant in entry["grants"]:
            if (not isinstance(grant, dict) or set(grant) != {"equipmentId", "groupKey", "target", "metricKeys"}
                    or grant["equipmentId"] not in devices or grant["target"] not in ("latest", "history")
                    or not valid_identifier(grant["groupKey"])
                    or not isinstance(grant["metricKeys"], list)
                    or any(not valid_identifier(key) for key in grant["metricKeys"])
                    or len(grant["metricKeys"]) != len(set(grant["metricKeys"]))):
                raise ValueError("invalid grant")
            key = (grant["equipmentId"], grant["groupKey"], grant["target"])
            if key in pairs:
                raise ValueError("duplicate grant")
            pairs.add(key)
        energy_grants = entry.get("energyGrants", [])
        if not isinstance(energy_grants, list):
            raise ValueError("invalid energy grants")
        energy_pairs = set()
        for grant in energy_grants:
            if (not isinstance(grant, dict) or set(grant) != {"meterId", "groupKey", "metricKeys"}
                    or grant["meterId"] not in meters or not valid_identifier(grant["groupKey"])
                    or not isinstance(grant["metricKeys"], list)
                    or any(not valid_identifier(key) for key in grant["metricKeys"])
                    or len(grant["metricKeys"]) != len(set(grant["metricKeys"]))):
                raise ValueError("invalid energy grant")
            key = (grant["meterId"], grant["groupKey"])
            if key in energy_pairs:
                raise ValueError("duplicate energy grant")
            energy_pairs.add(key)
        producers[entry["producerId"]] = entry
    rules = {}
    if not isinstance(document["historyRules"], list):
        raise ValueError("invalid history rules")
    for entry in document["historyRules"]:
        if (not isinstance(entry, dict) or set(entry) != {"equipmentId", "groupKey", "metricKeys", "intervalSeconds"}
                or entry["equipmentId"] not in devices or not valid_identifier(entry["groupKey"])
                or not isinstance(entry["metricKeys"], list) or any(not valid_identifier(key) for key in entry["metricKeys"])
                or type(entry["intervalSeconds"]) is not int or entry["intervalSeconds"] <= 0):
            raise ValueError("invalid history rule")
        key = (entry["equipmentId"], entry["groupKey"])
        if key in rules:
            raise ValueError("duplicate history rule")
        rules[key] = entry
    groups = {}
    if not isinstance(document["groupSettings"], list):
        raise ValueError("invalid group settings")
    for entry in document["groupSettings"]:
        if (not isinstance(entry, dict) or set(entry) != {"equipmentId", "groupKey", "staleAfterSeconds"}
                or entry["equipmentId"] not in devices or not valid_identifier(entry["groupKey"])
                or type(entry["staleAfterSeconds"]) is not int or not 1 <= entry["staleAfterSeconds"] <= 2**31 - 1):
            raise ValueError("invalid group settings")
        key = (entry["equipmentId"], entry["groupKey"])
        if key in groups:
            raise ValueError("duplicate group settings")
        groups[key] = entry
    return {"target": target, "devices": devices, "readScopes": read_scopes, "producers": producers,
            "historyRules": rules, "groupSettings": groups, "meters": meters, "meterReadScopes": meter_scopes}


@lru_cache(maxsize=1)
def get_profile():
    try:
        settings = ObservationSettings()
        if not settings.OBSERVATION_ENABLED or not settings.OBSERVATION_PROFILE_FILE:
            raise ValueError("disabled or missing profile")
        path = Path(settings.OBSERVATION_PROFILE_FILE).resolve(strict=True)
        repository = Path(__file__).resolve().parents[3]
        if not path.is_file() or path.is_relative_to(repository) or path.stat().st_size > 1048576:
            raise ValueError("private profile required")
        def unique_pairs(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate key")
                result[key] = value
            return result
        return parse_profile(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs))
    except (OSError, ValueError, TypeError, UnicodeError, AttributeError):
        raise ObservationError(503, "not_ready") from None


def authenticate(profile, authorization):
    scheme, separator, token = (authorization or "").partition(" ")
    if not separator or scheme.lower() != "bearer" or not token or " " in token:
        raise ObservationError(401, "unauthenticated")
    try:
        actual = hashlib.sha256(token.encode("ascii")).hexdigest()
    except UnicodeError:
        raise ObservationError(401, "unauthenticated") from None
    matched = None
    for producer in profile["producers"].values():
        if hmac.compare_digest(actual, producer["tokenSha256"]):
            matched = producer
    if matched is None:
        raise ObservationError(401, "unauthenticated")
    if not matched["enabled"]:
        raise ObservationError(403, "forbidden")
    return matched


def permitted(producer, equipment, group, target):
    for grant in producer["grants"]:
        if (grant["equipmentId"], grant["groupKey"], grant["target"]) == (equipment, group, target):
            return frozenset(grant["metricKeys"])
    raise ObservationError(403, "forbidden")


def allowed_devices(profile, user):
    return frozenset(profile["readScopes"].get(user.role, []))


def allowed_device(profile, user, equipment):
    if equipment not in allowed_devices(profile, user):
        raise ObservationError(403, "forbidden")
    return profile["devices"][equipment]


def allowed_meter(profile, user, meter):
    if meter not in profile.get("meterReadScopes", {}).get(user.role, []):
        raise ObservationError(403, "forbidden")
    return profile["meters"][meter]


def permitted_energy(producer, meter, group):
    for grant in producer.get("energyGrants", []):
        if (grant["meterId"], grant["groupKey"]) == (meter, group):
            return frozenset(grant["metricKeys"])
    raise ObservationError(403, "forbidden")
