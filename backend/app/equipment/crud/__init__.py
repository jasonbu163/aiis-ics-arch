"""
文件路径: /backend/app/equipment/crud/__init__.py
功能描述: 设备模块 CRUD 导出
主要功能:
    - 导出设备异步 CRUD 实例
"""
from app.equipment.crud.async_equipment import equipment_crud

__all__ = ["equipment_crud"]
