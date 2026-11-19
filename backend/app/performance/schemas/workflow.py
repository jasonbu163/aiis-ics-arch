"""实绩部分上报、人工编辑及同步结果。"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, StrictInt

from app.task.schemas.fields import TaskDateTime
from app.task.schemas.workflow import Outcome, ProductionStatus, Record, Upsert


class PerformanceUpsert(Upsert):
    productionStatus: ProductionStatus = 'running'
    observationSeq: StrictInt | None = Field(default=None, ge=1, le=9007199254740991)
    observedAt: TaskDateTime | None = None
    startedAt: TaskDateTime = Field(default=None)
    completedAt: TaskDateTime = Field(default=None)


class ManualEdit(Upsert):
    """已有实绩的人工项和备注。"""


class PerformanceRecord(Record):
    startedAt: datetime | None
    completedAt: datetime | None
    lastObservedAt: datetime | None
    hasPlan: bool


class PlanSync(BaseModel):
    outcome: Literal['skipped', 'synced', 'unchanged']
    reason: Literal['no_plan'] | None
    statusChanged: bool
    fieldsChanged: list[str]


class PerformanceResult(BaseModel):
    outcome: Outcome
    configVersion: int
    performance: PerformanceRecord
    planSync: PlanSync
