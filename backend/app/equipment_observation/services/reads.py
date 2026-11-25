"""按权限读取最近采样任务、整包快照、真实历史和曲线缺测。"""
import json
from datetime import timedelta
from sqlalchemy import func, or_, select

from .guard import current_clock
from ..domain import identifier, reject, task_no, wire_time
from ..models import CardConfig, CurveGroup, HistorySample, LatestSnapshot, MetricConfig, MetricGroup, Receipt, SlotBinding, WriteSource
from ..profile import allowed_device, allowed_devices
from . import write_sources
from .registered_ingest import TARGET_MODELS
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


async def options(db, profile, user, include_deleted=False):
    await write_sources.check_profile(db, profile)
    if include_deleted and user.role != 'admin':
        reject('forbidden', 403)
    legacy = [{'equipmentId': key, 'nameZh': profile['devices'][key]['nameZh'],
               'nameEn': profile['devices'][key]['nameEn']} for key in sorted(allowed_devices(profile, user))]
    registered = await write_sources.visible_sources(db, include_deleted=include_deleted)
    return legacy + [
        {'equipmentId': row.storage_identity, 'nameZh': row.name or row.source_key,
         'nameEn': row.name or row.source_key, **write_sources.source_projection(row)}
        for row in registered
    ]


async def _registered_device(db, equipment):
    return (await db.execute(select(WriteSource).where(
        WriteSource.storage_identity == equipment, WriteSource.deleted_at.is_(None)
    ))).scalar_one_or_none()


async def public_latest(db, profile, source_key, target, task):
    key = write_sources.source_key(source_key)
    if target not in TARGET_MODELS:
        reject()
    normalized_task = task_no(task) if task is not None else None
    await write_sources.check_profile(db, profile)
    source = await write_sources.source_row(db, key)
    if source is None or source.deleted_at is not None:
        reject('not_found', 404)
    model = TARGET_MODELS[target]
    query = select(model).where(model.equipment_id == source.storage_identity)
    if normalized_task is not None:
        query = query.where(model.task_no == normalized_task)
    row = (await db.execute(query.order_by(model.observed_at.desc(), model.task_no, model.id.desc()).limit(1))).scalar_one_or_none()
    if row is None:
        return None
    maps = await _maps(db, target)
    items = {}
    for group, slots in row.local_values.items():
        for slot, value in slots.items():
            metric = maps.get((group, slot))
            if metric is not None:
                items.setdefault(group, {})[metric.metric_key] = value
    return {'sourceKey': key, 'target': target, 'taskNo': row.task_no, 'observedAt': wire_time(row.observed_at),
            'quality': row.quality, 'items': items}


async def task_candidates(db, profile, user, equipment):
    await write_sources.check_profile(db, profile)
    if await _registered_device(db, equipment) is None:
        allowed_device(profile, user, equipment)
    rows = (await db.execute(select(LatestSnapshot).where(LatestSnapshot.equipment_id == equipment)
            .order_by(LatestSnapshot.observed_at.desc(), LatestSnapshot.task_no.asc()))).scalars().all()
    tie = len(rows) > 1 and rows[0].observed_at == rows[1].observed_at
    return {'equipmentId': equipment, 'mostRecentTaskNo': rows[0].task_no if rows else None, 'tied': tie,
            'tasks': [{'taskNo': row.task_no, 'observedAt': wire_time(row.observed_at)} for row in rows]}


async def latest_cards(db, profile, user, equipment, page, language, selected=None):
    if page not in ('production', 'cleaning', 'temperature', 'drive'):
        reject()
    await write_sources.check_profile(db, profile)
    registered = await _registered_device(db, equipment)
    stale_seconds = 60 if registered is not None else allowed_device(profile, user, equipment)['staleAfterSeconds']
    now = await current_clock(db)
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
                state = freshness(now, sample.observed_at, stale_seconds)
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
                      start=None, end=None, category=None, metric_key=None, registered=()):
    allowed = allowed_devices(profile, user) | set(registered)
    if equipment is not None and equipment not in registered:
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


async def sample_data(db, row, target, maps=None, details=False, source=None):
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
    if source is not None:
        result.update(write_sources.source_projection(source))
    if target == 'history':
        result['reviewMark'] = row.review_mark
    if details:
        receipt = await db.get(Receipt, row.ingest_receipt_id)
        result['sourceRefs'] = receipt.source_refs if receipt else None
        result['mappingId'] = receipt.mapping_id if receipt else None
        result['mappingRevision'] = receipt.mapping_revision if receipt else None
        result['producerId'] = receipt.producer_id if receipt and source is None else None
    return result


