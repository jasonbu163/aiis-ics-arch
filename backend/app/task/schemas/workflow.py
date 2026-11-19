"""计划与实绩共用的部分写入、记录和分页合同。"""
from datetime import datetime
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator

from app.task.schemas.fields import TaskDateTime

ProductionStatus = Literal['new', 'running', 'completed', 'error']
Outcome = Literal['created', 'updated', 'unchanged']
Module = Literal['plan', 'performance']
TaskRecord = TypeVar('TaskRecord')


class Upsert(BaseModel):
    model_config = ConfigDict(extra='forbid')

    taskNo: str
    targetKey: str | None = None
    producerId: str | None = None
    fieldConfigVersion: StrictInt | None = Field(default=None, ge=1)
    items: dict[str, Any] | None = None
    remark: str | None = Field(default=None, max_length=500)

    @field_validator('remark')
    @classmethod
    def valid_remark(cls, value):
        if value is not None:
            try:
                value.encode('utf-8')
            except UnicodeEncodeError:
                raise ValueError('invalid Unicode') from None
        return value


class QueryFilters(BaseModel):
    page: int = Field(default=1, ge=1)
    pageSize: int = Field(default=20, ge=1, le=100)
    taskNo: str | None = None
    targetKey: str | None = None
    productionStatus: ProductionStatus | None = None
    createdFrom: TaskDateTime | None = None
    createdTo: TaskDateTime | None = None
    sortOrder: Literal['asc', 'desc'] = 'desc'


class Record(BaseModel):
    id: str
    taskNo: str
    targetKey: str | None
    productionStatus: ProductionStatus
    remark: str | None
    createdAt: datetime
    updatedAt: datetime
    items: dict[str, str | bool | int | float | None]


class Page(BaseModel, Generic[TaskRecord]):
    items: list[TaskRecord]
    total: int
    page: int
    pageSize: int
    totalPages: int
