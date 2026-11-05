"""performance匿名业务事务；采用探针、实际业务、永久回执原子提交，未知提交不盲重做。"""
from datetime import datetime, timezone
from decimal import Decimal
import re
from types import SimpleNamespace
from sqlalchemy.exc import DBAPIError, IntegrityError
from common.exceptions import BusinessException
from common.integration.canonical import integration_digests, DIGEST_PROFILE
from common.integration.receipt import receipt_response
from common.integration.envelope import CONTRACT_VERSION, validate_source_clock, shanghai_time
from common.integration.storage import to_storage_time as storage_time, to_legacy_time as legacy_time
from common.log import log_event
from app.performance.crud import async_integration as crud
from app.performance.integration_error_codes import IntegrationError as Error
from app.performance.schemas import integration as dto


def fail(error: Error, status=409):
    if error == Error.SCOPE_REJECTED:
        raise BusinessException(Error.SCOPE_REJECTED, code=status)
    if error == Error.PARENT_NOT_FOUND:
        raise BusinessException(Error.PARENT_NOT_FOUND, code=status)
    if error == Error.EVENT_CONFLICT:
        raise BusinessException(Error.EVENT_CONFLICT, code=status)
    if error == Error.VALUE_CONFLICT:
        raise BusinessException(Error.VALUE_CONFLICT, code=status)
    if error == Error.OBSERVATION_TIME_CONFLICT:
        raise BusinessException(Error.OBSERVATION_TIME_CONFLICT, code=status)
    if error == Error.PARENT_MISMATCH:
        raise BusinessException(Error.PARENT_MISMATCH, code=status)
    if error == Error.PAYLOAD_TOO_LARGE:
        raise BusinessException(Error.PAYLOAD_TOO_LARGE, code=status)
    if error == Error.MEDIA_TYPE:
        raise BusinessException(Error.MEDIA_TYPE, code=status)
    if error == Error.INVALID_REQUEST:
        raise BusinessException(Error.INVALID_REQUEST, code=status)
    if error == Error.NOT_READY:
        raise BusinessException(Error.NOT_READY, code=status)
    if error == Error.UNAVAILABLE:
        raise BusinessException(Error.UNAVAILABLE, code=status)
    if error == Error.COMMIT_UNKNOWN:
        raise BusinessException(Error.COMMIT_UNKNOWN, code=status)
    if error == Error.INTERNAL_ERROR:
        raise BusinessException(Error.INTERNAL_ERROR, code=status)
    raise BusinessException(Error.INTERNAL_ERROR, code=500)


async def rollback(db, unknown=False):
    try:
        await db.rollback()
    except Exception:
        fail(Error.COMMIT_UNKNOWN if unknown else Error.UNAVAILABLE, 503)


def unique_race(exc):
    args = getattr(exc.orig, "args", ())
    key = re.search(r" for key ['`]([^'`]+)['`]$", str(args[1])) if len(args)>1 and args[0]==1062 else None
    return bool(key and key[1].split(".")[-1] in UNIQUE_KEYS)


def source_values(envelope):
    return [ref.model_dump(by_alias=True, exclude_unset=True) for ref in envelope.source_refs]


def legacy_sample(data, float_fields=()):
    """只读旧摘要输入；保留UTC算法，绝不伪造actor/sampleId。"""
    values = {key:getattr(data,key) for key in type(data).model_fields}
    for key,value in values.items():
        if isinstance(value, datetime):
            values[key] = value.astimezone(timezone.utc).replace(tzinfo=None)
        elif key in float_fields and value is not None:
            values[key] = float(value)
    return SimpleNamespace(**values, model_fields_set=data.model_fields_set)


