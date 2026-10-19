"""equipment受限补缺事务与传动读adapter；不调用旧sync Service。"""
import re
from sqlalchemy.exc import DBAPIError, IntegrityError
from common.exceptions import BusinessException
from common.log import log_event
from app.equipment.mapping_error_codes import MappingError
from app.equipment.mapping_domain import fingerprint, utc_time, json_number, float_number
from app.equipment.crud import async_mapping_ingest as receipts
from app.equipment.crud import async_drive_sample as crud

DRIVE_FIELDS = ('tv', 'km', 'dew_point_set', 'dew_point_actual', 'oxygen', 'muffle_pressure', 'nh3_flow_set', 'nh3_flow_actual', 'ng_flow_set', 'ng_flow_actual', 'uncoiler_set', 'uncoiler_actual', 'entry_looper_set', 'entry_looper_actual', 'furnace_set', 'furnace_actual', 'exit_looper_set', 'exit_looper_actual', 'recoiler_set', 'recoiler_actual')

async def rollback(db):
    try:
        await db.rollback()
    except Exception:
        raise BusinessException(MappingError.UNAVAILABLE, code=503) from None

def unique_race(exc):
    args = getattr(exc.orig, "args", ())
    key = re.search(r" for key ['`]([^'`]+)['`]$", str(args[1])) if len(args) > 1 and args[0] == 1062 else None
    return bool(key and key[1].split(".")[-1] in {"uq_equipment_mapping_delivery", "uq_equipment_drive_http_business", "uq_equipment_production_parameters_http_business"})


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


async def receive_partial(db, sample, actor, stream, access, fields, new_values):
    digest = fingerprint(sample, stream)
    for attempt in range(3):
        committing = False
        try:
            receipt = await receipts.get_receipt(db, actor, sample.equipment_id, stream, sample.sample_id)
            if receipt is not None:
                if receipt.fingerprint != digest:
                    raise BusinessException(MappingError.SAMPLE_ID_CONFLICT, code=409)
                result = dict(receipt.result, outcome="duplicate", sample_id=sample.sample_id)
            else:
                record = await access.get_business_record(db, sample)
                supplied = {field: getattr(sample, field) for field in fields if field in sample.model_fields_set}
                outcome = "created"
                if record is None:
                    record = await access.add_record(db, equipment_id=sample.equipment_id, timestamp=sample.sampled_at,
                        **{field: supplied.get(field) for field in fields}, **new_values)
                else:
                    # Validate the entire merge before applying any mutation.
                    for field, value in supplied.items():
                        old = getattr(record, field)
                        if isinstance(value, float) and old is not None:
                            old = float_number(old)
                        if old is not None and old != value:
                            raise BusinessException(MappingError.VALUE_CONFLICT, code=409)
                    updates = {field: value for field, value in supplied.items() if getattr(record, field) is None}
                    for field, value in updates.items():
                        setattr(record, field, value)
                    outcome = "updated" if updates else "duplicate"
                    await db.flush()
                # Refresh reads actual persisted FLOAT values, also checking the public tolerance.
                # 已锁行可能晚于初查receipt的RR视图提交；refresh继续current read，避免普通快照漏行。
                await db.refresh(record, with_for_update=True)
                for field, value in supplied.items():
                    stored = getattr(record, field)
                    if isinstance(value, float) and (stored is None or (value != 0 and stored == 0) or abs(stored-value) > max(1e-6, abs(value)*1e-6)):
                        raise BusinessException(MappingError.INVALID_SAMPLE, code=422)
                result = dict(record_id=record.id, equipment_id=sample.equipment_id, sample_id=sample.sample_id,
                              sampled_at=utc_time(sample.sampled_at), outcome=outcome)
                target = {"drive_record_id": record.id} if stream == "drive" else {"parameter_record_id": record.id}
                await receipts.add_receipt(db, actor_user_id=actor, equipment_id=sample.equipment_id, stream=stream,
                    sample_id=sample.sample_id, fingerprint=digest, sampled_at=sample.sampled_at,
                    outcome=outcome, result=result, **target)
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
            unavailable = committing or isinstance(exc, DBAPIError)
            if unavailable:
                raise BusinessException(MappingError.UNAVAILABLE, code=503) from None
            raise BusinessException(MappingError.INTERNAL_ERROR, code=500) from None
        log_event("INFO", "equipment_mapping_received", actor_user_id=actor, equipment_id=sample.equipment_id,
                  stream=stream, record_id=result["record_id"], outcome=result["outcome"])
        return result

async def receive_sample(db, sample, actor):
    return await receive_partial(db, sample, actor, "drive", crud, DRIVE_FIELDS, {})

def drive_dashboard(record):
    if record is None:
        return dict(process_params={}, tension_params={}, process_items=[], tension_items=[])
    def single(key, unit, decimals):
        return dict(id={"muffle_pressure":"mufflePressure"}.get(key,key), kind="single", value=getattr(record, key), unit=unit, decimals=decimals)
    def compare(key, set_key, actual_key, unit, decimals, tolerance):
        set_value, actual = getattr(record, set_key), getattr(record, actual_key)
        deviation = actual-set_value if actual is not None and set_value is not None else None
        status = None if deviation is None else "normal" if abs(deviation) <= tolerance else "warning" if abs(deviation) <= 2*tolerance else "danger"
        return dict(id={"dew_point":"dewPoint", "nh3_flow":"nh3Flow", "ng_flow":"ngFlow", "entry_looper":"entryLooper", "exit_looper":"exitLooper"}.get(key,key), kind="compare", set=set_value, actual=actual, deviation=deviation, status=status, unit=unit, decimals=decimals)
    process = [single("tv", "", 0), single("km", "", 2), single("oxygen", "ppm", 0), single("muffle_pressure", "Pa", 0)]
    process += [compare(key, key+"_set", key+"_actual", unit, 2, tolerance) for key, unit, tolerance in
                (("dew_point", "℃", 5), ("nh3_flow", "m³/h", 10), ("ng_flow", "m³/h", 10))]
    tensions = [compare(key, key+"_set", key+"_actual", "kN", 2, 2) for key in ("uncoiler", "entry_looper", "furnace", "exit_looper", "recoiler")]
    return dict(record_id=record.id, sampled_at=utc_time(record.timestamp), process_params={field:getattr(record,field) for field in DRIVE_FIELDS[:10]},
                tension_params={field:getattr(record,field) for field in DRIVE_FIELDS[10:]}, process_items=process, tension_items=tensions)

async def read_samples(db, equipment_id, record_id=None, limit=100):
    records = await crud.list_records(db, equipment_id, record_id, limit)
    return dict(equipment_id=equipment_id, items=[dict(record_id=r.id, equipment_id=r.equipment_id,
        sampled_at=utc_time(r.timestamp), **{f:getattr(r,f) for f in DRIVE_FIELDS}) for r in records],
        dashboard=drive_dashboard(records[0] if records else None))
