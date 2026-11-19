"""计划部分更新、同号读取及实绩回写。"""
from sqlalchemy import select

from app.performance.models import Performance
from app.plan.models.plan import Plan
from app.task.crud.async_records import require_row, task_page, task_query
from app.task.domain import (apply_changes, base_wire, business_now, invalid, item_patch, matching_target,
                             merge_values, record_items, slot_key, task_number)
from app.task.services.async_fields import current_config, record_use


async def lock_plan(db, task_no):
    return (await db.execute(task_query(Plan, task_no).with_for_update())).scalar_one_or_none()


def plan_wire(plan, fields):
    return {**base_wire(plan, record_items(fields, plan, 'plan')), 'priority': plan.priority}


async def find_plan(db, identity, *, by_task=False):
    _, fields = await current_config(db)
    return plan_wire(await require_row(db, Plan, identity, by_task=by_task), fields)


async def list_plans(db, filters):
    _, fields = await current_config(db)
    result, page = await task_page(db, Plan, filters, select(Plan))
    return {**page, 'items': [plan_wire(row, fields) for row in result.scalars()]}


async def upsert_plan(db, payload, *, human):
    task_no = task_number(payload['taskNo'])
    state, fields = await current_config(db, lock=True)
    plan = await lock_plan(db, task_no)
    performance = (await db.execute(task_query(Performance, task_no).with_for_update())).scalar_one_or_none()
    target = matching_target(payload, plan, performance)
    shared, local = item_patch(fields, payload.get('items'), 'plan', 'human' if human else 'integration')
    if payload.get('backfillExisting'):
        if plan is not None or performance is None:
            invalid('backfillExisting', 'existing_performance_without_plan_required')
        for field in fields:
            slot = slot_key(field.slot_no)
            if (field.scope == 'shared_sync' and field.enabled and field.sync_enabled
                    and slot not in shared and slot in performance.sync_values):
                shared[slot] = performance.sync_values[slot]

    now = business_now()
    outcome = 'created'
    if plan is None:
        status = performance.production_status if performance is not None else 'new'
        plan = Plan(task_no=task_no, target_key=target, field_config_version=state.active_version,
                    production_status=payload.get('productionStatus', status), priority=payload.get('priority', 5),
                    remark=payload.get('remark'), dispatch_status='not_required',
                    sync_values=merge_values({}, shared), local_values=merge_values({}, local),
                    created_at=now, updated_at=now)
        db.add(plan)
    else:
        patch = {'target_key': target, 'sync_values': merge_values(plan.sync_values, shared),
                 'local_values': merge_values(plan.local_values, local)}
        for field, attr in (('productionStatus', 'production_status'), ('priority', 'priority'), ('remark', 'remark')):
            if field in payload:
                patch[attr] = payload[field]
        outcome = 'updated' if apply_changes(plan, patch, now) else 'unchanged'
    await record_use(db, state.active_version, 'plan', task_no)
    await db.flush()
    return {'outcome': outcome, 'configVersion': state.active_version, 'plan': plan_wire(plan, fields)}


async def sync_plan(db, plan, fields, changes, status, version, now, *, sync_status):
    if plan is None:
        return {'outcome': 'skipped', 'reason': 'no_plan', 'statusChanged': False, 'fieldsChanged': []}
    before = plan.sync_values
    status_changed = sync_status and plan.production_status != status
    patch, names = {}, []
    for field in fields:
        slot = slot_key(field.slot_no)
        if field.scope == 'shared_sync' and field.enabled and field.sync_enabled and slot in changes:
            patch[slot] = changes[slot]
            if before.get(slot) != changes[slot]:
                names.append(field.name)
    updates = {'sync_values': merge_values(before, patch)}
    if sync_status:
        updates['production_status'] = status
    changed = apply_changes(plan, updates, now)
    if changed:
        await record_use(db, version, 'plan', plan.task_no)
    return {'outcome': 'synced' if changed else 'unchanged', 'reason': None,
            'statusChanged': status_changed, 'fieldsChanged': names}
