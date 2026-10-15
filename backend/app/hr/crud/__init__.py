"""
文件路径: /backend/app/hr/crud/__init__.py
功能描述: HR 模块 CRUD 导出
主要功能:
    - 导出部门、员工、考勤、招聘异步 CRUD 实例
"""
from app.hr.crud.async_hr import (
    async_crud_attendance,
    async_crud_department,
    async_crud_employee,
    async_crud_recruitment,
)

__all__ = ["async_crud_department", "async_crud_employee", "async_crud_attendance", "async_crud_recruitment"]
