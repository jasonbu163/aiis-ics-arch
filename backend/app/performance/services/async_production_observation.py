"""HTTP生产有序生命周期；水位、主行、回执同事务，人工重量优先。"""
import re
from datetime import timezone
from zoneinfo import ZoneInfo
from sqlalchemy import func
from sqlalchemy.exc import DBAPIError, IntegrityError
from common.exceptions import BusinessException
from common.log import log_event
from app.performance.mapping_error_codes import MappingError
from app.performance.mapping_domain import fingerprint, utc_time
from app.performance.crud import async_production_observation as crud, async_mapping_ingest as receipts

OBSERVED_FIELDS = ("grade", "weight", "total_length", "diameter", "density", "spec", "start_time", "end_time", "output_quantity", "qualified_quantity", "efficiency_rate", "quality_score", "remark")

async def rollback(db):
    try:
        await db.rollback()
    except Exception:
        raise BusinessException(MappingError.UNAVAILABLE, code=503) from None

def unique_race(exc):
    args = getattr(exc.orig, "args", ())
    key = re.search(r" for key ['`]([^'`]+)['`]$", str(args[1])) if len(args) > 1 and args[0] == 1062 else None
    return bool(key and key[1].split(".")[-1] in {"uq_performance_mapping_delivery", "uq_performance_main_http_business",
        "uq_performance_observation_equipment", "uq_process_temperature_http_business", "uq_process_tension_http_business", "uq_process_speed_http_business"})


async def delivery_after_rejection(db, actor, equipment, stream, sample_id, digest):
    """业务拒绝回滚后，在新一致性视图恢复已提交投递的优先级；不锁缺失回执。"""
    committing = False
    try:
        receipt = await receipts.get_receipt(db, actor, equipment, stream, sample_id)
        if receipt is None:
            await rollback(db)
            return None
        if receipt.fingerprint != digest:
            raise BusinessException(MappingError.SAMPLE_ID_CONFLICT, code=409)
        result = dict(receipt.result, outcome="duplicate", sample_id=sample_id)
        committing = True
        await db.commit()
        return result
    except BusinessException:
        await rollback(db)
        raise
    except Exception as exc:
        await rollback(db)
        if committing or isinstance(exc, DBAPIError):
            raise BusinessException(MappingError.UNAVAILABLE, code=503) from None
        raise BusinessException(MappingError.INTERNAL_ERROR, code=500) from None


async def transaction(db, sample, actor, stream, apply, **keys):
    digest = fingerprint(sample, stream, **keys)
    for attempt in range(3):
        committing = False
        try:
            receipt = await receipts.get_receipt(db, actor, sample.equipment_id, stream, sample.sample_id)
            if receipt is not None:
                if receipt.fingerprint != digest:
                    raise BusinessException(MappingError.SAMPLE_ID_CONFLICT, code=409)
                result = dict(receipt.result, outcome="duplicate", sample_id=sample.sample_id)
            else:
                if stream == "production_observation":
                    # 初查receipt（及认证读）可能已建立RR快照；尚未写业务，先结束该只读事务。
                    # 之后state FOR UPDATE本身不建立一致性视图，历史事件读在取得水位锁后才建新视图。
                    await rollback(db)
                result, targets = await apply(db, sample, digest)
                result.update(equipment_id=sample.equipment_id, sample_id=sample.sample_id)
                time = sample.sampled_at if stream == "production_observation" else sample.record_time
                await receipts.add_receipt(db, actor_user_id=actor, equipment_id=sample.equipment_id, stream=stream,
                    sample_id=sample.sample_id, fingerprint=digest, sampled_at=time, outcome=result["outcome"], result=result, **targets)
            committing = True
            await db.commit()
        except BusinessException as exc:
            await rollback(db)
            if exc.error_code == MappingError.SAMPLE_ID_CONFLICT or exc.code >= 500:
                raise
            result = await delivery_after_rejection(db, actor, sample.equipment_id, stream, sample.sample_id, digest)
            if result is None:
                raise
        except IntegrityError as exc:
            await rollback(db)
            if unique_race(exc) and attempt < 2:
                continue
            if unique_race(exc):
                raise BusinessException(MappingError.UNAVAILABLE, code=503) from None
            raise BusinessException(MappingError.INTERNAL_ERROR, code=500) from None
        except Exception as exc:
            await rollback(db)
            if committing or isinstance(exc, DBAPIError):
                raise BusinessException(MappingError.UNAVAILABLE, code=503) from None
            raise BusinessException(MappingError.INTERNAL_ERROR, code=500) from None
        log_event("INFO", "performance_mapping_received", actor_user_id=actor, equipment_id=sample.equipment_id,
            stream=stream, record_id=result.get("record_id"), outcome=result["outcome"])
        return result

