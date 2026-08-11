"""
文件路径: /backend/app/monitor/api/__init__.py
功能描述: 监控模块 API 包初始化
主要功能:
    - 导出监控数据路由
"""
from app.monitor.api.routes import router

__all__ = ["router"]
