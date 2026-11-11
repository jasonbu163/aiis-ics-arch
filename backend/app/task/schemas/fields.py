"""字段配置 API 请求结构，保留字段键和语言键原样。"""
from datetime import datetime
import re
from typing import Annotated, Any, Literal
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StrictBool, StrictInt
from app.task.errors import TaskErrorCode


_OFFSET_TIME = re.compile(
    r'[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt ][0-9]{2}:[0-9]{2}'
    r'(?::[0-9]{2}(?:[.,][0-9]{1,6})?)?(?:[Zz]|[+-][0-9]{2}:?[0-9]{2})'
)


def _task_time_input(value):
    if not isinstance(value, str) or not _OFFSET_TIME.fullmatch(value):
        raise ValueError('time must include an offset and at most six fractional digits')
    return value


TaskDateTime = Annotated[datetime, BeforeValidator(_task_time_input)]


class FieldChange(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scope: Literal['shared_sync', 'plan_local', 'performance_local']
    slotNo: StrictInt = Field(ge=1, le=100)
    name: str | None = None
    type: Literal['string', 'number', 'boolean'] | None = None
    labels: dict[str, str] | None = None
    unit: str | None = None
    isNullable: StrictBool | None = None
    enabled: StrictBool | None = None
    syncEnabled: StrictBool | None = None
    performanceOwner: Literal['order_snapshot', 'automated', 'manual'] | None = None
    planEditable: StrictBool | None = None
    performanceEditable: StrictBool | None = None
    planVisible: StrictBool | None = None
    performanceVisible: StrictBool | None = None
    planOrder: StrictInt | None = None
    performanceOrder: StrictInt | None = None


class ConfigSave(BaseModel):
    model_config = ConfigDict(extra='forbid')
    module: Literal['plan', 'performance']
    fieldConfigVersion: StrictInt = Field(ge=1)
    configRevision: str
    changes: list[FieldChange] = Field(max_length=200)


class Envelope(BaseModel):
    code: int = 200
    message: str = 'success'
    data: Any
    timestamp: int


class ErrorEnvelope(BaseModel):
    """任务接口的 HTTP 错误信封。"""
    code: int
    message: str
    data: None = None
    errorCode: TaskErrorCode
    timestamp: int
