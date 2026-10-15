"""
文件路径: /backend/app/hr/api/__init__.py
功能描述: HR 模块 API 导出
主要功能:
    - 导出 HR 命名空间与子模块路由
"""
from app.hr.api.routes import attendance_router, department_router, employee_router, recruitment_router, router

__all__ = ["router", "department_router", "employee_router", "attendance_router", "recruitment_router"]
