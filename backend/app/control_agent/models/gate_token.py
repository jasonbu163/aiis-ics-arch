"""
文件路径: /backend/app/control_agent/models/gate_token.py
功能描述: Control Agent 门禁临时 token 模型
主要功能:
    - 保存门禁 token hash 而非明文
    - 绑定 token 到最高权限用户
    - 记录有效期、撤销状态与使用审计字段
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base, IntPk, Timestamp, UpdatedAt


class ControlAgentGateToken(Base):
    """Control Agent 门禁临时 token。"""

    __tablename__ = "control_agent_gate_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_control_agent_gate_tokens_hash"),
        Index("ix_control_agent_gate_tokens_subject_status", "subject_user_id", "status"),
        Index("ix_control_agent_gate_tokens_expiry", "status", "expires_at"),
    )

    id: Mapped[IntPk]
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, comment="token SHA-256 hash")
    subject_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True, comment="绑定用户ID")
    subject_username: Mapped[str] = mapped_column(String(80), nullable=False, index=True, comment="绑定用户名")
    subject_role: Mapped[str] = mapped_column(String(30), nullable=False, comment="绑定用户角色")
    issued_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True, comment="签发用户ID")
    issued_by_username: Mapped[str] = mapped_column(String(80), nullable=False, comment="签发用户名")
    issued_by_role: Mapped[str] = mapped_column(String(30), nullable=False, comment="签发用户角色")
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False, index=True, comment="active/revoked/expired")
    allowed_scopes: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="允许的 action scope")
    resource_scope: Mapped[str] = mapped_column(String(120), default="*", nullable=False, comment="资源范围")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True, comment="过期时间")
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), comment="撤销时间")
    revoked_by: Mapped[str | None] = mapped_column(String(80), comment="撤销用户")
    revoke_reason: Mapped[str | None] = mapped_column(Text, comment="撤销原因")
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), comment="最后使用时间")
    use_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="使用次数")
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment="扩展审计信息")
    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]
