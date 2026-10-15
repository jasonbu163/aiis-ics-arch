"""
文件路径: /backend/app/performance/api/routes.py
功能描述: 实绩管理 API 路由定义
主要功能:
    - 实绩 CRUD 操作（创建、查询、更新、删除）
    - 实绩列表分页查询（支持料卷号、牌号、生产状态、日期范围筛选）
    - 获取单个实绩详情
    - 实绩数据统计接口
    - 过程数据查询（温度、张力、速度）
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import Optional, List
from datetime import date
from app.performance.schemas.performance_in import (
    PerformanceCreate,
    PerformanceUpdate,
)
from app.performance.schemas.performance_out import (
    PerformanceResponse,
    ProcessDataResponse,
    ProcessSpeedResponse,
    ProcessTemperatureResponse,
    ProcessTensionResponse,
    PushDownRecordResponse,
)
from common.response import SuccessResponse, PaginatedResponse
from app.performance.services.async_performance import async_performance_service
from core.deps import get_current_user, require_permissions
from app.user.schemas.user_out import UserResponse
from common.exceptions import BusinessException
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.models.user import User

router = APIRouter(prefix="/performances", tags=["Performance"])


@router.get("", response_model=SuccessResponse)
async def get_performance_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    coil_no: Optional[str] = Query(None, alias="coilNo"),
    grade: Optional[str] = None,
    observation_status: Optional[str] = Query(None, alias="observationStatus"),
    start_date: Optional[date] = Query(None, alias="startDate"),
    end_date: Optional[date] = Query(None, alias="endDate"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance"))
):

    result = await async_performance_service.get_list(
        db=db,
        page=page,
        page_size=page_size,
        coil_no=coil_no,
        grade=grade,
        observation_status=observation_status,
        start_date=start_date,
        end_date=end_date
    )
    
    from sqlalchemy import func
    from sqlalchemy.future import select
    from app.performance.models.performance import Split
    
    items = []
    for item in result["items"]:
        item_dict = PerformanceResponse.model_validate(item).model_dump(by_alias=True)
        
        if item.parent_coil_no == item.coil_no:
            split_count_result = await db.execute(
                select(func.count(Split.id)).where(Split.performance_id == item.id)
            )
            split_count = split_count_result.scalar()
            item_dict["splitCount"] = split_count
            item_dict["isSplitted"] = split_count > 0
        else:
            item_dict["splitCount"] = 0
            item_dict["isSplitted"] = False
        
        items.append(item_dict)
    
    return SuccessResponse(data={
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "pageSize": result["page_size"],
        "totalPages": result["total_pages"]
    })


@router.post("", response_model=SuccessResponse)
async def create_performance(
    performance_data: PerformanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance"))
):
    try:
        performance = await async_performance_service.create(db, performance_data)
        return SuccessResponse(
            message="创建成功",
            data=PerformanceResponse.model_validate(performance).model_dump(by_alias=True)
        )
    except BusinessException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{performance_id}", response_model=SuccessResponse)
async def get_performance(
    performance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance"))
):
    performance = await async_performance_service.get_by_id(db, performance_id)

    if not performance:
        raise HTTPException(status_code=404, detail="实绩不存在")
    
    return SuccessResponse(
        data=PerformanceResponse.model_validate(performance).model_dump(by_alias=True)
    )


@router.put("/{performance_id}", response_model=SuccessResponse)
async def update_performance(
    performance_id: int,
    performance_data: PerformanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance"))
):
    
    try:
        performance = await async_performance_service.update(db, performance_id, performance_data)
        if not performance:
            raise HTTPException(status_code=404, detail="实绩不存在")
        
        return SuccessResponse(
            message="更新成功",
            data=PerformanceResponse.model_validate(performance).model_dump(by_alias=True)
        )
    except BusinessException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{performance_id}", response_model=SuccessResponse)
async def delete_performance(
    performance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance"))
):
    
    try:
        success = await async_performance_service.delete(db, performance_id)
        if not success:
            raise HTTPException(status_code=404, detail="实绩不存在")
        
        return SuccessResponse(message="删除成功")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{performance_id}/process-data", response_model=SuccessResponse)
async def get_process_data(
    performance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance"))
):
    
    performance = await async_performance_service.get_by_id(db, performance_id)
    if not performance:
        raise HTTPException(status_code=404, detail="实绩不存在")
    
    process_data = await async_performance_service.get_process_data(db, performance_id)
    
    return SuccessResponse(data={
        "temperature": [
            ProcessTemperatureResponse.model_validate(t).model_dump(by_alias=True)
            for t in process_data["temperature"]
        ],
        "tension": [
            ProcessTensionResponse.model_validate(t).model_dump(by_alias=True)
            for t in process_data["tension"]
        ],
        "speed": [
            ProcessSpeedResponse.model_validate(s).model_dump(by_alias=True)
            for s in process_data["speed"]
        ]
    })


@router.post("/push-down", response_model=SuccessResponse)
async def batch_push_down(
    performance_ids: List[int] = Body(..., embed=True, alias="performanceIds"),
    target_system: Optional[str] = Body(None, embed=True, alias="targetSystem"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance"))
):
    if not performance_ids:
        raise HTTPException(status_code=400, detail="请选择要下推的实绩")
    
    try:
        records = await async_performance_service.push_down(
            db=db,
            performance_ids=performance_ids,
            operator_id=current_user.id,
            target_system=target_system
        )
        
        return SuccessResponse(
            message=f"成功下推 {len(records)} 条实绩",
            data=[
                PushDownRecordResponse.model_validate(r).model_dump(by_alias=True)
                for r in records
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{performance_id}/push-down", response_model=SuccessResponse)
async def single_push_down(
    performance_id: int,
    target_system: Optional[str] = Body(None, embed=True, alias="targetSystem"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance"))
):
    
    performance = await async_performance_service.get_by_id(db, performance_id)
    if not performance:
        raise HTTPException(status_code=404, detail="实绩不存在")
    
    try:
        records = await async_performance_service.push_down(
            db=db,
            performance_ids=[performance_id],
            operator_id=current_user.id,
            target_system=target_system
        )
        
        return SuccessResponse(
            message="下推成功",
            data=PushDownRecordResponse.model_validate(records[0]).model_dump(by_alias=True)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{performance_id}/push-down-records", response_model=SuccessResponse)
async def get_push_down_records(
    performance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance"))
):
    
    performance = await async_performance_service.get_by_id(db, performance_id)
    if not performance:
        raise HTTPException(status_code=404, detail="实绩不存在")
    
    records = await async_performance_service.get_push_down_records(db, performance_id)
    
    return SuccessResponse(data=[
        PushDownRecordResponse.model_validate(r).model_dump(by_alias=True)
        for r in records
    ])