async def transaction(db, envelope, adoption, resource, receipt_type, apply, parent_id=None):
    request_digest, business_digest = integration_digests(envelope, resource, parent_id)
    data = envelope.data
    time = getattr(data, "sampled_at", None) or data.record_time
    for attempt in range(3):
        committing = False
        try:
            try:
                now = await crud.probe_adoption(db, adoption)
            except ValueError:
                fail(Error.NOT_READY, 503)
            validate_source_clock(time, now)
            previous = await crud.get_receipt(db, envelope.producer_id, envelope.event_id)
            if previous is not None:
                if previous.request_digest != request_digest:
                    fail(Error.EVENT_CONFLICT)
                result = receipt_type.model_validate(dict(previous.result, outcome="duplicate"))
            else:
                decision, targets = await apply(db, envelope, business_digest, now)
                try:
                    now = await crud.probe_adoption(db, adoption)
                except ValueError:
                    fail(Error.NOT_READY,503)
                if resource=="production_observation" and decision["outcome"] in ("created","updated"):
                    event=await crud.get_event(db,data.equipment_id,storage_time(time))
                    event.committed_at=event.created_at=event.updated_at=storage_time(now)
                row = await crud.add_receipt(db, producer_id=envelope.producer_id.encode("utf-8"),
                    event_id=envelope.event_id.encode("utf-8"), contract_version=CONTRACT_VERSION, digest_profile=DIGEST_PROFILE,
                    equipment_id=data.equipment_id, stream=resource, mapping_id=envelope.mapping_id,
                    mapping_revision=envelope.mapping_revision, source_refs=source_values(envelope),
                    request_digest=request_digest, business_digest=business_digest, source_time=storage_time(time),
                    committed_at=storage_time(now), outcome=decision["outcome"], result={},
                    created_at=storage_time(now), updated_at=storage_time(now), **targets)
                result = receipt_type.model_validate(dict(contractVersion=CONTRACT_VERSION, digestProfile=DIGEST_PROFILE,
                    producerId=envelope.producer_id, eventId=envelope.event_id, resource=resource,
                    equipmentId=data.equipment_id, mappingId=envelope.mapping_id, mappingRevision=envelope.mapping_revision,
                    requestDigest=request_digest, businessDigest=business_digest, receiptId=row.id,
                    sourceTime=shanghai_time(time), committedAt=shanghai_time(now), status="committed",
                    businessRetention="no_auto_ttl", originalOutcome=decision["outcome"], **decision))
                row.result = result.model_dump(by_alias=True)
                await db.flush()
            # DTO/result validation precedes commit; local HTTP adapter waits for every dependency exit.
            receipt_response(result)
            committing = True
            await db.commit()
        except BusinessException as exc:
            await rollback(db, committing)
            if committing:
                fail(Error.COMMIT_UNKNOWN,503)
            if exc.code in (404,409) and exc.error_code != Error.EVENT_CONFLICT:
                # 新事务current read恢复投递冲突优先级，不让RR旧快照把已提交身份漏掉。
                try:
                    await crud.probe_adoption(db, adoption)
                    previous = await crud.get_receipt(db, envelope.producer_id, envelope.event_id)
                    if previous is not None:
                        if previous.request_digest != request_digest:
                            fail(Error.EVENT_CONFLICT)
                        result = receipt_type.model_validate(dict(previous.result, outcome="duplicate"))
                        committing = True
                        await db.commit()
                    else:
                        await rollback(db, committing)
                        raise exc
                except BusinessException:
                    await rollback(db, committing)
                    if committing:
                        fail(Error.COMMIT_UNKNOWN,503)
                    raise
                except Exception:
                    await rollback(db, committing)
                    fail(Error.COMMIT_UNKNOWN if committing else Error.UNAVAILABLE, 503)
            else:
                raise
        except ValueError:
            await rollback(db, committing)
            fail(Error.COMMIT_UNKNOWN if committing else Error.INVALID_REQUEST,503 if committing else 422)
        except IntegrityError as exc:
            await rollback(db, committing)
            if not committing and unique_race(exc) and attempt < 2:
                continue
            fail(Error.COMMIT_UNKNOWN if committing else Error.UNAVAILABLE if unique_race(exc) else Error.INTERNAL_ERROR,
                 503 if committing or unique_race(exc) else 500)
        except Exception as exc:
            await rollback(db, committing)
            fail(Error.COMMIT_UNKNOWN if committing else Error.UNAVAILABLE if isinstance(exc, DBAPIError) else Error.INTERNAL_ERROR,
                 503 if committing or isinstance(exc, DBAPIError) else 500)
        log_event("INFO", "business_integration_committed", module="performance", producer_id=envelope.producer_id,
            event_id=envelope.event_id, resource=resource, equipment_id=data.equipment_id,
            record_id=result.record_id, outcome=result.outcome)
        return result

from app.performance.services.async_production_observation import OBSERVED_FIELDS, apply_weight, apply_duration as legacy_duration
from app.performance.mapping_domain import fingerprint, utc_time
UNIQUE_KEYS={"uq_performance_integration_delivery","uq_performance_main_http_business","uq_performance_observation_equipment",
    "uq_performance_integration_observation_time","uq_process_temperature_http_business","uq_process_tension_http_business","uq_process_speed_http_business"}


