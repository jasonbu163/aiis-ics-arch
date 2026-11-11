"""按任务号保存完整自动快照、人工值与同事务计划回写。"""
import hashlib
import json
from sqlalchemy import func, select
from app.performance.models.performance import Performance
from app.plan.models import Plan
from app.plan.services.async_workflow import lock_plan, upsert_plan, plan_wire, sync_plan
from app.task.domain import task_number, identifier, local_time, wire_time, value_patch, merge_values, decode_values, slot_key, invalid
from app.task.eligibility import admit, target_mapping
from app.task.errors import TaskError, TaskErrorCode
from app.task.services.async_fields import config_state, definitions


def conflict(key=TaskErrorCode.STATE_CONFLICT):
    raise TaskError(key, 409)


async def performance_by_id(db, row_id):
    row = (await db.execute(select(Performance).where(Performance.id == row_id))).scalar_one_or_none()
    if row is None:
        raise TaskError(TaskErrorCode.NOT_FOUND, 404)
    return row


async def performance_by_task(db, task_no):
    row = (await db.execute(select(Performance).where(Performance.task_no == task_number(task_no)))).scalar_one_or_none()
    if row is None:
        raise TaskError(TaskErrorCode.NOT_FOUND, 404)
    return row


async def performance_wire(db, row, *, detail=False, fields=None, has_plan=None, current=False):
    if fields is None:
        fields = await definitions(db, row.field_config_version, overlay=True, current=current)
    visible = None if detail else 'performance_visible'
    if has_plan is None:
        has_plan = (await db.execute(select(Plan.id).where(Plan.task_no == row.task_no))).scalar_one_or_none() is not None
    return {'id': str(row.id), 'taskNo': row.task_no, 'targetKey': row.target_key,
            'fieldConfigVersion': row.field_config_version, 'productionStatus': row.production_status,
            'remark': row.remark, 'createdAt': wire_time(row.created_at), 'updatedAt': wire_time(row.updated_at),
            'startedAt': wire_time(row.started_at), 'completedAt': wire_time(row.completed_at),
            'lastObservedAt': wire_time(row.last_observed_at), 'observationSeq': row.observation_seq,
            'recordSource': row.record_source, 'hasPlan': has_plan,
            'syncValues': decode_values(fields, row.sync_values, 'shared_sync', visible),
            'localValues': decode_values(fields, row.local_values, 'performance_local', visible)}


