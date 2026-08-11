"""
文件路径: /backend/app/control_agent/services/__init__.py
功能描述: Control Agent Service 汇聚模块
主要功能:
    - 导出授权校验服务
    - 保持授权逻辑独立于 API 路由
"""
from app.control_agent.services.async_authorization import authorization_service

__all__ = ["authorization_service"]
