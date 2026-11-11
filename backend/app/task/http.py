"""任务接口统一 HTTP 错误、认证与权限适配。"""
from contextlib import AsyncExitStack
from time import time
from hashlib import sha256
from fastapi import Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from core.deps import get_current_user
from common.log import log_event
from app.task.errors import TaskError, TaskErrorCode


def response(data):
    return JSONResponse({'code': 200, 'message': 'success', 'data': data, 'timestamp': int(time() * 1000)})


class TaskRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()
        async def wrapped(request: Request):
            previous = None
            response_value = None
            pending_unknown = None
            try:
                keys = ('fastapi_inner_astack', 'fastapi_function_astack')
                previous = {key: request.scope[key] for key in keys}
                if not all(isinstance(stack, AsyncExitStack) for stack in previous.values()):
                    raise RuntimeError('unsupported dependency stack')
                async with AsyncExitStack() as request_stack, AsyncExitStack() as function_stack:
                    request.scope.update(fastapi_inner_astack=request_stack, fastapi_function_astack=function_stack)
                    try:
                        response_value = await handler(request)
                    except TaskError as error:
                        if error.key == TaskErrorCode.COMMIT_UNKNOWN:
                            pending_unknown = error
                        raise
                if pending_unknown is not None:
                    raise pending_unknown
                if response_value is None:
                    raise RuntimeError('suppressed request failure')
                return response_value
            except Exception as exc:
                if pending_unknown is not None:
                    error = pending_unknown
                elif isinstance(exc, RequestValidationError):
                    error = TaskError(TaskErrorCode.INVALID_REQUEST, 422)
                elif isinstance(exc, HTTPException):
                    key = TaskErrorCode.UNAUTHENTICATED if exc.status_code == 401 or not request.headers.get('authorization') else TaskErrorCode.FORBIDDEN
                    error = TaskError(key, 401 if key == TaskErrorCode.UNAUTHENTICATED else 403)
                elif isinstance(exc, TaskError):
                    error = exc
                elif response_value is not None and request.method not in ('GET', 'HEAD'):
                    error = TaskError(TaskErrorCode.COMMIT_UNKNOWN, 503)
                else:
                    error = TaskError(TaskErrorCode.UNAVAILABLE, 503)
            finally:
                if previous is not None:
                    request.scope.update(previous)
            return JSONResponse(status_code=error.status, content={'code': error.status, 'message': error.key.value,
                                'data': None, 'errorCode': error.key.value, 'timestamp': int(time() * 1000)})
        return wrapped


def authorize(request: Request, user, *permissions, roles=('admin', 'supervisor', 'operator')):
    if user.role not in roles:
        raise TaskError(TaskErrorCode.FORBIDDEN, 403)
    if user.role != 'admin':
        granted = getattr(request.app.state, 'role_api_permissions', {}).get(user.role, ())
        if any(permission not in granted for permission in permissions):
            raise TaskError(TaskErrorCode.FORBIDDEN, 403)
    return user


async def actor(user=Depends(get_current_user)):
    return user


async def commit(db):
    try:
        await db.commit()
    except Exception:
        try:
            await db.rollback()
        except Exception:
            pass
        raise TaskError(TaskErrorCode.COMMIT_UNKNOWN, 503) from None


def audit_event(event, **fields):
    """仅记录有限身份和结果；日志失败不改变已经提交的业务响应。"""
    event_id = fields.pop('event_id', None)
    if event_id is not None:
        raw = event_id.encode('utf-8', errors='surrogatepass')
        fields['event_id_sha256'] = sha256(raw).hexdigest()
        try:
            event_id.encode('utf-8')
            if len(event_id) <= 128:
                fields['event_id'] = event_id
        except UnicodeEncodeError:
            pass
    try:
        log_event('INFO', event, **fields)
    except Exception:
        pass
