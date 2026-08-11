"""
文件路径: /backend/app/monitor/api/realtime.py
功能描述: Monitor 实时快照 HTTP 接口
主要功能:
    - 提供 latest snapshot 查询
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.services.async_realtime import get_realtime_latest_data
from app.user.schemas.user_out import UserResponse
from common.response import SuccessResponse
from core.deps import get_current_user
from database import get_db


router = APIRouter(tags=["Monitor - Realtime"])


@router.get("/realtime/latest", response_model=SuccessResponse)
async def get_realtime_latest(
    device_id: int = Query(1, alias="deviceId", ge=1, description="设备ID"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取实时监控 latest snapshot，供上位机 HMI 页面展示。"""
    data = await get_realtime_latest_data(db, device_id)
    return SuccessResponse(data=data)
