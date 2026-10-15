"""
文件路径: /backend/app/equipment/services/__init__.py
功能描述: 设备模块 Service 导出
主要功能:
    - 导出设备业务服务实例
"""
from app.equipment.services.async_equipment import equipment_service

__all__ = ["equipment_service"]
