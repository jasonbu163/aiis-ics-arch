"""来源无关整包与表计样本写入；回执和业务记录在同一事务内提交。"""
from datetime import timedelta
from decimal import Decimal
import hashlib

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .guard import EvidenceUnavailable, current_clock, verify_energy_target
from common.integration.canonical import canonical_bytes
from ..domain import ObservationError, reject
from ..models import EnergyMetric, EnergyReceipt, EnergySample, HistorySample, LatestSnapshot, MetricConfig, MetricGroup, Receipt, SlotBinding
from ..profile import permitted, permitted_energy
from . import v2_domain, write_sources


def receipt_data(row):
    data = {"target": row.target, "producerId": row.producer_id, "eventId": row.event_id,
            "outcome": row.outcome, "recordId": str(row.result_record_id) if row.result_record_id else None}
    if row.result_detail:
        data.update(row.result_detail)
    return data


async def _previous(db, model, target, producer_id, event_id):
    query = select(model).where(model.target == target, model.producer_id == producer_id,
                                model.event_id == event_id).with_for_update()
    return (await db.execute(query)).scalar_one_or_none()


def _receipt(model, target, producer, event, doc, now):
    def json_safe(value):
        if isinstance(value, Decimal):
            return v2_domain.scalar(value, "number")
        if isinstance(value, list):
            return [json_safe(item) for item in value]
        if isinstance(value, dict):
            return {key: json_safe(item) for key, item in value.items()}
        return value
    return model(target=target, producer_id=producer["producerId"], event_id=event["eventId"],
                   request_digest=event["requestDigest"], outcome="pending", processed_at=now,
                   mapping_id=doc.get("mappingId"), mapping_revision=doc.get("mappingRevision"),
                   source_refs=json_safe(doc.get("sourceRefs")), task_evidence=None,
                   contract_version="aiis.metric-ingest/v2", result_version="r10")


async def _retry_receipt(db, model, target, producer, event):
    previous = await _previous(db, model, target, producer["producerId"], event["eventId"])
    if previous is None:
        return None
    if (previous.contract_version, previous.result_version) != ("aiis.metric-ingest/v2", "r10") or bytes(previous.request_digest) != event["requestDigest"]:
        reject("event_conflict", 409)
    result = receipt_data(previous)
    await db.rollback()
    return result


