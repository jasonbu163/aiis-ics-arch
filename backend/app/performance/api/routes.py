"""通用实绩读取、人工反馈和集成上报 HTTP 入口。"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from app.performance.schemas.workflow import ManualEdit, PerformanceRecord, PerformanceResult, PerformanceUpsert
from app.performance.services.async_workflow import find_performance, list_performances, upsert_performance
from app.task.http import TaskRoute, actor, audit_event, authorize, commit, response, retired
from app.task.schemas.fields import Envelope, ErrorEnvelope
from app.task.schemas.workflow import Page, QueryFilters

router = APIRouter(route_class=TaskRoute, tags=['Performance'],
                   responses={code: {'model': ErrorEnvelope} for code in (401, 403, 404, 409, 422, 503)})


@router.get('/performances', response_model=Envelope[Page[PerformanceRecord]])
async def performances(request: Request, filters: Annotated[QueryFilters, Query()], db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'performance')
    return response(await list_performances(db, filters))


@router.post('/performances/upsert', response_model=Envelope[PerformanceResult])
async def manual_edit(request: Request, body: ManualEdit, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'performance')
    result = await upsert_performance(db, body.model_dump(exclude_unset=True), human=True)
    await commit(db)
    audit_event('generic_task_performance_edit', actor_id=str(user.id),
                task_no=result['performance']['taskNo'], outcome=result['outcome'])
    return response(result)


@router.get('/performances/{id}', response_model=Envelope[PerformanceRecord])
async def detail(request: Request, id: int, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'performance')
    return response(await find_performance(db, id))


@router.post('/integration/performances/upsert', response_model=Envelope[PerformanceResult])
async def integration_performance_upsert(body: PerformanceUpsert, db: AsyncSession = Depends(get_db)):
    result = await upsert_performance(db, body.model_dump(exclude_unset=True), human=False)
    await commit(db)
    audit_event('generic_task_observation', task_no=result['performance']['taskNo'], producer_id=body.producerId,
                observation_seq=body.observationSeq, outcome=result['outcome'])
    return response(result)


@router.get('/integration/performances/by-task/{taskNo}', response_model=Envelope[PerformanceRecord])
async def integration_performance(taskNo: str, db: AsyncSession = Depends(get_db)):
    return response(await find_performance(db, taskNo, by_task=True))


router.add_api_route('/performances/{id}/actions/supplement-plan', retired, methods=['POST'], include_in_schema=False)
