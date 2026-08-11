"""
文件路径: /backend/app/schema_maintenance/api/routes.py
功能描述: Schema maintenance API 路由
主要功能:
    - admin-only 查询当前 model metadata 对应表状态
    - admin-only 显式创建缺失整表
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema_maintenance.services.async_schema import (
    SchemaMaintenanceRequestedAction,
    schema_maintenance_service,
)
from app.user.models.user import User
from common.response import SuccessResponse
from core.deps import get_current_active_admin
from database import get_db


router = APIRouter(prefix="/schema-maintenance", tags=["Schema Maintenance"])


@router.get("/status", response_model=SuccessResponse)
async def get_schema_maintenance_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    status = await schema_maintenance_service.get_status(db, current_user)
    return SuccessResponse(data=status)


@router.post("/initialize", response_model=SuccessResponse)
async def initialize_schema_maintenance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    result = await schema_maintenance_service.run_create_missing_action(
        db,
        current_user,
        SchemaMaintenanceRequestedAction.INITIALIZE,
    )
    return SuccessResponse(message="schema maintenance initialized", data=result)


@router.post("/upgrade", response_model=SuccessResponse)
async def upgrade_schema_maintenance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    result = await schema_maintenance_service.run_create_missing_action(
        db,
        current_user,
        SchemaMaintenanceRequestedAction.UPGRADE,
    )
    return SuccessResponse(message="schema maintenance upgraded", data=result)