def apply_duration(record):
    try:
        legacy_duration(record)
    except BusinessException:
        fail(Error.INVALID_REQUEST,422)


async def receive_observation(db,envelope,adoption):
    async def apply(db,envelope,digest,now):
        data=envelope.data
        time=storage_time(data.sampled_at)
        wall=storage_time(now)
        state=await crud.state_for_update(db,data.equipment_id,wall)
        previous=await crud.get_event(db,data.equipment_id,time)
        if previous is not None:
            if previous.business_digest!=digest:
                fail(Error.OBSERVATION_TIME_CONFLICT)
            return dict(previous.result,outcome="duplicate",applied=False,changedFields=[]),dict(performance_id=previous.performance_id)
        if state.last_sampled_at is not None and time<=state.last_sampled_at:
            if time==state.last_sampled_at:
                # 旧水位cache不是本通道历史成功证明，不冒认相同毫秒。
                fail(Error.OBSERVATION_TIME_CONFLICT)
            return dict(recordId=None,performanceId=None,affectedRecordIds=[],confirmation="decision_only",applied=False,
                outcome="stale",changedFields=[]),dict(performance_id=None)
        locked=await crud.active_records(db,data.equipment_id,data.coil_no if data.observation_status=="in_production" else None)
        active=[row for row in locked if row.observation_status in ("in_production","unknown")]
        record=None
        outcome="updated"
        changed=[]
        if data.observation_status=="in_production":
            record=next((row for row in locked if row.http_coil_key==data.coil_no.encode("utf-8")),None)
            if record is None:
                record=await crud.add_performance(db,equipment_id=data.equipment_id,http_coil_key=data.coil_no.encode("utf-8"),
                    coil_no=data.coil_no,parent_coil_no=data.coil_no,plan_id=None,device_id=None,
                    production_date=data.sampled_at.date(),first_observed_at=time,last_observed_at=time,
                    record_source="external_observation",created_at=wall,updated_at=wall)
                outcome="created"
            for field in OBSERVED_FIELDS:
                if field in data.model_fields_set:
                    target="collected_weight" if field=="weight" else "reported_"+field if field in ("start_time","end_time") else field
                    value=getattr(data,field)
                    if isinstance(value,datetime):
                        value=storage_time(value)
                    if getattr(record,target)!=value:
                        changed.append(type(data).model_fields[field].alias)
                    setattr(record,target,value)
            apply_weight(record)
            record.observation_status="in_production"
            record.last_observed_at=time
            if record.first_observed_at is None:
                record.first_observed_at=time
            record.updated_at=wall
            apply_duration(record)
        affected=[]
        for old in active:
            if record is not None and old.id==record.id:
                continue
            old.observation_status="not_in_production" if record is not None else data.observation_status
            old.last_observed_at=time
            old.updated_at=wall
            apply_duration(old)
            affected.append(old.id)
        if record is not None:
            affected.append(record.id)
        target=record.id if record is not None else (active[-1].id if data.observation_status=="unknown" and active else None)
        decision=dict(recordId=target,performanceId=target,affectedRecordIds=affected,confirmation="business_committed",
            applied=bool(affected),outcome=outcome,changedFields=changed if outcome=="updated" else [])
        # cache保留owner旧算法/旧wire，不用bi-json摘要覆盖旧fingerprint列。
        state.last_sampled_at=time
        state.fingerprint=fingerprint(legacy_sample(data),"production_observation")
        state.performance_id=target
        state.observation_status=data.observation_status
        state.result=dict(record_id=target,affected_record_ids=affected,sampled_at=utc_time(legacy_sample(data).sampled_at),outcome=outcome)
        state.updated_at=wall
        await crud.add_event(db,equipment_id=data.equipment_id,sampled_at=time,business_digest=digest,
            observation_status=data.observation_status,performance_id=target,mapping_id=envelope.mapping_id,
            mapping_revision=envelope.mapping_revision,source_refs=source_values(envelope),result=decision,
            committed_at=wall,created_at=wall,updated_at=wall)
        return decision,dict(performance_id=target)
    return await transaction(db,envelope,adoption,"production_observation",dto.ProductionObservationReceipt,apply)
