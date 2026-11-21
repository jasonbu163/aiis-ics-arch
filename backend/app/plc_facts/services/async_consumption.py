"""采集消费事务和栅栏；调用方负责发送目标 POST，本服务只持久化元数据。"""
from datetime import timedelta
from hmac import compare_digest
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from ..consumption_config import authorize
from ..consumption_domain import ConsumerError, delivery_id, fingerprint, require_identifier, sequence
from ..crud import async_consumption as crud
from ..crud import async_source_registry as registry
from ..crud import async_v2 as facts
from ..models.consumption import AcquisitionConsumer, AcquisitionDelivery, AcquisitionOperation
from ..v2_config import CONSUMPTION_REVISIONS
from ..v2_domain import MAX_SEQUENCE, V2Error, wire_time
from . import async_v2 as facts_service

LEASE_TTL = timedelta(seconds=30)


def target_wire(item):
    return {'kind': 'plc-facts-v2', 'instanceId': item.target_instance.decode(),
            'plcId': item.target_plc.decode(), 'dbNumber': item.target_db,
            'sourceGeneration': item.target_generation.decode()}


def delivery_target(item, event_seq):
    return {**target_wire(item), 'sampleId': delivery_id(item.consumer_id, event_seq), 'sourceSeq': str(event_seq)}


def created_wire(item):
    return {
        'consumerId': item.consumer_id, 'startAt': wire_time(item.start_at), 'startSeq': str(item.start_seq),
        'lastConfirmedSeq': str(item.start_seq if item.start_mode == 'now' else 0),
        'excludedHistory': {'count': str(item.excluded_count),
                            'firstEventSeq': str(item.excluded_first_seq) if item.excluded_first_seq else None,
                            'lastEventSeq': str(item.excluded_last_seq) if item.excluded_last_seq else None},
        'desiredState': 'paused',
    }


def lease_wire(item):
    return {'leaseId': item.lease_id, 'leaseGeneration': str(item.lease_generation),
            'expiresAt': wire_time(item.lease_expires_at),
            'renewAfterAt': wire_time(item.lease_expires_at - LEASE_TTL / 2)}


def pending_wire(item, row):
    return {'deliveryId': row.delivery_id, 'eventSeq': str(row.event_seq), 'configVersion': row.config_version,
            'configHash': bytes(row.config_hash).hex(), 'serializerVersion': row.serializer_version,
            'bodySha256': bytes(row.body_hash).hex(), 'target': delivery_target(item, row.event_seq)}


def confirmed_wire(row):
    return {'status': 'confirmed', 'deliveryId': row.delivery_id, 'lastConfirmedSeq': str(row.event_seq),
            'confirmedAt': wire_time(row.confirmed_at)}


def check_scope(grant, plc, number):
    if (facts.key(grant.plc_id), grant.db_number) != (plc, number):
        raise ConsumerError('scope_rejected', 403)


async def load_consumer(db, grant):
    item = await crud.scoped_consumer(db, grant.consumer_id, facts.key(grant.plc_id), grant.db_number)
    if item is not None:
        return item
    if await crud.consumer_exists(db, grant.consumer_id):
        raise ConsumerError('scope_rejected', 403)
    raise ConsumerError('not_found', 404)


def check_lease(item, supplied, now, worker=None):
    identity, generation = supplied.parsed()
    if (item.lease_id != identity or item.lease_generation != generation or item.lease_expires_at <= now
            or (worker is not None and item.worker_id != worker)):
        raise ConsumerError('lease_stale', 409)


def check_running(item):
    if item.desired_state != 'running':
        raise ConsumerError('paused', 409)


def gap(item, event_seq):
    return ConsumerError('gap', 410, {'eventSeq': str(event_seq), 'lastConfirmedSeq': str(item.last_confirmed_seq)})


async def first_event(db, item, now):
    stream, event, excluded = await crud.next_events(db, item)
    expected = item.last_confirmed_seq + 1
    if stream is None or item.last_confirmed_seq < stream.floor_seq or item.last_confirmed_seq > stream.last_seq:
        raise gap(item, expected)
    if event is None:
        if stream.last_seq - item.last_confirmed_seq != excluded:
            raise gap(item, expected)
        return None, None
    if (event.event_seq != expected + excluded or event.event_seq > stream.last_seq or event.expires_at <= now):
        raise gap(item, expected + excluded)
    sample = await crud.source_sample(db, event, now)
    if sample is None:
        raise gap(item, event.event_seq)
    return event, sample


async def dispatch(db, profile, boundary, action, grant, *args):
    """统一目标守卫及提交未知；纯查询关闭会话时归还行锁。"""
    if profile['target'].get('schemaRevision') not in CONSUMPTION_REVISIONS:
        raise ConsumerError('not_ready', 503)
    await facts.target_now(db, profile['target'])
    result = await action(db, grant, *args)
    if action in (create, set_run_state, change_lease, mark_pending, acknowledge):
        boundary['commit_attempted'] = True
        await db.commit()
    return result


