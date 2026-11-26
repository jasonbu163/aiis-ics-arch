"""能源价格的查询和原子写入 SQL；旧 GET 在同一价格事实中构造完整小时。"""
from sqlalchemy import and_, exists, func, literal_column, select, true, update
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import aliased

from app.energy.models.energy_pricing import EnergyPriceHourMeta as Meta, EnergyPriceItem as Item, EnergyPriceItemHour as Value
from app.energy.pricing import BUILTIN_ITEMS, range_filters


async def items_for_update(db, keys):
    # 相同顺序锁住相关项目，使启停、单位变更和价格写入有一致的事务顺序。
    query = select(Item).where(Item.item_key.in_(keys)).order_by(Item.item_key).with_for_update()
    return {item.item_key: item for item in (await db.scalars(query)).all()}


async def item_has_price(db, key):
    query = select(Value.hour_start).where(Value.item_key == key).limit(1).with_for_update()
    return (await db.scalar(query)) is not None


async def list_items(db, predicate=True):
    return (await db.scalars(select(Item).where(predicate).order_by(Item.sort_order, Item.item_key))).all()


def database_time():
    return func.timestampadd(literal_column("HOUR"), 8, func.utc_timestamp(6))


async def upsert_hour(db, hour, prices, operator, observed, remark_fields):
    # 小时元数据是这一小时所有价格事务的共同锁。没有内置价格时不产生兼容事件。
    builtin = any(key in BUILTIN_ITEMS for key in prices)
    insert_meta = insert(Meta).values(hour_start=hour, has_builtin=False)
    await db.execute(insert_meta.on_duplicate_key_update(hour_start=Meta.hour_start))
    # 在小时锁取得后取实际写入时刻，避免等待前取时造成时间回退。
    now = await db.scalar(select(database_time()))
    updates = {**remark_fields}
    if builtin:
        updates.update(
            has_builtin=True, observed_at=observed, operator=operator,
            created_at=func.coalesce(Meta.created_at, now),
        )
    if updates:
        await db.execute(update(Meta).where(Meta.hour_start == hour).values(**updates, updated_at=now))
    for key, fields in prices.items():
        statement = insert(Value).values(
            item_key=key, hour_start=hour, observed_at=observed, operator=operator,
            created_at=now, updated_at=now, price=fields["price"], remark=fields.get("remark"),
        )
        writable = {**fields, "observed_at": observed, "operator": operator, "updated_at": now}
        await db.execute(statement.on_duplicate_key_update(**writable))
    query = (select(Meta.remark, Value).join(Value, Value.hour_start == Meta.hour_start)
             .where(Meta.hour_start == hour, Value.item_key.in_(prices)))
    return (await db.execute(query)).all()


async def current_values(db, now):
    latest = (
        select(Value.item_key, func.max(Value.hour_start).label("hour_start"))
        .where(Value.observed_at <= now).group_by(Value.item_key).subquery()
    )
    query = (select(Item, Value)
             .outerjoin(latest, latest.c.item_key == Item.item_key)
             .outerjoin(Value, and_(Value.item_key == Item.item_key, Value.hour_start == latest.c.hour_start))
             .where(Item.enabled).order_by(Item.sort_order, Item.item_key))
    return (await db.execute(query)).all()


async def pricing_hours(db, page, size, bounds):
    filters = range_filters(Meta.hour_start, bounds)
    columns = await list_items(
        db, Item.enabled | exists(select(1).where(Value.item_key == Item.item_key, *range_filters(Value.hour_start, bounds))),
    )
    total = await db.scalar(select(func.count()).select_from(Meta).where(*filters))
    if (page - 1) * size >= total:
        return columns, [], total
    page_hours = (
        select(Meta.hour_start, Meta.remark).where(*filters).order_by(Meta.hour_start.desc())
        .offset((page - 1) * size).limit(size).subquery()
    )
    query = select(page_hours.c.remark, Value).join(Value, Value.hour_start == page_hours.c.hour_start)
    rows = (await db.execute(query.order_by(Value.hour_start.desc(), Value.item_key))).all()
    return columns, rows, total


def legacy_projection():
    components = [aliased(Value, name=key + "_at_hour") for key in BUILTIN_ITEMS]
    statement = select(
        Meta.id, Meta.hour_start, Meta.remark, Meta.observed_at, Meta.operator, Meta.created_at,
        func.greatest(Meta.updated_at, *(component.updated_at for component in components)).label("updated_at"),
        *(component.price.label(key + "_price") for key, component in zip(BUILTIN_ITEMS, components)),
        *(component.remark.label(key + "_remark") for key, component in zip(BUILTIN_ITEMS, components)),
    ).select_from(Meta).where(Meta.has_builtin)
    for key, component in zip(BUILTIN_ITEMS, components):
        latest = select(Value.hour_start).where(
            Value.item_key == key, Value.hour_start <= Meta.hour_start,
        ).correlate(Meta).order_by(Value.hour_start.desc()).limit(1).scalar_subquery()
        statement = statement.join(component, and_(
            component.item_key == key, component.hour_start == latest, component.hour_start <= Meta.hour_start,
        ))
    return statement


async def current_price(db, now):
    statement = legacy_projection().where(Meta.observed_at <= now).order_by(Meta.observed_at.desc(), Meta.id.desc()).limit(1)
    return (await db.execute(statement)).mappings().first()


async def price_history(db, page, size, bounds):
    # 总数、分页与三个价格来源使用同一 SQL 快照，也适用于 READ COMMITTED。
    complete = legacy_projection().where(*range_filters(Meta.observed_at, bounds)).cte("complete_hours")
    count = select(func.count().label("total")).select_from(complete).subquery()
    offset = min((page - 1) * size, 2**63 - 1)
    paged = (select(complete).order_by(complete.c.observed_at.desc(), complete.c.id.desc())
             .offset(offset).limit(size).subquery())
    query = (select(count.c.total, *paged.c).select_from(count.outerjoin(paged, true()))
             .order_by(paged.c.observed_at.desc(), paged.c.id.desc()))
    rows = (await db.execute(query)).mappings().all()
    return [row for row in rows if row["id"] is not None], rows[0]["total"]


async def saved_legacy_price(db, hour):
    statement = legacy_projection().where(Meta.hour_start == hour)
    return (await db.execute(statement)).mappings().one()
