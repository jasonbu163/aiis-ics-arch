"""
文件路径: /backend/app/project/schemas/project_in.py
功能描述: 项目模块写入 Schema
主要功能:
    - 定义项目创建与更新入参
    - 定义任务与里程碑写入入参
"""
from datetime import datetime
from typing import Optional

from common.schema_base import ApiSchema


class ProjectCreate(ApiSchema):
    name: str
    description: Optional[str] = None
    status: str = "active"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    owner: Optional[str] = None


class ProjectUpdate(ApiSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    owner: Optional[str] = None


class ProjectTaskCreate(ApiSchema):
    project_id: int
    name: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    assignee: Optional[str] = None


class ProjectTaskUpdate(ApiSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    assignee: Optional[str] = None


class ProjectMilestoneCreate(ApiSchema):
    project_id: int
    name: str
    description: Optional[str] = None
    due_date: datetime
    reached: bool = False
    reached_at: Optional[datetime] = None


class ProjectMilestoneUpdate(ApiSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    reached: Optional[bool] = None
    reached_at: Optional[datetime] = None
