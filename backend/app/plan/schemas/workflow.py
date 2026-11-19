"""计划部分写入及查询响应。"""
from pydantic import BaseModel, Field, StrictBool, StrictInt

from app.task.schemas.workflow import Outcome, ProductionStatus, Record, Upsert


class PlanUpsert(Upsert):
    productionStatus: ProductionStatus = 'new'
    priority: StrictInt = Field(default=5, ge=1, le=10)
    backfillExisting: StrictBool = False


class PlanRecord(Record):
    priority: int


class PlanResult(BaseModel):
    outcome: Outcome
    configVersion: int
    plan: PlanRecord
