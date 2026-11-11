"""计划、人工动作和现场领单的首版请求合同。"""
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from app.task.schemas.fields import TaskDateTime

MAX_SEQ = 9007199254740991


class StrictBody(BaseModel):
    model_config = ConfigDict(extra='forbid')


class PlanUpsert(StrictBody):
    taskNo: str
    fieldConfigVersion: StrictInt = Field(ge=1)
    targetKey: str | None = None
    priority: StrictInt | None = Field(default=None, ge=1, le=10)
    remark: str | None = Field(default=None, max_length=500)
    syncValues: dict[str, Any] | None = None
    localValues: dict[str, Any] | None = None
    producerId: str | None = None
    eventId: str | None = None


class PlanAction(StrictBody):
    actionRequestId: str
    fieldConfigVersion: StrictInt | None = Field(default=None, ge=1)
    targetKey: str | None = None
    priority: StrictInt | None = Field(default=None, ge=1, le=10)
    remark: str | None = Field(default=None, max_length=500)
    syncValues: dict[str, Any] | None = None
    localValues: dict[str, Any] | None = None
    dispatchId: str | None = None
    reason: str | None = Field(default=None, max_length=500)
    evidence: str | None = None


class Claim(StrictBody):
    targetKey: str
    producerId: str
    claimRequestId: str


class Report(StrictBody):
    dispatchId: str
    taskNo: str
    targetKey: str
    producerId: str
    outcome: Literal['plc_accepted', 'exception']
    requestSeq: StrictInt | None = Field(default=None, ge=0, le=MAX_SEQ)
    ackSeq: StrictInt | None = Field(default=None, ge=0, le=MAX_SEQ)
    ackObservedAt: TaskDateTime | None = None
    submissionPhase: Literal['not_submitted', 'possibly_submitted'] | None = None
    reasonCode: str | None = Field(default=None, max_length=64)
    detail: str | None = Field(default=None, max_length=500)

