"""完整温控样本dashboard，继承原温控read/scope和局部HTTP。"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request
from common.response import SuccessResponse
from common.exceptions import BusinessException
from app.equipment.error_codes import TemperatureError
from core.deps import require_permissions
from database import get_db
from app.equipment.api.temperature_http import TemperatureRoute
from app.equipment.config import TemperatureConfig, get_temperature_config
from app.equipment.schemas.mapping_sample_query import MappingSampleQuery
from app.equipment.services.async_temperature_dashboard import read_dashboard
router = APIRouter(prefix="/equipment", tags=["Equipment"], route_class=TemperatureRoute)
@router.get("/temperature-sample-dashboard", response_model=SuccessResponse)
async def temperature_dashboard(query: Annotated[MappingSampleQuery, Query()], request: Request,
        actor=Depends(require_permissions("equipment-temperature-read")), db=Depends(get_db),
        config: TemperatureConfig=Depends(get_temperature_config)):
    if actor.role not in {"admin", "supervisor", "operator"}:
        raise BusinessException(TemperatureError.FORBIDDEN, code=403)
    config.allowed_equipment(query.equipment_id)
    return SuccessResponse(data=await read_dashboard(db, query.equipment_id, query.record_id, query.limit))
