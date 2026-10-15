"""
文件路径: /backend/app/maintenance/api/routes.py
功能描述: 维保管理 API 路由定义
主要功能:
    - 维保信息 CRUD 操作
    - 维保记录 CRUD 操作
    - 支持按类型和状态筛选维保项
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.maintenance.schemas.maintenance_in import (
    MaintenanceCreate,
    MaintenanceLogCreate,
    MaintenanceLogUpdate,
    MaintenanceUpdate,
)
from app.maintenance.schemas.maintenance_out import MaintenanceLogResponse, MaintenanceResponse
from app.maintenance.services.async_maintenance import MaintenanceService
from app.user.schemas.user_out import UserResponse
from common.response import SuccessResponse
from core.deps import get_current_user, require_permissions
from database import get_db


router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"],
    dependencies=[Depends(require_permissions("maintenance"))],
)

maintenance_router = APIRouter(
    prefix="/items",
    tags=["Maintenance"],
    dependencies=[Depends(require_permissions("maintenance"))],
)


@maintenance_router.get("", response_model=SuccessResponse)
async def list_maintenances(
    maintenance_type: Optional[str] = Query(None, alias="maintenanceType"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = MaintenanceService(db)
    items, total = await service.list_maintenances(
        page=page,
        page_size=page_size,
        maintenance_type=maintenance_type,
        status=status,
    )
    return SuccessResponse(
        data={
            "items": [MaintenanceResponse.model_validate(i).model_dump(by_alias=True) for i in items],
            "total": total,
            "page": page,
            "pageSize": page_size,
        }
    )


@maintenance_router.get("/{id}", response_model=MaintenanceResponse)
async def get_maintenance(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = MaintenanceService(db)
    item = await service.get_maintenance(id)
    if not item:
        raise HTTPException(status_code=404, detail="维保项不存在")
    return MaintenanceResponse.model_validate(item)


@maintenance_router.post("", response_model=MaintenanceResponse)
async def create_maintenance(
    data: MaintenanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = MaintenanceService(db)
    item = await service.create_maintenance(data)
    return MaintenanceResponse.model_validate(item)


@maintenance_router.put("/{id}", response_model=MaintenanceResponse)
async def update_maintenance(
    id: int,
    data: MaintenanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = MaintenanceService(db)
    item = await service.update_maintenance(id, data)
    if not item:
        raise HTTPException(status_code=404, detail="维保项不存在")
    return MaintenanceResponse.model_validate(item)


@maintenance_router.delete("/{id}", response_model=SuccessResponse)
async def delete_maintenance(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = MaintenanceService(db)
    success = await service.delete_maintenance(id)
    if not success:
        raise HTTPException(status_code=404, detail="维保项不存在")
    return SuccessResponse(message="删除成功")


maintenance_log_router = APIRouter(
    prefix="/maintenance-logs",
    tags=["Maintenance - Logs"],
    dependencies=[Depends(require_permissions("maintenance"))],
)


@maintenance_log_router.get("", response_model=SuccessResponse)
async def list_maintenance_logs(
    maintenance_id: Optional[int] = Query(None, alias="maintenanceId"),
    equipment_name: Optional[str] = Query(None, alias="equipmentName"),
    maintenance_type: Optional[str] = Query(None, alias="maintenanceType"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = MaintenanceService(db)
    items, total = await service.list_maintenance_logs(
        page=page,
        page_size=page_size,
        maintenance_id=maintenance_id,
        equipment_name=equipment_name,
        maintenance_type=maintenance_type,
        status=status,
    )
    data_items = []
    for item in items:
        item_dict = MaintenanceLogResponse.model_validate(item).model_dump(by_alias=True)
        if item.maintenance:
            item_dict["maintenanceName"] = item.maintenance.name
            item_dict["maintenanceCode"] = item.maintenance.code
        data_items.append(item_dict)

    return SuccessResponse(data={"items": data_items, "total": total, "page": page, "pageSize": page_size})


@maintenance_log_router.get("/{id}", response_model=MaintenanceLogResponse)
async def get_maintenance_log(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = MaintenanceService(db)
    item = await service.get_maintenance_log(id)
    if not item:
        raise HTTPException(status_code=404, detail="保养记录不存在")
    return MaintenanceLogResponse.model_validate(item)


@maintenance_log_router.post("", response_model=MaintenanceLogResponse)
async def create_maintenance_log(
    data: MaintenanceLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = MaintenanceService(db)
    item = await service.create_maintenance_log(data)
    return MaintenanceLogResponse.model_validate(item)


@maintenance_log_router.put("/{id}", response_model=MaintenanceLogResponse)
async def update_maintenance_log(
    id: int,
    data: MaintenanceLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = MaintenanceService(db)
    item = await service.update_maintenance_log(id, data)
    if not item:
        raise HTTPException(status_code=404, detail="保养记录不存在")
    return MaintenanceLogResponse.model_validate(item)


@maintenance_log_router.delete("/{id}", response_model=SuccessResponse)
async def delete_maintenance_log(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    service = MaintenanceService(db)
    success = await service.delete_maintenance_log(id)
    if not success:
        raise HTTPException(status_code=404, detail="保养记录不存在")
    return SuccessResponse(message="删除成功")
