"""字段配置 API 请求结构，保留字段键和语言键原样。"""
from datetime import datetime
import re
from typing import Annotated, Generic, Literal, TypeVar
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
PerformanceOwner = Literal['order_snapshot', 'automated', 'manual', 'snapshot_auto']


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
    performanceOwner: PerformanceOwner | None = None
    planEditable: StrictBool | None = None
    performanceEditable: StrictBool | None = None
    planVisible: StrictBool | None = None
    performanceVisible: StrictBool | None = None
    planOrder: StrictInt | None = None
    performanceOrder: StrictInt | None = None


class ConfigSave(BaseModel):
    model_config = ConfigDict(extra='forbid')
    module: Literal['plan', 'performance', 'shared']
    configRevision: str = Field(pattern=r'^[1-9][0-9]{0,19}$')
    changes: list[FieldChange] = Field(max_length=200)


class FieldDelete(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scope: Literal['shared_sync', 'plan_local', 'performance_local']
    slotNo: StrictInt = Field(ge=1, le=100)
    name: str = Field(pattern=r'^[a-z][A-Za-z0-9_]{0,63}$')
    configRevision: str = Field(pattern=r'^[1-9][0-9]{0,19}$')


class SharedFieldIdentity(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scope: Literal['shared_sync']
    slotNo: StrictInt = Field(ge=1, le=100)
    name: str = Field(pattern=r'^[a-z][A-Za-z0-9_]{0,63}$')


class FieldBatchDelete(BaseModel):
    model_config = ConfigDict(extra='forbid')
    configRevision: str = Field(pattern=r'^[1-9][0-9]{0,19}$')
    fields: list[SharedFieldIdentity] = Field(min_length=1, max_length=100)


class LocalFieldIdentity(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scope: Literal['plan_local', 'performance_local']
    slotNo: StrictInt = Field(ge=1, le=100)
    name: str = Field(pattern=r'^[a-z][A-Za-z0-9_]{0,63}$')


class LocalFieldBatchDelete(BaseModel):
    model_config = ConfigDict(extra='forbid')
    module: Literal['plan', 'performance']
    configRevision: str = Field(pattern=r'^[1-9][0-9]{0,19}$')
    fields: list[LocalFieldIdentity] = Field(min_length=1, max_length=100)


class FieldDefinitionResult(BaseModel):
    scope: Literal['shared_sync', 'plan_local', 'performance_local']
    slotNo: int
    name: str
    type: Literal['string', 'number', 'boolean']
    labels: dict[Literal['zh-CN', 'en-US'], str]
    unit: str | None
    enabled: bool
    isNullable: bool
    syncEnabled: bool | None
    performanceOwner: PerformanceOwner | None
    planEditable: bool | None
    performanceEditable: bool | None
    planVisible: bool | None
    performanceVisible: bool | None
    planOrder: int | None
    performanceOrder: int | None


class FieldConfigResult(BaseModel):
    configVersion: int
    configRevision: str
    fields: list[FieldDefinitionResult]


class FieldDeleteResult(BaseModel):
    configVersion: int
    configRevision: str
    outcome: Literal['deleted']
    scope: Literal['shared_sync', 'plan_local', 'performance_local']
    slotNo: int
    name: str


class FieldBatchDeleteResult(BaseModel):
    outcome: Literal['deleted']
    deleted: list[SharedFieldIdentity]
    configVersion: int
    configRevision: str


class LocalFieldBatchDeleteResult(BaseModel):
    outcome: Literal['deleted']
    deleted: list[LocalFieldIdentity]
    configVersion: int
    configRevision: str


Payload = TypeVar('Payload')


class Envelope(BaseModel, Generic[Payload]):
    code: int = 200
    message: str = 'success'
    data: Payload
    timestamp: int


class ErrorEnvelope(BaseModel):
    """任务接口的 HTTP 错误信封。"""
    code: int
    message: str
    data: None = None
    errorCode: TaskErrorCode
    details: dict[str, str]
    timestamp: int
