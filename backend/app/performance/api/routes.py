"""通用实绩页面、补计划和 SMA/CA 自动快照入口。"""
from typing import Literal
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.task.eligibility import admit_read_target, get_profile
from app.task.http import TaskRoute, actor, audit_event, authorize, commit, response
from app.task.schemas.fields import Envelope, ErrorEnvelope, TaskDateTime
from app.performance.schemas.workflow import Snapshot, ManualEdit, Supplement
from app.performance.services.async_workflow import (list_performances, performance_by_id, performance_by_task,
    performance_wire, receive_snapshot, edit_manual, supplement)

router = APIRouter(route_class=TaskRoute, tags=['Performance'], responses={code: {'model': ErrorEnvelope} for code in (401,403,404,409,422,503)})


@router.get('/performances', response_model=Envelope)
async def performances(request: Request, page: int = Query(1, ge=1), pageSize: int = Query(20, ge=1, le=100),
                       taskNo: str | None = None, targetKey: str | None = None, productionStatus: str | None = None,
                       createdFrom: TaskDateTime | None = None, createdTo: TaskDateTime | None = None,
                       sortOrder: Literal['asc','desc'] = 'desc', db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'performance')
    return response(await list_performances(db, dict(page=page, pageSize=pageSize, taskNo=taskNo, targetKey=targetKey,
                    productionStatus=productionStatus, createdFrom=createdFrom, createdTo=createdTo, sortOrder=sortOrder)))


@router.post('/performances/upsert', response_model=Envelope)
async def manual_edit(request: Request, body: ManualEdit, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'performance')
    result = await edit_manual(db, body.model_dump(exclude_unset=True))
    await commit(db)
    audit_event('generic_task_performance_edit', actor_id=str(user.id), task_no=result['performance']['taskNo'], outcome=result['outcome'])
    return response(result)


@router.post('/performances/{id}/actions/supplement-plan', response_model=Envelope)
async def supplement_plan(request: Request, id: int, body: Supplement, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'performance', 'plan', roles=('admin','supervisor'))
    result = await supplement(db, id, body.model_dump(exclude_unset=True))
    await commit(db)
    audit_event('generic_task_supplement', actor_id=str(user.id), task_no=result['plan']['taskNo'], outcome=result['outcome'])
    return response(result)


@router.get('/performances/{id}', response_model=Envelope)
async def detail(request: Request, id: int, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'performance')
    return response(await performance_wire(db, await performance_by_id(db, id), detail=True))


@router.post('/integration/performances/upsert', response_model=Envelope)
async def integration_snapshot(body: Snapshot, db: AsyncSession = Depends(get_db)):
    result = await receive_snapshot(db, body.model_dump(exclude_unset=True))
    await commit(db)
    audit_event('generic_task_observation', task_no=result['taskNo'], producer_id=body.producerId, observation_seq=body.observationSeq, outcome=result['outcome'])
    return response(result)


@router.get('/integration/performances/by-task/{taskNo}', response_model=Envelope)
async def integration_performance(taskNo: str, db: AsyncSession = Depends(get_db)):
    get_profile()
    row = await performance_by_task(db, taskNo)
    admit_read_target(row.target_key)
    return response(await performance_wire(db, row, detail=True))
