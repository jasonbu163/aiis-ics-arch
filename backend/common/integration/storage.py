"""有限业务时间与采用凭据纯原语；不读文件、配置、SQL或任意表列。"""
from datetime import datetime, timezone
from hashlib import sha256
import json
from common.integration.envelope import BUSINESS_TIMEZONE, source_time

SCHEMA_REVISION = "1b3d5f7a9c20"
BASIS_PROFILE = "be010.fixed-basis/v1"


def storage_time(value, basis="utc_wall"):
    """明确offset优先；naive只按已证明的固定basis解释，返回上海DATETIME墙上值。"""
    if value is None:
        return None
    if basis not in ("utc_wall", "shanghai_wall") or not isinstance(value, datetime):
        raise ValueError("invalid time basis")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc if basis == "utc_wall" else BUSINESS_TIMEZONE)
    return value.astimezone(BUSINESS_TIMEZONE).replace(tzinfo=None)


def legacy_time(value, basis="utc_wall"):
    """只读旧wire视图；不修改绑定ORM字段或原JSON result。"""
    if value is None:
        return None
    if basis not in ("utc_wall", "shanghai_wall"):
        raise ValueError("invalid time basis")
    local = value.replace(tzinfo=BUSINESS_TIMEZONE) if value.tzinfo is None else value.astimezone(BUSINESS_TIMEZONE)
    return local.astimezone(timezone.utc if basis == "utc_wall" else BUSINESS_TIMEZONE).replace(tzinfo=None)


def database_clock(utc_now):
    """仅转换数据库UTC_TIMESTAMP(3)的已知UTC瞬间；不使用宿主时钟。"""
    return storage_time(utc_now, "utc_wall").replace(tzinfo=BUSINESS_TIMEZONE)


def column_digest(columns):
    payload = json.dumps(columns, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + sha256(payload).hexdigest()


def validate_adoption(document, module, columns):
    """校验有限采用证据结构；不是producer认证或对历史行的自证。"""
    required = {"version", "profile", "module", "serverUuid", "schema", "schemaRevision", "sourceRevision",
                "fixedColumnDigest", "basisProfile", "reports", "backupRef", "ownerApprovalRef", "verifiedAt", "state"}
    if not isinstance(document, dict) or set(document) != required:
        raise ValueError("invalid adoption evidence")
    if any(document[k] != v for k, v in {"version":"business-time-adoption/v1", "profile":"shanghai-v1",
            "module":module, "schemaRevision":SCHEMA_REVISION, "fixedColumnDigest":column_digest(columns), "state":"adopted"}.items()):
        raise ValueError("adoption profile mismatch")
    for key in ("serverUuid", "schema", "sourceRevision", "backupRef", "ownerApprovalRef"):
        if not isinstance(document[key], str) or not document[key].strip() or len(document[key]) > 512:
            raise ValueError("missing adoption reference")
    if not isinstance(document["verifiedAt"], str) or not document["verifiedAt"].endswith("+08:00"):
        raise ValueError("invalid adoption verification time")
    source_time(document["verifiedAt"])
    basis = document["basisProfile"]
    keys = {"profileId", "legacyNaive", "systemWire"} | ({"manualNaive", "manualAuditWire"} if module == "performance" else set())
    if not isinstance(basis, dict) or set(basis) != keys or basis["profileId"] != BASIS_PROFILE:
        raise ValueError("invalid basis profile")
    if any(basis[k] not in ("utc_wall", "shanghai_wall") for k in keys - {"profileId"}):
        raise ValueError("unknown time basis")
    reports = document["reports"]
    if not isinstance(reports, dict) or set(reports) != {"inspection", "migration", "verification"}:
        raise ValueError("missing adoption reports")
    for report in reports.values():
        if not isinstance(report, dict) or set(report) != {"reference", "digest"}:
            raise ValueError("invalid report reference")
        if not isinstance(report["reference"], str) or not report["reference"].strip():
            raise ValueError("missing report reference")
        digest=report["digest"]
        if not isinstance(digest,str) or len(digest)!=71 or not digest.startswith("sha256:") or any(c not in "0123456789abcdef" for c in digest[7:]):
            raise ValueError("invalid report digest")
    return document


def validate_target(adoption, target):
    """目标由owner CRUD查询；不缓存跨事务的探针或创建会话。"""
    if any(target[k] != adoption[k] for k in ("serverUuid", "schema", "schemaRevision")):
        raise ValueError("adoption target mismatch")
    return database_clock(target["utcNow"])


from dataclasses import dataclass
from collections.abc import Mapping


@dataclass(frozen=True)
class StorageProbe:
    serverUuid: str
    schema: str
    schemaRevision: str
    utcNow: datetime

    @property
    def server_uuid(self):return self.serverUuid

    @property
    def schema_revision(self):return self.schemaRevision

    @property
    def utc_now(self):return self.utcNow


@dataclass(frozen=True)
class AdoptionContext:
    manifest: Mapping
    database_now: datetime


def parse_adoption_manifest(value, module):
    """只验证有限凭据结构；固定列摘要由owner与目标探针进一步核对。"""
    if not isinstance(value, dict) or module not in ("equipment", "performance", "monitor"):
        raise ValueError("invalid adoption manifest")
    # profile摘要是owner负责的静态常量；Core不嵌入业务表列。
    copy = dict(value)
    digest = copy.get("fixedColumnDigest")
    if not isinstance(digest,str) or len(digest)!=71 or not digest.startswith("sha256:") or any(c not in "0123456789abcdef" for c in digest[7:]):
        raise ValueError("invalid fixed column digest")
    # 复用结构验证，列摘要匹配由owner执行。
    placeholder = {}
    copy["fixedColumnDigest"] = column_digest(placeholder)
    validate_adoption(copy,module,placeholder)
    return dict(value)


def validate_adoption_probe(manifest, probe):
    now = validate_target(manifest, {"serverUuid":probe.server_uuid,"schema":probe.schema,
        "schemaRevision":probe.schema_revision,"utcNow":probe.utc_now})
    return AdoptionContext(manifest, now)


def to_storage_time(value, basis="utc_wall"):
    return storage_time(value,basis)


def to_legacy_time(value, basis="utc_wall"):
    return legacy_time(value,basis)
