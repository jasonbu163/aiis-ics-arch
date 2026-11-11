"""计划写入、原子领取、批次报告及人工状态动作。"""
import hashlib
import json
from uuid import UUID, uuid4
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from app.plan.models.plan import Plan, DispatchAttempt, ActionEvent
from app.performance.models import Performance
from app.task.domain import task_number, identifier, local_time, wire_time, value_patch, merge_values, decode_values, slot_key, invalid
from app.task.eligibility import admit, get_profile, target_mapping
from app.task.errors import TaskError, TaskErrorCode
from app.task.services.async_fields import config_state, definitions


def conflict(key=TaskErrorCode.STATE_CONFLICT):
    raise TaskError(key, 409)


def uuid_string(value):
    try:
        result = str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        invalid()
    return result


async def lock_plan(db, task_no):
    return (await db.execute(select(Plan).where(Plan.task_no == task_no).with_for_update())).scalar_one_or_none()


async def plan_by_id(db, row_id, lock=False):
    query = select(Plan).where(Plan.id == row_id)
    row = (await db.execute(query.with_for_update() if lock else query)).scalar_one_or_none()
    if row is None:
        raise TaskError(TaskErrorCode.NOT_FOUND, 404)
    return row


async def plan_by_task(db, task_no):
    row = (await db.execute(select(Plan).where(Plan.task_no == task_number(task_no)))).scalar_one_or_none()
    if row is None:
        raise TaskError(TaskErrorCode.NOT_FOUND, 404)
    return row


def _ensure_mapping(target, version, fields, sync, local):
    mapping = target_mapping(target, version)
    by_name = {f.name: f for f in fields if f.enabled and f.scope in ('shared_sync', 'plan_local')}
    result = {}
    for name in mapping['dispatch']:
        field = by_name.get(name)
        if field is None or not field.plan_editable or field.sync_enabled:
            invalid()
        source = sync if field.scope == 'shared_sync' else local
        slot = slot_key(field.slot_no)
        if slot not in source:
            invalid()
        result[name] = decode_values([field], source, field.scope)[name]
    return result


def _changed(old, new):
    return old != new


async def upsert_plan(db, payload, *, human, allow_existing_performance=False, forced_status=None, production_status=None):
    task_no = task_number(payload.get('taskNo'))
    state = await config_state(db, lock=True)
    plan = await lock_plan(db, task_no)
    if not human:
        get_profile()
        if plan is not None:
            admit(plan.target_key, payload.get('producerId'), 'mes')
        if payload.get('targetKey') is not None:
            admit(payload['targetKey'], payload.get('producerId'), 'mes')
    perf = (await db.execute(select(Performance).where(Performance.task_no == task_no).with_for_update())).scalar_one_or_none()
    version = payload.get('fieldConfigVersion')
    if type(version) is not int or version < 1:
        invalid()
    if plan:
        if version != plan.field_config_version:
            conflict(TaskErrorCode.FIELD_VERSION_CONFLICT)
    elif perf:
        if not allow_existing_performance:
            conflict(TaskErrorCode.PLAN_SUPPLEMENT_REQUIRED)
        if version != perf.field_config_version:
            conflict(TaskErrorCode.FIELD_VERSION_CONFLICT)
    elif version != state.active_version:
        conflict(TaskErrorCode.FIELD_VERSION_CONFLICT)
    fields = await definitions(db, version, current=True)
    if plan is None:
        if not payload.get('targetKey'):
            invalid()
        target = identifier(payload['targetKey'])
        if not human:
            admit(target, payload.get('producerId'), 'mes')
        sync = merge_values({}, value_patch(fields, payload.get('syncValues', {}), 'shared_sync', 'plan'))
        local = merge_values({}, value_patch(fields, payload.get('localValues', {}), 'plan_local', 'plan'))
        _ensure_mapping(target, version, fields, sync, local)
        plan = Plan(task_no=task_no, target_key=target, field_config_version=version,
                    priority=payload.get('priority') or 5, remark=payload.get('remark'),
                    dispatch_status=forced_status or 'pending', production_status=production_status,
                    local_values=local, sync_values=sync)
        db.add(plan)
        await db.flush()
        await db.refresh(plan)
        return 'created', plan
    target = identifier(payload['targetKey']) if payload.get('targetKey') is not None else plan.target_key
    if not human:
        admit(plan.target_key, payload.get('producerId'), 'mes')
        admit(target, payload.get('producerId'), 'mes')
    priority = payload.get('priority') if payload.get('priority') is not None else plan.priority
    remark = payload['remark'] if 'remark' in payload else plan.remark
    sync = merge_values(plan.sync_values, value_patch(fields, payload.get('syncValues', {}), 'shared_sync', 'plan'))
    local = merge_values(plan.local_values, value_patch(fields, payload.get('localValues', {}), 'plan_local', 'plan'))
    business_changed = any((_changed(target, plan.target_key), _changed(priority, plan.priority),
                            _changed(sync, plan.sync_values), _changed(local, plan.local_values)))
    remark_changed = remark != plan.remark
    editable = plan.dispatch_status in ('pending', 'paused') and plan.production_status is None
    if business_changed and not editable:
        conflict()
    if remark_changed and not editable and (not human or plan.dispatch_status == 'cancelled'):
        conflict()
    if editable:
        _ensure_mapping(target, version, fields, sync, local)
    if not business_changed and not remark_changed:
        return 'unchanged', plan
    plan.target_key, plan.priority, plan.remark = target, priority, remark
    plan.sync_values, plan.local_values = sync, local
    await db.flush()
    await db.refresh(plan)
    return 'updated', plan


