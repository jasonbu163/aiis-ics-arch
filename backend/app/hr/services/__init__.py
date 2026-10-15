"""
文件路径: /backend/app/hr/services/__init__.py
功能描述: HR 模块 Service 导出
主要功能:
    - 导出 HR 异步业务服务实例
"""
from app.hr.services.async_hr import hr_service

__all__ = ["hr_service"]
