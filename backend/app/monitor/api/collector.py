"""
文件路径: /backend/app/monitor/api/collector.py
功能描述: Monitor collector 状态 HTTP 接口
主要功能:
    - 提供 collector 运行状态查询
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.services.collector.async_query import get_collector_status_data
from app.user.schemas.user_out import UserResponse
from common.response import SuccessResponse
from core.deps import get_current_user
from database import get_db


router = APIRouter(tags=["Monitor - Collector"])


@router.get("/collector/status", response_model=SuccessResponse)
async def get_collector_status(
    collector_key: str = Query("control-agent-plc", alias="collectorKey", description="采集器Key"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取 monitor collector 运行状态。"""
    data = await get_collector_status_data(db, collector_key)
    return SuccessResponse(data=data)
