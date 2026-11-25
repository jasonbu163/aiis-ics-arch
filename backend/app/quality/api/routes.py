"""
文件路径: /backend/app/quality/api/routes.py
功能描述: 质量管理 API 路由定义
主要功能:
    - 提供 SPC 统计接口
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.quality.schemas.quality_out import SPCDataPoint, SPCStats
from app.quality.services.async_quality import quality_service
from app.user.models.user import User
from common.response import SuccessResponse
from core.deps import require_permissions
from database import get_db

router = APIRouter(prefix="/quality", tags=["Quality"])
# 兼容包级导出。旧缺陷路由已退役，此对象不再注册。
defect_router = APIRouter(prefix="/defects", tags=["Quality - Defects"])


@router.get("/spc/data", response_model=SuccessResponse)
async def get_spc_data(
    item: str = Query("thickness", description="分析项目"),
    grade: Optional[str] = None,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("quality")),
):
    """获取 SPC 分析数据"""
    data = await quality_service.get_spc_data(db, item, grade, start_date, end_date)
    return SuccessResponse(data=[SPCDataPoint.model_validate(point).model_dump(by_alias=True) for point in data])


@router.get("/spc/stats", response_model=SuccessResponse)
async def get_spc_stats(
    item: str = Query("thickness"),
    grade: Optional[str] = None,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    subgroup_size: int = Query(5, ge=2, le=5, alias="subgroupSize"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("quality")),
):
    """获取 SPC 统计数据"""
    stats = await quality_service.get_spc_stats(db, item, grade, start_date, end_date, subgroup_size)
    return SuccessResponse(data=SPCStats.model_validate(stats).model_dump(by_alias=True))
