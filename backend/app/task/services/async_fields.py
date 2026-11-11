"""字段定义读取、历史显示叠加及带修订号的事务发布。"""
from types import SimpleNamespace
from sqlalchemy import select
from app.task.models.fields import FieldConfigState, FieldDefinition
from app.task.domain import FIELD_NAME, invalid
from app.task.errors import TaskError, TaskErrorCode

ATTRS = ('name', 'value_type', 'label_zh_cn', 'label_en_us', 'unit', 'is_nullable', 'enabled',
         'sync_enabled', 'plan_editable', 'performance_editable', 'performance_owner',
         'plan_visible', 'performance_visible', 'plan_order', 'performance_order')
DISPLAY = {'label_zh_cn', 'label_en_us', 'plan_visible', 'performance_visible', 'plan_order', 'performance_order'}
INPUT = {'name':'name', 'type':'value_type', 'unit':'unit', 'isNullable':'is_nullable', 'enabled':'enabled',
         'syncEnabled':'sync_enabled', 'planEditable':'plan_editable', 'performanceEditable':'performance_editable',
         'performanceOwner':'performance_owner', 'planVisible':'plan_visible', 'performanceVisible':'performance_visible',
         'planOrder':'plan_order', 'performanceOrder':'performance_order'}
BOOLS = {'is_nullable', 'enabled', 'sync_enabled', 'plan_editable', 'performance_editable', 'plan_visible', 'performance_visible'}


async def config_state(db, lock=False):
    query = select(FieldConfigState).where(FieldConfigState.id == 1)
    state = (await db.execute(query.with_for_update() if lock else query)).scalar_one_or_none()
    if state is None:
        raise TaskError(TaskErrorCode.UNAVAILABLE, 503)
    return state


async def definitions(db, version, *, overlay=False, current=False):
    state = await config_state(db, lock=current)
    if type(version) is not int or not 1 <= version <= state.active_version:
        raise TaskError(TaskErrorCode.NOT_FOUND, 404)
    query = select(FieldDefinition).where(FieldDefinition.config_version == version).order_by(FieldDefinition.scope, FieldDefinition.slot_no)
    rows = list((await db.execute(query.with_for_update() if current else query)).scalars())
    if overlay and version != state.active_version:
        active_query = select(FieldDefinition).where(FieldDefinition.config_version == state.active_version)
        active = list((await db.execute(active_query.with_for_update() if current else active_query)).scalars())
        mapping = {(x.scope, x.slot_no): x for x in active}
        result = []
        for row in rows:
            values = {k: getattr(row, k) for k in ATTRS}
            now = mapping.get((row.scope, row.slot_no))
            if now is not None:
                values.update({k: getattr(now, k) for k in DISPLAY})
            result.append(SimpleNamespace(scope=row.scope, slot_no=row.slot_no, **values))
        return result
    return rows


def field_wire(row):
    return {'scope': row.scope, 'slotNo': row.slot_no, 'name': row.name, 'type': row.value_type,
            'labels': {'zh-CN': row.label_zh_cn, 'en-US': row.label_en_us}, 'unit': row.unit,
            'isNullable': row.is_nullable, 'enabled': row.enabled, 'syncEnabled': row.sync_enabled,
            'performanceOwner': row.performance_owner, 'planEditable': row.plan_editable,
            'performanceEditable': row.performance_editable, 'planVisible': row.plan_visible,
            'performanceVisible': row.performance_visible, 'planOrder': row.plan_order,
            'performanceOrder': row.performance_order}


async def read_config(db, module, version=None, integration=False, current=False):
    if module not in ('plan', 'performance'):
        invalid()
    state = await config_state(db, lock=current)
    version = state.active_version if version is None else version
    fields = await definitions(db, version, overlay=True, current=current)
    allowed = {'shared_sync', module + '_local'}
    return {'fieldConfigVersion': version, 'activeVersion': state.active_version,
            'configRevision': str(state.config_revision), 'fields': [field_wire(f) for f in fields
                 if f.scope in allowed and (f.enabled or not integration)]}


