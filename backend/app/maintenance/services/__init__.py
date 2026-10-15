"""
文件路径: /backend/app/maintenance/services/__init__.py
功能描述: 维保管理 Service 导出
主要功能:
    - 导出异步维保管理 Service
"""
from app.maintenance.services.async_maintenance import MaintenanceService

__all__ = ["MaintenanceService"]
