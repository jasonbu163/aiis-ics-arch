"""能耗表计的数据库优先目录与事务化兼容覆盖。"""
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError

from ..domain import identifier, reject
from ..models import EnergyMeter
from .guard import current_clock, verify_energy_target
from .write_sources import commit


def _data(row):
    return {"meterId": row.meter_id, "nameZh": row.name_zh, "nameEn": row.name_en, "readRoles": row.read_roles}


def _legacy(profile, meter_id):
    meter = profile["meters"][meter_id]
    roles = sorted(role for role, meters in profile["meterReadScopes"].items() if meter_id in meters)
    return {**meter, "readRoles": roles}


async def catalog(db, profile):
    """每次请求使用独立快照，数据库表不可用时由路由报告失败。"""
    stored = (await db.execute(select(EnergyMeter))).scalars()
    meters = {key: _legacy(profile, key) for key in profile["meters"]}
    meters.update((row.meter_id, _data(row)) for row in stored)
    return meters


async def effective_profile(db, profile):
    await verify_energy_target(db, profile["target"])
    scopes = {}
    definitions = {}
    for key, meter in (await catalog(db, profile)).items():
        definitions[key] = {k: v for k, v in meter.items() if k != "readRoles"}
        for role in meter["readRoles"]:
            scopes.setdefault(role, []).append(key)
    return {**profile, "meters": definitions, "meterReadScopes": scopes}


def _fields(changes):
    if not changes or any(value is None for value in changes.values()):
        reject()
    if "read_roles" in changes:
        changes["read_roles"] = sorted(set(changes["read_roles"]))
    return changes


async def create(db, profile, key, changes):
    key = identifier(key)
    values = _fields(changes)
    if key in profile["meters"]:
        reject("configuration_conflict", 409)
    now = await current_clock(db)
    row = EnergyMeter(meter_id=key, created_at=now, updated_at=now, **values)
    db.add(row)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        reject("configuration_conflict", 409)
    result = _data(row)
    await commit(db)
    return result


async def change(db, profile, key, changes):
    key = identifier(key)
    values = _fields(changes)
    if key in profile["meters"]:
        legacy = _legacy(profile, key)
        now = await current_clock(db)
        seed = dict(meter_id=key, name_zh=legacy["nameZh"], name_en=legacy["nameEn"],
                    read_roles=legacy["readRoles"], created_at=now, updated_at=now)
        # 原子建行或锁定已有行，两个首次编辑不会从同一旧值覆盖各自字段。
        if db.get_bind().dialect.name == "sqlite":
            statement = sqlite_insert(EnergyMeter).values(**seed).on_conflict_do_nothing(index_elements=["meter_id"])
        else:
            statement = mysql_insert(EnergyMeter).values(**seed).on_duplicate_key_update(meter_id=EnergyMeter.meter_id)
        await db.execute(statement)
    query = select(EnergyMeter).where(EnergyMeter.meter_id == key).with_for_update()
    row = (await db.execute(query)).scalar_one_or_none()
    if row is None:
        await db.rollback()
        reject("not_found", 404)
    if any(getattr(row, field) != value for field, value in values.items()):
        for field, value in values.items():
            setattr(row, field, value)
        row.updated_at = await current_clock(db)
        await db.flush()
    result = _data(row)
    await commit(db)
    return result
