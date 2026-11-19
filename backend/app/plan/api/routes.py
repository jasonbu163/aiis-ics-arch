"""通用计划的登录和集成 HTTP 入口。"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from app.plan.schemas.workflow import PlanRecord, PlanResult, PlanUpsert
from app.plan.services.async_workflow import find_plan, list_plans, upsert_plan
from app.task.http import TaskRoute, actor, audit_event, authorize, commit, response, retired
from app.task.schemas.fields import Envelope, ErrorEnvelope
from app.task.schemas.workflow import Page, QueryFilters

router = APIRouter(route_class=TaskRoute, tags=['Plan'],
                   responses={code: {'model': ErrorEnvelope} for code in (401, 403, 404, 409, 422, 503)})


@router.get('/plans', response_model=Envelope[Page[PlanRecord]])
async def plans(request: Request, filters: Annotated[QueryFilters, Query()], db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'plan')
    return response(await list_plans(db, filters))


@router.post('/plans/upsert', response_model=Envelope[PlanResult])
async def save_plan(request: Request, body: PlanUpsert, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'plan', roles=('admin', 'supervisor'))
    result = await upsert_plan(db, body.model_dump(exclude_unset=True), human=True)
    await commit(db)
    audit_event('generic_task_plan_upsert', source='human', actor_id=str(user.id),
                task_no=result['plan']['taskNo'], outcome=result['outcome'])
    return response(result)


@router.get('/plans/{id}', response_model=Envelope[PlanRecord])
async def plan_detail(request: Request, id: int, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'plan')
    return response(await find_plan(db, id))


@router.get('/integration/plans', response_model=Envelope[Page[PlanRecord]])
async def integration_plans(filters: Annotated[QueryFilters, Query()], db: AsyncSession = Depends(get_db)):
    return response(await list_plans(db, filters))


@router.post('/integration/plans/upsert', response_model=Envelope[PlanResult])
async def integration_upsert(body: PlanUpsert, db: AsyncSession = Depends(get_db)):
    result = await upsert_plan(db, body.model_dump(exclude_unset=True), human=False)
    await commit(db)
    audit_event('generic_task_plan_upsert', source='integration', task_no=result['plan']['taskNo'],
                producer_id=body.producerId, outcome=result['outcome'])
    return response(result)


@router.get('/integration/plans/by-task/{taskNo}', response_model=Envelope[PlanRecord])
async def integration_plan(taskNo: str, db: AsyncSession = Depends(get_db)):
    return response(await find_plan(db, taskNo, by_task=True))


router.add_api_route('/integration/plans/dispatch/claim', retired, methods=['POST'], include_in_schema=False)
router.add_api_route('/integration/plans/dispatch/report', retired, methods=['POST'], include_in_schema=False)
router.add_api_route('/plans/{id}/actions/{action}', retired, methods=['POST'], include_in_schema=False)
