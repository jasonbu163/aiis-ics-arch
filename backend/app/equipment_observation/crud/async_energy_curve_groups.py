"""异步读写能耗曲线组和曲线指标引用。"""
from sqlalchemy import select

from ..models import EnergyCurveGroup, EnergyMetric


async def list_groups(db, meter_ids, enabled_only):
    if not meter_ids:
        return []
    query = select(EnergyCurveGroup).where(EnergyCurveGroup.meter_id.in_(meter_ids))
    if enabled_only:
        query = query.where(EnergyCurveGroup.enabled.is_(True))
    query = query.order_by(EnergyCurveGroup.sort_order, EnergyCurveGroup.curve_group_key)
    return (await db.execute(query)).scalars().all()


async def lock_group(db, key):
    query = select(EnergyCurveGroup).where(EnergyCurveGroup.curve_group_key == key).with_for_update()
    return (await db.execute(query)).scalar_one_or_none()


async def lock_metrics(db, meter, group, keys):
    query = select(EnergyMetric).where(
        EnergyMetric.meter_id == meter, EnergyMetric.group_key == group, EnergyMetric.metric_key.in_(keys)
    ).order_by(EnergyMetric.metric_key).with_for_update()
    return (await db.execute(query)).scalars().all()
