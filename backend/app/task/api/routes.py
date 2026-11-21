"""当前字段定义和管理员设置、删除 HTTP 入口。"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from app.task.http import TaskRoute, actor, audit_event, authorize, commit, response
from app.task.schemas.fields import (
    ConfigSave, Envelope, ErrorEnvelope, FieldBatchDelete, FieldBatchDeleteResult,
    FieldConfigResult, FieldDelete, FieldDeleteResult, LocalFieldBatchDelete, LocalFieldBatchDeleteResult,
)
from app.task.schemas.workflow import Module
from app.task.services.async_fields import delete_field, delete_local_fields, delete_shared_fields, read_config, save_config

router = APIRouter(route_class=TaskRoute, tags=['Task fields'],
                   responses={code: {'model': ErrorEnvelope} for code in (401, 403, 404, 409, 422, 503)})


@router.get('/task-field-configs', response_model=Envelope[FieldConfigResult])
async def get_fields(request: Request, module: Module, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, module)
    return response(await read_config(db, module))


@router.put('/task-field-configs', response_model=Envelope[FieldConfigResult])
async def put_fields(request: Request, body: ConfigSave, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, roles=('admin',))
    result = await save_config(db, body.model_dump(exclude_unset=True))
    await commit(db)
    audit_event('generic_task_config_saved', actor_id=str(user.id), module=body.module,
                field_config_version=result['configVersion'], config_revision=result['configRevision'])
    return response(result)


@router.post('/task-field-configs/delete', response_model=Envelope[FieldDeleteResult])
async def drop_field(request: Request, body: FieldDelete, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, roles=('admin',))
    result = await delete_field(db, body.model_dump())
    await commit(db)
    audit_event('generic_task_config_deleted', actor_id=str(user.id), scope=body.scope, field_name=body.name,
                field_config_version=result['configVersion'], config_revision=result['configRevision'])
    return response(result)


@router.post('/task-field-configs/batch-delete', response_model=Envelope[FieldBatchDeleteResult])
async def drop_shared_fields(request: Request, body: FieldBatchDelete, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, roles=('admin',))
    result = await delete_shared_fields(db, body.model_dump())
    await commit(db)
    audit_event('generic_task_config_batch_deleted', actor_id=str(user.id), scope='shared_sync',
                deleted_count=len(result['deleted']), field_config_version=result['configVersion'],
                config_revision=result['configRevision'])
    return response(result)


@router.post('/task-field-configs/local/batch-delete', response_model=Envelope[LocalFieldBatchDeleteResult])
async def drop_local_fields(request: Request, body: LocalFieldBatchDelete, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, roles=('admin',))
    result = await delete_local_fields(db, body.model_dump())
    await commit(db)
    audit_event('generic_task_config_batch_deleted', actor_id=str(user.id), scope=result['deleted'][0]['scope'],
                deleted_count=len(result['deleted']), field_config_version=result['configVersion'],
                config_revision=result['configRevision'])
    return response(result)


@router.get('/integration/task-field-configs', response_model=Envelope[FieldConfigResult])
async def integration_fields(module: Module, db: AsyncSession = Depends(get_db)):
    return response(await read_config(db, module, integration=True))
