"""
文件路径: /backend/app/hr/schemas/hr_in.py
功能描述: HR 模块写入 Schema
主要功能:
    - 定义部门、员工、考勤、招聘创建与更新入参
"""
import datetime
from typing import Optional

from common.schema_base import ApiSchema


class DepartmentCreate(ApiSchema):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    status: str = "active"


class DepartmentUpdate(ApiSchema):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None


class EmployeeCreate(ApiSchema):
    name: str
    department_id: Optional[int] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    join_date: Optional[datetime.date] = None
    status: str = "active"


class EmployeeUpdate(ApiSchema):
    name: Optional[str] = None
    department_id: Optional[int] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    join_date: Optional[datetime.date] = None
    status: Optional[str] = None


class AttendanceCreate(ApiSchema):
    employee_id: int
    date: datetime.date
    check_in: Optional[datetime.datetime] = None
    check_out: Optional[datetime.datetime] = None
    work_hours: Optional[int] = None
    status: str = "normal"
    remark: Optional[str] = None


class AttendanceUpdate(ApiSchema):
    check_in: Optional[datetime.datetime] = None
    check_out: Optional[datetime.datetime] = None
    work_hours: Optional[int] = None
    status: Optional[str] = None
    remark: Optional[str] = None


class RecruitmentCreate(ApiSchema):
    title: str
    department: Optional[str] = None
    count: int = 1
    applicants: int = 0
    status: str = "open"
    publish_date: Optional[datetime.date] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None


class RecruitmentUpdate(ApiSchema):
    title: Optional[str] = None
    department: Optional[str] = None
    count: Optional[int] = None
    applicants: Optional[int] = None
    status: Optional[str] = None
    publish_date: Optional[datetime.date] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
