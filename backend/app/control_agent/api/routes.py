"""
文件路径: /backend/app/control_agent/api/routes.py
功能描述: Control Agent 授权门禁 API
主要功能:
    - 提供高危动作前的授权校验入口
    - 只做授权验证，不远程执行 control-agent 动作
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.control_agent.schemas.authorization import (
    ControlAgentActionScopeRegistry,
    ControlAgentGateTokenCreate,
    ControlAgentGateTokenIssued,
    ControlAgentAuthorizationRequest,
    ControlAgentAuthorizationResponse,
)
from app.control_agent.services.async_authorization import authorization_service
from app.user.models.user import User
from common.response import StandardResponse
from core.deps import require_permissions
from database import get_db


router = APIRouter(prefix="/control-agent", tags=["Control Agent"])
gate_token_security = HTTPBearer(auto_error=False)


@router.get(
    "/action-scopes",
    response_model=StandardResponse[ControlAgentActionScopeRegistry],
)
async def list_control_agent_action_scopes(
    _current_user: User = Depends(require_permissions("control-agent-read")),
):
    """返回前端 / CA 可消费的 control-agent 授权动作 scope 注册表。"""

    return StandardResponse(data=authorization_service.list_action_scopes())


@router.post(
    "/gate-tokens",
    response_model=StandardResponse[ControlAgentGateTokenIssued],
)
async def issue_control_agent_gate_token(
    request: ControlAgentGateTokenCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("control-agent")),
):
    """由最高权限用户签发绑定指定高权限目标用户的 control-agent 门禁 token。"""

    try:
        issued = await authorization_service.issue_gate_token(
            db=db,
            request=request,
            current_user=current_user,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="control_agent_gate_token_subject_not_found",
        )
    return StandardResponse(data=issued)


@router.post(
    "/authorization/verify",
    response_model=StandardResponse[ControlAgentAuthorizationResponse],
)
async def verify_control_agent_authorization(
    request: ControlAgentAuthorizationRequest,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(gate_token_security),
):
    """校验 control-agent 高危动作前置授权。"""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="control_agent_gate_token_required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    decision = await authorization_service.verify_authorization(
        db=db,
        request=request,
        gate_token=credentials.credentials,
    )
    return StandardResponse(data=decision)
