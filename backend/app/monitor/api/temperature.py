"""
文件路径: /backend/app/monitor/api/temperature.py
功能描述: Monitor 温度与过程曲线 HTTP 接口
主要功能:
    - 提供全量生产过程曲线查询
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.services.async_temperature import get_curve_dashboard_data
from app.user.schemas.user_out import UserResponse
from common.response import SuccessResponse
from core.deps import get_current_user
from database import get_db


router = APIRouter(tags=["Monitor - Temperature"])


@router.get("/temperature", response_model=SuccessResponse)
async def get_temperature_curve(
    date: str = Query(..., description="日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取全量生产曲线数据（包含温、张、速、质）。"""
    data = await get_curve_dashboard_data(db, "all", date)
    return SuccessResponse(data=data)
