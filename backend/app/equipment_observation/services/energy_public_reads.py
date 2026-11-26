"""按表计和采样组读取最新能耗事实及按采集时刻分页的历史样本。"""
from sqlalchemy import func, select, true
from sqlalchemy.orm import aliased

from common.integration.envelope import fact_time
from ..domain import identifier, reject, wire_time
from ..models import EnergyMetric, EnergySample
from .guard import verify_energy_target
from .v2_domain import observed_time


def _scope(model, meter, group):
    conditions = []
    if meter is not None:
        conditions.append(model.meter_id == identifier(meter))
    if group is not None:
        conditions.append(model.group_key == identifier(group))
    return conditions


def _query_time(value):
    try:
        return observed_time(fact_time(value))
    except ValueError:
        reject("invalid_observed_at")


async def _items(db, rows, meter, group):
    metrics = (await db.execute(
        select(EnergyMetric.meter_id, EnergyMetric.group_key, EnergyMetric.slot_no, EnergyMetric.metric_key)
        .where(*_scope(EnergyMetric, meter, group))
    )).all()
    keys = {(meter_id, group_key, f"{slot_no:02d}"): metric_key
            for meter_id, group_key, slot_no, metric_key in metrics}
    items = []
    for row in rows:
        values = {}
        for slot, value in row.local_values.items():
            metric_key = keys.get((row.meter_id, row.group_key, slot))
            if metric_key is not None and type(value) in (int, float):
                values[metric_key] = value
        item = {"meterId": row.meter_id, "groupKey": row.group_key, "observedAt": wire_time(row.observed_at),
                "quality": row.quality, "values": values}
        if row.interval_start_at is not None and row.interval_end_at is not None:
            item["intervalStartAt"] = wire_time(row.interval_start_at)
            item["intervalEndAt"] = wire_time(row.interval_end_at)
        items.append(item)
    return items


async def latest(db, profile, meter, group):
    conditions = _scope(EnergySample, meter, group)
    await verify_energy_target(db, profile["target"])
    rank = func.row_number().over(
        partition_by=(EnergySample.meter_id, EnergySample.group_key),
        order_by=(EnergySample.observed_at.desc(), EnergySample.id.desc()),
    )
    ranked = select(EnergySample.id, rank.label("sample_rank")).where(*conditions).subquery()
    rows = (await db.execute(
        select(EnergySample).join(ranked, EnergySample.id == ranked.c.id).where(ranked.c.sample_rank == 1)
        .order_by(EnergySample.meter_id, EnergySample.group_key)
    )).scalars().all()
    return {"items": await _items(db, rows, meter, group)}


async def history(db, profile, meter, group, start, end, page, size):
    conditions = _scope(EnergySample, meter, group)
    beginning, ending = _query_time(start), _query_time(end)
    if beginning > ending:
        reject("invalid_time_range")
    conditions.extend((EnergySample.observed_at >= beginning, EnergySample.observed_at <= ending))
    await verify_energy_target(db, profile["target"])
    offset = min((page - 1) * size, (1 << 63) - 1)
    page_rows = (
        select(EnergySample).where(*conditions).order_by(EnergySample.observed_at.desc(), EnergySample.id.desc())
        .offset(offset).limit(size).subquery()
    )
    sample = aliased(EnergySample, page_rows)
    totals = select(func.count().label("total")).select_from(EnergySample).where(*conditions).subquery()
    # 总数与当前页来自同一语句，即使读已提交且当前页为空也保留总数。
    rows = (await db.execute(
        select(totals.c.total, sample).select_from(totals).outerjoin(page_rows, true())
        .order_by(sample.observed_at.desc(), sample.id.desc())
    )).all()
    total = rows[0].total
    items = await _items(db, (row for _, row in rows if row is not None), meter, group)
    return {"items": items, "total": total, "page": page, "pageSize": size,
            "totalPages": (total + size - 1) // size}
