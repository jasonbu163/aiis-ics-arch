"""同一snapshot内读取发布水位/feed/逐点latest；不按raw自增ID分页。"""
from sqlalchemy import select,and_,or_
from ..models import SampleReceipt,LatestPoint
from .async_ingest import key

async def feed(db,high,after,maximum=2000):
    return list((await db.execute(select(SampleReceipt).where(SampleReceipt.commit_serial<=high,
        or_(SampleReceipt.commit_serial>after[0],and_(SampleReceipt.commit_serial==after[0],SampleReceipt.ordinal>after[1])))
        .order_by(SampleReceipt.commit_serial,SampleReceipt.ordinal).limit(maximum))).scalars())

async def high_position(db,high):
    row=(await db.execute(select(SampleReceipt.ordinal).where(SampleReceipt.commit_serial==high).order_by(SampleReceipt.ordinal.desc()).limit(1))).scalar_one_or_none()
    return [high,row or 0]

async def latest_points(db,plc,epoch,after,query,maximum=501):
    stmt=select(LatestPoint).where(LatestPoint.plc_id==key(plc),LatestPoint.source_epoch==epoch)
    if query.db_number is not None: stmt=stmt.where(LatestPoint.db_number==query.db_number)
    if query.group_id: stmt=stmt.where(LatestPoint.group_id==key(query.group_id))
    if query.point_id: stmt=stmt.where(LatestPoint.point_id==key(query.point_id))
    if after:
        stmt=stmt.where(or_(LatestPoint.db_number>after[0],and_(LatestPoint.db_number==after[0],LatestPoint.point_id>key(after[1]))))
    return list((await db.execute(stmt.order_by(LatestPoint.db_number,LatestPoint.point_id).limit(maximum))).scalars())
