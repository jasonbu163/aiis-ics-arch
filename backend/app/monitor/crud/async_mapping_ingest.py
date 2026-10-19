"""曲线模块投递回执SQL；不提交。"""
from sqlalchemy import select
from app.monitor.models.mapping_ingest import MonitorMappingReceipt as Receipt
async def get_receipt(db, actor, equipment, sample_id):
    return (await db.execute(select(Receipt).where(Receipt.actor_user_id == actor, Receipt.equipment_id == equipment,
        Receipt.stream == "process_curve", Receipt.sample_id == sample_id))).scalar_one_or_none()
async def add_receipt(db, **values):
    row = Receipt(stream="process_curve", **values)
    db.add(row)
    await db.flush()
    return row
