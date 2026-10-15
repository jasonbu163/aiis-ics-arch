"""
文件路径: /backend/app/auxiliary/api/routes.py
功能描述: 辅助管理 API 路由定义
主要功能:
    - 班组管理 CRUD 操作
    - 班次管理 CRUD 操作
    - 停机记录 CRUD 操作
    - 排班规则读取与维护
"""
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auxiliary.schemas.auxiliary_in import (
    ShiftCreate,
    ShiftRuleUpdate,
    ShiftTeamCreate,
    ShiftTeamUpdate,
    ShiftUpdate,
    StopRecordCreate,
    StopRecordUpdate,
)
from app.auxiliary.schemas.auxiliary_out import ShiftResponse, ShiftRuleResponse, ShiftTeamResponse, StopRecordResponse
from app.auxiliary.services.async_auxiliary import AuxiliaryService
from common.exceptions import BusinessException
from app.auxiliary.error_codes import AuxiliaryErrorCode
from common.response import SuccessResponse
from core.deps import require_permissions
from database import get_db


router = APIRouter(
    prefix="/auxiliary",
    tags=["Auxiliary"],
    dependencies=[Depends(require_permissions("auxiliary"))],
)
shift_team_router = APIRouter(
    prefix="/shift-teams",
    tags=["Auxiliary - Shift Teams"],
    dependencies=[Depends(require_permissions("auxiliary"))],
)


