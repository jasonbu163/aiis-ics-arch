"""HTTP生产主记录及设备观察水位SQL，全部明确设备域。"""
from sqlalchemy import select, func, null
from app.performance.models.performance import Performance
from app.performance.models.mapping_ingest import PerformanceObservationState as State
async def state_for_update(db, equipment):
    state = (await db.execute(select(State).where(State.equipment_id == equipment).with_for_update())).scalar_one_or_none()
    if state is None:
        state = State(equipment_id=equipment)
        db.add(state)
        await db.flush()
    return state
async def by_coil(db, equipment, coil):
    return (await db.execute(select(Performance).where(Performance.equipment_id == equipment,
        Performance.http_coil_key == coil.encode("utf-8")).with_for_update())).scalar_one_or_none()
async def by_id(db, equipment, record_id, lock=False):
    query = select(Performance).where(Performance.equipment_id == equipment, Performance.id == record_id)
    if lock:
        query = query.with_for_update()
    return (await db.execute(query)).scalar_one_or_none()
async def active_records(db, equipment):
    return list((await db.execute(select(Performance).where(Performance.equipment_id == equipment,
        Performance.observation_status.in_(("in_production", "unknown"))).order_by(Performance.id).with_for_update())).scalars().all())
async def add_record(db, **values):
    # Explicit SQL NULL only for new HTTP rows; legacy ORM defaults remain unchanged.
    for key in ("output_quantity", "qualified_quantity", "efficiency_rate", "quality_score"):
        if values.get(key) is None:
            values[key] = null()
    row = Performance(**values)
    db.add(row)
    await db.flush()
    return row

async def parent_id_exists(db, record_id):
    return (await db.execute(select(Performance.id).where(Performance.id == record_id))).scalar_one_or_none() is not None

async def list_records(db, query):
    statement = select(Performance).where(Performance.equipment_id == query.equipment_id)
    for key in ("coil_no", "grade", "observation_status"):
        value = getattr(query,key)
        if value is not None:
            statement = statement.where(getattr(Performance,key) == value)
    if query.start_date is not None:
        statement = statement.where(Performance.production_date >= query.start_date)
    if query.end_date is not None:
        statement = statement.where(Performance.production_date <= query.end_date)
    total = (await db.execute(select(func.count()).select_from(statement.subquery()))).scalar_one()
    rows = list((await db.execute(statement.order_by(Performance.last_observed_at.desc(), Performance.id.desc())
        .offset((query.page-1)*query.page_size).limit(query.page_size))).scalars().all())
    return rows, total