async def samples(db, profile, user, target, filters, page, size, *, admin=False):
    await write_sources.check_profile(db, profile)
    sources = await write_sources.visible_sources(db, include_deleted=admin)
    registered = {row.storage_identity: row for row in sources}
    model = TARGET_MODELS[target]
    conditions = await _conditions(db, profile, user, model, registered=registered, **filters)
    total = (await db.execute(select(func.count()).select_from(model).where(*conditions))).scalar_one()
    rows = (await db.execute(select(model).where(*conditions).order_by(model.observed_at.desc(), model.id.desc())
                             .offset((page-1)*size).limit(size))).scalars().all()
    maps = await _maps(db, target)
    items = [await sample_data(db, row, target, maps, source=registered.get(row.equipment_id)) for row in rows]
    return {'items': items, 'total': total, 'page': page, 'pageSize': size,
            'totalPages': (total + size - 1) // size}


async def detail(db, profile, user, target, identity):
    await write_sources.check_profile(db, profile)
    model = TARGET_MODELS[target]
    sources = await write_sources.visible_sources(db, include_deleted=getattr(user, 'role', None) == 'admin')
    registered = {row.storage_identity: row for row in sources}
    allowed = allowed_devices(profile, user) | set(registered)
    row = (await db.execute(select(model).where(
        model.id == identity, model.equipment_id.in_(allowed)))).scalar_one_or_none()
    if row is None:
        reject('not_found', 404)
    return row, await sample_data(db, row, target, details=True, source=registered.get(row.equipment_id))


async def _curve_definitions(db, category):
    configs = (await db.execute(select(CurveGroup).where(CurveGroup.category == category, CurveGroup.enabled.is_(True))
                                .order_by(CurveGroup.sort_order, CurveGroup.curve_group_key))).scalars().all()
    if not configs:
        return []
    metrics = await _metrics(db)
    visible_groups = {row.group_key: row for row in
                      (await db.execute(select(MetricGroup).where(MetricGroup.enabled.is_(True)))).scalars()}
    slot_rows = (await db.execute(select(SlotBinding).where(SlotBinding.target == 'history'))).scalars().all()
    slots = {(slot.group_key, slot.metric_key): slot for slot in slot_rows}
    definitions = []
    for config in configs:
        series = []
        for item in config.series:
            if not item['enabled'] or item['metricKey'] not in metrics:
                continue
            metric = metrics[item['metricKey']]
            if metric.value_type != 'number' or metric.source_group_key not in visible_groups:
                continue
            slot = slots.get((metric.source_group_key, metric.metric_key))
            if slot is None:
                continue
            series.append((item, metric, visible_groups[metric.source_group_key], f'{slot.slot_no:02d}'))
        if series:
            definitions.append((config, series))
    return definitions


def _drawable_history_query(equipment, slots, task=None):
    numeric_slots = [
        func.json_type(func.json_extract(HistorySample.local_values, _json_path(group, slot))).in_(
            ('INTEGER', 'DOUBLE', 'DECIMAL')
        ) for group, slot in sorted(slots)
    ]
    query = select(HistorySample.equipment_id, HistorySample.task_no, HistorySample.observed_at).where(
        HistorySample.equipment_id.in_(sorted(equipment)), or_(*numeric_slots))
    if task is not None:
        query = query.where(HistorySample.task_no == task)
    return query.order_by(HistorySample.observed_at.desc(), HistorySample.id.desc())


async def history_default_context(db, profile, user, category, equipment, task=None):
    await write_sources.check_profile(db, profile)
    if category not in ('temperature', 'drive', 'cleaning'):
        reject()
    if equipment is not None:
        identifier(equipment)
        if await _registered_device(db, equipment) is None:
            allowed_device(profile, user, equipment)
        sources = {equipment}
    else:
        registered = await write_sources.visible_sources(db)
        sources = allowed_devices(profile, user) | {row.storage_identity for row in registered}
    if task is not None:
        task = task_no(task)
    definitions = await _curve_definitions(db, category)
    result = {'anchor': None, 'recentTasks': [], 'hasCurves': bool(definitions)}
    if not sources or not definitions:
        return result
    slots = {(metric.source_group_key, slot) for _, series in definitions for _, metric, _, slot in series}
    query = _drawable_history_query(sources, slots, task)
    row = (await db.execute(query.limit(1))).first()
    if row is None:
        return result
    stamp = wire_time(row.observed_at)
    result['anchor'] = {'equipmentId': row.equipment_id, 'taskNo': row.task_no, 'observedAt': stamp,
                        'from': wire_time(row.observed_at - timedelta(hours=8)), 'to': stamp}
    candidates = (await db.execute(_drawable_history_query({row.equipment_id}, slots).limit(100))).all()
    tasks = {}
    for candidate in candidates:
        tasks.setdefault(candidate.task_no, wire_time(candidate.observed_at))
    result['recentTasks'] = [{'taskNo': task, 'observedAt': observed} for task, observed in tasks.items()]
    return result


async def curves(db, profile, user, equipment, category, task, start, end, language):
    await write_sources.check_profile(db, profile)
    registered = await _registered_device(db, equipment)
    if registered is None:
        allowed_device(profile, user, equipment)
    if category not in ('temperature', 'drive', 'cleaning') or not start or not end:
        reject()
    conditions = await _conditions(db, profile, user, HistorySample, equipment=equipment, task=task, start=start, end=end,
                                   registered=(equipment,) if registered is not None else ())
    definitions = await _curve_definitions(db, category)
    rows = (await db.execute(select(HistorySample).where(*conditions)
                             .order_by(HistorySample.observed_at, HistorySample.id))).scalars().all() if definitions else []
    groups = []
    for config, definition in definitions:
        series = []
        unit = None
        for item, metric, group, slot_no in definition:
            unit = metric.unit
            points = []
            for row in rows:
                values = row.local_values.get(metric.source_group_key, {})
                present = slot_no in values
                points.append({'recordId': str(row.id), 'observedAt': wire_time(row.observed_at),
                               'present': present, 'value': values.get(slot_no) if present else None})
            rule = profile['historyRules'].get((equipment, metric.source_group_key))
            series.append({'groupKey': metric.source_group_key, 'groupLabel': _label(group, language),
                           'metricKey': metric.metric_key,
                           'label': _label(metric, language), 'points': points,
                           'lineStyle': item.get('lineStyle', 'solid'),
                           'intervalSeconds': rule['intervalSeconds'] if rule else None})
        if series:
            groups.append({'curveGroupKey': config.curve_group_key,
                           'title': config.title_en if language == 'en-US' else config.title_zh,
                           'unit': unit, 'series': series})
    return {'equipmentId': equipment, 'taskNo': task, 'groups': groups}
