"""equipment两stream回执访问；仅SQL/add/flush。"""
from sqlalchemy import select
from app.equipment.models.mapping_ingest import EquipmentMappingReceipt as Receipt
async def get_receipt(db, actor, equipment, stream, sample_id):
    return (await db.execute(select(Receipt).where(Receipt.actor_user_id == actor,
        Receipt.equipment_id == equipment, Receipt.stream == stream, Receipt.sample_id == sample_id))).scalar_one_or_none()
async def add_receipt(db, **values):
    receipt = Receipt(**values)
    db.add(receipt)
    await db.flush()
    return receipt
