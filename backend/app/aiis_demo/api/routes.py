"""
文件路径: /backend/app/aiis_demo/api/routes.py
功能描述: AIIS Demo 参考 API 路由
主要功能:
    - 提供默认关闭的静态 ping 端点
    - 保持 API -> Service -> Schema 的最小分层
"""
from fastapi import APIRouter

from app.aiis_demo.schemas.ping import PingResponse
from app.aiis_demo.services.async_ping import get_ping
from common.response import StandardResponse


router = APIRouter(prefix="/aiis-demo", tags=["AIIS Demo"])


@router.get("/ping", response_model=StandardResponse[PingResponse])
async def ping() -> StandardResponse[PingResponse]:
    """Return the static reference module health payload."""
    return StandardResponse(data=await get_ping())
