"""实绩的部分上报、人工反馈、订单快照和计划事务回写。"""
from sqlalchemy import select

from app.performance.models.performance import Performance
from app.plan.models import Plan
from app.plan.services.async_workflow import lock_plan, sync_plan
from app.task.crud.async_records import require_row, task_page, task_query
from app.task.domain import (apply_changes, base_wire, business_now, item_patch, local_time, matching_target,
                             merge_values, record_items, slot_key, task_number, wire_time)
from app.task.errors import TaskError, TaskErrorCode
from app.task.services.async_fields import current_config, record_use


def performance_wire(row, fields, has_plan):
    return {**base_wire(row, record_items(fields, row, 'performance')), 'hasPlan': has_plan,
            'startedAt': wire_time(row.started_at), 'completedAt': wire_time(row.completed_at),
            'lastObservedAt': wire_time(row.last_observed_at)}


async def find_performance(db, identity, *, by_task=False):
    _, fields = await current_config(db)
    row = await require_row(db, Performance, identity, by_task=by_task)
    has_plan = (await db.execute(select(task_query(Plan, row.task_no).exists()))).scalar_one()
    return performance_wire(row, fields, has_plan)


async def list_performances(db, filters):
    _, fields = await current_config(db)
    has_plan = select(Plan.id).where(Plan.task_no == Performance.task_no).exists()
    result, page = await task_page(db, Performance, filters, select(Performance, has_plan))
    return {**page, 'items': [performance_wire(row, fields, match) for row, match in result.all()]}


def _order_snapshot(fields, plan):
    if plan is None:
        return {}
    return {slot: plan.sync_values[slot] for field in fields
            if field.scope == 'shared_sync' and field.enabled
            and field.performance_owner in ('order_snapshot', 'snapshot_auto')
            and (slot := slot_key(field.slot_no)) in plan.sync_values}


async def upsert_performance(db, payload, *, human):
    task_no = task_number(payload['taskNo'])
    state, fields = await current_config(db, lock=True)
    plan = await lock_plan(db, task_no)
    row = (await db.execute(task_query(Performance, task_no).with_for_update())).scalar_one_or_none()
    if human and row is None:
        raise TaskError(TaskErrorCode.NOT_FOUND, 404, reason='task_not_found')
    target = matching_target(payload, row, plan, inherit=True)
    shared, local = item_patch(fields, payload.get('items'), 'performance', 'human' if human else 'integration')
    now = business_now()
    created = row is None
    if created:
        row = Performance(task_no=task_no, target_key=target, field_config_version=state.active_version,
                          production_status='running', sync_values=_order_snapshot(fields, plan), local_values={},
                          created_at=now, updated_at=now)
        db.add(row)
    patch = {'target_key': target, 'sync_values': merge_values(row.sync_values, shared),
             'local_values': merge_values(row.local_values, local)}
    for key, attr in (('productionStatus', 'production_status'), ('remark', 'remark')):
        if key in payload:
            patch[attr] = payload[key]
    for key, attr in (('startedAt', 'started_at'), ('completedAt', 'completed_at')):
        if key in payload:
            patch[attr] = local_time(payload[key], key)
    if not human and ('observedAt' in payload or shared or local):
        patch['last_observed_at'] = local_time(payload.get('observedAt'), 'observedAt')
    changed = apply_changes(row, patch, now)
    outcome = 'created' if created else 'updated' if changed else 'unchanged'

    await record_use(db, state.active_version, 'performance', task_no)
    # Flush the performance row first so rollback covers a failure during the following plan write.
    await db.flush()
    plan_sync = await sync_plan(db, plan, fields, shared, row.production_status, state.active_version, now,
                                sync_status=not human)
    await db.flush()
    return {'outcome': outcome, 'configVersion': state.active_version,
            'performance': performance_wire(row, fields, plan is not None), 'planSync': plan_sync}
