"""
文件路径: /backend/app/reports/api/routes.py
功能描述: 报表管理 API 路由定义
主要功能:
    - 质量报表数据查询
    - 生产报表统计
    - 绩效报表生成
    - 打印记录管理
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional
from common.response import SuccessResponse
from app.reports.services.async_assessment import assessment_service
from app.reports.services.async_efficiency import (
    build_efficiency_overview_response as service_build_efficiency_overview_response,
    build_efficiency_response as service_build_efficiency_response,
)
from app.reports.services.async_print import print_service
from app.reports.services.async_quality import reports_quality_service
from app.reports.services.async_reports import reports_service
from app.reports.services.async_target import target_service
from core.deps import get_current_user, require_permissions
from app.user.schemas.user_out import UserResponse
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(require_permissions("reports"))],
)


def _query_alias(request: Request, value: Optional[str], snake_key: str) -> Optional[str]:
    """兼容前端 camelCase 参数和历史测试/脚本中的 snake_case 参数。"""

    return value if value is not None else request.query_params.get(snake_key)


@router.get("", response_model=SuccessResponse)
async def get_report_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    report_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(data=await reports_service.list_reports(db, page, page_size, report_type, start_date, end_date))


@router.post("/generate", response_model=SuccessResponse)
async def generate_report(
    report_type: str,
    report_date: str,
    shift: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(
        message="报表生成成功",
        data=await reports_service.generate_report(db, report_type, report_date, shift, current_user.id)
    )


@router.get("/export", response_model=SuccessResponse)
async def export_report(
    report_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(data=await reports_service.export_reports(db, report_type, start_date, end_date))


@router.get("/trend", response_model=SuccessResponse)
async def get_trend_data(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(data=await reports_service.get_trend_data(db, days))


@router.get("/{report_id}", response_model=SuccessResponse)
async def get_report_detail(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(data=await reports_service.get_report_detail(db, report_id))


assessment_router = APIRouter(
    prefix="/assessments",
    tags=["Reports - Assessments"],
    dependencies=[Depends(require_permissions("reports"))],
)


@assessment_router.get("", response_model=SuccessResponse)
async def get_assessment_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    employee_name: Optional[str] = None,
    assessment_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(
        data=await assessment_service.list_assessments(db, page, page_size, employee_name, assessment_type)
    )


@assessment_router.post("", response_model=SuccessResponse)
async def create_assessment(
    employee_id: int,
    employee_name: str,
    assessment_type: str,
    assessment_period: str,
    production_score: float,
    quality_score: float,
    efficiency_score: float,
    overall_score: float,
    grade: str,
    assessment_date: str,
    comments: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(
        message="创建成功",
        data=await assessment_service.create_assessment(
            db,
            employee_id,
            employee_name,
            assessment_type,
            assessment_period,
            production_score,
            quality_score,
            efficiency_score,
            overall_score,
            grade,
            assessment_date,
            comments,
            current_user.id,
        ),
    )


@assessment_router.put("/{assessment_id}", response_model=SuccessResponse)
async def update_assessment(
    assessment_id: int,
    production_score: Optional[float] = None,
    quality_score: Optional[float] = None,
    efficiency_score: Optional[float] = None,
    overall_score: Optional[float] = None,
    grade: Optional[str] = None,
    comments: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    assessment = await assessment_service.update_assessment(
        db,
        assessment_id,
        production_score,
        quality_score,
        efficiency_score,
        overall_score,
        grade,
        comments,
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="评估记录不存在")

    return SuccessResponse(message="更新成功", data=assessment)


@assessment_router.get("/statistics", response_model=SuccessResponse)
async def get_assessment_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(data=await assessment_service.get_assessment_statistics(db))


efficiency_router = APIRouter(
    prefix="/statistics",
    tags=["Reports - Efficiency"],
    dependencies=[Depends(require_permissions("reports"))],
)


@efficiency_router.get("/efficiency", response_model=SuccessResponse)
async def get_efficiency_data(
    request: Request,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    shift: Optional[str] = None,
    group_by: str = Query("day", pattern="^(day|shift)$", alias="groupBy"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    start_date = _query_alias(request, start_date, "start_date")
    end_date = _query_alias(request, end_date, "end_date")
    group_by = request.query_params.get("group_by") or group_by or "day"
    payload = await service_build_efficiency_response(db, start_date, end_date, shift, group_by)
    total = len(payload["items"])
    offset = (page - 1) * page_size

    return SuccessResponse(data={
        "items": payload["items"][offset:offset + page_size],
        "total": total,
        "page": page,
        "pageSize": page_size,
        "totalPages": (total + page_size - 1) // page_size if total else 0,
        "summary": payload["summary"],
        "trend": payload["trend"],
        "downtimeAnalysis": payload["downtimeAnalysis"],
    })


@efficiency_router.get("/oee", response_model=SuccessResponse)
async def get_oee_data(
    request: Request,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    shift: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    start_date = _query_alias(request, start_date, "start_date")
    end_date = _query_alias(request, end_date, "end_date")
    payload = await service_build_efficiency_response(db, start_date, end_date, shift, "day")
    summary = payload["summary"]

    return SuccessResponse(data={
        "oee": summary["oee"],
        "availability": summary["availability"],
        "performance": summary["performance"],
        "quality": summary["quality"],
        "plannedTime": summary["plannedTime"],
        "actualTime": summary["actualTime"],
        "downtimeLoss": summary["downtimeLoss"],
        "theoreticalOutput": summary["theoreticalOutput"],
        "actualOutput": summary["actualOutput"],
        "speedLoss": summary["speedLoss"],
        "totalOutput": summary["totalOutput"],
        "qualifiedOutput": summary["qualifiedOutput"],
        "defectOutput": summary["defectOutput"],
        "trend": payload["trend"],
        "downtimeAnalysis": payload["downtimeAnalysis"],
    })


@efficiency_router.get("/overview", response_model=SuccessResponse)
async def get_efficiency_overview(
    request: Request,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    shift: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    start_date = _query_alias(request, start_date, "start_date")
    end_date = _query_alias(request, end_date, "end_date")
    return SuccessResponse(data=await service_build_efficiency_overview_response(db, start_date, end_date, shift))


print_router = APIRouter(
    prefix="/print",
    tags=["Reports - Print"],
    dependencies=[Depends(require_permissions("reports"))],
)


@print_router.get("/list", response_model=SuccessResponse)
async def get_print_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(data=await print_service.list_print_items(db, page, page_size))


@print_router.get("/data/{performance_id}", response_model=SuccessResponse)
async def get_print_data(
    performance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    print_data = await print_service.get_print_data(db, performance_id, current_user.name)
    if not print_data:
        raise HTTPException(status_code=404, detail="实绩不存在")

    return SuccessResponse(data=print_data)


@print_router.post("/submit", response_model=SuccessResponse)
async def submit_print(
    performance_ids: list[int],
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    count = await print_service.submit_print(db, performance_ids, current_user.id)
    return SuccessResponse(message=f"已提交 {count} 条打印任务")


quality_router = APIRouter(
    prefix="/quality",
    tags=["Reports - Quality Control"],
    dependencies=[Depends(require_permissions("reports"))],
)


@quality_router.get("/performances/{performance_id}/quality", response_model=SuccessResponse)
async def get_quality_records(
    performance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(data=await reports_quality_service.list_quality_records(db, performance_id))


@quality_router.post("/performances/{performance_id}/quality", response_model=SuccessResponse)
async def create_quality_record(
    performance_id: int,
    item_name: str,
    standard_value: Optional[str] = None,
    actual_value: Optional[str] = None,
    result: Optional[str] = None,
    inspector: Optional[str] = None,
    inspect_time: Optional[str] = None,
    remark: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(
        message="创建成功",
        data=await reports_quality_service.create_quality_record(
            db,
            performance_id,
            item_name,
            standard_value,
            actual_value,
            result,
            inspector,
            inspect_time,
            remark,
        ),
    )


@quality_router.put("/quality/{quality_id}", response_model=SuccessResponse)
async def update_quality_record(
    quality_id: int,
    standard_value: Optional[str] = None,
    actual_value: Optional[str] = None,
    result: Optional[str] = None,
    inspector: Optional[str] = None,
    inspect_time: Optional[str] = None,
    remark: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    success = await reports_quality_service.update_quality_record(
        db,
        quality_id,
        standard_value,
        actual_value,
        result,
        inspector,
        inspect_time,
        remark,
    )
    if not success:
        raise HTTPException(status_code=404, detail="质量记录不存在")

    return SuccessResponse(message="更新成功")


@quality_router.get("/quality/{quality_id}/defects", response_model=SuccessResponse)
async def get_defect_records(
    quality_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(data=await reports_quality_service.list_defect_records(db, quality_id))


@quality_router.post("/quality/{quality_id}/defects", response_model=SuccessResponse)
async def add_defect_record(
    quality_id: int,
    position: Optional[str] = None,
    defect_type: Optional[str] = None,
    defect_level: Optional[str] = None,
    length: Optional[int] = None,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    defect_id = await reports_quality_service.add_defect_record(
        db,
        quality_id,
        position,
        defect_type,
        defect_level,
        length,
        description,
    )
    if defect_id is None:
        raise HTTPException(status_code=404, detail="质量记录不存在")

    return SuccessResponse(
        message="添加成功",
        data={"id": defect_id}
    )


@quality_router.delete("/defects/{defect_id}", response_model=SuccessResponse)
async def delete_defect_record(
    defect_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    success = await reports_quality_service.delete_defect_record(db, defect_id)
    if not success:
        raise HTTPException(status_code=404, detail="缺陷记录不存在")

    return SuccessResponse(message="删除成功")


target_router = APIRouter(
    prefix="/targets",
    tags=["Reports - Targets"],
    dependencies=[Depends(require_permissions("reports"))],
)


@target_router.get("", response_model=SuccessResponse)
async def get_target_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    target_type: Optional[str] = None,
    period_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(data=await target_service.list_targets(db, page, page_size, target_type, period_type))


@target_router.post("", response_model=SuccessResponse)
async def create_target(
    target_type: str,
    target_value: float,
    period_type: str,
    period_start: str,
    period_end: str,
    department: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    return SuccessResponse(
        message="创建成功",
        data=await target_service.create_target(
            db,
            target_type,
            target_value,
            period_type,
            period_start,
            period_end,
            department,
            current_user.id,
        ),
    )


@target_router.put("/{target_id}", response_model=SuccessResponse)
async def update_target(
    target_id: int,
    target_value: Optional[float] = None,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    department: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    target = await target_service.update_target(db, target_id, target_value, period_start, period_end, department)
    if not target:
        raise HTTPException(status_code=404, detail="目标不存在")

    return SuccessResponse(message="更新成功", data=target)


@target_router.delete("/{target_id}", response_model=SuccessResponse)
async def delete_target(
    target_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    success = await target_service.delete_target(db, target_id)
    if not success:
        raise HTTPException(status_code=404, detail="目标不存在")

    return SuccessResponse(message="删除成功")


@target_router.get("/{target_id}/achievement", response_model=SuccessResponse)
async def get_target_achievement(
    target_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    achievement = await target_service.get_target_achievement(db, target_id)
    if not achievement:
        raise HTTPException(status_code=404, detail="目标不存在")

    return SuccessResponse(data=achievement)
