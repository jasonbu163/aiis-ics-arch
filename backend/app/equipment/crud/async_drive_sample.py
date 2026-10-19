"""equipment明确HTTP设备域访问；不提交事务。"""
from sqlalchemy import select
from app.equipment.models.equipment import EquipmentDrive as Record
async def get_business_record(db, sample):
    query = select(Record).where(Record.equipment_id == sample.equipment_id, Record.timestamp == sample.sampled_at)
    return (await db.execute(query.with_for_update())).scalar_one_or_none()
async def add_record(db, **values):
    record = Record(**values)
    db.add(record)
    await db.flush()
    return record
async def list_records(db, equipment_id, record_id=None, limit=100):
    query = select(Record).where(Record.equipment_id == equipment_id)
    if record_id is not None:
        query = query.where(Record.id == record_id)
    return list((await db.execute(query.order_by(Record.timestamp.desc(), Record.id.desc()).limit(limit))).scalars().all())
