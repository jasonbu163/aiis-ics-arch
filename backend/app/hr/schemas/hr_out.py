"""
文件路径: /backend/app/hr/schemas/hr_out.py
功能描述: HR 模块响应 Schema
主要功能:
    - 定义部门、员工、考勤、招聘响应结构
"""
import datetime
from typing import Optional

from pydantic import ConfigDict

from common.schema_base import ApiSchema


class DepartmentResponse(ApiSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    status: str = "active"
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None


class EmployeeResponse(ApiSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    department_id: Optional[int] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    join_date: Optional[datetime.date] = None
    status: str = "active"
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None


class AttendanceResponse(ApiSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    employee_id: int
    date: datetime.date
    check_in: Optional[datetime.datetime] = None
    check_out: Optional[datetime.datetime] = None
    work_hours: Optional[int] = None
    status: str = "normal"
    remark: Optional[str] = None
    created_at: datetime.datetime


class RecruitmentResponse(ApiSchema):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    department: Optional[str] = None
    count: int = 1
    applicants: int = 0
    status: str = "open"
    publish_date: Optional[datetime.date] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
