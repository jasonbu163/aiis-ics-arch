"""
文件路径: /backend/app/auxiliary/schemas/auxiliary_out.py
功能描述: 辅助管理响应模型
主要功能:
    - 定义班组响应模型
    - 定义班次响应模型
    - 定义停机记录响应模型
    - 定义排班规则响应模型
"""
import datetime
from typing import Optional

from common.schema_base import ApiSchema


class ShiftTeamResponse(ApiSchema):
    id: int
    team_name: str
    leader: Optional[str] = None
    members: int = 0
    phone: Optional[str] = None
    status: str = "active"
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None


class ShiftResponse(ApiSchema):
    id: int
    team_id: int
    date: datetime.date
    day_leader: Optional[str] = None
    night_leader: Optional[str] = None
    day_members: Optional[str] = None
    night_members: Optional[str] = None
    remark: Optional[str] = None
    created_at: datetime.datetime


class StopRecordResponse(ApiSchema):
    id: int
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = None
    duration: Optional[int] = None
    shift: Optional[str] = None
    operator: Optional[str] = None
    reason: Optional[str] = None
    stop_type: Optional[str] = None
    status: str = "active"
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None


class ShiftRuleResponse(ApiSchema):
    id: int
    name: str = "default"
    shift_mode: str = "two_shift"
    cycle_name: str = "四班三运转"
    day_shift_start: str = "08:00"
    day_shift_end: str = "20:00"
    middle_shift_start: Optional[str] = None
    middle_shift_end: Optional[str] = None
    night_shift_start: str = "20:00"
    night_shift_end: str = "08:00"
    status: str = "active"
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
