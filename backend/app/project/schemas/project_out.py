"""
文件路径: /backend/app/project/schemas/project_out.py
功能描述: 项目模块响应 Schema
主要功能:
    - 定义项目、任务、里程碑响应结构
    - 统一 snake_case 到 camelCase 序列化
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from common.schema_base import ApiSchema


class ProjectOut(ApiSchema):
    id: int
    name: str
    description: Optional[str] = None
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    owner: Optional[str] = None
    progress: Decimal
    created_at: datetime
    updated_at: datetime


class ProjectTaskOut(ApiSchema):
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    status: str
    priority: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    assignee: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProjectMilestoneOut(ApiSchema):
    id: int
    project_id: int
    name: str
    description: Optional[str] = None
    due_date: datetime
    reached: bool
    reached_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ProjectDetailOut(ProjectOut):
    tasks: List[ProjectTaskOut] = []
    milestones: List[ProjectMilestoneOut] = []
