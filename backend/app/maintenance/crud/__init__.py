"""
文件路径: /backend/app/maintenance/crud/__init__.py
功能描述: 维保管理 CRUD 导出
主要功能:
    - 导出异步维保管理 CRUD
"""
from app.maintenance.crud.async_maintenance import MaintenanceCRUD

__all__ = ["MaintenanceCRUD"]
