"""PLC 事实 v2 的样本写入与按 PLC/DB 范围读取入口。"""
from typing import Literal

from fastapi import APIRouter, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, Response

from common.log import log_event
from database import get_db_session
from ..services import async_v2 as service
from ..schemas.v2 import DetailOut, FailureOut, HistoryOut, LatestBrowseOut, LatestOut, OptionsOut, ReceiptOut, SampleV2In
from ..v2_config import get_profile
from ..v2_domain import MAX_BODY, V2Error, identifier, json_bytes, parse_sample, parse_time


class V2Route(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()
        async def wrapped(request):
            request.state.plc_facts_v2 = {}
            try:
                validate_query(request)
                if request.method == 'POST':
                    profile = get_profile()
                    raw = await body_bytes(request)
                    sample, document, digest = parse_sample(raw)
                    request._body = raw
                    request._json = document
                    request.state.plc_facts_v2.update(profile=profile, sample=sample, document=document, digest=digest)
                return await handler(request)
            except V2Error as error:
                status, code = error.status, error.key
            except RequestValidationError:
                status, code = 422, 'plc_facts_v2.invalid_request'
            except HTTPException:
                raise
            except Exception:
                status = 503
                code = ('plc_facts_v2.commit_outcome_unknown'
                        if request.state.plc_facts_v2.get('commit_attempted') else 'plc_facts_v2.not_ready')
            emit('plc_facts_v2_request_rejected', status=status, error_code=code)
            return JSONResponse(status_code=status, content={'code': status, 'message': code, 'data': None, 'errorCode': code})
        return wrapped


router = APIRouter(route_class=V2Route, tags=['plc-facts-v2'])
ERROR_RESPONSES = {status: {'model': FailureOut, 'description': 'PLC facts v2 failure'}
                   for status in (403, 409, 410, 413, 415, 422, 503)}
READ_RESPONSES = {403: {'description': 'PLC is not registered'},
                  404: {'model': FailureOut, 'description': 'Sample not found'},
                  422: {'model': FailureOut, 'description': 'Invalid query'},
                  503: {'model': FailureOut, 'description': 'Target unavailable'}}
HISTORY_RESPONSES = {status: response for status, response in READ_RESPONSES.items() if status != 403}


def success(data):
    return {'code': 200, 'message': 'success', 'data': data}


def validate_query(request):
    if any(len(request.query_params.getlist(key)) != 1 for key in request.query_params):
        raise V2Error('invalid_request', 422)


def emit(event, **fields):
    try:
        log_event('INFO', event, **fields)
    except Exception:
        pass


async def body_bytes(request):
    media = request.headers.get('content-type', '').split(';')
    if media[0].strip().lower() != 'application/json' or request.headers.get('content-encoding', 'identity').lower() != 'identity':
        raise V2Error('media_type', 415)
    for parameter in media[1:]:
        key, separator, value = parameter.strip().partition('=')
        if not separator or key.lower() != 'charset' or value.strip('"').lower() != 'utf-8':
            raise V2Error('media_type', 415)
    result = bytearray()
    async for chunk in request.stream():
        if len(result) + len(chunk) > MAX_BODY:
            raise V2Error('payload_too_large', 413)
        result.extend(chunk)
    return bytes(result)


@router.post('/integration/plc-facts/samples', operation_id='plc_facts_v2_sample', response_model=ReceiptOut, responses=ERROR_RESPONSES)
async def create_sample(request: Request, body: SampleV2In):
    boundary = request.state.plc_facts_v2
    db = await get_db_session()
    try:
        result = await service.write_sample(db, boundary['profile'], body, boundary['document'], boundary['digest'], boundary)
        emit('plc_facts_v2_sample_committed', instance_id=body.instance_id, sample_id=body.sample_id,
             outcome=result['data']['outcome'])
        return result
    finally:
        await db.close()


@router.get('/acquisition-data/options', operation_id='plc_facts_v2_options', response_model=OptionsOut, responses=READ_RESPONSES)
async def options(view: Literal['history'] | None = Query(None)):
    profile = get_profile()
    db = await get_db_session()
    try:
        return success(await service.options(db, profile, view))
    finally:
        await db.close()


@router.get('/acquisition-data/latest', operation_id='plc_facts_v2_latest', response_model=LatestOut, responses=READ_RESPONSES)
async def latest(plc_id: str = Query(alias='plcId'), db_number: int = Query(alias='dbNumber', ge=1, le=65535),
                 point_id: str | None = Query(None, alias='pointId')):
    profile = get_profile()
    identifier(plc_id)
    if point_id is not None:
        identifier(point_id)
    db = await get_db_session()
    try:
        return Response(json_bytes(success(await service.latest(db, profile, plc_id, db_number, point_id))),
                        media_type='application/json')
    finally:
        await db.close()


@router.get('/acquisition-data/latest/browse', operation_id='plc_facts_v2_latest_browse',
            response_model=LatestBrowseOut, responses=READ_RESPONSES)
async def latest_browse(plc_id: str | None = Query(None, alias='plcId'),
                        db_number: int | None = Query(None, alias='dbNumber', ge=1, le=65535),
                        point_search: str | None = Query(None, alias='pointSearch'),
                        page: int = Query(1, ge=1), page_size: int = Query(50, alias='pageSize', ge=1, le=100)):
    profile = get_profile()
    if plc_id is not None:
        identifier(plc_id)
    search = point_search.strip() if point_search is not None else ''
    if len(search) > 128:
        raise V2Error('invalid_request', 422)
    db = await get_db_session()
    try:
        return Response(json_bytes(success(await service.browse_latest(
            db, profile, plc_id, db_number, search, page, page_size))), media_type='application/json')
    finally:
        await db.close()


@router.get('/acquisition-data/history', operation_id='plc_facts_v2_history', response_model=HistoryOut, responses=HISTORY_RESPONSES)
async def history(start: str = Query(alias='from'), end: str = Query(alias='to'),
                  plc_id: str | None = Query(None, alias='plcId'),
                  db_number: int | None = Query(None, alias='dbNumber', ge=1, le=65535), page: int = Query(1, ge=1),
                  page_size: int = Query(50, alias='pageSize', ge=1, le=100)):
    profile = get_profile()
    if plc_id is not None:
        identifier(plc_id)
    start_time, end_time = parse_time(start), parse_time(end)
    db = await get_db_session()
    try:
        return success(await service.history(db, profile, plc_id, db_number, start_time, end_time, page, page_size))
    finally:
        await db.close()


@router.get('/acquisition-data/history/{id}', operation_id='plc_facts_v2_history_detail', response_model=DetailOut, responses=HISTORY_RESPONSES, response_model_exclude_unset=True)
async def detail(id: str):
    if not id.isascii() or not id.isdigit() or id.startswith('0') or len(id) > 19 or int(id) > 9223372036854775807:
        raise V2Error('not_found', 404)
    profile = get_profile()
    db = await get_db_session()
    try:
        return Response(json_bytes(success(await service.detail(db, profile, int(id)))),
                        media_type='application/json')
    finally:
        await db.close()
