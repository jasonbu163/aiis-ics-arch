"""采集消费者 HTTP 边界；业务事务由消费 Service 执行。"""
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from fastapi.security import HTTPBearer
from starlette.responses import JSONResponse, Response

from common.response import StandardResponse
from database import get_db_session
from ..consumption_config import authorize
from ..consumption_domain import (
    CONSUMER_ID_HEADER, DELIVERY_ID_HEADER, LEASE_GENERATION_HEADER, LEASE_ID_HEADER,
    ConsumerError, Lease, TargetWrite, consumer_uuid,
)
from ..schemas import consumption as schema
from ..services import async_consumption as service
from ..v2_config import get_profile
from ..v2_domain import V2Error, json_bytes
from .v2 import emit, success

ConsumerId = Annotated[schema.UuidText, Path(alias='consumerId')]
DeliveryId = Annotated[schema.UuidText, Path(alias='deliveryId')]

PATH_PERMISSIONS = {
    'create_consumer': 'create', 'set_run_state': 'run', 'change_lease': 'lease',
    'consumer_status': 'read', 'read_next': 'read', 'mark_pending': 'pending',
    'acknowledge': 'ack',
}


def lease_headers(
    lease_id: str | None = Header(default=None, alias=LEASE_ID_HEADER),
    lease_generation: str | None = Header(default=None, alias=LEASE_GENERATION_HEADER),
):
    return Lease(lease_id, lease_generation)


def target_headers(request):
    names = ('authorization', CONSUMER_ID_HEADER, DELIVERY_ID_HEADER, LEASE_ID_HEADER, LEASE_GENERATION_HEADER)
    headers = request.headers
    return TargetWrite(headers.get('authorization'), headers.get(CONSUMER_ID_HEADER),
                       headers.get(DELIVERY_ID_HEADER),
                       Lease(headers.get(LEASE_ID_HEADER), headers.get(LEASE_GENERATION_HEADER)),
                       any(len(headers.getlist(name)) > 1 for name in names))


class ConsumptionRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()
        action = self.endpoint.__name__

        async def wrapped(request):
            boundary = {'commit_attempted': False}
            request.state.acq006_boundary = boundary
            try:
                identity = consumer_uuid(request.path_params.get('consumerId'))
                for name in ('authorization', LEASE_ID_HEADER, LEASE_GENERATION_HEADER):
                    if len(request.headers.getlist(name)) > 1:
                        raise ConsumerError('invalid_request', 422)
                request.state.acq006_grant = authorize(request.headers.get('authorization'), identity,
                                                       PATH_PERMISSIONS[action])
                response = await handler(request)
                if boundary['commit_attempted']:
                    emit('acquisition_consumer_transition', action=action, consumer_id=identity)
                return response
            except ConsumerError as failure:
                error = failure
            except RequestValidationError:
                error = ConsumerError('invalid_request', 422)
            except V2Error:
                error = ConsumerError('not_ready', 503)
            except Exception:
                error = ConsumerError('commit_outcome_unknown' if boundary['commit_attempted'] else 'not_ready', 503)
            emit('acquisition_consumer_rejected', action=action, status=error.status, error_code=error.key)
            return JSONResponse(status_code=error.status, content={
                'code': error.status, 'message': error.key, 'data': error.data, 'errorCode': error.key,
            }, headers={'WWW-Authenticate': 'Bearer'} if error.status == 401 else None)
        return wrapped


router = APIRouter(prefix='/acquisition-consumers', tags=['acquisition-consumers'], route_class=ConsumptionRoute,
                   dependencies=[Depends(HTTPBearer(auto_error=False, scheme_name='AcquisitionConsumerBearer'))],
                   responses={code: {'model': schema.FailureOut, 'description': 'Acquisition consumer failure'}
                              for code in (401, 403, 404, 409, 410, 422, 503)})


async def execute(request, action, *args):
    profile = get_profile()
    db = await get_db_session()
    try:
        data = await service.dispatch(db, profile, request.state.acq006_boundary, action,
                                      request.state.acq006_grant, *args)
        return success(data)
    finally:
        await db.close()


@router.put('/{consumerId}', operation_id='acq_consumer_create', response_model=StandardResponse[schema.ConsumerCreatedOut])
async def create_consumer(consumer_id: ConsumerId, body: schema.CreateConsumerIn, request: Request):
    return await execute(request, service.create, body)


@router.put('/{consumerId}/run-state', operation_id='acq_consumer_run_state',
            response_model=StandardResponse[schema.RunStateOut])
async def set_run_state(consumer_id: ConsumerId, body: schema.RunStateIn, request: Request):
    return await execute(request, service.set_run_state, body)


@router.post('/{consumerId}/lease', operation_id='acq_consumer_lease', response_model=StandardResponse[schema.LeaseOut])
async def change_lease(consumer_id: ConsumerId, body: schema.LeaseIn, request: Request,
                       lease: Lease = Depends(lease_headers)):
    return await execute(request, service.change_lease, body, lease)


@router.get('/{consumerId}', operation_id='acq_consumer_status', response_model=StandardResponse[schema.ConsumerStatusOut])
async def consumer_status(consumer_id: ConsumerId, request: Request):
    return await execute(request, service.status)


@router.get('/{consumerId}/next', operation_id='acq_consumer_next',
            response_model=StandardResponse[schema.ReadyOut | schema.EmptyOut])
async def read_next(consumer_id: ConsumerId, request: Request, lease: Lease = Depends(lease_headers)):
    return Response(json_bytes(await execute(request, service.read_next, lease)), media_type='application/json')


@router.put('/{consumerId}/pending/{deliveryId}', operation_id='acq_consumer_pending',
            response_model=StandardResponse[schema.PendingOut])
async def mark_pending(consumer_id: ConsumerId, delivery_id: DeliveryId, body: schema.PendingIn,
                       request: Request, lease: Lease = Depends(lease_headers)):
    return await execute(request, service.mark_pending, delivery_id, body, lease)


@router.post('/{consumerId}/pending/{deliveryId}/ack', operation_id='acq_consumer_ack',
             response_model=StandardResponse[schema.ConfirmedOut])
async def acknowledge(consumer_id: ConsumerId, delivery_id: DeliveryId, body: schema.AckIn,
                      request: Request, lease: Lease = Depends(lease_headers)):
    return await execute(request, service.acknowledge, delivery_id, body, lease)
