"""
文件路径: /backend/app/quality/api/routes.py
功能描述: 质量管理 API 路由定义
主要功能:
    - 提供质量检验 CRUD 接口
    - 提供缺陷记录管理接口
    - 提供 SPC 统计接口
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.quality.schemas.quality_in import DefectRecordCreate, QualityInspectionCreate, QualityInspectionUpdate
from app.quality.schemas.quality_out import (
    DefectRecordResponse,
    QualityInspectionListResponse,
    QualityInspectionResponse,
    SPCDataPoint,
    SPCStats,
)
from app.quality.services.async_quality import quality_service
from app.user.models.user import User
from common.response import SuccessResponse
from core.deps import require_permissions
from database import get_db

router = APIRouter(prefix="/quality", tags=["Quality"])
defect_router = APIRouter(prefix="/defects", tags=["Quality - Defects"])


@defect_router.get("", response_model=SuccessResponse)
async def get_defect_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("quality")),
):
    """获取缺陷记录列表"""
    result = await quality_service.list_defects(db, page, page_size)
    return SuccessResponse(data={
        "items": [DefectRecordResponse.model_validate(defect).model_dump(by_alias=True) for defect in result["items"]],
        "total": result["total"],
        "page": result["page"],
        "pageSize": result["page_size"],
    })


@router.get("", response_model=SuccessResponse)
async def get_quality_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    coil_no: Optional[str] = Query(None, alias="coilNo"),
    grade: Optional[str] = None,
    quality_grade: Optional[str] = Query(None, alias="qualityGrade"),
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("quality")),
):
    """获取质量检验列表"""
    result = await quality_service.list_inspections(db, page, page_size, coil_no, grade, quality_grade, start_date, end_date)
    return SuccessResponse(data={
        "items": [
            QualityInspectionListResponse.model_validate(item).model_dump(by_alias=True)
            for item in result["items"]
        ],
        "total": result["total"],
        "page": result["page"],
        "pageSize": result["page_size"],
    })


@router.post("", response_model=SuccessResponse)
async def create_quality(
    quality_data: QualityInspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("quality")),
):
    """创建质量检验记录"""
    quality = await quality_service.create_inspection(db, quality_data, current_user.username)
    return SuccessResponse(
        message="创建成功",
        data=QualityInspectionResponse.model_validate(quality).model_dump(by_alias=True),
    )


@router.get("/{quality_id}", response_model=SuccessResponse)
async def get_quality(
    quality_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("quality")),
):
    """获取质量检验详情"""
    quality = await quality_service.get_inspection(db, quality_id)
    return SuccessResponse(data=QualityInspectionResponse.model_validate(quality).model_dump(by_alias=True))


@router.put("/{quality_id}", response_model=SuccessResponse)
async def update_quality(
    quality_id: int,
    quality_data: QualityInspectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("quality")),
):
    """更新质量检验记录"""
    quality = await quality_service.update_inspection(db, quality_id, quality_data)
    return SuccessResponse(
        message="更新成功",
        data=QualityInspectionResponse.model_validate(quality).model_dump(by_alias=True),
    )


@router.delete("/{quality_id}", response_model=SuccessResponse)
async def delete_quality(
    quality_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("quality")),
):
    """删除质量检验记录"""
    await quality_service.delete_inspection(db, quality_id)
    return SuccessResponse(message="删除成功")


@router.post("/{quality_id}/defects", response_model=SuccessResponse)
async def add_defect(
    quality_id: int,
    defect_data: DefectRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("quality")),
):
    """添加缺陷记录"""
    defect = await quality_service.add_defect(db, quality_id, defect_data)
    return SuccessResponse(
        message="添加成功",
        data=DefectRecordResponse.model_validate(defect).model_dump(by_alias=True),
    )


@router.delete("/{quality_id}/defects/{defect_id}", response_model=SuccessResponse)
async def delete_defect(
    quality_id: int,
    defect_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("quality")),
):
    """删除缺陷记录"""
    await quality_service.delete_defect(db, quality_id, defect_id)
    return SuccessResponse(message="删除成功")


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
