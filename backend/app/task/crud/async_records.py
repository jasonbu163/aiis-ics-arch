"""计划与实绩共用的查询、锁定与分页。"""
from sqlalchemy import func, select

from app.task.domain import identifier, local_time, task_number
from app.task.errors import TaskError, TaskErrorCode


def task_query(model, number):
    return select(model).where(model.task_no == number)


async def require_row(db, model, identity, *, by_task=False):
    query = task_query(model, task_number(identity)) if by_task else select(model).where(model.id == identity)
    row = (await db.execute(query)).scalar_one_or_none()
    if row is None:
        raise TaskError(TaskErrorCode.NOT_FOUND, 404, reason='task_not_found')
    return row


async def task_page(db, model, filters, query):
    conditions = []
    if filters.taskNo is not None:
        conditions.append(model.task_no == task_number(filters.taskNo))
    if filters.targetKey is not None:
        conditions.append(model.target_key == identifier(filters.targetKey, 'targetKey'))
    if filters.productionStatus is not None:
        conditions.append(model.production_status == filters.productionStatus)
    if filters.createdFrom is not None:
        conditions.append(model.created_at >= local_time(filters.createdFrom, 'createdFrom'))
    if filters.createdTo is not None:
        conditions.append(model.created_at < local_time(filters.createdTo, 'createdTo'))
    total = (await db.execute(select(func.count()).select_from(model).where(*conditions))).scalar_one()
    order = (model.created_at, model.id) if filters.sortOrder == 'asc' else (model.created_at.desc(), model.id.desc())
    page, size = filters.page, filters.pageSize
    result = await db.execute(query.where(*conditions).order_by(*order).offset((page - 1) * size).limit(size))
    return result, {'total': total, 'page': page, 'pageSize': size, 'totalPages': (total + size - 1) // size}
