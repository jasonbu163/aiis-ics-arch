"""管理员维护指标、独立槽位、卡片和曲线组。"""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..domain import identifier, reject
from ..models import CardConfig, CurveGroup, EnergyMetric, MetricConfig, MetricGroup, SlotBinding


def metric_data(row):
    return {"metricKey": row.metric_key, "sourceGroupKey": row.source_group_key, "category": row.category,
            "nameZh": row.name_zh, "nameEn": row.name_en, "valueType": row.value_type,
            "unit": row.unit, "decimals": row.decimals}


def binding_data(row):
    return {"target": row.target, "groupKey": row.group_key, "slotNo": row.slot_no,
            "metricKey": row.metric_key, "enabled": row.enabled,
            "listVisible": row.list_visible, "listOrder": row.list_order,
            "firstUsedAt": row.first_used_at.isoformat() + "+08:00" if row.first_used_at else None}


def card_data(row):
    return {"cardKey": row.card_key, "pageKey": row.page_key, "titleZh": row.title_zh,
            "titleEn": row.title_en, "enabled": row.enabled, "sortOrder": row.sort_order, "items": row.items}


def curve_data(row):
    return {"curveGroupKey": row.curve_group_key, "category": row.category, "titleZh": row.title_zh,
            "titleEn": row.title_en, "enabled": row.enabled, "sortOrder": row.sort_order,
            "series": [{"lineStyle": "solid", **item} for item in row.series]}


async def commit(db):
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        reject("configuration_conflict", 409)


async def metrics(db):
    rows = (await db.execute(select(MetricConfig).order_by(MetricConfig.metric_key))).scalars()
    return [metric_data(row) for row in rows]


async def create_metric(db, item):
    identifier(item.metric_key)
    identifier(item.source_group_key)
    identifier(item.category, 32)
    group = await db.get(MetricGroup, item.source_group_key)
    if group is None or group.category != item.category:
        reject("metric_scope")
    row = MetricConfig(**item.model_dump())
    db.add(row)
    await commit(db)
    return metric_data(row)


def group_data(row):
    return {"groupKey": row.group_key, "category": row.category, "nameZh": row.name_zh, "nameEn": row.name_en,
            "enabled": row.enabled, "sortOrder": row.sort_order}


async def save_group(db, item, key=None):
    if key is None:
        identifier(item.group_key)
        row = MetricGroup(**item.model_dump())
        db.add(row)
    else:
        row = (await db.execute(select(MetricGroup).where(MetricGroup.group_key == key).with_for_update())).scalar_one_or_none()
        if row is None:
            reject("not_found", 404)
        changes = item.model_dump(exclude_unset=True)
        if not changes or any(value is None for value in changes.values()):
            reject()
        if "category" in changes and changes["category"] != row.category:
            metrics = (await db.execute(select(MetricConfig).where(MetricConfig.source_group_key == key)
                                        .order_by(MetricConfig.metric_key).with_for_update())).scalars().all()
            keys = [metric.metric_key for metric in metrics]
            used = (await db.execute(select(SlotBinding.metric_key).where(SlotBinding.metric_key.in_(keys),
                SlotBinding.first_used_at.is_not(None)).limit(1).with_for_update())).first() if keys else None
            curves = (await db.execute(select(CurveGroup).with_for_update())).scalars().all()
            if used or any(any(entry["metricKey"] in keys for entry in curve.series) for curve in curves):
                reject("metric_in_use", 409)
            for metric in metrics:
                metric.category = changes["category"]
        for name, value in changes.items():
            setattr(row, name, value)
    await commit(db)
    return group_data(row)


def energy_metric_data(row):
    return {"meterId": row.meter_id, "groupKey": row.group_key, "metricKey": row.metric_key, "slotNo": row.slot_no,
            "nameZh": row.name_zh, "nameEn": row.name_en, "valueType": row.value_type, "quantityKey": row.quantity_key,
            "measurementMode": row.measurement_mode, "unit": row.unit, "decimals": row.decimals, "enabled": row.enabled,
            "listVisible": row.list_visible, "listOrder": row.list_order, "rules": row.rules,
            "firstUsedAt": row.first_used_at.isoformat() + "+08:00" if row.first_used_at else None}


