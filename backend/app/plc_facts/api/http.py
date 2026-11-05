"""本三路严格HTTP及依赖退出adapter；响应值保持Decimal及原point键。"""
import asyncio
from contextlib import AsyncExitStack
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DBAPIError
from starlette.responses import Response
from ..canonical import strict_json,canonical,MAX_BODY
from ..error_codes import FactsError
from ..schemas.receipt_out import ReceiptOut,FailureOut
from ..schemas.read_out import ReadOut
from ..services.async_ingest import emit

class FactsRoute(APIRoute):
    def get_route_handler(self):
        handler=super().get_route_handler()
        async def facts_handler(request):
            previous=None
            request.state.facts_boundary={}
            try:
                if request.method=='POST':
                    media=request.headers.get('content-type','').split(';')
                    if media[0].strip().lower()!='application/json' or request.headers.get('content-encoding','identity').lower()!='identity': raise FactsError('media_type',415)
                    for p in media[1:]:
                        k,sep,v=p.strip().partition('=')
                        if not sep or k.lower()!='charset' or v.strip('"').lower()!='utf-8': raise FactsError('media_type',415)
                    body=bytearray()
                    async for chunk in request.stream():
                        body.extend(chunk)
                        if len(body)>MAX_BODY: raise FactsError('payload_too_large',413)
                    request._body=bytes(body); request._json=strict_json(body)
                else:
                    keys=list(request.query_params)
                    if any(len(request.query_params.getlist(k))!=1 for k in keys): raise FactsError('invalid_request')
                stack_keys=('fastapi_inner_astack','fastapi_function_astack')
                previous={key:request.scope[key] for key in stack_keys}
                if not all(isinstance(s,AsyncExitStack) for s in previous.values()): raise RuntimeError('unsupported FastAPI dependency stack')
                async with asyncio.timeout(10 if request.method=='POST' else 5):
                    async with AsyncExitStack() as request_stack, AsyncExitStack() as function_stack:
                        request.scope.update(fastapi_inner_astack=request_stack,fastapi_function_astack=function_stack)
                        response=await handler(request)
                if response is None: raise RuntimeError('suppressed dependency error')
                return response
            except FactsError as exc:
                status=exc.code; suffix=exc.error_code.value; data=exc.data
            except RequestValidationError:
                status=422; suffix='plc_facts.invalid_request'; data=None
            except Exception as exc:
                boundary=request.state.facts_boundary
                if boundary.get('commitAttempted') or boundary.get('transactionStarted') and not boundary.get('known'):
                    status=503; suffix='plc_facts.commit_outcome_unknown'; data=dict(persistence='unknown',newFactsCommitted=None,retryable=True,retirementAllowed=False,diagnostics=[],rejectionToken=None)
                    emit('plc_facts_batch_commit_unknown',status=status)
                else:
                    status=503 if isinstance(exc,(DBAPIError,TimeoutError)) else 500
                    suffix='plc_facts.unavailable' if status==503 else 'plc_facts.internal_error'; data=None
            finally:
                if previous is not None: request.scope.update(previous)
            if data is None: data=dict(persistence='none',newFactsCommitted=False,retryable=status in (429,503),retirementAllowed=False,diagnostics=[])
            result=dict(code=status,message=suffix,errorCode=suffix,data=data)
            # Typed failure validation never echoes Pydantic errors or input.
            FailureOut.model_validate(result)
            emit('plc_facts_batch_rejected',status=status,error_code=suffix)
            return Response(canonical(result),status_code=status,media_type='application/json',headers={'Retry-After':'1'} if status==429 else None)
        async def timed_handler(request):
            try:
                async with asyncio.timeout(10 if request.method=='POST' else 5):
                    return await facts_handler(request)
            except TimeoutError:
                boundary=getattr(request.state,'facts_boundary',{})
                unknown=boundary.get('commitAttempted') or boundary.get('transactionStarted') and not boundary.get('known')
                suffix='plc_facts.commit_outcome_unknown' if unknown else 'plc_facts.unavailable'
                data=dict(persistence='unknown' if unknown else 'none',newFactsCommitted=None if unknown else False,retryable=True,retirementAllowed=False,diagnostics=[])
                result=dict(code=503,message=suffix,errorCode=suffix,data=data)
                emit('plc_facts_batch_commit_unknown' if unknown else 'plc_facts_batch_rejected',status=503,error_code=suffix)
                return Response(canonical(result),status_code=503,media_type='application/json')
        return timed_handler

def success(result):
    if 'status' in result['data']: ReceiptOut.model_validate(result)
    else: ReadOut.model_validate(result)
    return Response(canonical(result),media_type='application/json')

ERROR_RESPONSES={code:{'model':FailureOut,'description':'Typed PLC facts failure; persistence and retry boundary are explicit.'} for code in (403,409,410,413,415,422,429,503,500)}
