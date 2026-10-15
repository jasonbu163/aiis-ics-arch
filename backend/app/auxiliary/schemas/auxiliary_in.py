"""
文件路径: /backend/app/auxiliary/schemas/auxiliary_in.py
功能描述: 辅助管理创建和更新入参模型
主要功能:
    - 定义班组写入模型
    - 定义班次写入模型
    - 定义停机记录写入模型
    - 定义排班规则写入模型
"""
import datetime
from typing import Optional

from common.schema_base import ApiSchema


class ShiftTeamCreate(ApiSchema):
    team_name: str
    leader: Optional[str] = None
    members: int = 0
    phone: Optional[str] = None
    status: str = "active"


class ShiftTeamUpdate(ApiSchema):
    team_name: Optional[str] = None
    leader: Optional[str] = None
    members: Optional[int] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class ShiftCreate(ApiSchema):
    team_id: int
    date: datetime.date
    day_leader: Optional[str] = None
    night_leader: Optional[str] = None
    day_members: Optional[str] = None
    night_members: Optional[str] = None
    remark: Optional[str] = None


class ShiftUpdate(ApiSchema):
    day_leader: Optional[str] = None
    night_leader: Optional[str] = None
    day_members: Optional[str] = None
    night_members: Optional[str] = None
    remark: Optional[str] = None


class StopRecordCreate(ApiSchema):
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = None
    duration: Optional[int] = None
    shift: Optional[str] = None
    operator: Optional[str] = None
    reason: Optional[str] = None
    stop_type: Optional[str] = None
    status: str = "active"


class StopRecordUpdate(ApiSchema):
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    duration: Optional[int] = None
    shift: Optional[str] = None
    operator: Optional[str] = None
    reason: Optional[str] = None
    stop_type: Optional[str] = None
    status: Optional[str] = None


class ShiftRuleUpdate(ApiSchema):
    name: Optional[str] = None
    shift_mode: Optional[str] = None
    cycle_name: Optional[str] = None
    day_shift_start: Optional[str] = None
    day_shift_end: Optional[str] = None
    middle_shift_start: Optional[str] = None
    middle_shift_end: Optional[str] = None
    night_shift_start: Optional[str] = None
    night_shift_end: Optional[str] = None
    status: Optional[str] = None
