"""performance固定时间列及旧wire分组；纯规则不读取配置/文件/数据库。"""
from common.integration.storage import to_storage_time as storage_time, to_legacy_time as legacy_time

FIXED_COLUMNS = {'performance_main': ['reported_start_time', 'reported_end_time', 'first_observed_at', 'last_observed_at', 'start_time', 'end_time', 'manual_override_at', 'created_at', 'updated_at'], 'performance_process_temperature': ['record_time', 'created_at', 'updated_at'], 'performance_process_tension': ['record_time', 'created_at', 'updated_at'], 'performance_process_speed': ['record_time', 'created_at', 'updated_at'], 'performance_mapping_receipts': ['sampled_at', 'created_at', 'updated_at'], 'performance_mapping_observation_state': ['last_sampled_at', 'created_at', 'updated_at']}
import hashlib, json
FIXED_COLUMN_DIGEST = "sha256:"+hashlib.sha256(json.dumps(FIXED_COLUMNS,sort_keys=True,separators=(",", ":"),ensure_ascii=False).encode()).hexdigest()


def legacy_basis(table, field, adoption, channel="http", record_source=None):
    basis = adoption["basisProfile"]
    if table=="performance_main":
        if field in ("reported_start_time","reported_end_time"):
            return "utc_wall"
        if field in ("first_observed_at","last_observed_at") and record_source=="external_observation":
            return "utc_wall"
    if table in ("performance_mapping_receipts","performance_mapping_observation_state"):
        return "utc_wall"
    if table == "performance_main" and field in ("start_time", "end_time"):
        return basis["manualNaive"]
    if table == "performance_main" and field == "manual_override_at":
        return basis["manualAuditWire"]
    if field in ("created_at", "updated_at"):
        if table.endswith("receipts") or table == "equipment_temperature_samples" or table == "performance_mapping_observation_state":
            return "utc_wall"
        return basis["systemWire"]
    return basis["legacyNaive"] if channel == "legacy" else "utc_wall"


def input_time(value, table, field, adoption, channel="http"):
    return storage_time(value, legacy_basis(table, field, adoption, channel)) if adoption else value


def output_time(value, table, field, adoption, channel="http", record_source=None):
    return legacy_time(value, legacy_basis(table, field, adoption, channel,record_source)) if adoption else value


BUSINESS_TIME_COLUMN_PROFILE = {"profileId":"be010.fixed-columns/v1", "columns":FIXED_COLUMNS, "digest":FIXED_COLUMN_DIGEST}


def storage_sample(sample, adoption):
    """HTTP DTO只复制时间属性；旧摘要/结果使用调用方保留的原DTO。"""
    if adoption is None:
        return sample
    from datetime import datetime
    changes={key:storage_time(getattr(sample,key),"utc_wall") for key in type(sample).model_fields
        if isinstance(getattr(sample,key),datetime)}
    return sample.model_copy(update=changes)


def legacy_view(record, adoption, channel="http"):
    """固定列只读视图；原ORM保持上海值，不发生临时改回/脏写。"""
    if adoption is None or record is None:
        return record
    from types import SimpleNamespace
    table=record.__table__.name
    if table not in FIXED_COLUMNS:
        return record
    values={column.key:getattr(record,column.key) for column in record.__table__.columns}
    for field in FIXED_COLUMNS[table]:
        values[field]=output_time(values[field],table,field,adoption,channel,getattr(record,"record_source",None))
    for key in ("plan","temperature_records","tension_records","speed_records"):
        if key not in record.__dict__:
            continue
        value=record.__dict__[key]
        values[key]=[legacy_view(item,adoption,channel) for item in value] if isinstance(value,list) else value
    return SimpleNamespace(**values)


def legacy_input(value, fallback, adoption, basis="legacyNaive"):
    """legacy aware保留明确瞬间，naive只按证据basis；保留原解析责任。"""
    if adoption is None:
        return value
    from datetime import datetime
    candidate=value if value is not None and value!="" else fallback
    if isinstance(candidate,str):
        candidate=datetime.fromisoformat(candidate.strip().replace("Z","+00:00"))
    return storage_time(candidate,adoption["basisProfile"][basis])
