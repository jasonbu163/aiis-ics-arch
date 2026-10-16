"""完整温控新HTTP读写入口；认证、独立权限与唯一设备scope先于业务SQL。"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from common.response import SuccessResponse
from common.exceptions import BusinessException
from app.equipment.error_codes import TemperatureError
from core.deps import get_current_user, get_current_active_admin, require_permissions
from database import get_db
from app.equipment.config import TemperatureConfig, get_temperature_config
from app.equipment.api.temperature_http import TemperatureRoute
from app.equipment.schemas.temperature_sample_in import TemperatureSampleIn
from app.equipment.schemas.temperature_sample_query import TemperatureSampleQuery
from app.equipment.services import async_temperature_sample as service

router = APIRouter(prefix="/equipment", tags=["Equipment"], route_class=TemperatureRoute)


async def _actor_context(request: Request, actor=Depends(get_current_user)):
    request.state.temperature_actor_user_id = actor.id


@router.post("/temperature-samples", response_model=SuccessResponse,
             dependencies=[Depends(_actor_context), Depends(require_permissions("equipment-temperature-ingest"))])
async def receive_temperature_sample(sample: TemperatureSampleIn, request: Request,
        current_user=Depends(get_current_active_admin), db: AsyncSession=Depends(get_db),
        config: TemperatureConfig=Depends(get_temperature_config)):
    request.state.temperature_actor_user_id = current_user.id
    request.state.temperature_equipment_id = sample.equipment_id
    request.state.temperature_sample_id = sample.sample_id
    config.allowed_equipment(sample.equipment_id)
    return SuccessResponse(data=await service.receive_sample(db, sample, current_user.id))


@router.get("/temperature-samples", response_model=SuccessResponse, dependencies=[Depends(_actor_context)])
async def read_temperature_samples(query: Annotated[TemperatureSampleQuery, Query()], request: Request,
        current_user=Depends(require_permissions("equipment-temperature-read")), db: AsyncSession=Depends(get_db),
        config: TemperatureConfig=Depends(get_temperature_config)):
    request.state.temperature_actor_user_id = current_user.id
    if query.equipment_id is not None:
        request.state.temperature_equipment_id = query.equipment_id
    if current_user.role not in {"admin", "supervisor", "operator"}:
        raise BusinessException(TemperatureError.FORBIDDEN, code=403)
    equipment_id = config.allowed_equipment(query.equipment_id)
    return SuccessResponse(data=await service.read_samples(db, equipment_id, query.record_id, query.limit))
