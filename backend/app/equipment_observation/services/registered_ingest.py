"""登记来源采样规范化、事务内去重及两目标持久化。"""
from datetime import timedelta
from decimal import Decimal
import hashlib

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError

from common.integration.canonical import canonical_bytes
from common.integration.envelope import fact_time
from ..domain import ObservationError, identifier, reject, task_no, wire_time
from ..models import HistorySample, LatestSnapshot, MetricConfig, MetricGroup, Receipt, SlotBinding
from . import v2_domain, write_sources
from .guard import current_clock
from .ingest_v2 import _previous

CONTRACT_VERSION = "aiis.observation-write/v1"
RESULT_VERSION = "r1"
TARGET_MODELS = {"latest": LatestSnapshot, "history": HistorySample}


def normalize(document):
    if not isinstance(document, dict) or set(document) != {"sourceKey", "target", "taskNo", "observedAt", "items"}:
        reject()
    source = write_sources.source_key(document["sourceKey"])
    target = document["target"]
    if target not in ("latest", "history"):
        reject()
    task = task_no(document["taskNo"])
    try:
        when = v2_domain.observed_time(fact_time(document["observedAt"]))
    except ValueError:
        reject("invalid_observed_at")
    items = document["items"]
    if not isinstance(items, dict) or not items:
        reject("values")
    for group, values in items.items():
        identifier(group)
        if not isinstance(values, dict):
            reject("values")
        for key, value in values.items():
            identifier(key)
            if type(value) in (int, float, Decimal):
                v2_domain.scalar(value, "number")
            elif type(value) not in (bool, str):
                reject("metric_type")
    if not any(items.values()):
        reject("values")
    normalized = dict(document, taskNo=task, observedAt=wire_time(when))
    try:
        digest = hashlib.sha256(canonical_bytes(normalized)).digest()
    except (ValueError, TypeError, UnicodeError):
        reject()
    event_id = "obsreg1_" + hashlib.sha256(canonical_bytes(
        [CONTRACT_VERSION, source, target, task, normalized["observedAt"]]
    )).hexdigest()
    return normalized, when, digest, event_id


async def _local_values(db, target, items):
    groups = set((await db.execute(select(MetricGroup.group_key).where(
        MetricGroup.group_key.in_(items), MetricGroup.enabled.is_(True)
    ).order_by(MetricGroup.group_key).with_for_update(read=True))).scalars())
    if groups != set(items):
        reject("metric_scope")
    keys = {key for values in items.values() for key in values}
    metrics = {metric.metric_key: metric for metric in (await db.execute(select(MetricConfig).where(
        MetricConfig.metric_key.in_(keys)
    ).order_by(MetricConfig.metric_key).with_for_update(read=True))).scalars()}
    slots = {(slot.group_key, slot.metric_key): slot for slot in (await db.execute(select(SlotBinding).where(
        SlotBinding.target == target, SlotBinding.group_key.in_(groups), SlotBinding.metric_key.in_(keys)
    ).order_by(SlotBinding.group_key, SlotBinding.slot_no).with_for_update())).scalars()}
    local, used = {}, []
    for group, values in items.items():
        mapped = {}
        for key, value in values.items():
            metric, slot = metrics.get(key), slots.get((group, key))
            if metric is None or metric.source_group_key != group or slot is None or not slot.enabled:
                reject("metric_scope")
            mapped[f"{slot.slot_no:02d}"] = (value if metric.value_type == "string" and isinstance(value, str)
                                             else v2_domain.scalar(value, metric.value_type))
            used.append(slot)
        if mapped:
            local[group] = mapped
    return local, used


async def submit(db, profile, document):
    request, when, request_digest, event_id = normalize(document)
    target, key, task = request["target"], request["sourceKey"], request["taskNo"]
    result = {field: request[field] for field in ("sourceKey", "target", "taskNo", "observedAt")}
    for attempt in range(3):
        try:
            await write_sources.check_profile(db, profile)
            source = await write_sources.source_row(db, key, lock=True)
            if source is None or source.deleted_at is not None or not source.enabled:
                reject("source_not_enabled", 403)
            identity = source.storage_identity
            previous = await _previous(db, Receipt, target, identity, event_id)
            if previous is not None:
                if ((previous.contract_version, previous.result_version) != (CONTRACT_VERSION, RESULT_VERSION)
                        or bytes(previous.request_digest) != request_digest):
                    reject("event_conflict", 409)
                return dict(result, outcome=previous.outcome, receiptId=str(previous.id),
                            recordId=str(previous.result_record_id))
            now = await current_clock(db)
            if when > now + timedelta(seconds=30):
                reject("invalid_observed_at")
            model = TARGET_MODELS[target]
            record = None
            if target == "latest":
                query = select(model).where(model.equipment_id == identity, model.task_no == task)
                record = (await db.execute(query.with_for_update())).scalar_one_or_none()
                if record is not None and when == record.observed_at:
                    reject("sample_conflict", 409)
            local, used = await _local_values(db, target, request["items"])
            outcome = "stale" if record is not None and when < record.observed_at else "stored"
            receipt = Receipt(target=target, producer_id=identity, event_id=event_id, request_digest=request_digest,
                              outcome=outcome, processed_at=now, contract_version=CONTRACT_VERSION,
                              result_version=RESULT_VERSION)
            db.add(receipt)
            await db.flush()
            if outcome == "stored":
                if record is None:
                    record = model(equipment_id=identity, task_no=task, created_at=now)
                    db.add(record)
                record.observed_at, record.quality, record.local_values = when, "unknown", local
                record.ingest_receipt_id, record.updated_at = receipt.id, now
                record.source_sample_key = hashlib.sha256(canonical_bytes([identity, event_id])).digest()
                for slot in used:
                    if slot.first_used_at is None:
                        slot.first_used_at = now
                await db.flush()
            receipt.result_record_id = record.id
            await db.flush()
        except ObservationError:
            await db.rollback()
            raise
        except DBAPIError as exc:
            await db.rollback()
            if attempt == 2 or (getattr(exc.orig, "args", ()) or (None,))[0] not in (1062, 1205, 1213):
                reject("not_ready", 503)
            continue
        result = dict(result, outcome=outcome, receiptId=str(receipt.id), recordId=str(record.id))
        await write_sources.commit(db)
        return result
