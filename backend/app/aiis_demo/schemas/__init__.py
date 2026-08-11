"""
文件路径: /backend/app/aiis_demo/schemas/__init__.py
功能描述: AIIS Demo Schema package 入口
主要功能:
    - 导出 AIIS Demo ping 响应 Schema
"""
from app.aiis_demo.schemas.ping import PingResponse


__all__ = ["PingResponse"]
