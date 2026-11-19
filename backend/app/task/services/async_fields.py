"""当前字段配置、历史快照和事务化使用证据。"""
from collections import Counter

from sqlalchemy import DateTime, JSON, and_, column, or_, select, table

from app.task.domain import FIELD_NAME, business_now, invalid, slot_key
from app.task.errors import TaskError, TaskErrorCode
from app.task.models.fields import FieldConfigState, FieldConfigUse, FieldConfigVersion, FieldDefinition

ATTRS = ('name', 'value_type', 'label_zh_cn', 'label_en_us', 'unit', 'is_nullable', 'enabled',
         'sync_enabled', 'plan_editable', 'performance_editable', 'performance_owner',
         'plan_visible', 'performance_visible', 'plan_order', 'performance_order')
DISPLAY = {'label_zh_cn', 'label_en_us', 'plan_visible', 'performance_visible', 'plan_order', 'performance_order'}
INPUT = {'name': 'name', 'type': 'value_type', 'unit': 'unit', 'isNullable': 'is_nullable',
         'enabled': 'enabled', 'syncEnabled': 'sync_enabled', 'planEditable': 'plan_editable',
         'performanceEditable': 'performance_editable', 'performanceOwner': 'performance_owner',
         'planVisible': 'plan_visible', 'performanceVisible': 'performance_visible',
         'planOrder': 'plan_order', 'performanceOrder': 'performance_order'}
BOOLS = {'is_nullable', 'enabled', 'sync_enabled', 'plan_editable', 'performance_editable', 'plan_visible', 'performance_visible'}
SCOPES = {'plan': 'plan_local', 'performance': 'performance_local', 'shared': 'shared_sync'}
RESERVED = {'id', 'taskNo', 'targetKey', 'producerId', 'productionStatus', 'remark', 'priority',
            'createdAt', 'updatedAt', 'startedAt', 'completedAt', 'observedAt', 'lastObservedAt',
            'observationSeq', 'hasPlan', 'items', 'fieldConfigVersion', 'configVersion', 'backfillExisting'}
IDENTITY = ('name', 'value_type', 'unit')

# 历史引用属于持久表合同，避免共享模块反向依赖计划和实绩模块。
HISTORICAL_SUBJECTS = {
    'plan': ('plan_main', 'task_no'),
    'performance': ('performance_main', 'task_no'),
    'dispatch': ('plan_dispatch_attempts', 'dispatch_id'),
}


async def _state(db, *, lock=False):
    query = select(FieldConfigState).where(FieldConfigState.id == 1)
    state = (await db.execute(query.with_for_update() if lock else query)).scalar_one_or_none()
    if state is None:
        raise TaskError(TaskErrorCode.UNAVAILABLE, 503, reason='configuration_missing')
    return state


async def current_config(db, *, lock=False):
    if lock:
        # All task mutations and configuration publication use the singleton as their first write lock.
        state = await _state(db, lock=True)
        query = select(FieldDefinition).where(FieldDefinition.config_version == state.active_version)
        fields = (await db.execute(query.order_by(FieldDefinition.scope, FieldDefinition.slot_no).with_for_update())).scalars().all()
        return state, fields
    # Read state and definitions in one statement, also on READ COMMITTED installations.
    query = (select(FieldConfigState, FieldDefinition)
             .outerjoin(FieldDefinition, FieldDefinition.config_version == FieldConfigState.active_version)
             .where(FieldConfigState.id == 1).order_by(FieldDefinition.scope, FieldDefinition.slot_no))
    rows = (await db.execute(query)).all()
    if not rows:
        raise TaskError(TaskErrorCode.UNAVAILABLE, 503, reason='configuration_missing')
    return rows[0][0], [field for _, field in rows if field is not None]


def field_wire(row):
    plan = row.scope != 'performance_local'
    performance = row.scope != 'plan_local'
    return {'scope': row.scope, 'slotNo': row.slot_no, 'name': row.name, 'type': row.value_type,
            'labels': {'zh-CN': row.label_zh_cn, 'en-US': row.label_en_us}, 'unit': row.unit,
            'isNullable': row.is_nullable, 'enabled': row.enabled,
            'syncEnabled': row.sync_enabled if row.scope == 'shared_sync' else None,
            'performanceOwner': row.performance_owner, 'planEditable': row.plan_editable if plan else None,
            'performanceEditable': row.performance_editable if performance else None,
            'planVisible': row.plan_visible if plan else None,
            'performanceVisible': row.performance_visible if performance else None,
            'planOrder': row.plan_order, 'performanceOrder': row.performance_order}


def _result(state, fields, module, *, integration=False):
    allowed = {'shared_sync', SCOPES[module]}
    return {'configVersion': state.active_version, 'configRevision': str(state.config_revision),
            'fields': [field_wire(field) for field in fields
                       if field.scope in allowed and (field.enabled or not integration)]}


