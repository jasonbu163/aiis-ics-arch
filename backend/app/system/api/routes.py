"""
文件路径: /backend/app/system/api/routes.py
功能描述: 系统字典管理 API 路由定义
主要功能:
    - 字典类型查询与管理
    - 字典项 CRUD 操作
    - 按字典类型获取字典项列表
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.system.models.system_dict import SysDict, SysDictItem
from app.system.schemas.system_dict import (
    SysDictCreate,
    SysDictItemCreate,
    SysDictItemResponse,
    SysDictItemUpdate,
    SysDictResponse,
    SysDictUpdate,
)
from app.user.schemas.user_out import UserResponse
from common.async_crud_base import BaseService
from common.response import SuccessResponse
from core.deps import require_permissions
from database import get_db

router = APIRouter(prefix="/sys-dict", tags=["System - Dictionary"])


@router.get("", response_model=SuccessResponse)
async def list_dicts(
    dict_type: str = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("system-dict")),
):
    service = BaseService(db, SysDict)
    filters = {"dict_type": dict_type} if dict_type else None
    items, total = await service.list(page=page, page_size=page_size, filters=filters)
    return SuccessResponse(
        data={
            "items": [SysDictResponse.model_validate(i).model_dump() for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


@router.get("/type/{dict_type}", response_model=SuccessResponse)
async def get_dict_by_type(
    dict_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("system-dict")),
):
    result = await db.execute(select(SysDict).where(SysDict.dict_type == dict_type))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="字典不存在")
    items_result = await db.execute(select(SysDictItem).where(SysDictItem.dict_id == d.id).order_by(SysDictItem.sort))
    items = items_result.scalars().all()
    return SuccessResponse(
        data={
            "id": d.id,
            "dict_type": d.dict_type,
            "dict_name": d.dict_name,
            "description": d.description,
            "status": d.status,
            "items": [SysDictItemResponse.model_validate(i).model_dump() for i in items],
        }
    )


@router.post("", response_model=SysDictResponse)
async def create_dict(
    data: SysDictCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("system-dict")),
):
    service = BaseService(db, SysDict)
    item = await service.create(data.model_dump())
    return SysDictResponse.model_validate(item)


@router.put("/{id}", response_model=SysDictResponse)
async def update_dict(
    id: int,
    data: SysDictUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("system-dict")),
):
    service = BaseService(db, SysDict)
    item = await service.update(id, data.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=404, detail="字典不存在")
    return SysDictResponse.model_validate(item)


@router.delete("/{id}", response_model=SuccessResponse)
async def delete_dict(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("system-dict")),
):
    service = BaseService(db, SysDict)
    success = await service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="字典不存在")
    return SuccessResponse(message="删除成功")


dict_item_router = APIRouter(prefix="/sys-dict-items", tags=["System - Dictionary Items"])


@dict_item_router.get("", response_model=SuccessResponse)
async def list_dict_items(
    dict_id: int = None,
    dict_type: str = None,
    page: int = 1,
    page_size: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("system-dict")),
):
    if dict_id:
        result = await db.execute(select(SysDictItem).where(SysDictItem.dict_id == dict_id).order_by(SysDictItem.sort))
        items = result.scalars().all()
        return SuccessResponse(data={"items": [SysDictItemResponse.model_validate(i).model_dump() for i in items], "total": len(items)})
    elif dict_type:
        dict_result = await db.execute(select(SysDict).where(SysDict.dict_type == dict_type))
        d = dict_result.scalar_one_or_none()
        if not d:
            return SuccessResponse(data={"items": [], "total": 0})
        result = await db.execute(select(SysDictItem).where(SysDictItem.dict_id == d.id).order_by(SysDictItem.sort))
        items = result.scalars().all()
        return SuccessResponse(data={"items": [SysDictItemResponse.model_validate(i).model_dump() for i in items], "total": len(items)})
    return SuccessResponse(data={"items": [], "total": 0})


@dict_item_router.post("", response_model=SysDictItemResponse)
async def create_dict_item(
    data: SysDictItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("system-dict")),
):
    service = BaseService(db, SysDictItem)
    item = await service.create(data.model_dump())
    return SysDictItemResponse.model_validate(item)


@dict_item_router.put("/{id}", response_model=SysDictItemResponse)
async def update_dict_item(
    id: int,
    data: SysDictItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("system-dict")),
):
    service = BaseService(db, SysDictItem)
    item = await service.update(id, data.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return SysDictItemResponse.model_validate(item)


@dict_item_router.delete("/{id}", response_model=SuccessResponse)
async def delete_dict_item(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(require_permissions("system-dict")),
):
    service = BaseService(db, SysDictItem)
    success = await service.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return SuccessResponse(message="删除成功")
