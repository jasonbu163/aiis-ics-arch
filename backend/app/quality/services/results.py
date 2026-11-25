"""质量结果与字段配置的用例和事务。"""
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app.quality.crud.results import config_row, page_rows, result_row
from app.quality.domain import QualityError, QualityErrorCode, validate_definitions, validate_items
from app.quality.models.results import QualityResult
from common.integration.envelope import BUSINESS_TIMEZONE


async def _configuration(db, *, lock=False):
    row = await config_row(db, lock=lock)
    if row is None:
        raise QualityError(QualityErrorCode.UNAVAILABLE, 503, reason='configuration_missing')
    return row


def _definitions(row, *, enabled_only):
    return [d for d in row.definitions if d['enabled'] or not enabled_only]


def _result(row, definitions):
    return {
        'id': str(row.id), 'taskNo': row.task_no, 'targetKey': row.target_key,
        'items': {d['name']: row.items.get(d['name']) for d in definitions},
        'createdAt': row.created_at.isoformat(), 'updatedAt': row.updated_at.isoformat(),
    }


async def _existing(db, task_no, *, lock=False):
    row = await result_row(db, task_no, lock=lock)
    if row is None:
        raise QualityError(QualityErrorCode.NOT_FOUND, 404, field='taskNo')
    return row


async def get_config(db, *, enabled_only=False):
    row = await _configuration(db)
    return {'revision': row.revision, 'definitions': _definitions(row, enabled_only=enabled_only)}


async def save_config(db, body):
    row = await _configuration(db, lock=True)
    if row.revision != body.revision:
        raise QualityError(QualityErrorCode.CONFIG_REVISION_CONFLICT, 409, field='revision')
    definitions = validate_definitions(row.definitions, [d.model_dump(by_alias=True) for d in body.definitions])
    if definitions != row.definitions:
        row.definitions = definitions
        row.revision += 1
        row.updated_at = datetime.now(BUSINESS_TIMEZONE)
    return {'revision': row.revision, 'definitions': definitions}


async def get_result(db, task_no):
    definitions = _definitions(await _configuration(db), enabled_only=True)
    return _result(await _existing(db, task_no), definitions)


async def list_results(db, filters, *, include_fields=False):
    definitions = _definitions(await _configuration(db), enabled_only=True)
    rows, total = await page_rows(db, filters)
    page = {
        'items': [_result(row, definitions) for row in rows],
        'total': total, 'page': filters.page, 'pageSize': filters.pageSize,
        'totalPages': (total + filters.pageSize - 1) // filters.pageSize,
    }
    if include_fields:
        page['fields'] = definitions
    return page


async def _insert_result(db, body, patch, fields):
    now = datetime.now(BUSINESS_TIMEZONE)
    row = QualityResult(task_no=body.taskNo, target_key=body.targetKey, items=patch,
                        created_at=now, updated_at=now)
    db.add(row)
    await db.flush()
    return {'outcome': 'created', 'quality': _result(row, fields)}


async def create_result(db, body):
    # 与集成 upsert 同时锁定当前配置，串行判定任务号是否已存在。
    fields = _definitions(await _configuration(db, lock=True), enabled_only=True)
    if await result_row(db, body.taskNo, lock=True) is not None:
        raise QualityError(QualityErrorCode.TASK_NO_CONFLICT, 409, field='taskNo')
    patch = validate_items(body.items, fields, human=True)
    try:
        return await _insert_result(db, body, patch, fields)
    except IntegrityError as exc:
        # 兼容直接向同一库写入的竞争，只识别任务号唯一约束。
        args = getattr(exc.orig, 'args', ())
        dialect = db.get_bind().dialect.name
        mysql_duplicate = (dialect == 'mysql' and len(args) == 2 and args[0] == 1062
                           and str(args[1]).rpartition(" for key ")[2] in
                           {"'uq_quality_main_task_no'", "'quality_main.uq_quality_main_task_no'"})
        sqlite_duplicate = (dialect == 'sqlite' and
                            getattr(exc.orig, 'sqlite_errorname', '') == 'SQLITE_CONSTRAINT_UNIQUE'
                            and str(exc.orig) == 'UNIQUE constraint failed: quality_main.task_no')
        if mysql_duplicate or sqlite_duplicate:
            raise QualityError(QualityErrorCode.TASK_NO_CONFLICT, 409, field='taskNo') from None
        raise


async def save_result(db, body, *, human):
    # 单项目配置锁也负责序列化首次写入；并发上报不会丢失不同字段。
    config = await _configuration(db, lock=True)
    fields = _definitions(config, enabled_only=True)
    patch = validate_items(body.items, fields, human=human)
    row = (await _existing(db, body.taskNo, lock=True) if human
           else await result_row(db, body.taskNo, lock=True))
    target_set = 'targetKey' in body.model_fields_set
    if row is None:
        return await _insert_result(db, body, patch, fields)

    target = row.target_key
    if target_set:
        if target is not None and body.targetKey != target:
            raise QualityError(QualityErrorCode.TARGET_CONFLICT, 409, field='targetKey')
        target = body.targetKey
    items = {**row.items, **patch}
    if items == row.items and target == row.target_key:
        return {'outcome': 'unchanged', 'quality': _result(row, fields)}

    row.items, row.target_key = items, target
    row.updated_at = datetime.now(BUSINESS_TIMEZONE)
    return {'outcome': 'updated', 'quality': _result(row, fields)}
