"""新旧能源价格接口的共用事务与旧三价响应映射。"""
from app.energy.crud import async_energy_price as crud
from app.energy.pricing import BUILTIN_ITEMS, storage_bounds, storage_hour, storage_time
from app.energy.schemas.energy_price import OUTPUT_ZONE, HourlyPriceRecord, PriceCreate, PricePage
from common.log import log_event
from sqlalchemy.ext.asyncio import AsyncSession


def legacy_record(row):
    values = dict(row)
    for field in ("created_at", "updated_at", "hour_start", "observed_at"):
        values[field] = values[field].replace(tzinfo=OUTPUT_ZONE)
    return HourlyPriceRecord.model_validate(values)


async def current_price(db: AsyncSession, now):
    record = await crud.current_price(db, storage_time(now))
    return legacy_record(record) if record is not None else None


async def price_history(db: AsyncSession, page: int, page_size: int, day=None):
    rows, total = await crud.price_history(db, page, page_size, storage_bounds(day))
    return PricePage(items=[legacy_record(row) for row in rows], total=total, page=page, page_size=page_size)


async def save_price(db: AsyncSession, payload: PriceCreate, operator: str, observed_at):
    hour = storage_hour(observed_at)
    prices = {key: {"price": getattr(payload, key + "_price"), "remark": getattr(payload, key + "_remark")}
              for key in BUILTIN_ITEMS}
    record_id = None
    try:
        # 旧协议始终允许写入内置三项，其显示状态只影响新入口。
        items = await crud.items_for_update(db, BUILTIN_ITEMS)
        if set(items) != set(BUILTIN_ITEMS):
            raise RuntimeError("builtin price items missing; verify the pricing migration")
        await crud.upsert_hour(db, hour, prices, operator, storage_time(observed_at), {"remark": payload.remark})
        result = legacy_record(await crud.saved_legacy_price(db, hour))
        record_id = result.id
        result.model_dump(mode="json", by_alias=True)
        await db.commit()
    except Exception:
        await db.rollback()
        log_event("ERROR", "energy_price.save", actor=operator, record_id=record_id, result="failed")
        raise
    log_event("INFO", "energy_price.save", actor=operator, record_id=record_id, result="success")
    return result