async def list_performances(db, filters):
    has_plan = select(Plan.id).where(Plan.task_no == Performance.task_no).exists().label('has_plan')
    query = select(Performance, has_plan)
    for request, column in (('taskNo', Performance.task_no), ('targetKey', Performance.target_key),
                            ('productionStatus', Performance.production_status)):
        if filters.get(request) is not None:
            value = (task_number(filters[request]) if request == 'taskNo' else
                     identifier(filters[request]) if request == 'targetKey' else filters[request])
            query = query.where(column == value)
    if filters.get('createdFrom') is not None:
        query = query.where(Performance.created_at >= local_time(filters['createdFrom']))
    if filters.get('createdTo') is not None:
        query = query.where(Performance.created_at < local_time(filters['createdTo']))
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    page, size = filters['page'], filters['pageSize']
    if (page - 1) * size >= total:
        return {'items': [], 'total': total, 'page': page, 'pageSize': size, 'totalPages': (total + size - 1) // size}
    order = ((Performance.created_at.asc(), Performance.id.asc()) if filters['sortOrder'] == 'asc'
             else (Performance.created_at.desc(), Performance.id.desc()))
    rows = (await db.execute(query.order_by(*order).offset((page-1)*size).limit(size))).all()
    cached, items = {}, []
    for row, plan_exists in rows:
        if row.field_config_version not in cached:
            cached[row.field_config_version] = await definitions(db, row.field_config_version, overlay=True)
        items.append(await performance_wire(db, row, fields=cached[row.field_config_version], has_plan=bool(plan_exists)))
    return {'items': items, 'total': total, 'page': page,
            'pageSize': size, 'totalPages': (total + size - 1) // size}


def complete_snapshot(fields, data, scope):
    required = {f.name for f in fields if f.scope == scope and f.enabled and f.performance_owner == 'automated'}
    if not isinstance(data, dict) or set(data) != required:
        invalid()
    return value_patch(fields, data, scope, 'automated')


def feedback(fields, patch):
    allowed = {slot_key(f.slot_no) for f in fields if f.scope == 'shared_sync' and f.enabled and f.sync_enabled
               and f.performance_owner in ('automated','manual')}
    return {key: value for key, value in patch.items() if key in allowed}


async def receive_snapshot(db, payload):
    task_no, target = task_number(payload['taskNo']), identifier(payload['targetKey'])
    version, producer = payload['fieldConfigVersion'], identifier(payload['producerId'])
    admit(target, producer, 'automatic', version)
    source = target_mapping(target, version)['automatic']['recordSource']
    state = await config_state(db, lock=True)
    plan = await lock_plan(db, task_no)
    row = (await db.execute(select(Performance).where(Performance.task_no == task_no).with_for_update())).scalar_one_or_none()
    bound = row.field_config_version if row else (plan.field_config_version if plan else state.active_version)
    if version != bound:
        conflict(TaskErrorCode.FIELD_VERSION_CONFLICT)
    if (plan and plan.target_key != target) or (row and (row.target_key != target or row.record_source != source)):
        conflict()
    fields = await definitions(db, version, current=True)
    sync = complete_snapshot(fields, payload['syncValues'], 'shared_sync')
    local = complete_snapshot(fields, payload['localValues'], 'performance_local')
    observed = local_time(payload['observedAt'])
    started, completed = local_time(payload.get('startedAt')), local_time(payload.get('completedAt'))
    if completed is not None and payload['productionStatus'] != 'completed':
        invalid()
    normalized = {'taskNo': task_no, 'targetKey': target, 'fieldConfigVersion': version,
                  'productionStatus': payload['productionStatus'], 'observedAt': wire_time(observed),
                  'startedAt': wire_time(started), 'completedAt': wire_time(completed),
                  'syncValues': sync, 'localValues': local}
    digest = hashlib.sha256(json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).digest()
    seq = payload['observationSeq']
    if row:
        if seq < row.observation_seq:
            outcome = 'late'
        elif seq == row.observation_seq:
            if digest != row.observation_digest:
                conflict(TaskErrorCode.OBSERVATION_CONFLICT)
            outcome = 'duplicate'
        elif row.production_status == 'completed':
            outcome = 'already_completed'
        else:
            outcome = 'updated'
        if outcome in ('late','duplicate','already_completed'):
            return {'taskNo': task_no, 'outcome': outcome, 'hasPlan': plan is not None,
                    'planSync': {'outcome': 'skipped', 'slots': [], 'reason': 'report_ignored'}}
    else:
        inherited = {}
        if plan:
            for field in fields:
                slot = slot_key(field.slot_no)
                if (field.scope == 'shared_sync' and field.enabled and field.performance_owner == 'order_snapshot'
                        and slot in (plan.sync_values or {})):
                    inherited[slot] = plan.sync_values[slot]
        row = Performance(task_no=task_no, target_key=target, field_config_version=version,
                          record_source=source, sync_values=inherited, local_values={})
        db.add(row)
        outcome = 'created'
    row.sync_values = merge_values(row.sync_values, sync)
    row.local_values = merge_values(row.local_values, local)
    row.production_status, row.observation_seq, row.observation_digest = payload['productionStatus'], seq, digest
    row.last_observed_at = observed
    if started is not None: row.started_at = started
    if completed is not None: row.completed_at = completed
    result = sync_plan(plan, fields, feedback(fields, sync), row.production_status)
    await db.flush()
    return {'taskNo': task_no, 'outcome': outcome, 'hasPlan': plan is not None, 'planSync': result}


async def edit_manual(db, payload):
    task_no = task_number(payload['taskNo'])
    await config_state(db, lock=True)
    plan = await lock_plan(db, task_no)
    row = (await db.execute(select(Performance).where(Performance.task_no == task_no).with_for_update())).scalar_one_or_none()
    if row is None:
        raise TaskError(TaskErrorCode.NOT_FOUND, 404)
    if payload['fieldConfigVersion'] != row.field_config_version:
        conflict(TaskErrorCode.FIELD_VERSION_CONFLICT)
    fields = await definitions(db, row.field_config_version, current=True)
    shared = value_patch(fields, payload.get('syncValues', {}), 'shared_sync', 'manual')
    local = value_patch(fields, payload.get('localValues', {}), 'performance_local', 'manual')
    new_shared, new_local = merge_values(row.sync_values, shared), merge_values(row.local_values, local)
    remark = payload['remark'] if 'remark' in payload else row.remark
    changed = new_shared != row.sync_values or new_local != row.local_values or remark != row.remark
    if changed:
        row.sync_values, row.local_values, row.remark = new_shared, new_local, remark
        result = sync_plan(plan, fields, feedback(fields, shared), row.production_status)
        await db.flush()
        await db.refresh(row)
    else:
        result = {'outcome':'skipped', 'slots': [], 'reason':'no_value_change' if plan else 'no_plan'}
    return {'outcome': 'updated' if changed else 'unchanged', 'performance': await performance_wire(db, row, detail=True, current=True), 'planSync': result}


async def supplement(db, row_id, payload):
    initial = await performance_by_id(db, row_id)
    await config_state(db, lock=True)
    plan = await lock_plan(db, initial.task_no)
    row = (await db.execute(select(Performance).where(Performance.id == row_id).with_for_update())).scalar_one_or_none()
    if row is None:
        raise TaskError(TaskErrorCode.NOT_FOUND, 404)
    if plan is not None:
        return {'outcome': 'existing', 'plan': await plan_wire(db, plan, detail=True, sensitive=True, current=True)}
    if payload['fieldConfigVersion'] != row.field_config_version:
        conflict(TaskErrorCode.FIELD_VERSION_CONFLICT)
    if identifier(payload['targetKey']) != row.target_key:
        conflict()
    values = {k:v for k,v in payload.items() if k != 'backfillExisting'}
    values['taskNo'] = row.task_no
    _, plan = await upsert_plan(db, values, human=True, allow_existing_performance=True,
                                forced_status='not_required', production_status=row.production_status)
    if payload.get('backfillExisting'):
        fields = await definitions(db, row.field_config_version, current=True)
        sync_plan(plan, fields, feedback(fields, row.sync_values), row.production_status)
        await db.flush()
        await db.refresh(plan)
    return {'outcome': 'created', 'plan': await plan_wire(db, plan, detail=True, sensitive=True, current=True)}