async def create(db, grant, body):
    source = (facts.key(require_identifier(body.plc_id)), body.db_number)
    target = body.target
    target_key = (facts.key(require_identifier(target.plc_id)), target.db_number)
    require_identifier(target.instance_id)
    require_identifier(target.source_generation)
    check_scope(grant, *source)
    if source[0] == target_key[0]:
        raise ConsumerError('invalid_target', 422)

    # Registry -> sorted streams -> consumer is shared with the v2 target writer.
    binding = await registry.binding_for_update(db, target.plc_id)
    streams = {}
    for key in sorted((source, target_key)):
        streams[key] = await crud.lock_stream(db, *key)
    existing = await crud.consumer(db, grant.consumer_id)
    if existing is not None:
        if ((existing.plc_id, existing.db_number) != source or existing.start_mode != body.start_mode
                or target_wire(existing) != target.model_dump(by_alias=True)):
            raise ConsumerError('operation_conflict', 409)
        return created_wire(existing)

    if (binding is None or binding.source_type != 'external' or binding.instance_id != facts.key(target.instance_id)
            or binding.source_generation != facts.key(target.source_generation)):
        raise ConsumerError('invalid_target', 422)
    generation = facts.key(target.source_generation)
    if (await crud.bound_consumer(db, *target_key, generation)
            or await crud.target_occupied(db, *target_key, generation)):
        raise ConsumerError('target_in_use', 409)

    now = await crud.clock(db)
    start_seq = streams[source].last_seq
    count, first, last = (0, None, None)
    initial_position = start_seq
    if body.start_mode == 'retained':
        initial_position = streams[source].floor_seq
        count, first, last = await crud.historical_excluded(db, *source, start_seq, now)
    item = AcquisitionConsumer(
        consumer_id=grant.consumer_id, plc_id=source[0], db_number=source[1], start_mode=body.start_mode,
        start_at=now, start_seq=start_seq, last_confirmed_seq=initial_position, excluded_count=count,
        excluded_first_seq=first, excluded_last_seq=last, target_plc=target_key[0], target_db=target_key[1],
        target_instance=facts.key(target.instance_id), target_generation=generation,
        desired_state='paused', lease_generation=0,
    )
    db.add(item)
    try:
        await db.flush()
    except IntegrityError:
        raise ConsumerError('operation_conflict', 409) from None
    return created_wire(item)


async def replay(db, item, operation, body):
    digest = fingerprint(operation, body)
    row = await crud.operation(db, item.consumer_id, body.operation_id)
    if row is not None:
        if not compare_digest(row.fingerprint, digest):
            raise ConsumerError('operation_conflict', 409)
        return digest, row.result
    return digest, None


def store_operation(db, item, body, digest, result):
    db.add(AcquisitionOperation(consumer_id=item.consumer_id, operation_id=body.operation_id,
                                fingerprint=digest, result=result))
    return result


async def set_run_state(db, grant, body):
    item = await load_consumer(db, grant)
    digest, result = await replay(db, item, 'run-state', body)
    if result is not None:
        return result
    item.desired_state = body.desired_state
    return store_operation(db, item, body, digest, {'desiredState': item.desired_state})


async def change_lease(db, grant, body, supplied):
    item = await load_consumer(db, grant)
    worker = facts.key(require_identifier(body.worker_id))
    digest, result = await replay(db, item, 'lease', body)
    if result is not None:
        return result
    now = await crud.clock(db)
    if body.action == 'acquire':
        check_running(item)
        if item.lease_id is not None and item.lease_expires_at > now:
            raise ConsumerError('lease_occupied', 409)
        if item.lease_generation >= MAX_SEQUENCE:
            raise ConsumerError('not_ready', 503)
        item.lease_id = str(uuid4())
        item.lease_generation += 1
        item.worker_id = worker
    else:
        check_lease(item, supplied, now, worker)

    if body.action == 'release':
        item.lease_expires_at = now
        result = lease_wire(item)
        item.lease_id = None
        item.worker_id = None
        item.lease_expires_at = None
    else:
        item.lease_expires_at = now + LEASE_TTL
        result = lease_wire(item)
    return store_operation(db, item, body, digest, result)


async def status(db, grant):
    item = await load_consumer(db, grant)
    now = await crud.clock(db)
    pending = await crud.pending(db, item.consumer_id)
    initial = item.start_seq if item.start_mode == 'now' else 0
    state = 'pending' if pending else ('confirmed' if item.last_confirmed_seq > initial else 'idle')
    if await crud.target_is_active(db, item):
        try:
            await first_event(db, item, now)
        except ConsumerError as failure:
            if failure.status != 410:
                raise
            state = 'blocked'
    else:
        state = 'blocked'
    return {**created_wire(item), **{'plcId': item.plc_id.decode(), 'dbNumber': item.db_number,
            'startMode': item.start_mode, 'desiredState': item.desired_state,
            'lastConfirmedSeq': str(item.last_confirmed_seq), 'target': target_wire(item),
            'lease': lease_wire(item) if item.lease_id and item.lease_expires_at > now else None,
            'pending': pending_wire(item, pending) if pending else None, 'status': state}}


