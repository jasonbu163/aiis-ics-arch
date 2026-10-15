"""能源小时整组更新事务；API 事件时刻固定，补历史不改变 current 排序。"""
from datetime import timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.energy.crud import async_energy_price as crud
from app.energy.schemas.energy_price import canonical_hour_start, HourlyPriceRecord, PriceCreate, PricePage, history_bounds
from common.log import log_event


async def current_price(db: AsyncSession, now):
    record = await crud.current_price(db, now.astimezone(timezone.utc).replace(tzinfo=None))
    return HourlyPriceRecord.model_validate(record) if record is not None else None


async def price_history(db: AsyncSession, page: int, page_size: int, day=None):
    rows, total = await crud.price_history(db, page, page_size, history_bounds(day) if day else None)
    return PricePage(items=[HourlyPriceRecord.model_validate(row) for row in rows], total=total, page=page, page_size=page_size)


async def save_price(db: AsyncSession, payload: PriceCreate, operator: str, observed_at):
    record_id = None
    values = payload.model_dump(exclude={"observed_at"})
    values["observed_at"] = observed_at.astimezone(timezone.utc).replace(tzinfo=None)
    values["hour_start"] = canonical_hour_start(observed_at).replace(tzinfo=None)
    try:
        record = await crud.upsert_price(db, values, operator)
        record_id = record.id
        result = HourlyPriceRecord.model_validate(record)
        # Serialize before commit too: no successful write followed by output-format failure.
        result.model_dump(mode="json", by_alias=True)
        await db.commit()
    except Exception:
        await db.rollback()
        log_event("ERROR", "energy_price.save", actor=operator, record_id=record_id, result="failed")
        raise
    log_event("INFO", "energy_price.save", actor=operator, record_id=record_id, result="success")
    return result
