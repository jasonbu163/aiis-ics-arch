"""
文件路径: /backend/app/control_agent/models/__init__.py
功能描述: Control Agent 数据模型汇聚模块
主要功能:
    - 导出门禁临时 token 模型
    - 支撑 Alembic 与测试环境加载模型元数据
"""
from app.control_agent.models.gate_token import ControlAgentGateToken

__all__ = ["ControlAgentGateToken"]