def attempt_wire(attempt, *, sensitive=False):
    if attempt is None:
        return None
    result = {'dispatchId': attempt.dispatch_id, 'attemptNo': attempt.attempt_no,
              'attemptStatus': attempt.attempt_status, 'submissionPhase': attempt.submission_phase,
              'requestSeq': attempt.request_seq, 'ackSeq': attempt.ack_seq,
              'ackObservedAt': wire_time(attempt.ack_observed_at), 'claimedAt': wire_time(attempt.claimed_at)}
    if sensitive:
        result.update(failureKey=attempt.failure_key, failureDetail=attempt.failure_detail)
    return result


async def plan_wire(db, plan, *, detail=False, sensitive=False, fields=None, current=False):
    if fields is None:
        fields = await definitions(db, plan.field_config_version, overlay=True, current=current)
    visible = None if detail else 'plan_visible'
    result = {'id': str(plan.id), 'taskNo': plan.task_no, 'targetKey': plan.target_key,
              'fieldConfigVersion': plan.field_config_version, 'productionStatus': plan.production_status,
              'dispatchStatus': plan.dispatch_status, 'priority': plan.priority, 'remark': plan.remark,
              'createdAt': wire_time(plan.created_at), 'updatedAt': wire_time(plan.updated_at),
              'syncValues': decode_values(fields, plan.sync_values, 'shared_sync', visible),
              'localValues': decode_values(fields, plan.local_values, 'plan_local', visible)}
    if detail:
        latest = (await db.execute(select(DispatchAttempt).where(DispatchAttempt.task_no == plan.task_no)
                                   .order_by(DispatchAttempt.attempt_no.desc()).limit(1))).scalar_one_or_none()
        result['latestDispatchAttempt'] = attempt_wire(latest, sensitive=sensitive)
        if sensitive:
            events = (await db.execute(select(ActionEvent).where(ActionEvent.task_no == plan.task_no)
                                       .order_by(ActionEvent.id.desc()).limit(20))).scalars()
            result['recentActionEvents'] = [{'actionKey': e.action_key, 'actorId': str(e.actor_id),
                  'fromStatus': e.from_status, 'toStatus': e.to_status, 'dispatchId': e.dispatch_id,
                  'reason': e.reason, 'evidence': e.evidence, 'createdAt': wire_time(e.created_at)} for e in events]
    return result


