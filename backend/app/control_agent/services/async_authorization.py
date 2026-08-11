"""
文件路径: /backend/app/control_agent/services/async_authorization.py
功能描述: Control Agent 授权校验 Service
主要功能:
    - 校验 control-agent 高危动作授权范围
    - 生成无现场副作用的授权决策
    - 保持后端 API 与 CA 命令执行路径分离
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.control_agent.models.gate_token import ControlAgentGateToken
from app.control_agent.schemas.authorization import (
    ControlAgentActionScope,
    ControlAgentActionScopeRegistry,
    ControlAgentGateTokenCreate,
    ControlAgentGateTokenIssued,
    ControlAgentAuthorizationRequest,
    ControlAgentAuthorizationResponse,
)
from app.user.models.user import User


SELF_TEST_ACTION_SCOPE = "authorization.self_test"
SELF_TEST_RESOURCE_ID = "control-agent"
SELF_TEST_PAYLOAD_HASH = "sha256:self-test-payload"
ALLOWED_ACTION_SCOPES = {SELF_TEST_ACTION_SCOPE}
APPROVAL_TTL_SECONDS = 300
GATE_TOKEN_RESOURCE_SCOPE = "*"
GATE_TOKEN_MIN_HOURS = 1
GATE_TOKEN_MAX_HOURS = 12
GATE_TOKEN_ISSUER_ROLES = {"admin"}
GATE_TOKEN_SUBJECT_ROLES = {"admin", "supervisor"}
ACTION_SCOPE_REGISTRY_VERSION = "2026-06-24-control-agent-gate-v1"


class ControlAgentAuthorizationService:
    """Control Agent 授权校验服务。"""

    def list_action_scopes(self) -> ControlAgentActionScopeRegistry:
        """返回前端 / CA 可消费的动作 scope 注册表。"""

        return ControlAgentActionScopeRegistry(
            registry_version=ACTION_SCOPE_REGISTRY_VERSION,
            default_scope=SELF_TEST_ACTION_SCOPE,
            items=[
                ControlAgentActionScope(
                    action_scope=SELF_TEST_ACTION_SCOPE,
                    risk_level="self_test",
                    status="implemented",
                    requires_gate_token=True,
                    default_resource_id=SELF_TEST_RESOURCE_ID,
                    payload_hash_strategy="fixed_self_test",
                    sample_payload_hash=SELF_TEST_PAYLOAD_HASH,
                    allowed_subject_roles=sorted(GATE_TOKEN_SUBJECT_ROLES),
                    title_key="controlAgent.authorization.scope.selfTest.title",
                    description_key="controlAgent.authorization.scope.selfTest.description",
                )
            ],
        )

    async def issue_gate_token(
        self,
        db: AsyncSession,
        request: ControlAgentGateTokenCreate,
        current_user: User,
    ) -> ControlAgentGateTokenIssued:
        """为最高权限用户签发绑定指定高权限目标用户的门禁 token。"""

        self._ensure_highest_privilege_user(current_user)
        subject_user = await self._get_gate_token_subject(db, request)
        self._ensure_gate_token_subject(subject_user)

        duration_hours = min(max(request.duration_hours, GATE_TOKEN_MIN_HOURS), GATE_TOKEN_MAX_HOURS)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=duration_hours)
        gate_token = secrets.token_urlsafe(32)
        token_row = ControlAgentGateToken(
            token_hash=self._hash_token(gate_token),
            subject_user_id=subject_user.id,
            subject_username=subject_user.username,
            subject_role=subject_user.role,
            issued_by_user_id=current_user.id,
            issued_by_username=current_user.username,
            issued_by_role=current_user.role,
            status="active",
            allowed_scopes=sorted(ALLOWED_ACTION_SCOPES),
            resource_scope=GATE_TOKEN_RESOURCE_SCOPE,
            expires_at=expires_at,
            metadata_json={"duration_hours": duration_hours},
        )

        db.add(token_row)
        await db.commit()
        await db.refresh(token_row)

        return ControlAgentGateTokenIssued(
            gate_token=gate_token,
            token_id=token_row.id,
            subject_user_id=token_row.subject_user_id,
            subject_username=token_row.subject_username,
            subject_role=token_row.subject_role,
            issued_by_user_id=token_row.issued_by_user_id,
            issued_by_username=token_row.issued_by_username,
            issued_by_role=token_row.issued_by_role,
            allowed_scopes=token_row.allowed_scopes,
            resource_scope=token_row.resource_scope,
            expires_at=token_row.expires_at,
            fail_closed=True,
        )

    async def verify_authorization(
        self,
        db: AsyncSession,
        request: ControlAgentAuthorizationRequest,
        gate_token: str,
    ) -> ControlAgentAuthorizationResponse:
        """使用门禁 token 校验动作 scope 并返回 fail-closed 授权决策。"""

        now = datetime.now(timezone.utc)
        token_row = await self._get_active_gate_token(db, gate_token, now)
        if token_row is None:
            return self._deny(
                decision="invalid_token",
                request=request,
                operator_user_id=request.operator_user_id,
                operator_username=request.operator_username,
            )

        if token_row.subject_user_id != request.operator_user_id or token_row.subject_username != request.operator_username:
            return self._deny(
                decision="operator_mismatch",
                request=request,
                operator_user_id=token_row.subject_user_id,
                operator_username=token_row.subject_username,
            )

        if request.action_scope not in token_row.allowed_scopes:
            return self._deny(
                decision="scope_not_allowed",
                request=request,
                operator_user_id=token_row.subject_user_id,
                operator_username=token_row.subject_username,
            )

        if token_row.resource_scope != GATE_TOKEN_RESOURCE_SCOPE and token_row.resource_scope != request.resource_id:
            return self._deny(
                decision="resource_not_allowed",
                request=request,
                operator_user_id=token_row.subject_user_id,
                operator_username=token_row.subject_username,
            )

        token_row.last_used_at = now
        token_row.use_count += 1
        await db.commit()

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=APPROVAL_TTL_SECONDS)
        return ControlAgentAuthorizationResponse(
            allowed=True,
            decision="allowed",
            approval_id=f"auth-{token_row.id}-{uuid4().hex[:12]}",
            operator_user_id=token_row.subject_user_id,
            operator_username=token_row.subject_username,
            action_scope=request.action_scope,
            resource_id=request.resource_id,
            payload_hash=request.payload_hash,
            expires_at=expires_at,
            fail_closed=True,
        )

    async def _get_active_gate_token(
        self,
        db: AsyncSession,
        gate_token: str,
        now: datetime,
    ) -> ControlAgentGateToken | None:
        result = await db.execute(
            select(ControlAgentGateToken)
            .where(ControlAgentGateToken.token_hash == self._hash_token(gate_token))
            .where(ControlAgentGateToken.status == "active")
            .where(ControlAgentGateToken.revoked_at.is_(None))
            .where(ControlAgentGateToken.expires_at > now)
        )
        return result.scalar_one_or_none()

    async def _get_gate_token_subject(
        self,
        db: AsyncSession,
        request: ControlAgentGateTokenCreate,
    ) -> User:
        result = await db.execute(
            select(User)
            .where(User.id == request.subject_user_id)
            .where(User.username == request.subject_username)
            .where(User.is_active.is_(True))
        )
        subject_user = result.scalar_one_or_none()
        if subject_user is None:
            raise LookupError("control_agent_gate_token_subject_not_found")
        return subject_user

    def _ensure_highest_privilege_user(self, user: User) -> None:
        if user.role not in GATE_TOKEN_ISSUER_ROLES:
            raise PermissionError("control_agent_gate_token_requires_admin")

    def _ensure_gate_token_subject(self, user: User) -> None:
        if user.role not in GATE_TOKEN_SUBJECT_ROLES:
            raise PermissionError("control_agent_gate_token_subject_role_not_allowed")

    def _deny(
        self,
        *,
        decision: str,
        request: ControlAgentAuthorizationRequest,
        operator_user_id: int,
        operator_username: str,
    ) -> ControlAgentAuthorizationResponse:
        return ControlAgentAuthorizationResponse(
            allowed=False,
            decision=decision,
            approval_id=None,
            operator_user_id=operator_user_id,
            operator_username=operator_username,
            action_scope=request.action_scope,
            resource_id=request.resource_id,
            payload_hash=request.payload_hash,
            expires_at=None,
            fail_closed=True,
        )

    def _hash_token(self, gate_token: str) -> str:
        return hashlib.sha256(gate_token.encode("utf-8")).hexdigest()


authorization_service = ControlAgentAuthorizationService()
