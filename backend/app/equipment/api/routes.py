"""
文件路径: /backend/app/equipment/api/routes.py
功能描述: 设备管理/工艺监控 API 路由定义
主要功能:
    - 提供传动参数数据查询
    - 提供温控参数数据查询
    - 提供生产参数数据查询
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.equipment.services.async_equipment import equipment_service
from app.user.schemas.user_out import UserResponse
from common.response import SuccessResponse
from core.deps import get_current_user, require_permissions
from database import get_db

router = APIRouter(
    prefix="/equipment",
    tags=["Equipment"],
    dependencies=[Depends(require_permissions("equipment"))],
)


@router.get("/drive", response_model=SuccessResponse)
async def get_drive_data(
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取传动参数数据"""
    data = await equipment_service.get_drive_dashboard_data(db)
    return SuccessResponse(data=data)


@router.get("/temperature-control", response_model=SuccessResponse)
async def get_temperature_control_data(
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取温控参数数据"""
    data = await equipment_service.get_temperature_control_dashboard_data(db)
    return SuccessResponse(data=data)


@router.get("/production-parameters", response_model=SuccessResponse)
async def get_production_parameters_data(
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """获取生产参数数据"""
    data = await equipment_service.get_production_parameters_dashboard_data(db)
    return SuccessResponse(data=data)
