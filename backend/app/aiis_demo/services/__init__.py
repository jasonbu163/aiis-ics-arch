"""
文件路径: /backend/app/aiis_demo/services/__init__.py
功能描述: AIIS Demo Service package 入口
主要功能:
    - 导出 AIIS Demo ping Service
"""
from app.aiis_demo.services.async_ping import get_ping


__all__ = ["get_ping"]
