"""生产/过程stream回执SQL；无事务提交。"""
from sqlalchemy import select
from app.performance.models.mapping_ingest import PerformanceMappingReceipt as Receipt
async def get_receipt(db, actor, equipment, stream, sample_id):
    return (await db.execute(select(Receipt).where(Receipt.actor_user_id == actor, Receipt.equipment_id == equipment,
        Receipt.stream == stream, Receipt.sample_id == sample_id))).scalar_one_or_none()
async def get_applied_event(db, equipment, sampled_at):
    return (await db.execute(select(Receipt).where(Receipt.equipment_id == equipment,
        Receipt.stream == "production_observation", Receipt.sampled_at == sampled_at, Receipt.outcome != "stale").order_by(Receipt.id).limit(1))).scalar_one_or_none()
async def add_receipt(db, **values):
    receipt = Receipt(**values)
    db.add(receipt)
    await db.flush()
    return receipt