async def list_plans(db, filters):
    query = select(Plan)
    for request, column in (('taskNo', Plan.task_no), ('targetKey', Plan.target_key),
                            ('productionStatus', Plan.production_status), ('dispatchStatus', Plan.dispatch_status)):
        if filters.get(request) is not None:
            value = (task_number(filters[request]) if request == 'taskNo' else
                     identifier(filters[request]) if request == 'targetKey' else filters[request])
            query = query.where(column == value)
    if filters.get('createdFrom') is not None:
        query = query.where(Plan.created_at >= local_time(filters['createdFrom']))
    if filters.get('createdTo') is not None:
        query = query.where(Plan.created_at < local_time(filters['createdTo']))
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    page, size = filters['page'], filters['pageSize']
    if (page - 1) * size >= total:
        return {'items': [], 'total': total, 'page': page, 'pageSize': size, 'totalPages': (total + size - 1) // size}
    order = (Plan.created_at.asc(), Plan.id.asc()) if filters['sortOrder'] == 'asc' else (Plan.created_at.desc(), Plan.id.desc())
    rows = (await db.execute(query.order_by(*order).offset((page-1)*size).limit(size))).scalars()
    cached, items = {}, []
    for row in rows:
        if row.field_config_version not in cached:
            cached[row.field_config_version] = await definitions(db, row.field_config_version, overlay=True)
        items.append(await plan_wire(db, row, fields=cached[row.field_config_version]))
    return {'items': items, 'total': total, 'page': page,
            'pageSize': size, 'totalPages': (total + size - 1) // size}


def sync_plan(plan, fields, changes, production_status):
    if plan is None:
        return {'outcome': 'skipped', 'slots': [], 'reason': 'no_plan'}
    plan.production_status = production_status
    eligible = {slot_key(f.slot_no): f for f in fields if f.scope == 'shared_sync' and f.enabled
                and f.sync_enabled and f.performance_owner in ('automated', 'manual')}
    values = dict(plan.sync_values or {})
    changed, skipped = [], []
    for slot, value in changes.items():
        if slot not in eligible:
            skipped.append({'slot': slot, 'reason': 'incompatible_definition'})
        elif (slot in values and value is None) or (value is not None and values.get(slot) != value):
            if value is None:
                values.pop(slot, None)
            else:
                values[slot] = value
            changed.append(slot)
    if changed:
        plan.sync_values = values
        result = {'outcome': 'synced', 'slots': sorted(changed)}
        if skipped:
            result['skippedSlots'] = skipped
        return result
    return {'outcome': 'skipped', 'slots': [], 'reason': 'incompatible_definition' if skipped else ('no_value_change' if changes else 'no_eligible_values')}


def claim_wire(attempt):
    return {'dispatchId': attempt.dispatch_id, 'claimRequestId': attempt.claim_request_id,
            'taskNo': attempt.task_no, 'targetKey': attempt.target_key, 'attemptStatus': attempt.attempt_status,
            'fieldConfigVersion': attempt.field_config_version, 'parameters': attempt.parameters}


async def claim(db, payload):
    target, producer = identifier(payload['targetKey']), identifier(payload['producerId'])
    request_id = uuid_string(payload['claimRequestId'])
    await config_state(db, lock=True)
    previous = (await db.execute(select(DispatchAttempt).where(DispatchAttempt.claim_request_id == request_id).with_for_update())).scalar_one_or_none()
    if previous:
        if (previous.target_key, previous.producer_id) != (target, producer):
            conflict(TaskErrorCode.DISPATCH_CONFLICT)
        return {'outcome': 'existing_attempt', 'attempt': claim_wire(previous)}
    busy = (await db.execute(select(DispatchAttempt.dispatch_id).where(DispatchAttempt.active_target_key == target).with_for_update())).first()
    if busy:
        return {'outcome': 'target_busy', 'attempt': None}
    plan = (await db.execute(select(Plan).where(Plan.target_key == target, Plan.dispatch_status == 'pending',
                 Plan.production_status.is_(None)).order_by(Plan.priority, Plan.created_at, Plan.id)
                 .limit(1).with_for_update())).scalar_one_or_none()
    if plan is None:
        previous = (await db.execute(select(DispatchAttempt).where(DispatchAttempt.claim_request_id == request_id).with_for_update())).scalar_one_or_none()
        if previous:
            if (previous.target_key, previous.producer_id) != (target, producer):
                conflict(TaskErrorCode.DISPATCH_CONFLICT)
            return {'outcome': 'existing_attempt', 'attempt': claim_wire(previous)}
        busy = (await db.execute(select(DispatchAttempt.dispatch_id).where(DispatchAttempt.active_target_key == target).with_for_update())).first()
        return {'outcome': 'target_busy' if busy else 'no_task', 'attempt': None}
    fields = await definitions(db, plan.field_config_version, current=True)
    parameters = _ensure_mapping(target, plan.field_config_version, fields, plan.sync_values, plan.local_values)
    latest = (await db.execute(select(DispatchAttempt).where(DispatchAttempt.task_no == plan.task_no)
                               .order_by(DispatchAttempt.attempt_no.desc()).limit(1).with_for_update())).scalar_one_or_none()
    number = (latest.attempt_no if latest else 0) + 1
    attempt = DispatchAttempt(dispatch_id=str(uuid4()), claim_request_id=request_id, task_no=plan.task_no,
                target_key=target, producer_id=producer, field_config_version=plan.field_config_version,
                parameters=parameters, attempt_no=number, attempt_status='claimed')
    plan.dispatch_status = 'claimed'
    db.add(attempt)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        previous = (await db.execute(select(DispatchAttempt).where(DispatchAttempt.claim_request_id == request_id))).scalar_one_or_none()
        if previous:
            if (previous.target_key, previous.producer_id) != (target, producer):
                conflict(TaskErrorCode.DISPATCH_CONFLICT)
            return {'outcome': 'existing_attempt', 'attempt': claim_wire(previous)}
        return {'outcome': 'target_busy', 'attempt': None}
    return {'outcome': 'claimed', 'attempt': claim_wire(attempt)}


async def report(db, payload):
    dispatch = uuid_string(payload['dispatchId'])
    task_no, target, producer = task_number(payload['taskNo']), identifier(payload['targetKey']), identifier(payload['producerId'])
    plan = await lock_plan(db, task_no)
    attempt = (await db.execute(select(DispatchAttempt).where(DispatchAttempt.dispatch_id == dispatch).with_for_update())).scalar_one_or_none()
    latest = (await db.execute(select(DispatchAttempt).where(DispatchAttempt.task_no == task_no).order_by(DispatchAttempt.attempt_no.desc()).limit(1).with_for_update())).scalar_one_or_none()
    if not plan or not attempt or not latest or (attempt.task_no, attempt.target_key, attempt.producer_id, attempt.attempt_no) != (task_no, target, producer, latest.attempt_no):
        conflict(TaskErrorCode.DISPATCH_CONFLICT)
    sequence_limit = target_mapping(target, attempt.field_config_version)['plcSeqMax']
    if any(payload.get(key) is not None and payload[key] > sequence_limit for key in ('requestSeq', 'ackSeq')):
        invalid()
    outcome = payload['outcome']
    if outcome == 'plc_accepted':
        if any(payload.get(k) is not None for k in ('submissionPhase', 'reasonCode', 'detail')):
            invalid()
        seq, ack, observed = payload.get('requestSeq'), payload.get('ackSeq'), local_time(payload.get('ackObservedAt'))
        if seq is None or ack is None or observed is None:
            invalid()
        if seq != ack:
            conflict(TaskErrorCode.DISPATCH_CONFLICT)
        if attempt.attempt_status == 'plc_accepted':
            if (attempt.request_seq, attempt.ack_seq, attempt.ack_observed_at) != (seq, ack, observed):
                conflict(TaskErrorCode.DISPATCH_CONFLICT)
            result = 'duplicate'
        elif attempt.attempt_status in ('claimed', 'exception') and (attempt.request_seq is None or attempt.request_seq == seq):
            attempt.attempt_status, plan.dispatch_status = 'plc_accepted', 'plc_accepted'
            attempt.submission_phase, attempt.request_seq, attempt.ack_seq, attempt.ack_observed_at = 'acknowledged', seq, ack, observed
            result = 'accepted'
        else:
            conflict(TaskErrorCode.DISPATCH_CONFLICT)
    else:
        if payload.get('ackSeq') is not None or payload.get('ackObservedAt') is not None:
            invalid()
        phase, reason, seq, detail = payload.get('submissionPhase'), payload.get('reasonCode'), payload.get('requestSeq'), payload.get('detail')
        if phase not in ('not_submitted','possibly_submitted') or not reason:
            invalid()
        identifier(reason)
        if attempt.attempt_status == 'exception':
            if (attempt.submission_phase, attempt.failure_key, attempt.request_seq, attempt.failure_detail) != (phase, reason, seq, detail):
                conflict(TaskErrorCode.DISPATCH_CONFLICT)
            result = 'duplicate'
        elif attempt.attempt_status == 'claimed':
            attempt.attempt_status, plan.dispatch_status = 'exception', 'exception'
            attempt.submission_phase, attempt.failure_key, attempt.request_seq, attempt.failure_detail = phase, reason, seq, detail
            result = 'exception_recorded'
        else:
            conflict(TaskErrorCode.DISPATCH_CONFLICT)
    await db.flush()
    return {'outcome': result, 'dispatchId': dispatch, 'taskNo': task_no,
            'attemptStatus': attempt.attempt_status, 'dispatchStatus': plan.dispatch_status}


async def action(db, row_id, action_name, payload, actor_id):
    allowed = {
        'pause': {'actionRequestId', 'reason'},
        'save-and-resume': {'actionRequestId', 'fieldConfigVersion', 'targetKey', 'priority', 'remark', 'syncValues', 'localValues'},
        'cancel': {'actionRequestId', 'reason'},
        'return-to-paused': {'actionRequestId', 'dispatchId', 'reason', 'evidence'},
    }
    if action_name not in allowed or set(payload) - allowed[action_name]:
        invalid()
    request_id = uuid_string(payload['actionRequestId'])
    payload = dict(payload)
    payload['actionRequestId'] = request_id
    if payload.get('dispatchId'):
        payload['dispatchId'] = uuid_string(payload['dispatchId'])
    digest = hashlib.sha256(json.dumps({'id': str(row_id), 'action': action_name, 'actorId': str(actor_id), **payload},
                                       sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).digest()
    previous = (await db.execute(select(ActionEvent).where(ActionEvent.action_request_id == request_id))).scalar_one_or_none()
    if previous:
        if previous.request_digest != digest:
            conflict(TaskErrorCode.ACTION_REQUEST_CONFLICT)
        return {'outcome': 'duplicate', 'taskNo': previous.task_no, 'resultingDispatchStatus': previous.to_status}
    await config_state(db, lock=True)
    plan = await plan_by_id(db, row_id, lock=True)
    previous = (await db.execute(select(ActionEvent).where(ActionEvent.action_request_id == request_id).with_for_update())).scalar_one_or_none()
    if previous:
        if previous.request_digest != digest:
            conflict(TaskErrorCode.ACTION_REQUEST_CONFLICT)
        return {'outcome': 'duplicate', 'taskNo': previous.task_no, 'resultingDispatchStatus': previous.to_status}
    old = plan.dispatch_status
    reason, evidence, dispatch = payload.get('reason'), payload.get('evidence'), payload.get('dispatchId')
    if action_name == 'pause' and old == 'pending' and plan.production_status is None:
        plan.dispatch_status = 'paused'
    elif action_name == 'cancel' and old in ('pending', 'paused') and plan.production_status is None:
        if not isinstance(reason, str) or not reason.strip(): invalid()
        plan.dispatch_status = 'cancelled'
    elif action_name == 'return-to-paused' and old in ('claimed','exception') and plan.production_status is None:
        if not isinstance(reason, str) or not reason.strip() or not isinstance(evidence, str) or not evidence.strip() or not dispatch:
            invalid()
        dispatch = uuid_string(dispatch)
        attempt = (await db.execute(select(DispatchAttempt).where(DispatchAttempt.dispatch_id == dispatch).with_for_update())).scalar_one_or_none()
        latest = (await db.execute(select(DispatchAttempt).where(DispatchAttempt.task_no == plan.task_no).order_by(DispatchAttempt.attempt_no.desc()).limit(1).with_for_update())).scalar_one_or_none()
        if not attempt or not latest or attempt.task_no != plan.task_no or attempt.attempt_no != latest.attempt_no or attempt.attempt_status not in ('claimed','exception'):
            conflict(TaskErrorCode.DISPATCH_CONFLICT)
        attempt.attempt_status, plan.dispatch_status = 'returned', 'paused'
    elif action_name == 'save-and-resume' and old == 'paused' and plan.production_status is None:
        fields_payload = {k: v for k,v in payload.items() if k in ('targetKey','priority','remark','syncValues','localValues','fieldConfigVersion')}
        fields_payload['taskNo'] = plan.task_no
        if 'fieldConfigVersion' not in fields_payload:
            invalid()
        await upsert_plan(db, fields_payload, human=True)
        plan.dispatch_status = 'pending'
    else:
        conflict()
    event = ActionEvent(action_request_id=request_id, request_digest=digest, task_no=plan.task_no,
                        action_key=action_name, actor_id=actor_id, from_status=old, to_status=plan.dispatch_status,
                        dispatch_id=dispatch, reason=reason, evidence=evidence)
    db.add(event)
    await db.flush()
    return {'outcome': 'applied', 'taskNo': plan.task_no, 'resultingDispatchStatus': plan.dispatch_status}