def _energy_rules(rules):
    if not isinstance(rules, dict) or not set(rules).issubset({"continuityConfirmed", "maxGapSeconds"}):
        reject()
    if ("continuityConfirmed" in rules and type(rules["continuityConfirmed"]) is not bool
            or "maxGapSeconds" in rules and (type(rules["maxGapSeconds"]) is not int or rules["maxGapSeconds"] <= 0)):
        reject()


async def save_energy_metric(db, item, identity=None):
    changes = item.model_dump(exclude_unset=True)
    if identity is None:
        for key in ("meter_id", "group_key", "metric_key", "quantity_key"):
            identifier(changes[key])
        _energy_rules(changes.get("rules", {}))
        row = EnergyMetric(**item.model_dump())
        db.add(row)
    else:
        row = (await db.execute(select(EnergyMetric).where(EnergyMetric.meter_id == identity[0],
            EnergyMetric.group_key == identity[1], EnergyMetric.metric_key == identity[2]).with_for_update())).scalar_one_or_none()
        if row is None:
            reject("not_found", 404)
        if not changes or any(changes.get(key, "present") is None for key in
                              ("slot_no", "name_zh", "name_en", "value_type", "quantity_key", "measurement_mode", "enabled", "list_visible", "rules")):
            reject()
        if "rules" in changes:
            _energy_rules(changes["rules"])
        if row.first_used_at is not None and any(key in changes and changes[key] != getattr(row, key)
                for key in ("slot_no", "value_type", "quantity_key", "measurement_mode", "unit")):
            reject("metric_in_use", 409)
        for key, value in changes.items():
            setattr(row, key, value)
    await commit(db)
    return energy_metric_data(row)


async def update_metric(db, key, patch):
    row = (await db.execute(select(MetricConfig).where(MetricConfig.metric_key == key).with_for_update())).scalar_one_or_none()
    if row is None:
        reject("not_found", 404)
    changes = patch.model_dump(exclude_unset=True)
    if any(changes.get(name, "present") is None for name in ("name_zh", "name_en", "value_type")):
        reject()
    used = (await db.execute(select(SlotBinding.metric_key).where(
        SlotBinding.metric_key == key, SlotBinding.first_used_at.is_not(None)).limit(1).with_for_update())).first()
    if used and any(name in changes and getattr(row, name) != changes[name] for name in ("value_type", "unit")):
        reject("metric_in_use", 409)
    changing_to_non_number = "value_type" in changes and changes["value_type"] != "number" and changes["value_type"] != row.value_type
    changing_unit = "unit" in changes and changes["unit"] != row.unit
    if changing_to_non_number or changing_unit:
        # Locking reads see the latest committed curve configuration even under REPEATABLE READ.
        groups = (await db.execute(select(CurveGroup).with_for_update())).scalars().all()
        for group in groups:
            if changing_to_non_number and any(entry["metricKey"] == key for entry in group.series):
                reject("curve_items", 409)
            selected = [entry["metricKey"] for entry in group.series if entry["enabled"]]
            if not changing_unit or not group.enabled or key not in selected:
                continue
            others = (await db.execute(select(MetricConfig).where(
                MetricConfig.metric_key.in_([name for name in selected if name != key])))).scalars().all()
            if any(metric.unit != changes["unit"] for metric in others):
                reject("curve_units")
    for name, value in changes.items():
        setattr(row, name, value)
    await commit(db)
    return metric_data(row)


