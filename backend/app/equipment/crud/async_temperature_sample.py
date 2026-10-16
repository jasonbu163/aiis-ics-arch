"""新温控async SQL访问；只查询/add/flush，事务由Service拥有。"""
from sqlalchemy import select
from app.equipment.models.temperature_sample import EquipmentTemperatureSample as Sample, EquipmentTemperatureSampleReceipt as Receipt


async def get_receipt(db, actor_user_id, equipment_id, sample_id):
    return (await db.execute(select(Receipt).where(Receipt.actor_user_id == actor_user_id,
            Receipt.equipment_id == equipment_id, Receipt.sample_id == sample_id))).scalar_one_or_none()


async def get_sample(db, equipment_id, sampled_at):
    return (await db.execute(select(Sample).where(Sample.equipment_id == equipment_id,
            Sample.sampled_at == sampled_at))).scalar_one_or_none()


async def add_sample(db, **values):
    sample = Sample(**values)
    db.add(sample)
    await db.flush()
    return sample


async def add_receipt(db, **values):
    receipt = Receipt(**values)
    db.add(receipt)
    await db.flush()
    return receipt


async def list_samples(db, equipment_id, record_id=None, limit=100):
    query = select(Sample).where(Sample.equipment_id == equipment_id)
    if record_id is not None:
        query = query.where(Sample.id == record_id)
    query = query.order_by(Sample.sampled_at.desc(), Sample.id.desc()).limit(limit)
    return list((await db.execute(query)).scalars().all())
