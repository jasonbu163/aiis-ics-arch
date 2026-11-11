"""实绩自动快照、人工编辑和补建计划请求。"""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt
from app.task.schemas.fields import TaskDateTime

MAX_SEQ = 9007199254740991


class StrictBody(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Snapshot(StrictBody):
    producerId: str
    taskNo: str
    targetKey: str
    fieldConfigVersion: StrictInt = Field(ge=1)
    productionStatus: Literal['running', 'completed']
    observationSeq: StrictInt = Field(ge=1, le=MAX_SEQ)
    observedAt: TaskDateTime | None
    startedAt: TaskDateTime | None = None
    completedAt: TaskDateTime | None = None
    syncValues: dict[str, Any]
    localValues: dict[str, Any]

class ManualEdit(StrictBody):
    taskNo: str
    fieldConfigVersion: StrictInt = Field(ge=1)
    remark: str | None = Field(default=None, max_length=500)
    syncValues: dict[str, Any] | None = None
    localValues: dict[str, Any] | None = None


class Supplement(StrictBody):
    targetKey: str
    fieldConfigVersion: StrictInt = Field(ge=1)
    priority: StrictInt | None = Field(default=None, ge=1, le=10)
    remark: str | None = Field(default=None, max_length=500)
    syncValues: dict[str, Any] | None = None
    localValues: dict[str, Any] | None = None
    backfillExisting: StrictBool = False
