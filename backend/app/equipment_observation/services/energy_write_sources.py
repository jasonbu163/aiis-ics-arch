"""独立能耗来源的登记管理及写入状态锁。"""
import hashlib

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..domain import reject
from ..models import EnergyReceipt, EnergyWriteSource
from .guard import current_clock
from .write_sources import commit, data, source_key


def storage_identity(key):
    # 私用字符不会通过旧 v2 生产者标识校验。utf8mb4_bin 保留该命名空间。
    return "\ue000" + hashlib.sha256(key.encode("ascii")).hexdigest()[:63]


async def source_row(db, key):
    query = select(EnergyWriteSource).where(EnergyWriteSource.source_key == source_key(key))
    return (await db.execute(query.with_for_update())).scalar_one_or_none()


async def list_sources(db):
    query = select(EnergyWriteSource).where(EnergyWriteSource.deleted_at.is_(None)).order_by(EnergyWriteSource.source_key)
    return [data(row) for row in (await db.execute(query)).scalars()]


async def create(db, key, name, enabled):
    key = source_key(key)
    identity = storage_identity(key)
    now = await current_clock(db)
    row = EnergyWriteSource(source_key=key, storage_identity=identity, name=name, enabled=enabled,
                            created_at=now, updated_at=now)
    db.add(row)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        reject("configuration_conflict", 409)
    # 防止通过导入等非 API 路径产生的历史身份被误认作本次登记。
    query = select(EnergyReceipt.id).where(EnergyReceipt.producer_id == identity, EnergyReceipt.target == "energy")
    if (await db.execute(query.limit(1))).first():
        await db.rollback()
        reject("configuration_conflict", 409)
    result = data(row)
    await commit(db)
    return result


async def change(db, key, changes, *, delete=False):
    row = await source_row(db, key)
    if row is None or row.deleted_at is not None:
        await db.rollback()
        reject("not_found", 404)
    if not delete and all(getattr(row, field) == value for field, value in changes.items()):
        result = data(row)
        await db.rollback()
        return result
    row.updated_at = await current_clock(db)
    if delete:
        row.deleted_at, row.enabled = row.updated_at, False
        result = {"sourceKey": key, "deleted": True}
    else:
        for field, value in changes.items():
            setattr(row, field, value)
        result = data(row)
    await db.flush()
    await commit(db)
    return result
