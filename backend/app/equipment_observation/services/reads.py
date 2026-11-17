"""按权限读取最近采样任务、整包快照、真实历史和曲线缺测。"""
import json
from datetime import timedelta
from sqlalchemy import func, or_, select

from ..services.guard import probe_target
from ..domain import identifier, reject, task_no, wire_time
from ..models import CardConfig, CurveGroup, HistorySample, LatestSnapshot, MetricConfig, MetricGroup, Receipt, SlotBinding
from ..profile import allowed_device, allowed_devices
from .v2_domain import observed_time


async def _maps(db, target):
    rows = (await db.execute(select(SlotBinding, MetricConfig).join(
        MetricConfig, MetricConfig.metric_key == SlotBinding.metric_key).where(SlotBinding.target == target))).all()
    return {(slot.group_key, f'{slot.slot_no:02d}'): metric for slot, metric in rows}


async def _metrics(db):
    return {row.metric_key: row for row in (await db.execute(select(MetricConfig))).scalars()}


def _json_path(*keys):
    return '$' + ''.join('.' + json.dumps(key, ensure_ascii=False) for key in keys)


def _label(row, language):
    return row.name_en if language == 'en-US' else row.name_zh


def freshness(now, observed_at, stale_after_seconds):
    return 'stale' if now - observed_at > timedelta(seconds=stale_after_seconds) else 'fresh'


async def options(profile, user):
    return [{'equipmentId': key, 'nameZh': profile['devices'][key]['nameZh'],
             'nameEn': profile['devices'][key]['nameEn']} for key in sorted(allowed_devices(profile, user))]


async def task_candidates(db, profile, user, equipment):
    allowed_device(profile, user, equipment)
    await probe_target(db, profile['target'])
    rows = (await db.execute(select(LatestSnapshot).where(LatestSnapshot.equipment_id == equipment)
            .order_by(LatestSnapshot.observed_at.desc(), LatestSnapshot.task_no.asc()))).scalars().all()
    tie = len(rows) > 1 and rows[0].observed_at == rows[1].observed_at
    return {'equipmentId': equipment, 'mostRecentTaskNo': rows[0].task_no if rows else None, 'tied': tie,
            'tasks': [{'taskNo': row.task_no, 'observedAt': wire_time(row.observed_at)} for row in rows]}


async def latest_cards(db, profile, user, equipment, page, language, selected=None):
    device = allowed_device(profile, user, equipment)
    if page not in ('production', 'cleaning', 'temperature', 'drive'):
        reject()
    now = await probe_target(db, profile['target'])
    query = select(LatestSnapshot).where(LatestSnapshot.equipment_id == equipment)
    if selected:
        query = query.where(LatestSnapshot.task_no == task_no(selected))
    rows = (await db.execute(query.order_by(LatestSnapshot.observed_at.desc(), LatestSnapshot.task_no.asc()))).scalars().all()
    if selected and not rows:
        reject('not_found', 404)
    sample = rows[0] if rows else None
    tied = not selected and len(rows) > 1 and rows[0].observed_at == rows[1].observed_at
    configs = (await db.execute(select(CardConfig).where(CardConfig.page_key == page, CardConfig.enabled.is_(True))
                                .order_by(CardConfig.sort_order, CardConfig.card_key))).scalars().all()
    metrics = await _metrics(db)
    visible_groups = set((await db.execute(select(MetricGroup.group_key).where(MetricGroup.enabled.is_(True)))).scalars())
    slots = (await db.execute(select(SlotBinding).where(SlotBinding.target == 'latest'))).scalars().all()
    bindings = {(slot.group_key, slot.metric_key): slot for slot in slots}
    cards = []
    for card in configs:
        items = []
        for item in card.items:
            if not item['enabled'] or item['metricKey'] not in metrics:
                continue
            metric = metrics[item['metricKey']]
            if metric.source_group_key not in visible_groups:
                continue
            slot = bindings.get((metric.source_group_key, metric.metric_key))
            group = sample.local_values.get(metric.source_group_key, {}) if sample else {}
            key = f'{slot.slot_no:02d}' if slot is not None else None
            present = key in group
            state = 'missing'
            if present:
                state = freshness(now, sample.observed_at, device['staleAfterSeconds'])
            items.append({'metricKey': metric.metric_key, 'label': _label(metric, language),
                          'value': group[key] if present else None, 'valueType': metric.value_type,
                          'unit': metric.unit, 'decimals': metric.decimals, 'sourceGroupKey': metric.source_group_key,
                          'observedAt': wire_time(sample.observed_at) if sample else None, 'dataState': state,
                          'quality': sample.quality if sample else None})
        if items:
            cards.append({'cardKey': card.card_key, 'title': card.title_en if language == 'en-US' else card.title_zh,
                          'items': items})
    return {'equipmentId': equipment, 'taskNo': sample.task_no if sample else None,
            'taskState': 'sampled' if sample else 'none', 'tied': tied,
            'observedAt': wire_time(sample.observed_at) if sample else None, 'cards': cards}


