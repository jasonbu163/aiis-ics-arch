"""通用计划页面和 MES / CA-FF 的 HTTP 入口。"""
from typing import Literal
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from app.task.eligibility import admit, admit_read_target, get_profile
from app.task.errors import TaskError, TaskErrorCode
from app.task.http import TaskRoute, actor, audit_event, authorize, commit, response
from app.task.schemas.fields import Envelope, ErrorEnvelope, TaskDateTime
from app.plan.schemas.workflow import PlanUpsert, PlanAction, Claim, Report
from app.plan.services.async_workflow import upsert_plan, plan_wire, plan_by_id, plan_by_task, list_plans, claim, report, action as apply_action

router = APIRouter(route_class=TaskRoute, tags=['Plan'], responses={code: {'model': ErrorEnvelope} for code in (401,403,404,409,422,503)})


@router.get('/plans', response_model=Envelope)
async def plans(request: Request, page: int = Query(1, ge=1), pageSize: int = Query(20, ge=1, le=100),
                taskNo: str | None = None, targetKey: str | None = None, productionStatus: str | None = None,
                dispatchStatus: str | None = None, createdFrom: TaskDateTime | None = None, createdTo: TaskDateTime | None = None,
                sortOrder: Literal['asc','desc'] = 'desc', db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'plan')
    return response(await list_plans(db, dict(page=page, pageSize=pageSize, taskNo=taskNo, targetKey=targetKey,
                    productionStatus=productionStatus, dispatchStatus=dispatchStatus, createdFrom=createdFrom,
                    createdTo=createdTo, sortOrder=sortOrder)))


@router.post('/plans/upsert', response_model=Envelope)
async def save_plan(request: Request, body: PlanUpsert, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'plan', roles=('admin','supervisor'))
    data = body.model_dump(exclude_unset=True)
    if 'producerId' in data or 'eventId' in data:
        raise TaskError(TaskErrorCode.INVALID_REQUEST, 422)
    outcome, plan = await upsert_plan(db, data, human=True)
    result = await plan_wire(db, plan, detail=True, sensitive=True, current=True)
    await commit(db)
    audit_event('generic_task_plan_upsert', source='human', actor_id=str(user.id), task_no=plan.task_no, outcome=outcome)
    return response({'outcome': outcome, 'plan': result})


@router.post('/plans/{id}/actions/{action}', response_model=Envelope)
async def plan_action(request: Request, id: int, action: str, body: PlanAction,
                      db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'plan', roles=('admin','supervisor'))
    result = await apply_action(db, id, action, body.model_dump(exclude_unset=True), user.id)
    await commit(db)
    audit_event('generic_task_plan_action', actor_id=str(user.id), task_no=result['taskNo'], action=action, outcome=result['outcome'])
    return response(result)


@router.get('/plans/{id}', response_model=Envelope)
async def plan_detail(request: Request, id: int, db: AsyncSession = Depends(get_db), user=Depends(actor)):
    authorize(request, user, 'plan')
    plan = await plan_by_id(db, id)
    return response(await plan_wire(db, plan, detail=True, sensitive=user.role in ('admin','supervisor')))


@router.post('/integration/plans/upsert', response_model=Envelope)
async def integration_upsert(body: PlanUpsert, db: AsyncSession = Depends(get_db)):
    get_profile()
    data = body.model_dump(exclude_unset=True)
    if not data.get('producerId'):
        raise TaskError(TaskErrorCode.FORBIDDEN, 403)
    outcome, plan = await upsert_plan(db, data, human=False)
    result = await plan_wire(db, plan, detail=True, current=True)
    await commit(db)
    audit_event('generic_task_plan_upsert', source='mes', task_no=plan.task_no, producer_id=data['producerId'], event_id=data.get('eventId'), outcome=outcome)
    return response({'outcome': outcome, 'plan': result})


@router.post('/integration/plans/dispatch/claim', response_model=Envelope)
async def integration_claim(body: Claim, db: AsyncSession = Depends(get_db)):
    data = body.model_dump()
    admit(data['targetKey'], data['producerId'], 'executors')
    result = await claim(db, data)
    await commit(db)
    audit_event('generic_task_dispatch_claim', target_key=data['targetKey'], producer_id=data['producerId'], outcome=result['outcome'])
    return response(result)


@router.post('/integration/plans/dispatch/report', response_model=Envelope)
async def integration_report(body: Report, db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_unset=True)
    admit(data['targetKey'], data['producerId'], 'executors')
    result = await report(db, data)
    await commit(db)
    audit_event('generic_task_dispatch_report', task_no=result['taskNo'], producer_id=data['producerId'], dispatch_id=result['dispatchId'], outcome=result['outcome'])
    return response(result)


@router.get('/integration/plans/by-task/{taskNo}', response_model=Envelope)
async def integration_plan(taskNo: str, db: AsyncSession = Depends(get_db)):
    get_profile()
    plan = await plan_by_task(db, taskNo)
    admit_read_target(plan.target_key)
    return response(await plan_wire(db, plan, detail=True))
