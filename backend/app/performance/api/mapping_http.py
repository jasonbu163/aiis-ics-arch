"""本模块新增映射JSON路由：完成依赖退出后再返回真实HTTP响应及无损解析。"""
from contextlib import AsyncExitStack
from decimal import Decimal, InvalidOperation
import json
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from sqlalchemy.exc import DBAPIError
from common.exceptions import BusinessException
from common.log import log_event
from app.performance.mapping_error_codes import MappingError


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError("non-finite JSON number")


class MappingRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()
        async def mapping_handler(request):
            previous_stacks = None
            try:
                # FastAPI 0.135.1用这两键求解yield依赖；只在本JSON route提前完成其退出。
                stack_keys = ("fastapi_inner_astack", "fastapi_function_astack")
                previous_stacks = {key: request.scope[key] for key in stack_keys}
                if not all(isinstance(stack, AsyncExitStack) for stack in previous_stacks.values()):
                    raise RuntimeError("Invalid dependency stack environment")
                response = None
                async with AsyncExitStack() as request_stack:
                    async with AsyncExitStack() as function_stack:
                        request.scope["fastapi_inner_astack"] = request_stack
                        request.scope["fastapi_function_astack"] = function_stack
                        scheme, _, credential = request.headers.get("authorization", "").partition(" ")
                        if scheme.lower() != "bearer" or not credential.strip():
                            raise BusinessException(MappingError.UNAUTHENTICATED, code=401)
                        if request.method in {"POST", "PUT"}:
                            try:
                                request._json = json.loads(await request.body(), parse_float=Decimal,
                                                           object_pairs_hook=_pairs, parse_constant=_nonfinite)
                            except (ValueError, UnicodeError, InvalidOperation, RecursionError):
                                raise BusinessException(MappingError.INVALID_SAMPLE, code=422) from None
                        response = await handler(request)
                if response is None:
                    raise RuntimeError("Dependency suppressed request failure")
                return response
            except BusinessException as exc:
                if isinstance(exc.error_code, MappingError):
                    error, code = exc.error_code, exc.code
                else:
                    error, code = MappingError.INTERNAL_ERROR, 500
            except HTTPException as exc:
                unauthenticated = exc.status_code == 401 or (exc.status_code == 403 and
                    isinstance(exc.detail, str) and exc.detail in {"Not authenticated", "Invalid authentication credentials"})
                if unauthenticated:
                    error, code = MappingError.UNAUTHENTICATED, 401
                elif exc.status_code == 403:
                    error, code = MappingError.FORBIDDEN, 403
                elif exc.status_code == 422:
                    error, code = MappingError.INVALID_SAMPLE, 422
                elif exc.status_code == 503:
                    error, code = MappingError.UNAVAILABLE, 503
                else:
                    error, code = MappingError.INTERNAL_ERROR, 500
            except RequestValidationError:
                error, code = MappingError.INVALID_SAMPLE, 422
            except DBAPIError:
                error, code = MappingError.UNAVAILABLE, 503
            except Exception:
                error, code = MappingError.INTERNAL_ERROR, 500
            finally:
                if previous_stacks is not None:
                    request.scope.update(previous_stacks)
            context = {key: getattr(request.state, "performance_mapping_" + key) for key in
                       ("actor_user_id", "equipment_id", "sample_id") if hasattr(request.state, "performance_mapping_" + key)}
            try:
                log_event("WARNING" if code < 500 else "ERROR", "performance_mapping_request_rejected",
                          method=request.method, error_code=error.value, status=code, **context)
            except Exception:
                # 日志sink不可用时仍返回脱敏错误，不能落入DEBUG traceback响应。
                pass
            return JSONResponse(status_code=code, content=dict(code=code, message=error.value, data=None, errorCode=error.value),
                                headers={"WWW-Authenticate": "Bearer"} if code == 401 else None)
        return mapping_handler


class PerformanceLegacyRoute(MappingRoute):
    """仅显式HTTP PUT/DELETE采用新边界；旧路由全局合同保留。"""
    def get_route_handler(self):
        legacy = APIRoute.get_route_handler(self)
        mapping = MappingRoute.get_route_handler(self)
        async def select_handler(request):
            if request.method in {"PUT", "DELETE"} and request.query_params.get("dataSource") == "http":
                return await mapping(request)
            return await legacy(request)
        return select_handler
