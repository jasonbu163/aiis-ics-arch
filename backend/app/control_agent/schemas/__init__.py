"""
文件路径: /backend/app/control_agent/schemas/__init__.py
功能描述: Control Agent Schema 汇聚模块
主要功能:
    - 导出授权门禁请求与响应模型
    - 统一使用后端 API camelCase 序列化契约
"""
from app.control_agent.schemas.authorization import (
    ControlAgentActionScope,
    ControlAgentActionScopeRegistry,
    ControlAgentGateTokenCreate,
    ControlAgentGateTokenIssued,
    ControlAgentAuthorizationRequest,
    ControlAgentAuthorizationResponse,
)

__all__ = [
    "ControlAgentActionScope",
    "ControlAgentActionScopeRegistry",
    "ControlAgentGateTokenCreate",
    "ControlAgentGateTokenIssued",
    "ControlAgentAuthorizationRequest",
    "ControlAgentAuthorizationResponse",
]
