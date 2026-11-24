"""质量结果和本地字段配置的 Web 与可信网络 API。"""
from decimal import Decimal, InvalidOperation
import json
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.quality.domain import QualityError, QualityErrorCode
from app.quality.schemas.results import (
    ConfigSnapshot, Envelope, ErrorEnvelope, IntegrationUpsert, Page, QueryFilters,
    ReadPage, Result, SaveResult, TaskNo, Upsert,
)
from app.quality.services import results
from common.log import log_event
from core.deps import get_current_user, require_permissions
from database import get_db


def _decimal(token):
    try:
        return Decimal(token)
    except InvalidOperation:
        return Decimal('NaN')


def _integer(token):
    try:
        return int(token)
    except ValueError:
        return _decimal(token)


class _ExactRequest(Request):
    async def json(self):
        if not hasattr(self, '_json'):
            self._json = json.loads(await self.body(), parse_float=_decimal, parse_int=_integer)
        return self._json


class QualityRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()
        annotation = self.body_field.field_info.annotation if self.body_field is not None else None
        exact = isinstance(annotation, type) and issubclass(annotation, Upsert)

        async def dispatch(request):
            try:
                return await handler(_ExactRequest(request.scope, request.receive) if exact else request)
            except RequestValidationError as exc:
                item = exc.errors()[0]
                field = '.'.join(str(part) for part in item['loc'] if part not in ('body', 'query', 'path'))
                field = field[:256].encode('utf-8', errors='replace').decode('utf-8')
                error = QualityError(QualityErrorCode.INVALID_REQUEST, 422, field=field or None,
                                     reason=item['type'])
            except StarletteHTTPException as exc:
                if exc.status_code == 401 or not request.headers.get('Authorization'):
                    error = QualityError(QualityErrorCode.UNAUTHENTICATED, 401)
                elif exc.status_code == 403:
                    error = QualityError(QualityErrorCode.FORBIDDEN, 403)
                else:
                    error = QualityError(QualityErrorCode.INVALID_REQUEST, exc.status_code)
            except QualityError as exc:
                error = exc
            except SQLAlchemyError:
                error = QualityError(QualityErrorCode.UNAVAILABLE, 503)
            log_event('WARNING', 'quality.result.request_rejected',
                      route_name=self.name, error_code=error.code.value)
            body = ErrorEnvelope(code=error.status, message=error.code.value,
                                 errorCode=error.code, details=error.details)
            return JSONResponse(status_code=error.status, content=body.model_dump(mode='json'))

        return dispatch


router = APIRouter(route_class=QualityRoute, tags=['Quality Results'],
                   responses={code: {'model': ErrorEnvelope} for code in (401, 403, 404, 409, 422, 503)})
quality_user = require_permissions('quality')


async def admin(user=Depends(get_current_user)):
    if user.role != 'admin':
        raise QualityError(QualityErrorCode.FORBIDDEN, 403)
    return user


def _response(data):
    # 类型化信封不递归改写 items 中由项目定义的键。
    return {'data': data}


async def _commit(db):
    try:
        await db.commit()
    except SQLAlchemyError:
        raise QualityError(QualityErrorCode.COMMIT_UNKNOWN, 503) from None


@router.get('/quality/results', response_model=Envelope[ReadPage])
async def quality_page(filters: Annotated[QueryFilters, Query()], _user=Depends(quality_user), db=Depends(get_db)):
    return _response(await results.list_results(db, filters, include_fields=True))


@router.get('/quality/results/by-task/{taskNo}', response_model=Envelope[Result])
async def quality_by_task(taskNo: TaskNo, _user=Depends(quality_user), db=Depends(get_db)):
    return _response(await results.get_result(db, taskNo))


@router.post('/quality/results/upsert', response_model=Envelope[SaveResult])
async def quality_edit(body: Upsert, user=Depends(quality_user), db=Depends(get_db)):
    if user.role not in {'admin', 'supervisor', 'operator'}:
        raise QualityError(QualityErrorCode.FORBIDDEN, 403)
    result = await results.save_result(db, body, human=True)
    await _commit(db)
    log_event('INFO', 'quality.result.saved', source='human', actor_id=str(user.id),
              task_no=body.taskNo, outcome=result['outcome'])
    return _response(result)


@router.get('/quality/field-config', response_model=Envelope[ConfigSnapshot])
async def quality_config(_user=Depends(admin), db=Depends(get_db)):
    return _response(await results.get_config(db))


@router.put('/quality/field-config', response_model=Envelope[ConfigSnapshot])
async def quality_config_save(body: ConfigSnapshot, user=Depends(admin), db=Depends(get_db)):
    result = await results.save_config(db, body)
    await _commit(db)
    log_event('INFO', 'quality.configuration.saved', actor_id=str(user.id), revision=result['revision'])
    return _response(result)


@router.get('/integration/quality', response_model=Envelope[Page])
async def integrated_quality_page(filters: Annotated[QueryFilters, Query()], db=Depends(get_db)):
    return _response(await results.list_results(db, filters))


@router.get('/integration/quality/by-task/{taskNo}', response_model=Envelope[Result])
async def integrated_quality_by_task(taskNo: TaskNo, db=Depends(get_db)):
    return _response(await results.get_result(db, taskNo))


@router.post('/integration/quality/upsert', response_model=Envelope[SaveResult])
async def integrated_quality_upsert(body: IntegrationUpsert, db=Depends(get_db)):
    result = await results.save_result(db, body, human=False)
    await _commit(db)
    log_event('INFO', 'quality.result.saved', source='integration',
              task_no=body.taskNo, outcome=result['outcome'])
    return _response(result)


@router.get('/integration/quality/field-config', response_model=Envelope[ConfigSnapshot])
async def integrated_quality_config(db=Depends(get_db)):
    return _response(await results.get_config(db, enabled_only=True))
