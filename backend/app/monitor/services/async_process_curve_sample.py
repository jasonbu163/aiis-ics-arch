"""不可变HTTP曲线事务及现有四图窄adapter，保留全部33观测。"""
import re
from sqlalchemy.exc import DBAPIError, IntegrityError
from common.exceptions import BusinessException
from common.log import log_event
from app.monitor.mapping_error_codes import MappingError
from app.monitor.mapping_domain import fingerprint, utc_time
from app.monitor.crud import async_process_curve_sample as crud, async_mapping_ingest as receipts
FIELDS = ('line_speed_set', 'line_speed_act', 'unc_set_tension_p', 'unc_act_tension_p', 'rec_set_tension_p', 'rec_act_tension_p', 'unc_set_tension_kg', 'rec_set_tension_kg', 'furn_set_tension_kg', 'furn_act_tension_kg', 'cool_fan1_set_fre', 'cool_fan1_act_fre', 'cool_fan2_set_fre', 'cool_fan2_act_fre', 'n2_total', 'elect_consum', 'h2_flow', 'n2_flow', 'oxygen_content', 'dew_point', 'muffle_pressure', 'z1_temp_set', 'z1_temp_act', 'z2_temp_set', 'z2_temp_act', 'z3_temp_set', 'z3_temp_act', 'z4_temp_set', 'z4_temp_act', 'z5_temp_set', 'z5_temp_act', 'z6_temp_set', 'z6_temp_act')
async def rollback(db):
    try:
        await db.rollback()
    except Exception:
        raise BusinessException(MappingError.UNAVAILABLE, code=503) from None

def unique_race(exc):
    args = getattr(exc.orig,"args",())
    key = re.search(r" for key ['`]([^'`]+)['`]$", str(args[1])) if len(args)>1 and args[0]==1062 else None
    return bool(key and key[1].split(".")[-1] in {"uq_monitor_mapping_delivery", "uq_monitor_curve_http_business"})


async def delivery_after_rejection(db, actor, equipment, sample_id, digest):
    """业务拒绝回滚后，在新一致性视图恢复已提交投递的优先级；不锁缺失回执。"""
    committing = False
    try:
        receipt = await receipts.get_receipt(db, actor, equipment, sample_id)
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


async def receive_sample(db, sample, actor):
    digest = fingerprint(sample,"process_curve")
    for attempt in range(3):
        committing = False
        try:
            receipt = await receipts.get_receipt(db,actor,sample.equipment_id,sample.sample_id)
            if receipt is not None:
                if receipt.fingerprint != digest:
                    raise BusinessException(MappingError.SAMPLE_ID_CONFLICT, code=409)
                result = dict(receipt.result,outcome="duplicate",sample_id=sample.sample_id)
            else:
                row = await crud.get_sample(db,sample.equipment_id,sample.sampled_at)
                outcome = "duplicate"
                if row is not None and row.fingerprint != digest:
                    raise BusinessException(MappingError.SAMPLE_TIME_CONFLICT, code=409)
                if row is None:
                    row = await crud.add_sample(db,equipment_id=sample.equipment_id,sampled_at=sample.sampled_at,
                        fingerprint=digest,device_id=None,coil_number=sample.coil_number,**{f:getattr(sample,f) for f in FIELDS})
                    await db.refresh(row)
                    for field in FIELDS:
                        value, stored = getattr(sample,field),getattr(row,field)
                        if isinstance(value,float) and (stored is None or (value != 0 and stored == 0) or abs(stored-value)>max(1e-6,abs(value)*1e-6)):
                            raise BusinessException(MappingError.INVALID_SAMPLE, code=422)
                    outcome = "created"
                result = dict(record_id=row.id,equipment_id=sample.equipment_id,sample_id=sample.sample_id,
                    sampled_at=utc_time(sample.sampled_at),outcome=outcome)
                await receipts.add_receipt(db,actor_user_id=actor,equipment_id=sample.equipment_id,sample_id=sample.sample_id,
                    fingerprint=digest,sampled_at=sample.sampled_at,outcome=outcome,result=result,curve_record_id=row.id)
            committing = True
            await db.commit()
        except BusinessException as exc:
            await rollback(db)
            if exc.error_code == MappingError.SAMPLE_ID_CONFLICT or exc.code >= 500:
                raise
            result = await delivery_after_rejection(db, actor, sample.equipment_id, sample.sample_id, digest)
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
            if committing or isinstance(exc,DBAPIError):
                raise BusinessException(MappingError.UNAVAILABLE, code=503) from None
            raise BusinessException(MappingError.INTERNAL_ERROR, code=500) from None
        log_event("INFO","monitor_mapping_received",actor_user_id=actor,equipment_id=sample.equipment_id,
                  stream="process_curve",record_id=result["record_id"],outcome=result["outcome"])
        return result

async def read_samples(db,equipment,day,record_id=None,limit=1000):
    records = await crud.list_samples(db,equipment,day,record_id,limit)
    items = [dict(record_id=r.id,equipment_id=r.equipment_id,sampled_at=utc_time(r.sampled_at),coil_number=r.coil_number,
                  **{f:getattr(r,f) for f in FIELDS}) for r in records]
    trends = []
    for row in items:
        trends.append(dict(row,time=row["sampled_at"],unc_tension=row["unc_act_tension_p"],rec_tension=row["rec_act_tension_p"],
            furn_tension=row["furn_act_tension_kg"],oxygen=row["oxygen_content"],pressure=row["muffle_pressure"]))
    return dict(equipment_id=equipment,items=items,trends=trends,latest=trends[-1] if trends else {})
