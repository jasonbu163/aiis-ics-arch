"""performance匿名业务SQL边界；只使用调用方AsyncSession，不提交/回滚。"""
from sqlalchemy import select, text, or_
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from common.integration.storage import StorageProbe
from app.performance.models.integration import PerformanceIntegrationReceipt as Receipt


async def probe_storage(db):
    target = dict((await db.execute(text("SELECT @@server_uuid AS serverUuid, DATABASE() AS `schema`, UTC_TIMESTAMP(3) AS utcNow"))).mappings().one())
    try:
        target["schemaRevision"] = (await db.execute(text("SELECT version_num FROM alembic_version FOR SHARE"))).scalar_one()
    except (NoResultFound,MultipleResultsFound):
        raise ValueError("adoption requires one exact schema revision") from None
    return StorageProbe(target["serverUuid"],target["schema"],target["schemaRevision"],target["utcNow"])


async def probe_adoption(db, adoption):
    from common.integration.storage import validate_adoption_probe
    return validate_adoption_probe(adoption, await probe_storage(db)).database_now



async def get_receipt(db, producer, event):
    return (await db.execute(select(Receipt).where(Receipt.producer_id == producer.encode("utf-8"),
        Receipt.event_id == event.encode("utf-8")).with_for_update())).scalar_one_or_none()


async def add_receipt(db, **values):
    row = Receipt(**values)
    db.add(row)
    await db.flush()
    return row

from sqlalchemy import null
from app.performance.models.performance import Performance, ProcessTemperature, ProcessTension, ProcessSpeed
from app.performance.models.mapping_ingest import PerformanceObservationState as State
from app.performance.models.integration import PerformanceIntegrationObservationEvent as Event
MODELS = {"temperature": ProcessTemperature, "tension": ProcessTension, "speed": ProcessSpeed}


async def state_for_update(db, equipment, now):
    row = (await db.execute(select(State).where(State.equipment_id == equipment).with_for_update())).scalar_one_or_none()
    if row is None:
        row = State(equipment_id=equipment, created_at=now, updated_at=now)
        db.add(row)
        await db.flush()
    return row


async def get_event(db, equipment, time):
    return (await db.execute(select(Event).where(Event.equipment_id == equipment,
        Event.sampled_at == time).with_for_update())).scalar_one_or_none()


async def add_event(db, **values):
    row = Event(**values)
    db.add(row)
    await db.flush()
    return row


async def active_records(db, equipment, target_coil=None):
    # 活跃行和可能较小ID的inactive目标一次current read，统一主键升序锁定。
    condition=Performance.observation_status.in_(("in_production", "unknown"))
    if target_coil is not None:
        condition=or_(condition,Performance.http_coil_key==target_coil.encode("utf-8"))
    return list((await db.execute(select(Performance).where(Performance.equipment_id==equipment,
        condition).order_by(Performance.id).with_for_update())).scalars().all())


async def parent(db, parent_id):
    return (await db.execute(select(Performance).where(Performance.id == parent_id).with_for_update())).scalar_one_or_none()


async def parent_event(db, equipment, parent_id):
    return (await db.execute(select(Event.id).where(Event.equipment_id == equipment,
        Event.performance_id == parent_id, Event.observation_status == "in_production").limit(1).with_for_update())).scalar_one_or_none()


async def add_performance(db, **values):
    for key in ("output_quantity", "qualified_quantity", "efficiency_rate", "quality_score"):
        if values.get(key) is None:
            values[key] = null()
    row = Performance(**values)
    db.add(row)
    await db.flush()
    # MySQL无INSERT RETURNING；SQL null()会使默认观测列过期，后续规则不得隐式async懒加载。
    await db.refresh(row, with_for_update=True)
    return row


async def get_process(db, kind, parent_id, data, time):
    model = MODELS[kind]
    return (await db.execute(select(model).where(model.equipment_id == data.equipment_id,
        model.performance_id == parent_id, model.http_zone_key == data.zone.encode("utf-8"),
        model.record_time == time).with_for_update())).scalar_one_or_none()


async def add_process(db, kind, **values):
    row = MODELS[kind](**values)
    db.add(row)
    await db.flush()
    return row


async def storage_context(db):
    """旧入口默认直接旁路；adopted每次事务在业务SQL前验目标。"""
    from app.performance.integration_config import IntegrationConfig
    from settings import resolve_env_file
    adoption=IntegrationConfig(_env_file=resolve_env_file()).adoption()
    if adoption is None:
        return None
    now=await probe_adoption(db,adoption)
    return adoption,now
