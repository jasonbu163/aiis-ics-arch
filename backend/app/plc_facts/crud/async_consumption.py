"""采集消费事务的行锁与元数据 SQL；提交权留在 Service。"""
from sqlalchemy import and_, func, select, text
from sqlalchemy.dialects.mysql import insert

from ..consumption_domain import ConsumerError
from ..models.consumption import (
    AcquisitionConsumer, AcquisitionDelivery, AcquisitionOperation,
    ConsumptionEvent, ConsumptionStream,
)
from ..models.source_registry import PlcSourceRegistry
from ..models.v2 import SampleV2


async def clock(db):
    return (await db.execute(text('SELECT CURRENT_TIMESTAMP(6)'))).scalar_one().replace(tzinfo=None)


async def lock_stream(db, plc, number):
    statement = insert(ConsumptionStream).values(plc_id=plc, db_number=number, last_seq=0, floor_seq=0)
    await db.execute(statement.on_duplicate_key_update(last_seq=ConsumptionStream.last_seq))
    return await db.get(ConsumptionStream, (plc, number), with_for_update=True, populate_existing=True)


async def set_append_marker(db, event_seq, digest=None):
    await db.execute(text('SET @acq006_append_seq = :seq, @acq006_append_hash = UNHEX(:digest)'),
                     {'seq': event_seq, 'digest': digest.hex() if digest is not None else None})


async def target_occupied(db, plc, number, generation):
    for model in (ConsumptionEvent, SampleV2):
        query = (select(model.plc_id).where(model.plc_id == plc, model.db_number == number,
                                          model.source_generation == generation)
                 .limit(1).with_for_update(read=True))
        if (await db.execute(query)).first() is not None:
            return True
    return False


async def consumer(db, consumer_id):
    return await db.get(AcquisitionConsumer, consumer_id, with_for_update=True, populate_existing=True)


async def scoped_consumer(db, consumer_id, plc, number):
    query = (select(AcquisitionConsumer)
             .where(AcquisitionConsumer.consumer_id == consumer_id,
                    AcquisitionConsumer.plc_id == plc, AcquisitionConsumer.db_number == number)
             .with_for_update())
    return (await db.execute(query)).scalar_one_or_none()


async def consumer_exists(db, consumer_id):
    query = select(AcquisitionConsumer.consumer_id).where(AcquisitionConsumer.consumer_id == consumer_id)
    return (await db.execute(query)).first() is not None


async def target_is_active(db, item):
    query = select(PlcSourceRegistry.plc_id).where(
        PlcSourceRegistry.plc_id == item.target_plc, PlcSourceRegistry.source_type == 'external',
        PlcSourceRegistry.instance_id == item.target_instance,
        PlcSourceRegistry.source_generation == item.target_generation,
    )
    return (await db.execute(query)).first() is not None


async def bound_consumer(db, plc, number, generation):
    query = (select(AcquisitionConsumer)
             .where(AcquisitionConsumer.target_plc == plc, AcquisitionConsumer.target_db == number,
                    AcquisitionConsumer.target_generation == generation).with_for_update())
    return (await db.execute(query)).scalar_one_or_none()


async def operation(db, consumer_id, operation_id):
    return await db.get(AcquisitionOperation, (consumer_id, operation_id), with_for_update=True)


async def delivery(db, consumer_id, delivery_id):
    return await db.get(AcquisitionDelivery, (consumer_id, delivery_id), with_for_update=True)


async def pending(db, consumer_id):
    query = (select(AcquisitionDelivery).where(AcquisitionDelivery.consumer_id == consumer_id,
                                              AcquisitionDelivery.confirmed_at.is_(None))
             .order_by(AcquisitionDelivery.event_seq).limit(2).with_for_update())
    rows = (await db.execute(query)).scalars().all()
    if len(rows) > 1:
        raise ConsumerError('not_ready', 503)
    return rows[0] if rows else None


async def historical_excluded(db, plc, number, start_seq, start_at):
    query = select(func.count(), func.min(ConsumptionEvent.event_seq), func.max(ConsumptionEvent.event_seq)).where(
        ConsumptionEvent.plc_id == plc, ConsumptionEvent.db_number == number,
        ConsumptionEvent.event_seq <= start_seq, ConsumptionEvent.expires_at <= start_at,
    )
    return (await db.execute(query)).one()


async def next_events(db, item):
    """同一一致性读取得流头和第一条合格事件，检测意外缺号。"""
    stream = await db.get(ConsumptionStream, (item.plc_id, item.db_number), populate_existing=True)
    if stream is None:
        return None, None, 0
    query = select(ConsumptionEvent).where(
        ConsumptionEvent.plc_id == item.plc_id, ConsumptionEvent.db_number == item.db_number,
        ConsumptionEvent.event_seq > item.last_confirmed_seq, ConsumptionEvent.event_seq <= stream.last_seq,
    )
    if item.start_mode == 'retained':
        skipped = query.where(ConsumptionEvent.event_seq <= item.start_seq,
                              ConsumptionEvent.expires_at <= item.start_at)
        query = query.where(~and_(ConsumptionEvent.event_seq <= item.start_seq,
                                  ConsumptionEvent.expires_at <= item.start_at))
    event = (await db.execute(query.order_by(ConsumptionEvent.event_seq).limit(1))).scalar_one_or_none()
    skipped_count = 0
    if item.start_mode == 'retained':
        limit = event.event_seq if event else stream.last_seq + 1
        count_query = select(func.count()).select_from(skipped.where(ConsumptionEvent.event_seq < limit).subquery())
        skipped_count = (await db.execute(count_query)).scalar_one()
    return stream, event, skipped_count


async def source_sample(db, event, now):
    query = select(SampleV2).where(
        SampleV2.id == event.history_id, SampleV2.plc_id == event.plc_id,
        SampleV2.db_number == event.db_number, SampleV2.instance_id == event.instance_id,
        SampleV2.sample_id == event.sample_id, SampleV2.source_generation == event.source_generation,
        SampleV2.expires_at > now,
    )
    return (await db.execute(query)).scalar_one_or_none()
