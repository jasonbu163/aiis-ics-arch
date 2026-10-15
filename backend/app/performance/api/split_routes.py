"""
文件路径: /backend/app/performance/api/split_routes.py
功能描述: 分卷管理 API 路由定义
主要功能:
    - 分卷 CRUD 操作（创建、查询、更新、删除）
    - 获取可分卷的母卷列表
    - 自动生成分卷号
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import Optional, List
from app.performance.schemas.performance_in import SplitCreate, SplitUpdate
from app.performance.schemas.performance_out import SplitResponse
from common.response import SuccessResponse, PaginatedResponse
from app.performance.services.async_split import SplitService
from core.deps import get_current_user, require_permissions
from app.user.schemas.user_out import UserResponse
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.performance.models.performance import Performance

router = APIRouter(
    prefix="/splits",
    tags=["Performance - Split"],
    dependencies=[Depends(require_permissions("performance"))],
)


@router.get("", response_model=SuccessResponse)
async def get_split_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    parent_coil_no: Optional[str] = Query(None, alias="parentCoilNo"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    获取分卷列表
    """
    split_service = SplitService(db)
    result = await split_service.get_list(
        page=page,
        page_size=page_size,
        parent_coil_no=parent_coil_no
    )
    
    items = []
    for item in result["items"]:
        item_dict = SplitResponse.model_validate(item).model_dump()
        if item.performance:
            item_dict["performance_coil_no"] = item.performance.coil_no
        else:
            perf_result = await db.execute(
                select(Performance).where(Performance.id == item.performance_id)
            )
            perf = perf_result.scalar_one_or_none()
            item_dict["performance_coil_no"] = perf.coil_no if perf else '-'
        items.append(item_dict)
    
    return SuccessResponse(data={
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "total_pages": result["total_pages"]
    })


@router.get("/parent-coils", response_model=SuccessResponse)
async def get_parent_coils(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    获取可分卷的母卷列表
    """
    split_service = SplitService(db)
    parent_coils = await split_service.get_parent_coils()
    
    return SuccessResponse(data=parent_coils)


@router.get("/{split_id}", response_model=SuccessResponse)
async def get_split(
    split_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    获取分卷详情
    """
    split_service = SplitService(db)
    split = await split_service.get_by_id(split_id)
    
    if not split:
        raise HTTPException(status_code=404, detail="分卷不存在")
    
    return SuccessResponse(
        data=SplitResponse.model_validate(split).model_dump()
    )


@router.post("", response_model=SuccessResponse)
async def create_split(
    split_data: SplitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    创建分卷
    """
    split_service = SplitService(db)
    
    try:
        split = await split_service.create(split_data)
        return SuccessResponse(
            message="创建成功",
            data=SplitResponse.model_validate(split).model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{split_id}", response_model=SuccessResponse)
async def update_split(
    split_id: int,
    split_data: SplitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    更新分卷
    """
    split_service = SplitService(db)
    
    try:
        split = await split_service.update(split_id, split_data)
        if not split:
            raise HTTPException(status_code=404, detail="分卷不存在")
        
        return SuccessResponse(
            message="更新成功",
            data=SplitResponse.model_validate(split).model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{split_id}", response_model=SuccessResponse)
async def delete_split(
    split_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    删除分卷
    """
    split_service = SplitService(db)
    
    try:
        success = await split_service.delete(split_id)
        if not success:
            raise HTTPException(status_code=404, detail="分卷不存在")
        
        return SuccessResponse(message="删除成功")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{split_id}/generate-split-no", response_model=SuccessResponse)
async def generate_split_no(
    split_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    自动生成分卷号
    """
    split_service = SplitService(db)
    
    try:
        split_no = await split_service.generate_split_no(split_id)
        return SuccessResponse(data={"split_no": split_no})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