async def _conditions(db, profile, user, model, equipment=None, group=None, task=None,
                      start=None, end=None, category=None, metric_key=None):
    allowed = allowed_devices(profile, user)
    if equipment is not None:
        allowed_device(profile, user, equipment)
    conditions = [model.equipment_id.in_([equipment] if equipment else list(allowed))]
    if group:
        identifier(group)
        conditions.append(func.json_contains_path(model.local_values, 'one', _json_path(group)) == 1)
    if task:
        conditions.append(model.task_no == task_no(task))
    if start:
        conditions.append(model.observed_at >= observed_time(start))
    if end:
        conditions.append(model.observed_at <= observed_time(end))
    if start and end and observed_time(end) < observed_time(start):
        reject('invalid_time_range')
    if category:
        groups = (await db.execute(select(MetricConfig.source_group_key).where(MetricConfig.category == category).distinct())).scalars().all()
        conditions.append(or_(*[func.json_contains_path(model.local_values, 'one', _json_path(group)) == 1 for group in groups]) if groups else False)
    if metric_key:
        target = 'history' if model is HistorySample else 'latest'
        slots = (await db.execute(select(SlotBinding).where(
            SlotBinding.target == target, SlotBinding.metric_key == metric_key))).scalars().all()
        conditions.append(or_(*[func.json_contains_path(model.local_values, 'one', _json_path(slot.group_key, f'{slot.slot_no:02d}')) == 1
                                for slot in slots]) if slots else False)
    return conditions


async def sample_data(db, row, target, maps=None, details=False):
    maps = maps if maps is not None else await _maps(db, target)
    values = []
    for group, slots in row.local_values.items():
        for key, value in slots.items():
            metric = maps.get((group, key))
            if metric is not None:
                values.append({'groupKey': group, 'metricKey': metric.metric_key, 'nameZh': metric.name_zh,
                               'nameEn': metric.name_en, 'value': value, 'valueType': metric.value_type,
                               'unit': metric.unit, 'decimals': metric.decimals})
    result = {'id': str(row.id), 'equipmentId': row.equipment_id, 'groupKeys': list(row.local_values),
              'taskNo': row.task_no, 'observedAt': wire_time(row.observed_at), 'quality': row.quality,
              'values': values, 'remark': row.remark, 'createdAt': wire_time(row.created_at),
              'updatedAt': wire_time(row.updated_at)}
    if target == 'history':
        result['reviewMark'] = row.review_mark
    if details:
        receipt = await db.get(Receipt, row.ingest_receipt_id)
        result['sourceRefs'] = receipt.source_refs if receipt else None
        result['mappingId'] = receipt.mapping_id if receipt else None
        result['mappingRevision'] = receipt.mapping_revision if receipt else None
        result['producerId'] = receipt.producer_id if receipt else None
    return result


async def samples(db, profile, user, target, filters, page, size):
    await probe_target(db, profile['target'])
    model = HistorySample if target == 'history' else LatestSnapshot
    conditions = await _conditions(db, profile, user, model, **filters)
    total = (await db.execute(select(func.count()).select_from(model).where(*conditions))).scalar_one()
    rows = (await db.execute(select(model).where(*conditions).order_by(model.observed_at.desc(), model.id.desc())
                             .offset((page-1)*size).limit(size))).scalars().all()
    maps = await _maps(db, target)
    items = [await sample_data(db, row, target, maps) for row in rows]
    return {'items': items, 'total': total, 'page': page, 'pageSize': size,
            'totalPages': (total + size - 1) // size}


async def detail(db, profile, user, target, identity):
    await probe_target(db, profile['target'])
    model = HistorySample if target == 'history' else LatestSnapshot
    row = (await db.execute(select(model).where(
        model.id == identity, model.equipment_id.in_(allowed_devices(profile, user))))).scalar_one_or_none()
    if row is None:
        reject('not_found', 404)
    return row, await sample_data(db, row, target, details=True)


async def curves(db, profile, user, equipment, category, task, start, end, language):
    allowed_device(profile, user, equipment)
    await probe_target(db, profile['target'])
    if category not in ('temperature', 'drive', 'cleaning') or not start or not end:
        reject()
    configs = (await db.execute(select(CurveGroup).where(CurveGroup.category == category, CurveGroup.enabled.is_(True))
                                .order_by(CurveGroup.sort_order, CurveGroup.curve_group_key))).scalars().all()
    metrics = await _metrics(db)
    visible_groups = {row.group_key: row for row in
                      (await db.execute(select(MetricGroup).where(MetricGroup.enabled.is_(True)))).scalars()}
    slot_rows = (await db.execute(select(SlotBinding).where(SlotBinding.target == 'history'))).scalars().all()
    slots = {(slot.group_key, slot.metric_key): slot for slot in slot_rows}
    conditions = await _conditions(db, profile, user, HistorySample, equipment=equipment, task=task, start=start, end=end)
    rows = (await db.execute(select(HistorySample).where(*conditions)
                             .order_by(HistorySample.observed_at, HistorySample.id))).scalars().all()
    groups = []
    for config in configs:
        series = []
        unit = None
        for item in config.series:
            if not item['enabled'] or item['metricKey'] not in metrics:
                continue
            metric = metrics[item['metricKey']]
            if metric.source_group_key not in visible_groups:
                continue
            slot = slots.get((metric.source_group_key, metric.metric_key))
            if slot is None:
                continue
            unit = metric.unit
            slot_no = f'{slot.slot_no:02d}'
            points = []
            for row in rows:
                values = row.local_values.get(metric.source_group_key, {})
                present = slot_no in values
                points.append({'recordId': str(row.id), 'observedAt': wire_time(row.observed_at),
                               'present': present, 'value': values.get(slot_no) if present else None})
            rule = profile['historyRules'].get((equipment, metric.source_group_key))
            series.append({'groupKey': metric.source_group_key, 'groupLabel': _label(visible_groups[metric.source_group_key], language),
                           'metricKey': metric.metric_key,
                           'label': _label(metric, language), 'points': points,
                           'intervalSeconds': rule['intervalSeconds'] if rule else None})
        if series:
            groups.append({'curveGroupKey': config.curve_group_key,
                           'title': config.title_en if language == 'en-US' else config.title_zh,
                           'unit': unit, 'series': series})
    return {'equipmentId': equipment, 'taskNo': task, 'groups': groups}
