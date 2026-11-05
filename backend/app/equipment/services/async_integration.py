"""equipment匿名业务事务；采用探针、实际业务、永久回执原子提交，未知提交不盲重做。"""
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
from app.equipment.crud import async_integration as crud
from app.equipment.integration_error_codes import IntegrationError as Error
from app.equipment.schemas import integration as dto


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
        log_event("INFO", "business_integration_committed", module="equipment", producer_id=envelope.producer_id,
            event_id=envelope.event_id, resource=resource, equipment_id=data.equipment_id,
            record_id=result.record_id, outcome=result.outcome)
        return result

from app.equipment.temperature_sample_domain import TEMPERATURE_FIELDS, fingerprint as temperature_fingerprint
from app.equipment.services.async_drive_sample import DRIVE_FIELDS
from app.equipment.services.async_production_parameter_sample import FIELDS as PARAMETER_FIELDS
FIELDS = {"temperature": TEMPERATURE_FIELDS, "drive": DRIVE_FIELDS, "production_parameters": PARAMETER_FIELDS}
TYPES = {"temperature": dto.TemperatureReceipt, "drive": dto.DriveReceipt, "production_parameters": dto.ProductionParameterReceipt}
UNIQUE_KEYS = {"uq_equipment_integration_delivery", "uq_temperature_sample_business", "uq_equipment_drive_http_business", "uq_equipment_production_parameters_http_business"}


async def receive_sample(db, envelope, adoption, resource):
    async def apply(db, envelope, digest, now):
        data = envelope.data
        fields = FIELDS[resource]
        values = {field:getattr(data,field) for field in fields if field in data.model_fields_set}
        if "entry_time" in values:
            values["entry_time"] = storage_time(values["entry_time"])
        time = storage_time(data.sampled_at)
        row = await crud.get_record(db, resource, data, time)
        updates = dict(values)
        outcome = "created"
        if row is not None:
            stored_floats = await crud.stored_float_values(db,resource,row.id)
            for field, value in values.items():
                old = stored_floats[field] if field in stored_floats else getattr(row,field)
                if isinstance(value,Decimal) and isinstance(old,float):
                    old = Decimal.from_float(old)
                if old is not None and old != value:
                    fail(Error.VALUE_CONFLICT)
            updates = {key:value for key,value in values.items() if getattr(row,key) is None}
            outcome = "updated" if updates else "duplicate"
            for key,value in updates.items():
                setattr(row,key,value)
        else:
            base = dict(equipment_id=data.equipment_id, **{field:values.get(field) for field in fields})
            if resource == "temperature":
                base.update(sampled_at=time, quality="good", fingerprint=temperature_fingerprint(legacy_sample(data)),
                    created_at=storage_time(now), updated_at=storage_time(now))
            else:
                base["timestamp"] = time
                if resource == "production_parameters":
                    base.update(coil_no=data.coil_no, http_coil_key=data.coil_no.encode("utf-8"), process_steps=[])
            row = await crud.add_record(db, resource, **base)
        await db.flush()
        await db.refresh(row, with_for_update=True)
        # 按实际列复核FLOAT32及NULL，不能拿请求回显替代持久目标。
        stored_floats = await crud.stored_float_values(db,resource,row.id)
        for field,value in values.items():
            stored = stored_floats[field] if field in stored_floats else getattr(row,field)
            if isinstance(value,Decimal) and isinstance(stored,float):
                stored=Decimal.from_float(stored)
            if stored != value:
                fail(Error.INVALID_REQUEST,422)
        aliases = type(data).model_fields
        return dict(recordId=row.id, performanceId=None, affectedRecordIds=[row.id],
            confirmation="business_committed", applied=outcome!="duplicate", outcome=outcome,
            changedFields=[aliases[key].alias for key in updates] if outcome=="updated" else []), {
                {"temperature":"temperature_record_id", "drive":"drive_record_id", "production_parameters":"parameter_record_id"}[resource]:row.id}
    return await transaction(db, envelope, adoption, resource, TYPES[resource], apply)
