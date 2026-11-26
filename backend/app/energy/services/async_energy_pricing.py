"""项目维护、按项目当前价和分时历史事务。"""
from enum import StrEnum

from sqlalchemy.exc import IntegrityError

from app.energy.crud import async_energy_price as crud
from app.energy.pricing import storage_bounds, storage_hour, storage_time
from app.energy.schemas.energy_pricing import CurrentPrice, PriceValue, PricingHour, PricingItem, PricingPage
from common.exceptions import BusinessException
from common.log import log_event
from app.energy.models.energy_pricing import EnergyPriceItem


class PricingError(StrEnum):
    DUPLICATE = "energy.pricing_item_exists"
    MISSING = "energy.pricing_item_missing"
    DISABLED = "energy.pricing_item_disabled"
    UNIT = "energy.pricing_unit_in_use"
    INVALID = "energy.pricing_item_invalid"


async def list_items(db):
    return [PricingItem.model_validate(item) for item in await crud.list_items(db)]


async def save_item(db, payload, operator, key=None):
    action = "create" if key is None else "update"
    try:
        if key is None:
            item = EnergyPriceItem(**payload.model_dump())
            db.add(item)
        else:
            item = (await crud.items_for_update(db, [key])).get(key)
            if item is None:
                raise BusinessException(PricingError.MISSING, 422)
            values = payload.model_dump(exclude_unset=True)
            if any(field in values and values[field] is None for field in ("unit", "sort_order", "enabled")):
                raise BusinessException(PricingError.INVALID, 422)
            if not (values.get("name_zh", item.name_zh) or values.get("name_en", item.name_en)):
                raise BusinessException(PricingError.INVALID, 422)
            if "unit" in values and values["unit"] != item.unit and await crud.item_has_price(db, key):
                raise BusinessException(PricingError.UNIT, 422)
            for field, value in values.items():
                setattr(item, field, value)
        result = PricingItem.model_validate(item)
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        log_event("ERROR", "energy_pricing.item", actor=operator, action=action, result="failed")
        if action == "create" and exc.orig.args[0] == 1062:
            raise BusinessException(PricingError.DUPLICATE, 409) from exc
        raise
    except Exception:
        await db.rollback()
        log_event("ERROR", "energy_pricing.item", actor=operator, action=action, result="failed")
        raise
    log_event("INFO", "energy_pricing.item", actor=operator, action=action, item_key=result.item_key, result="success")
    return result


async def current_prices(db, now):
    rows = await crud.current_values(db, storage_time(now))
    return [
        CurrentPrice(
            item_key=item.item_key, name_zh=item.name_zh, name_en=item.name_en, unit=item.unit,
            **({name: getattr(value, name) for name in PriceValue.model_fields} if value is not None else {}),
        )
        for item, value in rows
    ]


async def price_history(db, page, size, day):
    columns, rows, total = await crud.pricing_hours(db, page, size, storage_bounds(day))
    hours = {}
    for remark, value in rows:
        if value.hour_start not in hours:
            hours[value.hour_start] = PricingHour(hour_start=value.hour_start, remark=remark, values={})
        hours[value.hour_start].values[value.item_key] = PriceValue.model_validate(value)
    return PricingPage(
        columns=[PricingItem.model_validate(item) for item in columns], items=list(hours.values()),
        total=total, page=page, page_size=size,
    )


async def save_hour(db, payload, operator, observed):
    hour = storage_hour(observed)
    prices = {key: value.model_dump(exclude_unset=True) for key, value in payload.items.items()}
    total_remark = payload.model_dump(include={"remark"}, exclude_unset=True)
    try:
        definitions = await crud.items_for_update(db, prices)
        if set(definitions) != set(prices):
            raise BusinessException(PricingError.MISSING, 422)
        if any(not item.enabled for item in definitions.values()):
            raise BusinessException(PricingError.DISABLED, 422)
        saved = await crud.upsert_hour(db, hour, prices, operator, storage_time(observed), total_remark)
        values = {value.item_key: PriceValue.model_validate(value) for _, value in saved}
        result = PricingHour(hour_start=hour, remark=saved[0][0], values=values)
        result.model_dump(mode="json", by_alias=True)
        await db.commit()
    except Exception:
        await db.rollback()
        log_event("ERROR", "energy_pricing.save", actor=operator, result="failed")
        raise
    log_event("INFO", "energy_pricing.save", actor=operator, hour=hour.isoformat(), item_count=len(prices), result="success")
    return result