async def read_next(db, grant, supplied):
    item = await load_consumer(db, grant)
    check_running(item)
    now = await crud.clock(db)
    check_lease(item, supplied, now)
    pending = await crud.pending(db, item.consumer_id)
    event, sample = await first_event(db, item, now)
    if pending and (event is None or event.event_seq != pending.event_seq):
        raise gap(item, pending.event_seq)
    if event is None:
        return {'status': 'empty'}
    return {'status': 'ready', 'eventSeq': str(event.event_seq),
            'deliveryId': delivery_id(item.consumer_id, event.event_seq),
            'target': delivery_target(item, event.event_seq), 'sample': facts_service.sample_detail(sample)}


async def mark_pending(db, grant, identity, body, supplied):
    item = await load_consumer(db, grant)
    now = await crud.clock(db)
    check_lease(item, supplied, now)
    event_seq = sequence(body.event_seq)
    if identity != delivery_id(item.consumer_id, event_seq):
        raise ConsumerError('delivery_mismatch', 409)
    expected_target = delivery_target(item, event_seq)
    if body.target.model_dump(by_alias=True) != expected_target:
        raise ConsumerError('delivery_mismatch', 409)

    existing = await crud.delivery(db, item.consumer_id, identity)
    if existing is not None:
        actual = pending_wire(item, existing)
        if any(actual[k] != v for k, v in body.model_dump(by_alias=True).items()):
            raise ConsumerError('pending_conflict', 409)
        return actual

    check_running(item)
    event, _ = await first_event(db, item, now)
    if not await crud.target_is_active(db, item):
        raise ConsumerError('target_not_active', 409)
    if event is None or event.event_seq != event_seq or await crud.pending(db, item.consumer_id):
        raise ConsumerError('delivery_out_of_order', 409)
    row = AcquisitionDelivery(consumer_id=item.consumer_id, delivery_id=identity, event_seq=event_seq,
                              config_version=require_identifier(body.config_version),
                              config_hash=bytes.fromhex(body.config_hash),
                              serializer_version=require_identifier(body.serializer_version),
                              body_hash=bytes.fromhex(body.body_sha256), created_at=now)
    db.add(row)
    return pending_wire(item, row)


async def acknowledge(db, grant, identity, body, supplied):
    item = await load_consumer(db, grant)
    digest, result = await replay(db, item, f'ack:{identity}', body)
    if result is not None:
        return result
    now = await crud.clock(db)
    check_lease(item, supplied, now)
    row = await crud.delivery(db, item.consumer_id, identity)
    if row is None or body.instance_id != item.target_instance.decode() or body.sample_id != identity:
        raise ConsumerError('receipt_mismatch', 409)
    if not row.confirmed_at:
        event, _ = await first_event(db, item, now)
        if not await crud.target_is_active(db, item):
            raise ConsumerError('target_not_active', 409)
        if event is None or row.event_seq != event.event_seq:
            raise ConsumerError('delivery_out_of_order', 409)
        row.confirmed_at = now
        item.last_confirmed_seq = row.event_seq
    return store_operation(db, item, body, digest, confirmed_wire(row))


async def reserve_sample_event(db, sample, digest, request, source_type):
    """在事实 INSERT 前锁流并检查绑定目标，后续由 DB 触发器原子追加事件。"""
    plc, generation = facts.key(sample.plc_id), facts.key(sample.source_generation)
    stream = await crud.lock_stream(db, plc, sample.db_number)
    await enforce_target(db, sample, digest, request, source_type, plc, generation)
    if stream.last_seq >= MAX_SEQUENCE:
        raise V2Error('not_ready', 503)
    stream.last_seq += 1
    await db.flush()
    return stream.last_seq


async def enforce_target(db, sample, digest, request, source_type, plc=None, generation=None):
    plc = facts.key(sample.plc_id) if plc is None else plc
    generation = facts.key(sample.source_generation) if generation is None else generation
    item = await crud.bound_consumer(db, plc, sample.db_number, generation)
    if item is None:
        return
    if request is None:
        raise ConsumerError('authentication_required', 401)
    if request.duplicate_headers:
        raise ConsumerError('invalid_request', 422)
    grant = authorize(request.authorization, item.consumer_id, 'target')
    check_scope(grant, item.plc_id, item.db_number)
    if source_type != 'external':
        raise ConsumerError('scope_rejected', 403)
    check_running(item)
    now = await crud.clock(db)
    check_lease(item, request.lease, now)
    if request.consumer_id != item.consumer_id or request.delivery_id != sample.sample_id:
        raise ConsumerError('delivery_mismatch', 409)
    row = await crud.delivery(db, item.consumer_id, sample.sample_id)
    if (row is None or row.confirmed_at is not None or item.target_instance != facts.key(sample.instance_id)
            or row.event_seq != int(sample.source_seq) or not compare_digest(row.body_hash, digest)):
        raise ConsumerError('pending_conflict', 409)
    event, _ = await first_event(db, item, now)
    if event is None or row.event_seq != event.event_seq:
        raise ConsumerError('delivery_out_of_order', 409)
