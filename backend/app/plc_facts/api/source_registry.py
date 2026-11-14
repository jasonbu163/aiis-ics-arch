"""采集来源管理员接口，登记、编辑、接管及删除均由服务层提交。"""
import json

from fastapi import APIRouter, Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from common.log import log_event
from core.deps import get_current_active_admin
from database import get_db_session
from ..schemas.source_registry import FailureOut, PageOut, RegistrationIn, RegistrationOut, UpdateIn
from ..services import async_source_registry as service
from ..v2_config import get_profile


class RegistryRequest(Request):
    async def json(self):
        try:
            return await super().json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Let the existing authentication dependency run before body validation.
            return None


class RegistryRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def wrapped(request):
            try:
                return await handler(RegistryRequest(request.scope, request.receive))
            except HTTPException as error:
                if not request.headers.get('authorization'):
                    raise HTTPException(status_code=401, detail='Authentication required',
                                        headers={'WWW-Authenticate': 'Bearer'}) from None
                raise error
            except RequestValidationError:
                error = service.RegistryError('invalid_request', 422)
            except service.RegistryError as failure:
                error = failure
            except Exception:
                error = service.RegistryError('not_ready', 503)
            try:
                log_event('WARNING', 'acquisition_source_rejected',
                          action=request.method, status=error.status, error_code=error.key)
            except Exception:
                pass
            return JSONResponse(status_code=error.status, content={
                'code': error.status, 'message': error.key, 'data': None, 'errorCode': error.key,
            })
        return wrapped


router = APIRouter(route_class=RegistryRoute, tags=['acquisition-sources'],
                   responses={code: {'model': FailureOut, 'description': 'Source registry failure'}
                              for code in (404, 409, 422, 503)})


async def authenticated_request(request: Request, user=Depends(get_current_active_admin)):
    if any(len(request.query_params.getlist(key)) != 1 for key in request.query_params):
        raise service.RegistryError('invalid_request', 422)
    return user


def audit(action, user, body, source, outcome, previous=None):
    try:
        expected = getattr(body, 'expected', None)
        log_event('INFO', 'acquisition_source_changed', action=action, actor_id=str(user.id),
                  plc_id=body.plc_id, outcome=outcome,
                  previous_instance_id=expected.instance_id if expected else None,
                  previous_generation=expected.source_generation if expected else None,
                  previous_source_type=previous['sourceType'] if previous else None,
                  instance_id=source['instanceId'], source_generation=source['sourceGeneration'],
                  source_type=source['sourceType'])
    except Exception:
        pass


@router.get('/admin/acquisition-sources', response_model=PageOut)
async def sources(page: int = Query(1, ge=1), page_size: int = Query(50, alias='pageSize', ge=1, le=100),
                  user=Depends(authenticated_request)):
    profile = get_profile()
    db = await get_db_session()
    try:
        return {'code': 200, 'message': 'success',
                'data': await service.list_sources(db, profile, page, page_size)}
    finally:
        await db.close()


@router.post('/admin/acquisition-sources', response_model=RegistrationOut)
async def register(body: RegistrationIn, user=Depends(authenticated_request)):
    profile = get_profile()
    db = await get_db_session()
    try:
        outcome, source = await service.register(db, profile, body)
        audit('register', user, body, source, outcome)
        return {'code': 200, 'message': 'success', 'data': {'outcome': outcome, 'source': source}}
    finally:
        await db.close()


@router.patch('/admin/acquisition-sources', response_model=RegistrationOut)
async def update(body: UpdateIn, user=Depends(authenticated_request)):
    profile = get_profile()
    db = await get_db_session()
    try:
        outcome, source, previous = await service.update(db, profile, body)
        audit(body.action, user, body, source, outcome, previous)
        return {'code': 200, 'message': 'success', 'data': {'outcome': outcome, 'source': source}}
    finally:
        await db.close()
