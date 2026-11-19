"""任务接口统一 HTTP 错误、认证与权限适配。"""
from contextlib import AsyncExitStack
from decimal import Decimal, InvalidOperation
import json
from time import time
from hashlib import sha256
from fastapi import Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from core.deps import get_current_user
from common.log import log_event
from app.task.errors import TaskError, TaskErrorCode
from app.task.schemas.workflow import Upsert


def response(data):
    return JSONResponse({'code': 200, 'message': 'success', 'data': data, 'timestamp': int(time() * 1000)})


def _parse_task_decimal(token):
    try:
        return Decimal(token)
    except InvalidOperation:
        # 合法 JSON 的指数可能超出 Decimal 表示范围，交由字段校验拒绝。
        return Decimal('NaN')


def _parse_task_integer(token):
    try:
        return int(token)
    except ValueError:
        # 保留正常 JSON 整数类型，超长整数在业务边界按范围拒绝。
        return _parse_task_decimal(token)


class _TaskUpsertRequest(Request):
    async def json(self):
        if not hasattr(self, '_json'):
            self._json = json.loads(await self.body(), parse_float=_parse_task_decimal, parse_int=_parse_task_integer)
        return self._json


class TaskRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()
        body_model = self.body_field.field_info.annotation if self.body_field is not None else None
        exact_numbers = isinstance(body_model, type) and issubclass(body_model, Upsert)

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
                        if exact_numbers:
                            request = _TaskUpsertRequest(request.scope, request.receive)
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
                    issue = exc.errors()[0]
                    field = '.'.join(str(part) for part in issue['loc'] if part not in ('body', 'query', 'path'))
                    field = field[:256].encode('utf-8', errors='replace').decode('utf-8')
                    error = TaskError(TaskErrorCode.INVALID_REQUEST, 422, field=field or None, reason=issue['type'])
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
                                'data': None, 'errorCode': error.key.value, 'details': error.details, 'timestamp': int(time() * 1000)})
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


async def retired():
    """对退役动作返回固定响应，无请求体、认证或会话依赖。"""
    raise TaskError(TaskErrorCode.ENDPOINT_RETIRED, 410, reason='retired_action')
