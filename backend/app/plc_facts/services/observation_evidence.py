"""只读 v2 任务点证据，供设备状态模块按采样时刻确认任务。"""
from datetime import timedelta
import re

from sqlalchemy import select

from ..crud import async_v2 as crud
from ..models.source_registry import PlcSourceRegistry
from ..models.v2 import LatestPointV2, SampleV2
from ..v2_config import get_profile
from ..v2_domain import V2Error, parse_time, wire_time

TASK_NO = re.compile(r"^[A-Z0-9_.-]{1,50}$")


class EvidenceUnavailable(Exception):
    """事实 provider 不可用或目标未就绪。"""


def _profile():
    try:
        return get_profile()
    except V2Error as exc:
        raise EvidenceUnavailable() from exc


async def probe_target(db, target):
    try:
        return await crud.target_now(db, target)
    except V2Error as exc:
        raise EvidenceUnavailable() from exc


def normalize_task(value):
    if not isinstance(value, str) or not value.isascii():
        return None
    result = value.strip().upper()
    return result if TASK_NO.fullmatch(result) else None


async def _source(db, binding):
    # A shared lock makes source deletion/replacement and evidence admission serial.
    query = (select(PlcSourceRegistry).where(PlcSourceRegistry.plc_id == crud.key(binding["plcId"]))
             .with_for_update(read=True).execution_options(populate_existing=True))
    source = (await db.execute(query)).scalar_one_or_none()
    if source is None:
        return None
    return source.instance_id.decode("utf-8"), source.source_generation.decode("utf-8")


def _task_value(point, binding, when):
    if not isinstance(point, dict) or point.get("pointId") != binding["taskPointId"]:
        return None
    try:
        observed = parse_time(point["observedAt"])
    except (KeyError, ValueError, TypeError, V2Error):
        return (None, None)
    if observed > when:
        return None
    value = point.get("value")
    valid = (point.get("quality") == "good" and isinstance(value, str)
             and str(point.get("dataType", "")).startswith("STRING["))
    if not valid or when - observed > timedelta(seconds=binding["maxTaskAgeSeconds"]):
        return (observed, None)
    if value == binding["idleValue"]:
        return (observed, "idle")
    return (observed, normalize_task(value))


async def current_task(db, binding):
    profile = _profile()
    now = await probe_target(db, profile["target"])
    source = await _source(db, binding)
    if source is None:
        return {"state": "unknown", "taskNo": None}
    rows = await crud.latest(db, binding["plcId"], binding["dbNumber"], source, now, binding["taskPointId"])
    if not rows:
        return {"state": "unknown", "taskNo": None}
    row = rows[0]
    point = {"pointId": binding["taskPointId"], "observedAt": wire_time(row.observed_at),
             "value": row.value_json, "quality": row.quality, "dataType": row.data_type}
    result = _task_value(point, binding, now)
    if not result or result[1] is None:
        return {"state": "unknown", "taskNo": None}
    return {"state": "idle" if result[1] == "idle" else "active",
            "taskNo": None if result[1] == "idle" else result[1], "observedAt": wire_time(result[0])}


def _evidence(row, point_id, observed_at):
    """Return the accepted task point identity so it survives v2 expiry."""
    return {"instanceId": row.instance_id.decode(), "sampleId": row.sample_id.decode(),
            "plcId": row.plc_id.decode(), "dbNumber": row.db_number, "pointId": point_id,
            "sourceGeneration": row.source_generation.decode(), "sourceSeq": str(row.source_seq),
            "observedAt": wire_time(observed_at)}


async def confirm_task(db, binding, task_no, sampled_at, refs, caller_type):
    profile = _profile()
    now = await probe_target(db, profile["target"])
    source = await _source(db, binding)
    if source is None:
        return False
    instance, generation = source
    expected = normalize_task(task_no)
    if expected is None or sampled_at > now + timedelta(minutes=5):
        return False
    if caller_type == "sma":
        if not refs or any(ref.get("kind") != "plc_fact" for ref in refs):
            return False
        identities = {(ref.get("instanceId"), ref.get("sampleId"), ref.get("plcId")) for ref in refs}
        if len(identities) != 1:
            return False
        ref_instance, ref_sample, ref_plc = next(iter(identities))
        if ref_instance != instance or ref_plc != binding["plcId"]:
            return False
        statement = select(SampleV2).where(
            SampleV2.instance_id == crud.key(ref_instance), SampleV2.sample_id == crud.key(ref_sample),
            SampleV2.plc_id == crud.key(ref_plc), SampleV2.db_number == binding["dbNumber"],
            SampleV2.source_generation == crud.key(generation), SampleV2.expires_at > now,
        )
        row = (await db.execute(statement)).scalar_one_or_none()
        if row is None or row.sampled_at != sampled_at:
            return False
        points = {point["pointId"]: point for point in row.points_json}
        for ref in refs:
            point = points.get(ref.get("pointId"))
            if point is None:
                return False
            if ("sourceGeneration" in ref and ref["sourceGeneration"] != generation
                    or "configRevision" in ref and ref["configRevision"] != (row.config_revision.decode() if row.config_revision else None)
                    or "observedAt" in ref and ref["observedAt"] != point.get("observedAt")):
                return False
        if binding["taskPointId"] not in {ref.get("pointId") for ref in refs}:
            return False
        result = _task_value(points.get(binding["taskPointId"]), binding, sampled_at)
        return _evidence(row, binding["taskPointId"], result[0]) if result and result[1] == expected else None
    if caller_type != "external":
        return False
    lower = sampled_at - timedelta(seconds=binding["maxTaskAgeSeconds"], minutes=5)
    statement = select(SampleV2).where(
        SampleV2.instance_id == crud.key(instance), SampleV2.plc_id == crud.key(binding["plcId"]),
        SampleV2.db_number == binding["dbNumber"], SampleV2.source_generation == crud.key(generation),
        SampleV2.sampled_at >= lower, SampleV2.sampled_at <= sampled_at + timedelta(minutes=5),
        SampleV2.expires_at > now,
    )
    rows = (await db.execute(statement)).scalars().all()
    observed = []
    for row in rows:
        for point in row.points_json:
            result = _task_value(point, binding, sampled_at)
            if result and result[0] is not None:
                observed.append((result[0], row.source_seq, row.id, result[1], row))
    selected = max(observed, key=lambda item: item[:3]) if observed else None
    return _evidence(selected[4], binding["taskPointId"], selected[0]) if selected and selected[3] == expected else None
