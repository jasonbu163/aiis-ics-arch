"""字段配置的登录与集成入口；集成查询按登记目标与来源放行。"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.task.eligibility import get_profile
from app.task.http import TaskRoute, actor, audit_event, authorize, commit, response
from app.task.schemas.fields import ConfigSave, Envelope, ErrorEnvelope
from app.task.services.async_fields import read_config, save_config

router = APIRouter(route_class=TaskRoute, tags=['Task fields'], responses={code: {'model': ErrorEnvelope} for code in (401,403,404,409,422,503)})


@router.get('/task-field-configs', response_model=Envelope)
async def get_fields(request: Request, module: str, fieldConfigVersion: int | None = Query(None, ge=1),
                     db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, module)
    return response(await read_config(db, module, fieldConfigVersion))


@router.put('/task-field-configs', response_model=Envelope)
async def put_fields(request: Request, body: ConfigSave, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, body.module, roles=('admin',))
    result = await save_config(db, body.model_dump(exclude_unset=True))
    await commit(db)
    audit_event('generic_task_config_saved', actor_id=str(user.id), module=body.module, field_config_version=result['fieldConfigVersion'], config_revision=result['configRevision'])
    return response(result)


@router.get('/integration/task-field-configs', response_model=Envelope)
async def integration_fields(module: str, fieldConfigVersion: int | None = Query(None, ge=1),
                             db: AsyncSession = Depends(get_db)):
    get_profile()
    return response(await read_config(db, module, fieldConfigVersion, integration=True))
