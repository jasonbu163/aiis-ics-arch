"""局部严格 JSON/HTTP 适配；完整退出 yield 依赖后才允许发送响应，错误始终脱敏。"""
from contextlib import AsyncExitStack
from decimal import Decimal, InvalidOperation
import json

from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from sqlalchemy.exc import DBAPIError
from starlette.responses import JSONResponse
from common.exceptions import BusinessException
from common.log import log_event

MAX_BODY_BYTES = 65536
MAX_DEPTH = 12


class IntegrationPayloadError(ValueError):
    def __init__(self, status, suffix):
        self.status, self.suffix = status, suffix
        super().__init__(suffix)


def strict_json(body):
    """原始 UTF-8 数字直接 Decimal；重复键与过深对象在 DTO 前拒绝。"""
    if len(body) > MAX_BODY_BYTES:
        raise IntegrationPayloadError(413, "payload_too_large")
    nesting, quoted, escaped = 0, False, False
    for byte in body:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 34:
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):
            nesting += 1
            if nesting > MAX_DEPTH:
                raise IntegrationPayloadError(413, "payload_too_large")
        elif byte in (93, 125):
            nesting -= 1
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate key")
            key.encode("utf-8", errors="strict")
            result[key] = value
        return result
    def number(token):
        result = Decimal(token)
        if not result.is_finite() or len(result.as_tuple().digits) > 256 or abs(result.as_tuple().exponent) > 1000:
            raise ValueError("unrepresentable number")
        return result
    def reject(_):
        raise ValueError("nonfinite number")
    def depth(value, level=0):
        if isinstance(value, (dict, list)):
            if level + 1 > MAX_DEPTH:
                raise IntegrationPayloadError(413, "payload_too_large")
            for item in value.values() if isinstance(value, dict) else value:
                depth(item, level + 1)
        elif isinstance(value, str):
            value.encode("utf-8", errors="strict")
    try:
        result = json.loads(body.decode("utf-8", errors="strict"), parse_float=number,
                            parse_int=number, parse_constant=reject, object_pairs_hook=pairs)
        depth(result)
        if not isinstance(result, dict):
            raise ValueError("object required")
        refs = result.get("sourceRefs")
        if isinstance(refs, list) and len(refs) > 128:
            raise IntegrationPayloadError(413, "payload_too_large")
        return result
    except IntegrationPayloadError:
        raise
    except (ValueError, UnicodeError, InvalidOperation, RecursionError):
        raise IntegrationPayloadError(422, "invalid_request") from None


def _commit_unknown(exception, error_type):
    """只保留当前owner的既有503未知事实；cleanup的cause/context不能将其降为格式错误。"""
    pending=[exception]
    seen=set()
    while pending:
        current=pending.pop()
        if current is None or id(current) in seen:
            continue
        seen.add(id(current))
        if (isinstance(current,BusinessException) and error_type is not None
                and isinstance(current.error_code,error_type) and current.code==503
                and current.error_code==getattr(error_type,"COMMIT_UNKNOWN",None)):
            return current
        pending.extend((current.__cause__,current.__context__))
    return None


class IntegrationRoute(APIRoute):
    """模块子类必须给出 error_type StrEnum；不注入用户或数据库。"""
    error_type = None
    owner = None

    def get_route_handler(self):
        handler = super().get_route_handler()
        async def integration_handler(request):
            previous = None
            commit_unknown = None
            response = None
            try:
                keys = ("fastapi_inner_astack", "fastapi_function_astack")
                previous = {key: request.scope[key] for key in keys}
                if not all(isinstance(stack, AsyncExitStack) for stack in previous.values()):
                    raise RuntimeError("unsupported dependency stack")
                async with AsyncExitStack() as request_stack, AsyncExitStack() as function_stack:
                    request.scope.update(fastapi_inner_astack=request_stack,
                                         fastapi_function_astack=function_stack)
                    media = request.headers.get("content-type", "").split(";")
                    parameters = [tuple(value.strip().lower() for value in part.partition("=")[::2])
                                  for part in media[1:]]
                    if media[0].strip().lower() != "application/json" or any(
                        key == "charset" and value.strip('"') != "utf-8" for key, value in parameters
                    ) or request.headers.get("content-encoding", "identity").strip().lower() != "identity":
                        raise IntegrationPayloadError(415, "media_type")
                    body = bytearray()
                    async for chunk in request.stream():
                        body.extend(chunk)
                        if len(body) > MAX_BODY_BYTES:
                            raise IntegrationPayloadError(413, "payload_too_large")
                    request._body = bytes(body)
                    request._json = strict_json(bytes(body))
                    try:
                        response = await handler(request)
                    except Exception as exc:
                        commit_unknown = _commit_unknown(exc,self.error_type)
                        raise
                if commit_unknown is not None:
                    raise commit_unknown
                if response is None:
                    raise RuntimeError("suppressed request failure")
                return response
            except Exception as exc:
                commit_unknown = commit_unknown or _commit_unknown(exc,self.error_type)
                if commit_unknown is not None:
                    error, code = self.error_type.COMMIT_UNKNOWN, 503
                elif isinstance(exc,BusinessException):
                    if isinstance(exc.error_code,self.error_type):
                        error, code = exc.error_code, exc.code
                    else:
                        error, code = self.error_type.INTERNAL_ERROR, 500
                elif isinstance(exc,IntegrationPayloadError):
                    error, code = self.error_type(f"{self.owner}.integration_{exc.suffix}"), exc.status
                elif isinstance(exc,RequestValidationError):
                    error, code = self.error_type.INVALID_REQUEST, 422
                elif isinstance(exc,DBAPIError):
                    error, code = self.error_type.UNAVAILABLE, 503
                else:
                    error, code = self.error_type.INTERNAL_ERROR, 500
            finally:
                if previous is not None:
                    request.scope.update(previous)
            try:
                log_event("WARNING" if code < 500 else "ERROR", "business_integration_rejected",
                          module=self.owner, status=code, error_code=error.value,
                          **getattr(request.state, "integration_context", {}))
            except Exception:
                pass
            return JSONResponse(status_code=code, content={"code": code, "message": error.value,
                                "data": None, "errorCode": error.value})
        return integration_handler
