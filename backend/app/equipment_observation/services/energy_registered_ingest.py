"""规范化一包多表样本，以能耗登记锁保证完整提交和稳定重放。"""
import hashlib

from sqlalchemy import select, tuple_
from sqlalchemy.exc import DBAPIError

from common.integration.canonical import canonical_bytes
from common.integration.envelope import fact_time
from ..domain import ObservationError, identifier, reject, wire_time
from ..models import EnergyMetric, EnergyReceipt, EnergySample
from . import energy_write_sources, v2_domain
from .energy_meters import catalog
from .guard import current_clock, verify_energy_target
from .ingest_v2 import _previous
from .write_sources import commit, source_key

CONTRACT_VERSION = "aiis.energy-registered/v1"
RESULT_VERSION = "r1"
_GROUP_FIELDS = {"values", "quality", "intervalStartAt", "intervalEndAt"}


def _time(value, reason):
    try:
        return v2_domain.observed_time(fact_time(value))
    except (ValueError, ObservationError):
        reject(reason)


def normalize(document):
    if (not isinstance(document, dict) or set(document) != {"sourceKey", "target", "observedAt", "items"}
            or document["target"] != "energy"):
        reject()
    key = source_key(document["sourceKey"])
    when = _time(document["observedAt"], "invalid_observed_at")
    items = document["items"]
    if not isinstance(items, dict) or not items:
        reject("values")
    groups = {}
    canonical_items = {}
    for meter, meter_items in items.items():
        identifier(meter)
        if not isinstance(meter_items, dict) or not meter_items:
            reject("values")
        canonical_items[meter] = {}
        for group, fields in meter_items.items():
            identifier(group)
            if not isinstance(fields, dict) or not set(fields).issubset(_GROUP_FIELDS):
                reject()
            values = fields.get("values")
            if not isinstance(values, dict) or not values:
                reject("values")
            for metric, value in values.items():
                identifier(metric)
                v2_domain.scalar(value, "number")
            quality = fields.get("quality")
            if quality is None:
                quality = "unknown"
            if quality not in ("good", "bad", "unknown"):
                reject("quality")
            start = end = None
            if {"intervalStartAt", "intervalEndAt"}.intersection(fields):
                start = _time(fields.get("intervalStartAt"), "invalid_time_range")
                end = _time(fields.get("intervalEndAt"), "invalid_time_range")
                if start >= end:
                    reject("invalid_time_range")
            groups[meter, group] = {"values": values, "quality": quality, "start": start, "end": end}
            canonical_items[meter][group] = {"values": values, "quality": quality,
                                            "intervalStartAt": wire_time(start), "intervalEndAt": wire_time(end)}
    stamp = wire_time(when)
    result = {"sourceKey": key, "target": "energy", "observedAt": stamp}
    try:
        digest = hashlib.sha256(canonical_bytes(dict(result, items=canonical_items))).digest()
    except (ValueError, TypeError, UnicodeError):
        reject()
    # 生产者身份已由能耗登记隔离。批次事件键仅表达规范采集时刻。
    return result, when, digest, "energyreg1_" + stamp, groups


async def _validated_samples(db, meters, groups):
    if any(meter not in meters for meter, _ in groups):
        reject("metric_scope")
    keys = [(meter, group, key) for (meter, group), item in groups.items() for key in item["values"]]
    query = select(EnergyMetric).where(
        tuple_(EnergyMetric.meter_id, EnergyMetric.group_key, EnergyMetric.metric_key).in_(keys)
    ).order_by(EnergyMetric.meter_id, EnergyMetric.group_key, EnergyMetric.metric_key).with_for_update()
    configs = {(row.meter_id, row.group_key, row.metric_key): row for row in (await db.execute(query)).scalars()}
    if len(configs) != len(keys) or any(not row.enabled for row in configs.values()):
        reject("metric_scope")
    for (meter, group), item in groups.items():
        has_interval = any(configs[meter, group, key].measurement_mode == "interval" for key in item["values"])
        if has_interval != (item["start"] is not None):
            reject("invalid_time_range")
    return configs


async def submit(db, profile, document):
    result, when, digest, event_id, groups = normalize(document)
    for attempt in range(3):
        try:
            await verify_energy_target(db, profile["target"])
            source = await energy_write_sources.source_row(db, result["sourceKey"])
            if source is None or source.deleted_at is not None or not source.enabled:
                reject("source_not_enabled", 403)
            previous = await _previous(db, EnergyReceipt, "energy", source.storage_identity, event_id)
            if previous is not None:
                if ((previous.contract_version, previous.result_version) != (CONTRACT_VERSION, RESULT_VERSION)
                        or bytes(previous.request_digest) != digest):
                    reject("event_conflict", 409)
                replay = dict(result, outcome=previous.outcome, receiptId=str(previous.id),
                              records=previous.result_detail["records"])
                await db.rollback()
                return replay
            configs = await _validated_samples(db, await catalog(db, profile), groups)
            now = await current_clock(db)
            receipt = EnergyReceipt(target="energy", producer_id=source.storage_identity, event_id=event_id,
                                    request_digest=digest, outcome="stored", processed_at=now,
                                    contract_version=CONTRACT_VERSION, result_version=RESULT_VERSION)
            db.add(receipt)
            await db.flush()
            samples = []
            for meter, group in sorted(groups, key=lambda pair: (pair[0].encode("utf-8"), pair[1].encode("utf-8"))):
                item = groups[meter, group]
                values = {}
                for key, value in item["values"].items():
                    config = configs[meter, group, key]
                    values[f"{config.slot_no:02d}"] = v2_domain.scalar(value, "number")
                    if config.first_used_at is None:
                        config.first_used_at = now
                samples.append(EnergySample(meter_id=meter, group_key=group, observed_at=when,
                                            interval_start_at=item["start"], interval_end_at=item["end"],
                                            quality=item["quality"], local_values=values, ingest_receipt_id=receipt.id,
                                            created_at=now, updated_at=now))
            db.add_all(samples)
            await db.flush()
            records = [{"meterId": row.meter_id, "groupKey": row.group_key, "recordId": str(row.id)} for row in samples]
            receipt.result_detail = {"records": records}
            await db.flush()
            stored = dict(result, outcome=receipt.outcome, receiptId=str(receipt.id), records=records)
        except ObservationError:
            await db.rollback()
            raise
        except DBAPIError as exc:
            await db.rollback()
            if attempt == 2 or (getattr(exc.orig, "args", ()) or (None,))[0] not in (1062, 1205, 1213):
                reject("not_ready", 503)
            continue
        await commit(db)
        return stored