async def device(db, profile, producer, target, document, decimal_document=None):
    data = document.get("data") if isinstance(document, dict) else None
    if isinstance(document, dict) and (
        document.get("contractVersion") == "aiis.metric-ingest/v1"
        or isinstance(data, dict) and "sampledAt" in data
    ):
        equipment = data.get("equipmentId") if isinstance(data, dict) else None
        group = data.get("groupKey") if isinstance(data, dict) else None
        values = data.get("values") if isinstance(data, dict) else None
        if document.get("producerId", producer["producerId"]) != producer["producerId"]:
            reject("forbidden", 403)
        if (not isinstance(equipment, str) or equipment not in profile["devices"]
                or not isinstance(group, str) or not isinstance(values, dict)):
            reject("forbidden", 403)
        if not set(values) <= permitted(producer, equipment, group, target):
            reject("forbidden", 403)
        reject("contract_version", 409)
    event = v2_domain.device_event(decimal_document or document, producer, target)
    equipment = event["equipmentId"]
    if equipment not in profile["devices"]:
        reject("forbidden", 403)
    if not any(grant["equipmentId"] == equipment and grant["target"] == target for grant in producer["grants"]):
        reject("forbidden", 403)
    producers = list(profile.get("producers", {}).values()) + [producer]
    configured_groups = {grant["groupKey"] for candidate in producers for grant in candidate["grants"]
                         if grant["equipmentId"] == equipment}
    for attempt in range(3):
        commit_started = False
        try:
            now = await current_clock(db)
            await write_sources.check_profile(db, profile, writing_as=(equipment, producer["producerId"]))
            device_profile = profile["devices"][equipment]
            record = None
            if target == "latest":
                query = select(LatestSnapshot).where(LatestSnapshot.equipment_id == equipment,
                    LatestSnapshot.task_no == event["taskNo"]).with_for_update()
                record = (await db.execute(query)).scalar_one_or_none()
            existing_groups = set(record.local_values) if record is not None else set()
            scoped_groups = configured_groups | existing_groups | set(event["groups"])
            group_rows = (await db.execute(select(MetricGroup).where(MetricGroup.group_key.in_(scoped_groups)).with_for_update())).scalars().all()
            registered = {row.group_key for row in group_rows}
            if set(event["groups"]) - registered or existing_groups - registered:
                reject("metric_scope")
            metric_rows = (await db.execute(select(MetricConfig).where(MetricConfig.source_group_key.in_(scoped_groups))
                                            .order_by(MetricConfig.metric_key).with_for_update())).scalars().all()
            metrics = {(metric.source_group_key, metric.metric_key): metric for metric in metric_rows}
            slots = (await db.execute(select(SlotBinding).where(SlotBinding.target == target,
                SlotBinding.group_key.in_(scoped_groups)).order_by(SlotBinding.group_key, SlotBinding.slot_no).with_for_update())).scalars().all()
            groups_to_authorize = ({slot.group_key for slot in slots} | existing_groups | set(event["groups"])
                                   if target == "latest" else set(event["groups"]))
            for group in groups_to_authorize:
                allowed = permitted(producer, equipment, group, target)
                required = ({slot.metric_key for slot in slots if slot.group_key == group} | set(event["groups"].get(group, {}))
                            if target == "latest" else set(event["groups"][group]))
                if not required.issubset(allowed):
                    reject("forbidden", 403)
            previous = await _retry_receipt(db, Receipt, target, producer, event)
            if previous is not None:
                return previous
            if event["observedAt"] > now + timedelta(seconds=device_profile["futureToleranceSeconds"]):
                reject("invalid_observed_at")
            if record is not None:
                for group, old_values in record.local_values.items():
                    known = {f"{slot.slot_no:02d}" for slot in slots if slot.group_key == group}
                    if set(old_values) - known:
                        reject("metric_scope")
            bindings = {(slot.group_key, slot.metric_key): slot for slot in slots}
            local, stored, skipped, used = {}, [], [], []
            for group, values in event["groups"].items():
                permitted_keys = permitted(producer, equipment, group, target)
                output = {}
                accepted = []
                for key, raw in values.items():
                    metric = metrics.get((group, key))
                    if metric is None:
                        reject("metric_scope")
                    if key not in permitted_keys:
                        reject("forbidden", 403)
                    value = v2_domain.scalar(raw, metric.value_type)
                    slot = bindings.get((group, key))
                    if slot is None or not slot.enabled:
                        skipped.append({"groupKey": group, "metricKey": key,
                                        "reason": "history_disabled" if target == "history" else "latest_disabled"})
                        continue
                    output[f"{slot.slot_no:02d}"] = value
                    accepted.append(key)
                    used.append(slot)
                if output:
                    local[group] = output
                    stored.append({"groupKey": group, "metricKeys": accepted})
            has_history = any(slot.enabled and slot.group_key in configured_groups for slot in slots)
            receipt = _receipt(Receipt, target, producer, event, decimal_document or document, now)
            db.add(receipt)
            await db.flush()
            outcome = "stored"
            if target == "history" and not has_history:
                outcome = "no_history_metrics"
            elif target == "history":
                record = HistorySample(equipment_id=equipment, task_no=event["taskNo"], observed_at=event["observedAt"],
                    quality=event["quality"], local_values=local, ingest_receipt_id=receipt.id,
                    source_sample_key=hashlib.sha256(canonical_bytes([producer["producerId"], event["eventId"]])).digest(),
                    created_at=now, updated_at=now)
                db.add(record)
                await db.flush()
            else:
                if record is not None and event["observedAt"] < record.observed_at:
                    outcome = "stale"
                elif record is not None and event["observedAt"] == record.observed_at:
                    if record.local_values != local or record.quality != event["quality"]:
                        reject("sample_conflict", 409)
                    outcome = "already_stored"
                elif record is not None:
                    record.observed_at, record.quality, record.local_values = event["observedAt"], event["quality"], local
                    record.ingest_receipt_id, record.updated_at = receipt.id, now
                    record.source_sample_key = hashlib.sha256(canonical_bytes([producer["producerId"], event["eventId"]])).digest()
                else:
                    record = LatestSnapshot(equipment_id=equipment, task_no=event["taskNo"], observed_at=event["observedAt"],
                        quality=event["quality"], local_values=local, ingest_receipt_id=receipt.id,
                        source_sample_key=hashlib.sha256(canonical_bytes([producer["producerId"], event["eventId"]])).digest(),
                        created_at=now, updated_at=now)
                    db.add(record)
                    await db.flush()
            if outcome == "stored":
                for slot in used:
                    if slot.first_used_at is None:
                        slot.first_used_at = now
            receipt.outcome = outcome
            receipt.result_record_id = record.id if record else None
            receipt.result_detail = {"stored": stored if outcome in ("stored", "already_stored") else [], "skipped": skipped}
            await db.flush()
            result = receipt_data(receipt)
            commit_started = True
            await db.commit()
            return result
        except IntegrityError:
            await db.rollback()
            if commit_started:
                reject("commit_unknown", 503)
            if attempt == 2:
                reject("not_ready", 503)
        except ObservationError:
            await db.rollback()
            raise
        except EvidenceUnavailable:
            await db.rollback()
            reject("not_ready", 503)
        except Exception:
            await db.rollback()
            reject("commit_unknown" if commit_started else "not_ready", 503)


