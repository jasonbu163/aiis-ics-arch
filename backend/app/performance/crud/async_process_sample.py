"""父实绩过程HTTP域SQL；父/子明确设备，CRUD不提交。"""
from sqlalchemy import select
from app.performance.models.performance import ProcessTemperature, ProcessTension, ProcessSpeed
MODELS = {"temperature": ProcessTemperature, "tension": ProcessTension, "speed": ProcessSpeed}
async def get_record(db, kind, parent_id, sample):
    model = MODELS[kind]
    return (await db.execute(select(model).where(model.equipment_id == sample.equipment_id,
        model.performance_id == parent_id, model.http_zone_key == sample.zone.encode("utf-8"),
        model.record_time == sample.record_time).with_for_update())).scalar_one_or_none()
async def add_record(db, kind, **values):
    row = MODELS[kind](**values)
    db.add(row)
    await db.flush()
    return row
async def list_records(db, kind, parent_id, equipment):
    model = MODELS[kind]
    return list((await db.execute(select(model).where(model.equipment_id == equipment,
        model.performance_id == parent_id).order_by(model.record_time, model.id))).scalars().all())
