"""
文件路径: /backend/app/hr/schemas/__init__.py
功能描述: HR 模块 Schema 导出
主要功能:
    - 导出 HR 写入、响应与查询模型
"""
from app.hr.schemas.hr_in import (
    AttendanceCreate,
    AttendanceUpdate,
    DepartmentCreate,
    DepartmentUpdate,
    EmployeeCreate,
    EmployeeUpdate,
    RecruitmentCreate,
    RecruitmentUpdate,
)
from app.hr.schemas.hr_out import AttendanceResponse, DepartmentResponse, EmployeeResponse, RecruitmentResponse
from app.hr.schemas.hr_query import AttendanceQueryParams, EmployeeQueryParams, RecruitmentQueryParams

__all__ = [
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentResponse",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "AttendanceCreate",
    "AttendanceUpdate",
    "AttendanceResponse",
    "RecruitmentCreate",
    "RecruitmentUpdate",
    "RecruitmentResponse",
    "EmployeeQueryParams",
    "AttendanceQueryParams",
    "RecruitmentQueryParams",
]
