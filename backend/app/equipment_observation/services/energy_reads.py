"""受表计范围约束的原始能耗样本、只读统计与管理标注。"""
from sqlalchemy import func, select

from .guard import verify_energy_target
from ..domain import reject, wire_time
from ..models import EnergyMetric, EnergySample
from ..profile import allowed_meter
from .energy_statistics import summarize
from .v2_domain import observed_time, scalar


async def sample_data(db, row, metrics=None):
    if metrics is None:
        metrics = (await db.execute(select(EnergyMetric).where(EnergyMetric.meter_id == row.meter_id,
                   EnergyMetric.group_key == row.group_key))).scalars().all()
    slots = {f'{metric.slot_no:02d}': metric for metric in metrics}
    values = [{'metricKey': slots[key].metric_key, 'value': value, 'nameZh': slots[key].name_zh,
               'nameEn': slots[key].name_en, 'unit': slots[key].unit, 'measurementMode': slots[key].measurement_mode}
              for key, value in row.local_values.items() if key in slots]
    return {'id': str(row.id), 'meterId': row.meter_id, 'groupKey': row.group_key,
            'observedAt': wire_time(row.observed_at), 'quality': row.quality,
            'intervalStartAt': wire_time(row.interval_start_at), 'intervalEndAt': wire_time(row.interval_end_at),
            'values': values, 'remark': row.remark, 'reviewMark': row.review_mark,
            'createdAt': wire_time(row.created_at), 'updatedAt': wire_time(row.updated_at)}


async def samples(db, profile, user, meter, group, start, end, page, size):
    allowed_meter(profile, user, meter)
    await verify_energy_target(db, profile['target'])
    conditions = [EnergySample.meter_id == meter]
    if group:
        conditions.append(EnergySample.group_key == group)
    if start:
        conditions.append(EnergySample.observed_at >= observed_time(start))
    if end:
        conditions.append(EnergySample.observed_at <= observed_time(end))
    if start and end and observed_time(start) > observed_time(end):
        reject('invalid_time_range')
    count = (await db.execute(select(func.count()).select_from(EnergySample).where(*conditions))).scalar_one()
    rows = (await db.execute(select(EnergySample).where(*conditions)
            .order_by(EnergySample.observed_at.desc(), EnergySample.id.desc()).offset((page-1)*size).limit(size))).scalars().all()
    return {'items': [await sample_data(db, row) for row in rows], 'total': count, 'page': page,
            'pageSize': size, 'totalPages': (count+size-1)//size}


async def summary(db, profile, user, meter, group, metric_key, start, end):
    allowed_meter(profile, user, meter)
    await verify_energy_target(db, profile['target'])
    beginning, ending = observed_time(start), observed_time(end)
    if beginning >= ending:
        reject('invalid_time_range')
    config = await db.get(EnergyMetric, (meter, group, metric_key))
    if config is None:
        reject('not_found', 404)
    conditions = [EnergySample.meter_id == meter, EnergySample.group_key == group]
    if config.measurement_mode == 'interval':
        conditions.extend([EnergySample.interval_start_at < ending, EnergySample.interval_end_at > beginning])
    else:
        conditions.extend([EnergySample.observed_at >= beginning, EnergySample.observed_at <= ending])
    rows = (await db.execute(select(EnergySample).where(*conditions)
                             .order_by(EnergySample.observed_at, EnergySample.id))).scalars().all()
    slot = f'{config.slot_no:02d}'
    decoded = [{'observedAt': row.observed_at, 'quality': row.quality, 'value': row.local_values.get(slot),
                'intervalStartAt': row.interval_start_at, 'intervalEndAt': row.interval_end_at} for row in rows]
    result = summarize(config.measurement_mode, config.unit, decoded, beginning, ending, config.rules or {})
    for key in ('amount', 'latest'):
        if result[key] is not None:
            result[key] = scalar(result[key], 'number')
    return {'meterId': meter, 'groupKey': group, 'metricKey': metric_key, 'measurementMode': config.measurement_mode,
            'quantityKey': config.quantity_key, 'unit': config.unit, 'from': wire_time(beginning), 'to': wire_time(ending), **result}


async def detail(db, profile, user, identity):
    await verify_energy_target(db, profile['target'])
    row = await db.get(EnergySample, identity)
    if row is None or row.meter_id not in profile.get('meterReadScopes', {}).get(user.role, []):
        reject('not_found', 404)
    return row
