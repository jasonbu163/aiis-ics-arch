"""
文件路径: /backend/app/plan/api/routes.py
功能描述: 生产计划管理 API 路由
主要功能:
    - 提供计划创建、查询、更新与删除
    - 计划只表达人工或 XLSX 导入的生产意图
    - 不暴露设备执行、任务中断或 Worker 状态接口
"""
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.plan.schemas.plan import PlanCreate, PlanLinkRequest, PlanResponse, PlanUpdate
from app.plan.services.async_service import async_plan_service
from app.plan.services.xlsx_io import XLSX_MEDIA_TYPE
from common.response import SuccessResponse
from core.deps import require_permissions
from database import get_db


router = APIRouter(prefix="/plans", tags=["Plan"])


@router.get("", response_model=SuccessResponse)
async def get_plan_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    coil_no: str | None = Query(None, alias="coilNo"),
    grade: str | None = None,
    material_status: str | None = Query(None, alias="materialStatus"),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions("plan")),
):
    """获取生产计划列表。"""
    result = await async_plan_service.list_plans(
        db,
        page=page,
        page_size=page_size,
        coil_no=coil_no,
        grade=grade,
        material_status=material_status,
        status=status,
    )
    items = [
        PlanResponse.model_validate(plan).model_dump(by_alias=True)
        for plan in result["items"]
    ]
    return SuccessResponse(
        data={
            "items": items,
            "total": result["total"],
            "page": result["page"],
            "pageSize": result["page_size"],
            "totalPages": result["total_pages"],
        }
    )


@router.post("", response_model=SuccessResponse)
async def create_plan(
    plan_data: PlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions("plan")),
):
    """创建生产计划。"""
    try:
        plan = await async_plan_service.create_plan(db, plan_data)
        return SuccessResponse(
            message="创建成功",
            data=PlanResponse.model_validate(plan).model_dump(by_alias=True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/xlsx/template")
async def download_plan_xlsx_template(
    current_user=Depends(require_permissions("plan")),
):
    """下载计划 XLSX 导入模板。"""
    content = async_plan_service.build_xlsx_template()
    return StreamingResponse(
        BytesIO(content),
        media_type=XLSX_MEDIA_TYPE,
        headers={
            "Content-Disposition": 'attachment; filename="plan-import-template.xlsx"',
        },
    )


@router.get("/xlsx/export")
async def export_plan_xlsx(
    plan_ids: list[int] | None = Query(None, alias="planIds"),
    coil_no: str | None = Query(None, alias="coilNo"),
    grade: str | None = None,
    material_status: str | None = Query(None, alias="materialStatus"),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions("plan")),
):
    """按当前筛选或选中 ID 导出计划 XLSX。"""
    content = await async_plan_service.build_xlsx_export(
        db,
        plan_ids=plan_ids,
        coil_no=coil_no,
        grade=grade,
        material_status=material_status,
        status=status,
        operator_id=current_user.id,
    )
    return StreamingResponse(
        BytesIO(content),
        media_type=XLSX_MEDIA_TYPE,
        headers={
            "Content-Disposition": 'attachment; filename="plans-export.xlsx"',
        },
    )


@router.post("/xlsx/import", response_model=SuccessResponse)
async def import_plan_xlsx(
    file: UploadFile = File(...),
    dry_run: bool = Query(True, alias="dryRun"),
    conflict_strategy: str = Query("reject", alias="conflictStrategy"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions("plan")),
):
    """导入计划 XLSX，默认 dry-run 只校验不写入。"""
    result = await async_plan_service.import_xlsx(
        db,
        content=await file.read(),
        dry_run=dry_run,
        conflict_strategy=conflict_strategy,
        operator_id=current_user.id,
    )
    return SuccessResponse(data=result)


@router.get("/linkage/performances/{performance_id}/candidates", response_model=SuccessResponse)
async def get_plan_link_candidates(
    performance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions("plan")),
):
    """获取某条实绩可手动关联的计划候选。"""
    result = await async_plan_service.get_link_candidates(
        db,
        performance_id=performance_id,
    )
    return SuccessResponse(data=result)


@router.post("/linkage/performances/{performance_id}/sync-observation", response_model=SuccessResponse)
async def sync_plan_observation(
    performance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions("plan")),
):
    """按实绩料卷号同步已有计划观测状态；无计划时不自动创建。"""
    result = await async_plan_service.sync_observation(
        db,
        performance_id=performance_id,
        operator_id=current_user.id,
    )
    return SuccessResponse(data=result)


@router.post("/linkage/performances/{performance_id}/link", response_model=SuccessResponse)
async def link_existing_plan_to_performance(
    performance_id: int,
    link_data: PlanLinkRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions("plan")),
):
    """把未计划实绩手动关联到同料卷号计划。"""
    result = await async_plan_service.link_existing_plan(
        db,
        performance_id=performance_id,
        plan_id=link_data.plan_id,
        operator_id=current_user.id,
    )
    return SuccessResponse(data=result)


@router.post("/linkage/performances/{performance_id}/backfill", response_model=SuccessResponse)
async def backfill_plan_from_performance(
    performance_id: int,
    plan_data: PlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions("plan")),
):
    """基于未计划实绩回补同料卷号计划，并立即关联为 observed。"""
    result = await async_plan_service.backfill_plan_from_performance(
        db,
        performance_id=performance_id,
        plan_data=plan_data,
        operator_id=current_user.id,
    )
    return SuccessResponse(data=result)


@router.get("/{plan_id}", response_model=SuccessResponse)
async def get_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions("plan")),
):
    """获取单个生产计划。"""
    plan = await async_plan_service.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    return SuccessResponse(data=PlanResponse.model_validate(plan).model_dump(by_alias=True))


@router.put("/{plan_id}", response_model=SuccessResponse)
async def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions("plan")),
):
    """更新生产计划。"""
    try:
        plan = await async_plan_service.update_plan(db, plan_id, plan_data)
        if not plan:
            raise HTTPException(status_code=404, detail="计划不存在")
        return SuccessResponse(
            message="更新成功",
            data=PlanResponse.model_validate(plan).model_dump(by_alias=True),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{plan_id}", response_model=SuccessResponse)
async def delete_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permissions("plan")),
):
    """软删除生产计划。"""
    try:
        if not await async_plan_service.delete_plan(db, plan_id):
            raise HTTPException(status_code=404, detail="计划不存在")
        return SuccessResponse(message="删除成功")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