async def read_config(db, module, *, integration=False):
    state, fields = await current_config(db)
    return _result(state, fields, module, integration=integration)


def _validate(row):
    name = row['name']
    if not isinstance(name, str) or not FIELD_NAME.fullmatch(name) or name in RESERVED:
        invalid('changes.name', 'invalid_field_name')
    if row['value_type'] not in ('string', 'number', 'boolean'):
        invalid('changes.type', 'invalid_field_type')
    for key in ('label_zh_cn', 'label_en_us'):
        if not isinstance(row[key], str) or not row[key].strip() or len(row[key]) > 128:
            invalid('changes.labels', 'invalid_label')
    if row['unit'] is not None and len(row['unit']) > 32:
        invalid('changes.unit', 'length_limit')
    for key in ('label_zh_cn', 'label_en_us', 'unit'):
        if row[key] is not None:
            try:
                row[key].encode('utf-8')
            except UnicodeEncodeError:
                invalid('changes', 'invalid_unicode')
    for key in BOOLS:
        if type(row[key]) is not bool:
            invalid('changes', 'invalid_boolean')
    for key in ('plan_order', 'performance_order'):
        if row[key] is not None and not 0 <= row[key] <= 65535:
            invalid('changes', 'invalid_display_order')
    scope, owner = row['scope'], row['performance_owner']
    if scope == 'plan_local':
        if owner is not None or row['performance_editable'] or row['performance_visible'] or row['performance_order'] is not None:
            invalid('changes', 'setting_not_applicable')
    elif scope == 'performance_local':
        if owner not in ('automated', 'manual'):
            invalid('changes.performanceOwner', 'invalid_field_owner')
        if row['plan_editable'] or row['plan_visible'] or row['plan_order'] is not None:
            invalid('changes', 'setting_not_applicable')
    elif owner not in ('order_snapshot', 'automated', 'manual'):
        invalid('changes.performanceOwner', 'invalid_field_owner')
    if row['sync_enabled'] and (scope != 'shared_sync' or owner == 'order_snapshot'):
        invalid('changes.syncEnabled', 'field_cannot_sync')
    if row['performance_editable'] and owner != 'manual':
        invalid('changes.performanceEditable', 'field_owner')


def _merge_change(row, change):
    if 'labels' in change:
        labels = change['labels']
        if not isinstance(labels, dict) or set(labels) != {'zh-CN', 'en-US'}:
            invalid('changes.labels', 'invalid_languages')
        row['label_zh_cn'], row['label_en_us'] = labels['zh-CN'], labels['en-US']
    for name, attr in INPUT.items():
        if name not in change:
            continue
        value = change[name]
        scope = row['scope']
        inapplicable = (attr.startswith('plan_') and scope == 'performance_local'
                        or attr.startswith('performance_') and scope == 'plan_local'
                        or attr == 'sync_enabled' and scope != 'shared_sync')
        if inapplicable:
            if value is not None:
                invalid(f'changes.{name}', 'setting_not_applicable')
        else:
            row[attr] = value
    _validate(row)


def _revision(state, expected):
    if expected != str(state.config_revision):
        raise TaskError(TaskErrorCode.CONFIG_REVISION_CONFLICT, 409, field='configRevision', reason='stale_revision')


def _values(field):
    return {'scope': field.scope, 'slot_no': field.slot_no, **{name: getattr(field, name) for name in ATTRS}}


def _publish(db, state, rows):
    state.active_version += 1
    now = business_now()
    new = [FieldDefinition(config_version=state.active_version, created_at=now, updated_at=now, **row) for row in rows]
    db.add_all(new)
    db.add(FieldConfigVersion(config_version=state.active_version, definition_count=len(new)))
    return new


async def save_config(db, payload):
    module = payload['module']
    state, fields = await current_config(db, lock=True)
    _revision(state, payload['configRevision'])
    existing = {(field.scope, field.slot_no): field for field in fields}
    merged = {key: _values(field) for key, field in existing.items()}
    touched = set()
    for change in payload['changes']:
        scope, slot = change['scope'], change['slotNo']
        key = (scope, slot)
        if scope != SCOPES[module]:
            invalid('changes.scope', 'scope_mismatch')
        if key in touched:
            invalid('changes.slotNo', 'duplicate_slot')
        touched.add(key)
        prior = existing.get(key)
        row = merged.setdefault(key, {'scope': scope, 'slot_no': slot, 'name': None, 'value_type': None,
                                     'label_zh_cn': None, 'label_en_us': None, 'unit': None,
                                     **dict.fromkeys(BOOLS, False), 'performance_owner': None,
                                     'plan_order': None, 'performance_order': None})
        _merge_change(row, change)
        if prior is not None and any(row[attr] != getattr(prior, attr) for attr in IDENTITY):
            invalid('changes', 'immutable_field_identity')
    for group in ('plan_local', 'performance_local'):
        names = [row['name'] for row in merged.values() if row['scope'] in ('shared_sync', group)]
        if len(names) != len(set(names)):
            invalid('changes.name', 'duplicate_field_name')
    changed = {key: row for key, row in merged.items() if key not in existing or row != _values(existing[key])}
    if not changed:
        return _result(state, fields, module)
    business = any(key not in existing or any(row[attr] != getattr(existing[key], attr)
                   for attr in set(ATTRS) - DISPLAY) for key, row in changed.items())
    if business:
        fields = _publish(db, state, [merged[key] for key in sorted(merged)])
    else:
        for key, row in changed.items():
            for attr in DISPLAY:
                setattr(existing[key], attr, row[attr])
            existing[key].updated_at = business_now()
    state.config_revision += 1
    state.updated_at = business_now()
    await db.flush()
    return _result(state, fields, module)