def apply_duration(record):
    pairs = ((record.start_time, record.end_time, "manual_time"),
             (record.reported_start_time, record.reported_end_time, "reported_time"),
             (record.first_observed_at, record.last_observed_at, "external_observed"))
    # Reject invalid supplied pairs even if a higher-priority pair is available.
    for start, end, _ in pairs:
        if start is not None and end is not None and end < start:
            raise BusinessException(MappingError.INVALID_SAMPLE, code=422)
    for start, end, source in pairs:
        if start is not None and end is not None:
            seconds = int((end-start).total_seconds())
            if seconds > 2147483647:
                raise BusinessException(MappingError.INVALID_SAMPLE, code=422)
            record.total_duration_seconds = seconds
            record.total_duration_source = source
            return
    record.total_duration_seconds = None
    record.total_duration_source = "unavailable"

def apply_weight(record):
    if record.manual_override_weight is not None:
        # Existing manual source/audit and values are authoritative, including zero.
        return
    record.weight = record.collected_weight
    record.effective_weight = record.collected_weight
    record.effective_weight_source = "collected_weight" if record.collected_weight is not None else "unavailable"

async def apply_observation(db, sample, digest):
    state = await crud.state_for_update(db, sample.equipment_id)
    previous = await receipts.get_applied_event(db, sample.equipment_id, sample.sampled_at)
    if previous is not None:
        if previous.fingerprint != digest:
            raise BusinessException(MappingError.OBSERVATION_TIME_CONFLICT, code=409)
        return dict(previous.result, outcome="duplicate"), dict(performance_id=previous.performance_id)
    if state.last_sampled_at is not None and sample.sampled_at <= state.last_sampled_at:
        if sample.sampled_at == state.last_sampled_at:
            if state.fingerprint != digest:
                raise BusinessException(MappingError.OBSERVATION_TIME_CONFLICT, code=409)
            return dict(state.result, outcome="duplicate"), dict(performance_id=state.performance_id)
        return dict(record_id=state.performance_id, affected_record_ids=[], sampled_at=utc_time(sample.sampled_at), outcome="stale"), dict(performance_id=state.performance_id)
    active = await crud.active_records(db, sample.equipment_id)
    record = None
    outcome = "updated"
    if sample.observation_status == "in_production":
        record = await crud.by_coil(db, sample.equipment_id, sample.coil_no)
        if record is None:
            record = await crud.add_record(db, equipment_id=sample.equipment_id, http_coil_key=sample.coil_no.encode("utf-8"),
                coil_no=sample.coil_no, parent_coil_no=sample.coil_no, plan_id=None, device_id=None,
                production_date=sample.sampled_at.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("Asia/Shanghai")).date(),
                first_observed_at=sample.sampled_at, last_observed_at=sample.sampled_at, record_source="external_observation",
                output_quantity=None, qualified_quantity=None, efficiency_rate=None, quality_score=None)
            outcome = "created"
        for field in OBSERVED_FIELDS:
            if field in sample.model_fields_set:
                target = "collected_weight" if field == "weight" else "reported_"+field if field in ("start_time", "end_time") else field
                setattr(record, target, getattr(sample, field))
        apply_weight(record)
        record.observation_status = "in_production"
        record.last_observed_at = sample.sampled_at
        if record.first_observed_at is None:
            record.first_observed_at = sample.sampled_at
        apply_duration(record)
    affected = []
    for old in active:
        if record is not None and old.id == record.id:
            continue
        status = "not_in_production" if record is not None else sample.observation_status
        old_status = old.observation_status
        old.observation_status = status
        old.last_observed_at = sample.sampled_at
        apply_duration(old)
        affected.append(old.id)
        log_event("INFO", "performance_mapping_transition", equipment_id=sample.equipment_id, record_id=old.id,
                  old_status=old_status, new_status=status, outcome="staged")
    if record is not None:
        affected.append(record.id)
    current_id = record.id if record is not None else (active[-1].id if sample.observation_status == "unknown" and active else None)
    result = dict(record_id=record.id if record is not None else current_id, affected_record_ids=affected,
                  sampled_at=utc_time(sample.sampled_at), outcome=outcome)
    state.last_sampled_at = sample.sampled_at
    state.fingerprint = digest
    state.performance_id = current_id
    state.observation_status = sample.observation_status
    state.result = result
    await db.flush()
    return result, dict(performance_id=result["record_id"])

async def receive_observation(db, sample, actor):
    return await transaction(db, sample, actor, "production_observation", apply_observation)