async def energy(db, profile, producer, document):
    event = v2_domain.energy_event(document, producer)
    allowed = permitted_energy(producer, event["meterId"], event["groupKey"])
    if event["meterId"] not in profile["meters"] or not set(event["values"]).issubset(allowed):
        reject("forbidden", 403)
    for attempt in range(3):
        commit_started = False
        try:
            await verify_energy_target(db, profile["target"])
            now = await current_clock(db)
            previous = await _retry_receipt(db, EnergyReceipt, "energy", producer, event)
            if previous is not None:
                return previous
            query = select(EnergyMetric).where(EnergyMetric.meter_id == event["meterId"],
                EnergyMetric.group_key == event["groupKey"], EnergyMetric.metric_key.in_(list(event["values"])))
            rows = (await db.execute(query.order_by(EnergyMetric.metric_key).with_for_update())).scalars().all()
            configs = {row.metric_key: row for row in rows}
            if set(configs) != set(event["values"]) or any(not row.enabled for row in rows):
                reject("metric_scope")
            has_interval = any(row.measurement_mode == "interval" for row in rows)
            if has_interval != (event["intervalStartAt"] is not None):
                reject("invalid_time_range")
            values = {f"{configs[key].slot_no:02d}": v2_domain.scalar(value, "number")
                      for key, value in event["values"].items()}
            receipt = _receipt(EnergyReceipt, "energy", producer, event, document, now)
            db.add(receipt)
            await db.flush()
            row = EnergySample(meter_id=event["meterId"], group_key=event["groupKey"], observed_at=event["observedAt"],
                interval_start_at=event["intervalStartAt"], interval_end_at=event["intervalEndAt"],
                quality=event["quality"], local_values=values, ingest_receipt_id=receipt.id, created_at=now, updated_at=now)
            db.add(row)
            await db.flush()
            for config in rows:
                if config.first_used_at is None:
                    config.first_used_at = now
            receipt.outcome, receipt.result_record_id = "stored", row.id
            receipt.result_detail = {"stored": list(event["values"]), "skipped": []}
            await db.flush()
            result = receipt_data(receipt)
            commit_started = True
            await db.commit()
            return result
        except IntegrityError:
            await db.rollback()
            if commit_started:
                reject("commit_unknown", 503)
            if attempt == 2:
                reject("not_ready", 503)
        except ObservationError:
            await db.rollback()
            raise
        except EvidenceUnavailable:
            await db.rollback()
            reject("not_ready", 503)
        except Exception:
            await db.rollback()
            reject("commit_unknown" if commit_started else "not_ready", 503)
