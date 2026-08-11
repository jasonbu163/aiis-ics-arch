"""
文件路径: /backend/app/control_agent/api/__init__.py
功能描述: Control Agent API 汇聚模块
主要功能:
    - 导出授权门禁路由
    - 保持 API 层只做认证、参数接收与 Service 调用
"""
from app.control_agent.api.routes import router

__all__ = ["router"]