async def energy_metric_configs(db, meter_ids, group):
    if not meter_ids:
        return []
    query = select(EnergyMetric).where(EnergyMetric.meter_id.in_(meter_ids))
    if group:
        query = query.where(EnergyMetric.group_key == group)
    query = query.order_by(EnergyMetric.meter_id, EnergyMetric.group_key, EnergyMetric.slot_no, EnergyMetric.metric_key)
    return [energy_metric_data(row) for row in (await db.execute(query)).scalars().all()]


async def bindings(db, target, group):
    query = select(SlotBinding)
    if target is not None:
        if target not in ("latest", "history"):
            reject()
        query = query.where(SlotBinding.target == target)
    if group is not None:
        identifier(group)
        query = query.where(SlotBinding.group_key == group)
    rows = (await db.execute(query.order_by(SlotBinding.target, SlotBinding.group_key, SlotBinding.slot_no))).scalars().all()
    return {"items": [binding_data(row) for row in rows],
            "remaining": 100 - len(rows) if target is not None and group is not None else None}


async def create_binding(db, item):
    metric = await db.get(MetricConfig, item.metric_key)
    if metric is None or metric.source_group_key != item.group_key:
        reject("metric_scope")
    row = SlotBinding(**item.model_dump())
    db.add(row)
    await commit(db)
    return binding_data(row)


async def update_binding(db, target, group, number, patch):
    row = await db.get(SlotBinding, (target, group, number))
    if row is None:
        reject("not_found", 404)
    changes = patch.model_dump(exclude_unset=True)
    if not changes or any(changes.get(name, True) is None for name in ("enabled", "list_visible")):
        reject()
    for name, value in changes.items():
        setattr(row, name, value)
    await commit(db)
    return binding_data(row)


async def list_columns(db, target):
    if target not in ("latest", "history"):
        reject()
    query = (select(SlotBinding, MetricConfig).join(MetricConfig, MetricConfig.metric_key == SlotBinding.metric_key)
             .where(SlotBinding.target == target)
             .order_by(SlotBinding.list_order.is_(None), SlotBinding.list_order,
                       SlotBinding.group_key, SlotBinding.metric_key))
    rows = (await db.execute(query)).all()
    return {"target": target, "items": [
        {**binding_data(slot), **metric_data(metric)} for slot, metric in rows
    ]}


async def validate_items(db, items, category=None):
    keys = [item["metricKey"] for item in items]
    if len(keys) != len(set(keys)) or category is None and sum(item["enabled"] for item in items) > 10:
        reject("display_items")
    query = select(MetricConfig).where(MetricConfig.metric_key.in_(keys)).order_by(MetricConfig.metric_key)
    if category is not None:
        # Serialize curve admission with metric type/unit updates on the same rows.
        query = query.with_for_update()
    rows = (await db.execute(query)).scalars().all() if keys else []
    metrics = {row.metric_key: row for row in rows}
    if set(keys) != set(metrics):
        reject("display_items")
    if category is not None:
        chosen = [metrics[item["metricKey"]] for item in items if item["enabled"]]
        if any(metric.category != category or metric.value_type != "number" for metric in metrics.values()):
            reject("curve_items")
        if len({metric.unit for metric in chosen}) > 1:
            reject("curve_units")


async def save_display(db, model, key, data, category=None, existing=False):
    row = None
    if existing:
        row = await db.get(model, key, with_for_update=True) if model is CurveGroup else await db.get(model, key)
    if existing and row is None:
        reject("not_found", 404)
    if model is CurveGroup and "series" in data:
        previous = {item["metricKey"]: item.get("lineStyle", "solid") for item in row.series} if row else {}
        data = {**data, "series": [
            {"lineStyle": previous.get(item["metricKey"], "solid"), **item} for item in data["series"]
        ]}
    if row is None:
        row = model(**data)
        db.add(row)
    else:
        for name, value in data.items():
            setattr(row, name, value)
    items = row.series if model is CurveGroup else row.items
    await validate_items(db, items, row.category if model is CurveGroup else None)
    await commit(db)
    return curve_data(row) if model is CurveGroup else card_data(row)
