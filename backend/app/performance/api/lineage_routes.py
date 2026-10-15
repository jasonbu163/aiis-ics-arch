"""
文件路径: /backend/app/performance/api/lineage_routes.py
功能描述: B17 实绩 transform / lineage API 路由
主要功能:
    - 提交分卷 / 合卷 transform
    - 查询 transform 与单条实绩可用重量
    - 提交人工有效重量覆盖
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.performance.schemas.performance_all import PerformanceResponse
from app.performance.schemas.performance_lineage import (
    EffectiveWeightOverrideIn,
    MergeTransformCreateIn,
    PerformanceLineageSummaryResponse,
    PerformanceTransformResponse,
    SplitTransformCreateIn,
)
from app.performance.services.async_lineage import async_performance_lineage_service
from app.user.models.user import User
from common.response import SuccessResponse
from core.deps import require_permissions
from database import get_db


transform_router = APIRouter(prefix="/performance-transforms", tags=["Performance - Lineage"])
performance_lineage_router = APIRouter(prefix="/performances", tags=["Performance - Lineage"])


def _operator_id(current_user: User) -> int | None:
    return getattr(current_user, "id", None)


@transform_router.post("/split", response_model=SuccessResponse)
async def create_split_transform(
    data: SplitTransformCreateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance")),
):
    transform = await async_performance_lineage_service.split(
        db,
        data,
        _operator_id(current_user),
    )

    return SuccessResponse(
        message="split committed",
        data=PerformanceTransformResponse.model_validate(transform).model_dump(by_alias=True),
    )


@transform_router.post("/merge", response_model=SuccessResponse)
async def create_merge_transform(
    data: MergeTransformCreateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance")),
):
    transform = await async_performance_lineage_service.merge(
        db,
        data,
        _operator_id(current_user),
    )

    return SuccessResponse(
        message="merge committed",
        data=PerformanceTransformResponse.model_validate(transform).model_dump(by_alias=True),
    )


@transform_router.get("/{transform_id}", response_model=SuccessResponse)
async def get_transform(
    transform_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance")),
):
    transform = await async_performance_lineage_service.get_transform(db, transform_id)

    return SuccessResponse(
        data=PerformanceTransformResponse.model_validate(transform).model_dump(by_alias=True),
    )


@performance_lineage_router.post("/{performance_id}/effective-weight", response_model=SuccessResponse)
async def override_effective_weight(
    performance_id: int,
    data: EffectiveWeightOverrideIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance")),
):
    performance = await async_performance_lineage_service.override_effective_weight(
        db,
        performance_id,
        data,
        _operator_id(current_user),
    )

    return SuccessResponse(
        message="effective weight updated",
        data=PerformanceResponse.model_validate(performance).model_dump(by_alias=True),
    )


@performance_lineage_router.get("/{performance_id}/lineage-summary", response_model=SuccessResponse)
async def get_lineage_summary(
    performance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("performance")),
):
    summary = await async_performance_lineage_service.get_summary(db, performance_id)

    return SuccessResponse(
        data=PerformanceLineageSummaryResponse.model_validate(summary).model_dump(by_alias=True),
    )
