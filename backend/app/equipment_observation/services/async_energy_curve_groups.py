"""能耗曲线组的表计授权、曲线校验和事务合并。"""
from sqlalchemy.exc import IntegrityError

from ..crud import async_energy_curve_groups as crud
from ..domain import identifier, reject
from ..models import EnergyCurveGroup
from ..profile import allowed_meter
from .energy_meters import effective_profile
from .write_sources import commit


_FIELDS = ("title_zh", "title_en", "meter_id", "group_key", "sort_order", "enabled", "series")


def _data(row):
    return {
        "curveGroupKey": row.curve_group_key, "titleZh": row.title_zh, "titleEn": row.title_en,
        "meterId": row.meter_id, "groupKey": row.group_key, "sortOrder": row.sort_order,
        "enabled": row.enabled, "series": row.series,
    }


async def list_groups(db, profile, user, meter, *, enabled_only):
    profile = await effective_profile(db, profile)
    if meter is not None:
        allowed_meter(profile, user, meter)
        meter_ids = (meter,)
    else:
        meter_ids = profile["meterReadScopes"].get(user.role, ())
    return [_data(row) for row in await crud.list_groups(db, meter_ids, enabled_only)]


async def _validate(db, profile, user, values):
    meter = identifier(values["meter_id"])
    group = identifier(values["group_key"])
    allowed_meter(profile, user, meter)
    for field in ("title_zh", "title_en"):
        values[field] = values[field].strip()
    if not values["title_zh"] and not values["title_en"]:
        reject()

    series = values["series"]
    keys = [identifier(item["metricKey"]) for item in series]
    enabled = [item["metricKey"] for item in series if item["enabled"]]
    if not enabled or len(keys) != len(set(keys)):
        reject("curve_items")
    metrics = {row.metric_key: row for row in await crud.lock_metrics(db, meter, group, keys)}
    # 指标停用只影响写入，现有序列仍可用于历史展示。
    if set(metrics) != set(keys) or any(row.value_type != "number" for row in metrics.values()):
        reject("curve_items")
    units = {(metrics[key].quantity_key, metrics[key].unit or "") for key in enabled}
    if len(units) != 1:
        reject("curve_units")


async def create(db, profile, user, item):
    profile = await effective_profile(db, profile)
    key = identifier(item.curve_group_key)
    values = item.model_dump(exclude={"curve_group_key"})
    values["series"] = [entry.model_dump(by_alias=True) for entry in item.series]
    await _validate(db, profile, user, values)
    row = EnergyCurveGroup(curve_group_key=key, **values)
    db.add(row)
    try:
        await db.flush()
    except IntegrityError as exc:
        duplicate = (exc.orig.args[:1] == (1062,)
                     or getattr(exc.orig, "sqlite_errorname", "") == "SQLITE_CONSTRAINT_PRIMARYKEY")
        if not duplicate:
            raise
        await db.rollback()
        reject("configuration_conflict", 409)
    result = _data(row)
    await commit(db)
    return result


async def patch(db, profile, user, key, item):
    identifier(key)
    profile = await effective_profile(db, profile)
    changes = item.model_dump(exclude_unset=True)
    if not changes:
        reject()
    if "series" in changes:
        changes["series"] = [entry.model_dump(by_alias=True) for entry in item.series]
    row = await crud.lock_group(db, key)
    if row is None:
        reject("not_found", 404)
    allowed_meter(profile, user, row.meter_id)
    values = {field: getattr(row, field) for field in _FIELDS}
    values.update(changes)
    await _validate(db, profile, user, values)
    for field, value in values.items():
        setattr(row, field, value)
    result = _data(row)
    await commit(db)
    return result
