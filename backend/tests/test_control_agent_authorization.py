"""
文件路径: /backend/tests/test_control_agent_authorization.py
功能描述: Control Agent 授权门禁 API 测试
主要功能:
    - 验证授权 self-test 成功路径
    - 验证未知 action scope fail-closed
    - 验证认证与权限边界
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.control_agent.models.gate_token import ControlAgentGateToken
from app.user.models.user import User
from core.security import hash_password


AUTHORIZATION_VERIFY_PATH = "/api/v1/control-agent/authorization/verify"
GATE_TOKENS_PATH = "/api/v1/control-agent/gate-tokens"
ACTION_SCOPES_PATH = "/api/v1/control-agent/action-scopes"


def _authorization_payload(
    *,
    operator_user_id: int,
    operator_username: str,
    action_scope: str = "authorization.self_test",
) -> dict:
    return {
        "operatorUserId": operator_user_id,
        "operatorUsername": operator_username,
        "actionScope": action_scope,
        "resourceId": "control-agent",
        "payloadHash": "sha256:self-test-payload",
    }


async def _get_user(db_session: AsyncSession, username: str) -> User:
    result = await db_session.execute(select(User).where(User.username == username))
    user = result.scalar_one()
    return user


async def _create_user(
    db_session: AsyncSession,
    *,
    username: str,
    password: str,
    name: str,
    role: str,
) -> User:
    await db_session.execute(
        text(
            """
            INSERT INTO users (username, password, name, `role`, is_active, created_at, updated_at)
            VALUES (:username, :password, :name, :role, :is_active, NOW(), NOW())
            """
        ),
        {
            "username": username,
            "password": hash_password(password),
            "name": name,
            "role": role,
            "is_active": True,
        },
    )
    await db_session.commit()
    return await _get_user(db_session, username)


async def _issue_gate_token(
    test_client: AsyncClient,
    auth_headers: dict,
    *,
    subject_user_id: int,
    subject_username: str,
    duration_hours: int = 2,
) -> str:
    response = await test_client.post(
        GATE_TOKENS_PATH,
        json={
            "subjectUserId": subject_user_id,
            "subjectUsername": subject_username,
            "durationHours": duration_hours,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["data"]["gateToken"]
    return body["data"]["gateToken"]


@pytest.mark.asyncio
async def test_list_control_agent_action_scopes_for_admin(
    test_client: AsyncClient,
    auth_headers: dict,
):
    """admin 可以读取 CA 授权动作 scope 注册表。"""

    response = await test_client.get(ACTION_SCOPES_PATH, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["data"]["registryVersion"] == "2026-06-24-control-agent-gate-v1"
    assert body["data"]["defaultScope"] == "authorization.self_test"
    assert body["data"]["items"] == [
        {
            "actionScope": "authorization.self_test",
            "riskLevel": "self_test",
            "status": "implemented",
            "requiresGateToken": True,
            "defaultResourceId": "control-agent",
            "payloadHashStrategy": "fixed_self_test",
            "samplePayloadHash": "sha256:self-test-payload",
            "allowedSubjectRoles": ["admin", "supervisor"],
            "titleKey": "controlAgent.authorization.scope.selfTest.title",
            "descriptionKey": "controlAgent.authorization.scope.selfTest.description",
        }
    ]


@pytest.mark.asyncio
async def test_list_control_agent_action_scopes_rejects_operator(
    test_client: AsyncClient,
    db_session: AsyncSession,
):
    """普通 operator 不能读取 CA 授权动作 scope 注册表。"""

    await _create_user(
        db_session,
        username="operator_scope_ca",
        password="operator123",
        name="Operator Scope CA",
        role="operator",
    )

    login_response = await test_client.post(
        "/api/v1/auth/login",
        json={"username": "operator_scope_ca", "password": "operator123"},
    )
    token = login_response.json()["data"]["accessToken"]

    response = await test_client.get(ACTION_SCOPES_PATH, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["detail"] == "权限不足，需要 control-agent-read 权限"


@pytest.mark.asyncio
async def test_issue_control_agent_gate_token_for_admin(
    test_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """admin 可以签发绑定指定 admin 的门禁 token，数据库只保存 hash。"""

    admin_user = await _get_user(db_session, "admin")

    response = await test_client.post(
        GATE_TOKENS_PATH,
        json={
            "subjectUserId": admin_user.id,
            "subjectUsername": admin_user.username,
            "durationHours": 1,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    token_value = body["data"]["gateToken"]
    assert body["data"]["subjectUserId"] == admin_user.id
    assert body["data"]["subjectUsername"] == "admin"
    assert body["data"]["subjectRole"] == "admin"
    assert body["data"]["issuedByUserId"] == admin_user.id
    assert body["data"]["issuedByUsername"] == "admin"
    assert body["data"]["issuedByRole"] == "admin"
    assert body["data"]["allowedScopes"] == ["authorization.self_test"]
    assert body["data"]["resourceScope"] == "*"
    assert body["data"]["failClosed"] is True

    result = await db_session.execute(select(ControlAgentGateToken))
    token_row = result.scalar_one()
    assert token_row.subject_username == "admin"
    assert token_row.subject_role == "admin"
    assert token_row.issued_by_username == "admin"
    assert token_row.issued_by_role == "admin"
    assert token_row.status == "active"
    assert token_row.token_hash != token_value
    assert len(token_row.token_hash) == 64


@pytest.mark.asyncio
async def test_verify_control_agent_authorization_allows_self_test(
    test_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """门禁 token 可以通过 authorization.self_test 授权校验。"""

    supervisor = await _create_user(
        db_session,
        username="supervisor_ca",
        password="supervisor123",
        name="Supervisor CA",
        role="supervisor",
    )
    gate_token = await _issue_gate_token(
        test_client,
        auth_headers,
        subject_user_id=supervisor.id,
        subject_username=supervisor.username,
    )

    response = await test_client.post(
        AUTHORIZATION_VERIFY_PATH,
        json=_authorization_payload(
            operator_user_id=supervisor.id,
            operator_username=supervisor.username,
        ),
        headers={"Authorization": f"Bearer {gate_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert body["data"]["allowed"] is True
    assert body["data"]["decision"] == "allowed"
    assert body["data"]["approvalId"].startswith("auth-")
    assert body["data"]["operatorUserId"] == supervisor.id
    assert body["data"]["operatorUsername"] == "supervisor_ca"
    assert body["data"]["actionScope"] == "authorization.self_test"
    assert body["data"]["resourceId"] == "control-agent"
    assert body["data"]["payloadHash"] == "sha256:self-test-payload"
    assert body["data"]["expiresAt"]
    assert body["data"]["failClosed"] is True


@pytest.mark.asyncio
async def test_verify_control_agent_authorization_denies_unknown_scope(
    test_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """未知 action scope 返回业务拒绝，并保持 fail-closed。"""

    admin_user = await _get_user(db_session, "admin")
    gate_token = await _issue_gate_token(
        test_client,
        auth_headers,
        subject_user_id=admin_user.id,
        subject_username=admin_user.username,
    )

    response = await test_client.post(
        AUTHORIZATION_VERIFY_PATH,
        json=_authorization_payload(
            operator_user_id=admin_user.id,
            operator_username=admin_user.username,
            action_scope="unknown.action",
        ),
        headers={"Authorization": f"Bearer {gate_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["data"]["allowed"] is False
    assert body["data"]["decision"] == "scope_not_allowed"
    assert body["data"]["approvalId"] is None
    assert body["data"]["expiresAt"] is None
    assert body["data"]["failClosed"] is True


@pytest.mark.asyncio
async def test_verify_control_agent_authorization_requires_token(
    test_client: AsyncClient,
    db_session: AsyncSession,
):
    """缺少门禁 token 时由后端认证依赖拒绝。"""

    admin_user = await _get_user(db_session, "admin")
    response = await test_client.post(
        AUTHORIZATION_VERIFY_PATH,
        json=_authorization_payload(
            operator_user_id=admin_user.id,
            operator_username=admin_user.username,
        ),
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_issue_control_agent_gate_token_rejects_operator_permission(
    test_client: AsyncClient,
    db_session: AsyncSession,
):
    """普通 operator 没有门禁 token 签发权限。"""

    operator = await _create_user(
        db_session,
        username="operator_ca",
        password="operator123",
        name="Operator CA",
        role="operator",
    )
    await db_session.commit()

    login_response = await test_client.post(
        "/api/v1/auth/login",
        json={"username": "operator_ca", "password": "operator123"},
    )
    token = login_response.json()["data"]["accessToken"]

    response = await test_client.post(
        GATE_TOKENS_PATH,
        json={
            "subjectUserId": operator.id,
            "subjectUsername": operator.username,
            "durationHours": 1,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_issue_control_agent_gate_token_rejects_operator_subject(
    test_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """admin 不能给普通 operator 发放门禁 token。"""

    operator = await _create_user(
        db_session,
        username="operator_subject_ca",
        password="operator123",
        name="Operator Subject CA",
        role="operator",
    )

    response = await test_client.post(
        GATE_TOKENS_PATH,
        json={
            "subjectUserId": operator.id,
            "subjectUsername": operator.username,
            "durationHours": 1,
        },
        headers=auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "control_agent_gate_token_subject_role_not_allowed"


@pytest.mark.asyncio
async def test_verify_control_agent_authorization_rejects_operator_mismatch(
    test_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """门禁 token 只能由绑定用户使用。"""

    admin_user = await _get_user(db_session, "admin")
    gate_token = await _issue_gate_token(
        test_client,
        auth_headers,
        subject_user_id=admin_user.id,
        subject_username=admin_user.username,
    )

    response = await test_client.post(
        AUTHORIZATION_VERIFY_PATH,
        json=_authorization_payload(
            operator_user_id=admin_user.id,
            operator_username="other-admin",
        ),
        headers={"Authorization": f"Bearer {gate_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["allowed"] is False
    assert body["data"]["decision"] == "operator_mismatch"
