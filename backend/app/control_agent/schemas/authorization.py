"""
文件路径: /backend/app/control_agent/schemas/authorization.py
功能描述: Control Agent 授权门禁 Schema
主要功能:
    - 定义授权校验请求结构
    - 定义授权校验响应结构
    - 通过 ApiSchema 输出 camelCase JSON 字段
"""
from datetime import datetime

from pydantic import Field

from common.schema_base import ApiSchema


class ControlAgentGateTokenCreate(ApiSchema):
    """Control Agent 门禁 token 签发请求。"""

    subject_user_id: int = Field(..., ge=1)
    subject_username: str = Field(..., min_length=1, max_length=80)
    duration_hours: int = Field(default=2, ge=1, le=12)


class ControlAgentGateTokenIssued(ApiSchema):
    """Control Agent 门禁 token 签发响应。"""

    gate_token: str
    token_id: int
    subject_user_id: int
    subject_username: str
    subject_role: str
    issued_by_user_id: int
    issued_by_username: str
    issued_by_role: str
    allowed_scopes: list[str]
    resource_scope: str
    expires_at: datetime
    fail_closed: bool = True


class ControlAgentAuthorizationRequest(ApiSchema):
    """Control Agent 授权校验请求。"""

    operator_user_id: int = Field(..., ge=1)
    operator_username: str = Field(..., min_length=1, max_length=80)
    action_scope: str = Field(..., min_length=1, max_length=120)
    resource_id: str = Field(..., min_length=1, max_length=120)
    payload_hash: str = Field(..., min_length=1, max_length=160)


class ControlAgentAuthorizationResponse(ApiSchema):
    """Control Agent 授权校验响应。"""

    allowed: bool
    decision: str
    approval_id: str | None = None
    operator_user_id: int
    operator_username: str
    action_scope: str
    resource_id: str
    payload_hash: str
    expires_at: datetime | None = None
    fail_closed: bool = True


class ControlAgentActionScope(ApiSchema):
    """Control Agent 可授权动作 scope 描述。"""

    action_scope: str
    risk_level: str
    status: str
    requires_gate_token: bool
    default_resource_id: str | None = None
    payload_hash_strategy: str
    sample_payload_hash: str | None = None
    allowed_subject_roles: list[str]
    title_key: str
    description_key: str


class ControlAgentActionScopeRegistry(ApiSchema):
    """Control Agent 可授权动作 scope 注册表。"""

    items: list[ControlAgentActionScope]
    default_scope: str
    registry_version: str