@shift_team_router.get("", response_model=SuccessResponse)
async def list_shift_teams(
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    items, total = await service.list_shift_teams(page=page, page_size=page_size)
    return SuccessResponse(
        data={
            "items": [ShiftTeamResponse.model_validate(i).model_dump(by_alias=True) for i in items],
            "total": total,
            "page": page,
            "pageSize": page_size,
        }
    )


@shift_team_router.get("/{id}", response_model=SuccessResponse)
async def get_shift_team(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    item = await service.get_shift_team(id)
    if not item:
        raise BusinessException(AuxiliaryErrorCode.NOT_FOUND, code=404)
    return SuccessResponse(data=ShiftTeamResponse.model_validate(item))


@shift_team_router.post("", response_model=SuccessResponse)
async def create_shift_team(
    data: ShiftTeamCreate,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    item = await service.create_shift_team(data)
    return SuccessResponse(data=ShiftTeamResponse.model_validate(item))


@shift_team_router.put("/{id}", response_model=SuccessResponse)
async def update_shift_team(
    id: int,
    data: ShiftTeamUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    item = await service.update_shift_team(id, data)
    if not item:
        raise BusinessException(AuxiliaryErrorCode.NOT_FOUND, code=404)
    return SuccessResponse(data=ShiftTeamResponse.model_validate(item))


@shift_team_router.delete("/{id}", response_model=SuccessResponse)
async def delete_shift_team(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    success = await service.delete_shift_team(id)
    if not success:
        raise BusinessException(AuxiliaryErrorCode.NOT_FOUND, code=404)
    return SuccessResponse()


shift_router = APIRouter(
    prefix="/shifts",
    tags=["Auxiliary - Shifts"],
    dependencies=[Depends(require_permissions("auxiliary"))],
)


@shift_router.get("", response_model=SuccessResponse)
async def list_shifts(
    team_id: Optional[int] = None,
    start_date: Optional[date] = Query(None, alias="startDate"),
    end_date: Optional[date] = Query(None, alias="endDate"),
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    items, total = await service.list_shifts(
        page=page,
        page_size=page_size,
        team_id=team_id,
        start_date=start_date,
        end_date=end_date,
    )
    return SuccessResponse(
        data={
            "items": [ShiftResponse.model_validate(i).model_dump(by_alias=True) for i in items],
            "total": total,
            "page": page,
            "pageSize": page_size,
        }
    )


@shift_router.get("/{id}", response_model=SuccessResponse)
async def get_shift(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    item = await service.get_shift(id)
    if not item:
        raise BusinessException(AuxiliaryErrorCode.NOT_FOUND, code=404)
    return SuccessResponse(data=ShiftResponse.model_validate(item))


@shift_router.post("", response_model=SuccessResponse)
async def create_shift(
    data: ShiftCreate,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    item = await service.create_shift(data)
    return SuccessResponse(data=ShiftResponse.model_validate(item))


@shift_router.put("/{id}", response_model=SuccessResponse)
async def update_shift(
    id: int,
    data: ShiftUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    item = await service.update_shift(id, data)
    if not item:
        raise BusinessException(AuxiliaryErrorCode.NOT_FOUND, code=404)
    return SuccessResponse(data=ShiftResponse.model_validate(item))


@shift_router.delete("/{id}", response_model=SuccessResponse)
async def delete_shift(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    success = await service.delete_shift(id)
    if not success:
        raise BusinessException(AuxiliaryErrorCode.NOT_FOUND, code=404)
    return SuccessResponse()


shift_rule_router = APIRouter(
    prefix="/shift-rules",
    tags=["Auxiliary - Shift Rules"],
    dependencies=[Depends(require_permissions("auxiliary"))],
)


@shift_rule_router.get("", response_model=SuccessResponse)
async def get_shift_rule(
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    item = await service.get_shift_rule()
    return SuccessResponse(data=ShiftRuleResponse.model_validate(item) if item is not None else None)


@shift_rule_router.put("/{id}", response_model=SuccessResponse)
async def update_shift_rule(
    id: int,
    data: ShiftRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    item = await service.update_shift_rule(id, data)
    if not item:
        raise BusinessException(AuxiliaryErrorCode.NOT_FOUND, code=404)
    return SuccessResponse(data=ShiftRuleResponse.model_validate(item))


stop_record_router = APIRouter(
    prefix="/stop-records",
    tags=["Auxiliary - Stop Records"],
    dependencies=[Depends(require_permissions("auxiliary"))],
)


@stop_record_router.get("", response_model=SuccessResponse)
async def list_stop_records(
    status: Optional[str] = None,
    shift: Optional[str] = None,
    start_time: Optional[datetime] = Query(None, alias="startTime"),
    end_time: Optional[datetime] = Query(None, alias="endTime"),
    stop_type: Optional[str] = Query(None, alias="stopType"),
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    items, total = await service.list_stop_records(
        page=page,
        page_size=page_size,
        status=status,
        shift=shift,
        start_time=start_time,
        end_time=end_time,
        stop_type=stop_type,
    )
    return SuccessResponse(
        data={
            "items": [StopRecordResponse.model_validate(i).model_dump(by_alias=True) for i in items],
            "total": total,
            "page": page,
            "pageSize": page_size,
        }
    )


@stop_record_router.get("/{id}", response_model=SuccessResponse)
async def get_stop_record(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    item = await service.get_stop_record(id)
    if not item:
        raise BusinessException(AuxiliaryErrorCode.NOT_FOUND, code=404)
    return SuccessResponse(data=StopRecordResponse.model_validate(item))


@stop_record_router.post("", response_model=SuccessResponse)
async def create_stop_record(
    data: StopRecordCreate,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    item = await service.create_stop_record(data)
    return SuccessResponse(data=StopRecordResponse.model_validate(item))


@stop_record_router.put("/{id}", response_model=SuccessResponse)
async def update_stop_record(
    id: int,
    data: StopRecordUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    item = await service.update_stop_record(id, data)
    if not item:
        raise BusinessException(AuxiliaryErrorCode.NOT_FOUND, code=404)
    return SuccessResponse(data=StopRecordResponse.model_validate(item))


@stop_record_router.delete("/{id}", response_model=SuccessResponse)
async def delete_stop_record(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    service = AuxiliaryService(db)
    success = await service.delete_stop_record(id)
    if not success:
        raise BusinessException(AuxiliaryErrorCode.NOT_FOUND, code=404)
    return SuccessResponse()
