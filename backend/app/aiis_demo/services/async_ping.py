"""
文件路径: /backend/app/aiis_demo/services/async_ping.py
功能描述: AIIS Demo ping 异步业务 Service
主要功能:
    - 返回不依赖外部系统的静态参考健康 payload
"""
from app.aiis_demo.schemas.ping import PingResponse


async def get_ping() -> PingResponse:
    """Build the static reference payload without I/O or runtime setup."""
    return PingResponse(module="aiis_demo", status="ok", reference=True)
