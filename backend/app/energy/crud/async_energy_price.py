"""小时价格 SQL：MySQL 唯一键原子整组 upsert；不控制事务。"""
from sqlalchemy import func, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.energy.models.energy_price_hour import EnergyPriceHour


def ordered_prices():
    return select(EnergyPriceHour).order_by(EnergyPriceHour.observed_at.desc(), EnergyPriceHour.id.desc())


def day_filters(bounds):
    if bounds is None:
        return ()
    start, end = bounds
    return (EnergyPriceHour.observed_at >= start,) + ((EnergyPriceHour.observed_at < end,) if end is not None else ())


async def current_price(db: AsyncSession, now):
    statement = ordered_prices().where(EnergyPriceHour.observed_at <= now).limit(1)
    return (await db.execute(statement)).scalar_one_or_none()


async def price_history(db: AsyncSession, page: int, page_size: int, bounds=None):
    filters = day_filters(bounds)
    total = (await db.execute(select(func.count()).select_from(EnergyPriceHour).where(*filters))).scalar_one()
    statement = ordered_prices().where(*filters).offset((page - 1) * page_size).limit(page_size)
    return (await db.execute(statement)).scalars().all(), total


def upsert_statement(values: dict, operator: str):
    statement = insert(EnergyPriceHour).values(**values, operator=operator)
    writable = ("electric_price", "hydrogen_price", "argon_price", "electric_remark",
                "hydrogen_remark", "argon_remark", "remark", "observed_at", "operator")
    return statement.on_duplicate_key_update(
        **{name: statement.inserted[name] for name in writable}, updated_at=func.utc_timestamp(6),
    )


async def upsert_price(db: AsyncSession, values: dict, operator: str):
    await db.execute(upsert_statement(values, operator))
    # The upsert retains the row lock until Service commits; read our complete snapshot.
    statement = select(EnergyPriceHour).where(EnergyPriceHour.hour_start == values["hour_start"]).execution_options(populate_existing=True)
    return (await db.execute(statement)).scalar_one()
