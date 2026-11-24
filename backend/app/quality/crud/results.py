"""按质量表查询结果和配置，不读取其他业务表。"""
from sqlalchemy import func, select, update

from app.quality.models.results import QualityFieldConfig, QualityResult


async def config_row(db, *, lock=False):
    query = select(QualityFieldConfig).where(QualityFieldConfig.id == 1)
    if lock:
        if db.get_bind().dialect.name == 'sqlite':
            # SQLite 忽略 FOR UPDATE。先取得写锁，再读取最新配置或结果。
            await db.execute(update(QualityFieldConfig).where(QualityFieldConfig.id == 1)
                             .values(revision=QualityFieldConfig.revision))
        else:
            query = query.with_for_update()
    return (await db.execute(query)).scalar_one_or_none()


async def result_row(db, task_no, *, lock=False):
    query = select(QualityResult).where(QualityResult.task_no == task_no)
    if lock:
        query = query.with_for_update()
    return (await db.execute(query)).scalar_one_or_none()


async def page_rows(db, filters):
    conditions = []
    for column, value in ((QualityResult.task_no, filters.taskNo),
                          (QualityResult.target_key, filters.targetKey)):
        if value is not None:
            conditions.append(column == value)
    if filters.createdFrom is not None:
        conditions.append(QualityResult.created_at >= filters.createdFrom)
    if filters.createdTo is not None:
        conditions.append(QualityResult.created_at < filters.createdTo)
    total = (await db.execute(select(func.count()).select_from(QualityResult)
                              .where(*conditions))).scalar_one()
    if (filters.page - 1) * filters.pageSize >= total:
        return [], total
    query = (select(QualityResult).where(*conditions)
             .order_by(QualityResult.created_at.desc(), QualityResult.id.desc())
             .offset((filters.page - 1) * filters.pageSize).limit(filters.pageSize))
    return (await db.execute(query)).scalars().all(), total
