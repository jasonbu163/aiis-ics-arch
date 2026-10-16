"""完整样本接收与持久幂等；Service拥有完整commit/rollback及有界竞争恢复。"""
import re
from sqlalchemy.exc import DBAPIError, IntegrityError
from app.equipment.crud import async_temperature_sample as crud
from app.equipment.error_codes import TemperatureError
from app.equipment.schemas.temperature_sample_out import TemperatureSampleResult, TemperatureSampleOut, TemperatureSamplesOut
from app.equipment.temperature_sample_domain import TEMPERATURE_FIELDS, fingerprint
from common.exceptions import BusinessException
from common.log import log_event


async def _rollback(db):
    try:
        await db.rollback()
    except Exception:
        raise BusinessException(TemperatureError.UNAVAILABLE, code=503) from None


def _unique_race(exc):
    args = getattr(exc.orig, "args", ())
    if not args or args[0] != 1062 or len(args) < 2:
        return False
    key = re.search(r" for key ['`]([^'`]+)['`]$", str(args[1]))
    return bool(key and key[1].split(".")[-1] in {"uq_temperature_sample_business", "uq_temperature_sample_delivery"})


async def receive_sample(db, sample, actor_user_id):
    digest = fingerprint(sample)
    for attempt in range(3):
        committing = False
        try:
            receipt = await crud.get_receipt(db, actor_user_id, sample.equipment_id, sample.sample_id)
            if receipt is not None:
                if receipt.fingerprint != digest:
                    raise BusinessException(TemperatureError.SAMPLE_ID_CONFLICT, code=409)
                result = TemperatureSampleResult(record_id=receipt.sample_record_id, equipment_id=receipt.equipment_id,
                    sample_id=sample.sample_id, sampled_at=receipt.sampled_at, outcome="duplicate")
            else:
                record = await crud.get_sample(db, sample.equipment_id, sample.sampled_at)
                outcome = "duplicate"
                if record is not None and record.fingerprint != digest:
                    raise BusinessException(TemperatureError.SAMPLE_TIME_CONFLICT, code=409)
                if record is None:
                    record = await crud.add_sample(db, equipment_id=sample.equipment_id,
                        sampled_at=sample.sampled_at, quality=sample.quality, fingerprint=digest,
                        **{key: getattr(sample, key) for key in TEMPERATURE_FIELDS})
                    outcome = "created"
                await crud.add_receipt(db, actor_user_id=actor_user_id, equipment_id=sample.equipment_id,
                    sample_id=sample.sample_id, fingerprint=digest, sample_record_id=record.id,
                    sampled_at=sample.sampled_at, outcome=outcome)
                result = TemperatureSampleResult(record_id=record.id, equipment_id=sample.equipment_id,
                    sample_id=sample.sample_id, sampled_at=sample.sampled_at, outcome=outcome)
            committing = True
            await db.commit()
        except BusinessException as exc:
            await _rollback(db)
            log_event("WARNING", "temperature_sample_conflict", actor_user_id=actor_user_id, equipment_id=sample.equipment_id,
                      sample_id=sample.sample_id, error_code=exc.error_code.value)
            raise
        except IntegrityError as exc:
            await _rollback(db)
            if _unique_race(exc) and attempt < 2:
                continue
            log_event("ERROR", "temperature_sample_transaction_failed", actor_user_id=actor_user_id,
                      equipment_id=sample.equipment_id, sample_id=sample.sample_id)
            if _unique_race(exc):
                raise BusinessException(TemperatureError.UNAVAILABLE, code=503) from None
            raise BusinessException(TemperatureError.INTERNAL_ERROR, code=500) from None
        except Exception as exc:
            await _rollback(db)
            unavailable = committing or isinstance(exc, DBAPIError)
            log_event("ERROR", "temperature_sample_transaction_failed", actor_user_id=actor_user_id,
                      equipment_id=sample.equipment_id, sample_id=sample.sample_id)
            if unavailable:
                raise BusinessException(TemperatureError.UNAVAILABLE, code=503) from None
            raise BusinessException(TemperatureError.INTERNAL_ERROR, code=500) from None
        # 已提交后日志/响应失败交局部HTTP层返回500；客户端同键重试恢复，不再次补写。
        log_event("INFO", "temperature_sample_received", actor_user_id=actor_user_id,
                  equipment_id=sample.equipment_id, sample_id=sample.sample_id, record_id=result.record_id, outcome=result.outcome)
        return result


async def read_samples(db, equipment_id, record_id=None, limit=100):
    records = await crud.list_samples(db, equipment_id, record_id, limit)
    return TemperatureSamplesOut(equipment_id=equipment_id, items=[TemperatureSampleOut(
        record_id=record.id, equipment_id=record.equipment_id, sampled_at=record.sampled_at,
        quality=record.quality, created_at=record.created_at,
        **{key: getattr(record, key) for key in TEMPERATURE_FIELDS}) for record in records])