def validate_definition(row):
    if not isinstance(row['name'], str) or not FIELD_NAME.fullmatch(row['name']):
        invalid()
    if row['value_type'] not in ('string', 'number', 'boolean'):
        invalid()
    for key in ('label_zh_cn', 'label_en_us'):
        if not isinstance(row[key], str) or not row[key].strip() or len(row[key]) > 128:
            invalid()
    if row['unit'] is not None and (not isinstance(row['unit'], str) or len(row['unit']) > 32):
        invalid()
    for key in BOOLS:
        if type(row[key]) is not bool:
            invalid()
    for key in ('plan_order', 'performance_order'):
        if row[key] is not None and (type(row[key]) is not int or not 0 <= row[key] <= 65535):
            invalid()
    scope, owner = row['scope'], row['performance_owner']
    if scope == 'plan_local':
        if owner is not None or row['performance_editable'] or row['performance_visible'] or row['sync_enabled']:
            invalid()
    elif scope == 'performance_local':
        if owner not in ('automated', 'manual') or row['plan_editable'] or row['plan_visible'] or row['sync_enabled']:
            invalid()
    elif scope == 'shared_sync':
        if owner not in ('order_snapshot', 'automated', 'manual'):
            invalid()
        if row['sync_enabled'] and (owner not in ('automated', 'manual') or row['plan_editable']):
            invalid()
    else:
        invalid()
    if row['performance_editable'] and owner != 'manual':
        invalid()


async def save_config(db, payload):
    module = payload.get('module')
    if module not in ('plan', 'performance'):
        invalid()
    state = await config_state(db, lock=True)
    if payload.get('configRevision') != str(state.config_revision):
        raise TaskError(TaskErrorCode.CONFIG_REVISION_CONFLICT, 409)
    if payload.get('fieldConfigVersion') != state.active_version:
        raise TaskError(TaskErrorCode.FIELD_VERSION_CONFLICT, 409)
    changes = payload.get('changes')
    if not isinstance(changes, list):
        invalid()
    if not changes:
        return await read_config(db, module, current=True)
    current = await definitions(db, state.active_version, current=True)
    existing = {(f.scope, f.slot_no): f for f in current}
    merged = {(f.scope, f.slot_no): {'scope': f.scope, 'slot_no': f.slot_no,
                                     **{k: getattr(f, k) for k in ATTRS}} for f in current}
    touched = set()
    for change in changes:
        if not isinstance(change, dict) or set(change) - ({'scope', 'slotNo', 'labels'} | set(INPUT)):
            invalid()
        scope, slot = change.get('scope'), change.get('slotNo')
        key = (scope, slot)
        if scope not in ('shared_sync', module + '_local') or type(slot) is not int or not 1 <= slot <= 100 or key in touched:
            invalid()
        touched.add(key)
        row = merged.get(key)
        if row is None:
            if not {'name', 'type', 'labels'} <= set(change):
                invalid()
            row = {'scope': scope, 'slot_no': slot, 'name': None, 'value_type': None,
                   'label_zh_cn': None, 'label_en_us': None, 'unit': None,
                   **{name: False for name in BOOLS}, 'performance_owner': None,
                   'plan_order': None, 'performance_order': None}
            merged[key] = row
        if 'labels' in change:
            labels = change['labels']
            if not isinstance(labels, dict) or set(labels) != {'zh-CN', 'en-US'}:
                invalid()
            row['label_zh_cn'], row['label_en_us'] = labels['zh-CN'], labels['en-US']
        for input_name, attr in INPUT.items():
            if input_name not in change:
                continue
            if attr.startswith('plan_') and attr in DISPLAY and module != 'plan':
                invalid()
            if attr.startswith('performance_') and attr in DISPLAY and module != 'performance':
                invalid()
            row[attr] = change[input_name]
        prior = existing.get(key)
        if prior and any(row[k] != getattr(prior, k) for k in ('name', 'value_type', 'unit')):
            invalid()
        validate_definition(row)
    # A name keeps its historical slot; each module may not collide with the shared group.
    historical = list((await db.execute(select(FieldDefinition).with_for_update())).scalars())
    for key, row in merged.items():
        for old in historical:
            if (old.name == row['name'] and (old.scope, old.slot_no) != key
                    and (old.scope == row['scope'] or 'shared_sync' in (old.scope, row['scope']))):
                invalid()
    for scope in ('shared_sync', 'plan_local', 'performance_local'):
        names = [x['name'] for x in merged.values() if x['scope'] in ('shared_sync', scope)]
        if scope != 'shared_sync' and len(names) != len(set(names)):
            invalid()
    changed = [(key, row) for key, row in merged.items() if key not in existing or any(row[k] != getattr(existing[key], k) for k in ATTRS)]
    if not changed:
        return await read_config(db, module, current=True)
    business = any(key not in existing or any(row[k] != getattr(existing[key], k) for k in ATTRS if k not in DISPLAY) for key, row in changed)
    if business:
        state.active_version += 1
        for row in merged.values():
            db.add(FieldDefinition(config_version=state.active_version, **row))
    else:
        for key, row in changed:
            for attr in DISPLAY:
                setattr(existing[key], attr, row[attr])
    state.config_revision += 1
    await db.flush()
    return await read_config(db, module, current=True)
