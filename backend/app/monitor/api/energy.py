"""
文件路径: /backend/app/monitor/api/energy.py
功能描述: Monitor 能耗统计 HTTP 接口
主要功能:
    - 提供能耗统计汇总查询
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.services.async_energy import get_energy_summary_data
from app.user.schemas.user_out import UserResponse
from common.response import SuccessResponse
from core.deps import get_current_user
from database import get_db


router = APIRouter(tags=["Monitor - Energy"])


@router.get("/energy", response_model=SuccessResponse)
async def get_energy_summary(
    time_range: str = Query("realtime", alias="timeRange", description="时间范围"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取能耗统计汇总数据。"""
    data = await get_energy_summary_data(db, time_range)
    return SuccessResponse(data=data)
