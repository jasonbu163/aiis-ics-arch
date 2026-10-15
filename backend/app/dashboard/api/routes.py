"""
文件路径: /backend/app/dashboard/api/routes.py
功能描述: Dashboard 看板数据 API 路由
主要功能:
    - 提供看板各类数据的查询接口
    - 调用 DashboardService 获取业务数据
    - 使用统一响应包裹返回数据
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dashboard.services.async_dashboard import dashboard_service
from app.user.schemas.user_out import UserResponse
from common.response import SuccessResponse
from core.deps import get_current_user, require_permissions
from database import get_db


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(require_permissions("dashboard"))],
)


@router.get("/stats", response_model=SuccessResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取看板统计数据"""
    return SuccessResponse(data=await dashboard_service.get_dashboard_stats(db))


@router.get("/production-trend", response_model=SuccessResponse)
async def get_production_trend(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取近7日产量趋势"""
    return SuccessResponse(data=await dashboard_service.get_production_trend(db))


@router.get("/quality-distribution", response_model=SuccessResponse)
async def get_quality_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取生产质量分布"""
    return SuccessResponse(data=await dashboard_service.get_quality_distribution(db))


@router.get("/oee-analysis", response_model=SuccessResponse)
async def get_oee_analysis(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取 OEE 分析数据"""
    return SuccessResponse(data=await dashboard_service.get_oee_analysis(db))


@router.get("/temperature-trend", response_model=SuccessResponse)
async def get_temperature_trend(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取炉区温度趋势"""
    return SuccessResponse(data=await dashboard_service.get_temperature_trend(db))


@router.get("/energy-consumption", response_model=SuccessResponse)
async def get_energy_consumption(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取能耗数据"""
    return SuccessResponse(data=await dashboard_service.get_energy_consumption(db))


@router.get("/downtime-analysis", response_model=SuccessResponse)
async def get_downtime_analysis(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取停机原因分析"""
    return SuccessResponse(data=await dashboard_service.get_downtime_analysis(db))


@router.get("/production-status", response_model=SuccessResponse)
async def get_production_status(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取生产状态"""
    return SuccessResponse(data=await dashboard_service.get_production_status(db))


@router.get("/recent-plans", response_model=SuccessResponse)
async def get_recent_plans(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取近期计划"""
    return SuccessResponse(data=await dashboard_service.get_recent_plans(db))
