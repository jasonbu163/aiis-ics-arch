"""曲线HTTP域、上海日UTC边界和最近limit后升序；无事务提交。"""
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select
from app.monitor.models.business_history import HistoryProcessCurve as Curve
async def get_sample(db, equipment, sampled_at):
    return (await db.execute(select(Curve).where(Curve.equipment_id == equipment, Curve.sampled_at == sampled_at))).scalar_one_or_none()
async def add_sample(db, **values):
    row = Curve(**values)
    db.add(row)
    await db.flush()
    return row
async def list_samples(db, equipment, day, record_id=None, limit=1000):
    start = datetime.combine(day, time(), ZoneInfo("Asia/Shanghai")).astimezone(timezone.utc).replace(tzinfo=None)
    end = start+timedelta(days=1)
    query = select(Curve).where(Curve.equipment_id == equipment, Curve.sampled_at >= start, Curve.sampled_at < end)
    if record_id is not None:
        query = query.where(Curve.id == record_id)
    records = list((await db.execute(query.order_by(Curve.sampled_at.desc(), Curve.id.desc()).limit(limit))).scalars().all())
    return list(reversed(records))