async def record_use(db, version, module, task_no):
    identity = {'config_version': version, 'subject_kind': module, 'subject_key': task_no}
    if await db.get(FieldConfigUse, identity, with_for_update=True) is None:
        db.add(FieldConfigUse(**identity))


def _in_use(reason):
    raise TaskError(TaskErrorCode.FIELD_IN_USE, 409, field='name', reason=reason)


async def _verify_subject_history(db, subject_kinds, histories, current):
    versions = {field.config_version: field for field in histories}
    continuous = current
    while continuous.config_version - 1 in versions:
        continuous = versions[continuous.config_version - 1]

    uses = FieldConfigUse.__table__
    for kind in subject_kinds:
        name, identity = HISTORICAL_SUBJECTS[kind]
        version = column('field_config_version')
        key = column(identity)
        columns = [version, key]
        conditions = [version.in_(versions), version.is_(None), version < 1, version > current.config_version,
                      uses.c.config_version.is_(None)]
        if kind != 'dispatch':
            values = column('sync_values' if current.scope == 'shared_sync' else 'local_values', JSON)
            updated = column('updated_at', DateTime())
            columns.extend((values, updated))
            # 旧任务更新后仍绑定创建版本。已存槽值或发布时间后的行变更需要使用证据。
            conditions.extend((values[slot_key(current.slot_no)].as_string().is_not(None),
                               updated >= continuous.created_at))
        subject = table(name, *columns)
        proof = subject.outerjoin(uses, and_(uses.c.subject_kind == kind,
                                             uses.c.subject_key == key,
                                             uses.c.config_version == version))
        query = select(version).select_from(proof).where(or_(*conditions)).limit(1).with_for_update()
        if (await db.execute(query)).first() is not None:
            _in_use('historical_usage_unverifiable')


async def delete_field(db, payload):
    state, fields = await current_config(db, lock=True)
    _revision(state, payload['configRevision'])
    scope, slot, name = payload['scope'], payload['slotNo'], payload['name']
    current = next((f for f in fields if (f.scope, f.slot_no, f.name) == (scope, slot, name)), None)
    if current is None:
        raise TaskError(TaskErrorCode.NOT_FOUND, 404, field='name', reason='field_identity_not_found')
    table = FieldConfigVersion
    versions = (await db.execute(select(table).order_by(table.config_version).with_for_update())).scalars().all()
    counts = Counter((await db.execute(select(FieldDefinition.config_version).with_for_update())).scalars())
    if len(versions) != state.active_version or any(
        v.config_version != index or counts.pop(index, 0) != v.definition_count
        for index, v in enumerate(versions, 1)
    ) or counts:
        _in_use('historical_configuration_unverifiable')
    histories = (await db.execute(select(FieldDefinition).where(
        FieldDefinition.scope == scope, FieldDefinition.slot_no == slot, FieldDefinition.name == name
    ).with_for_update())).scalars().all()
    if any(old.value_type != current.value_type or old.unit != current.unit for old in histories):
        _in_use('historical_field_identity_unverifiable')
    subject_kinds = ('plan', 'performance', 'dispatch') if scope == 'shared_sync' else (
        scope.removesuffix('_local'), 'dispatch')
    use = (await db.execute(select(FieldConfigUse.config_version).where(
        FieldConfigUse.config_version.in_([old.config_version for old in histories]),
        FieldConfigUse.subject_kind.in_(subject_kinds)
    ).limit(1).with_for_update())).first()
    if use is not None:
        _in_use('referenced_by_task_or_dispatch')
    await _verify_subject_history(db, subject_kinds, histories, current)
    _publish(db, state, [_values(field) for field in fields if field is not current])
    state.config_revision += 1
    state.updated_at = business_now()
    await db.flush()
    return {'outcome': 'deleted', 'scope': scope, 'slotNo': slot, 'name': name,
            'configVersion': state.active_version, 'configRevision': str(state.config_revision)}
