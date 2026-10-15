"""
文件路径: /backend/app/hr/schemas/hr_query.py
功能描述: HR 模块查询 Schema
主要功能:
    - 定义员工、考勤、招聘查询参数
"""
from typing import Optional

from pydantic import Field

from common.schema_base import ApiSchema


class EmployeeQueryParams(ApiSchema):
    department_id: Optional[int] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AttendanceQueryParams(ApiSchema):
    employee_id: Optional[int] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class RecruitmentQueryParams(ApiSchema):
    status: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
