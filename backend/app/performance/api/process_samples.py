"""三类过程POST，父id由生产观察返回，不自动寻找或建立父。"""
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Request
from common.response import SuccessResponse
from core.deps import get_current_active_admin, require_permissions
from database import get_db
from app.performance.api.mapping_http import MappingRoute
from app.performance.api.mapping_observations import actor_context
from app.performance.mapping_config import MappingConfig, get_mapping_config
from app.performance.schemas.process_sample_in import ProcessTemperatureIn, ProcessTensionIn, ProcessSpeedIn
from app.performance.services.async_process_sample import receive_sample
router = APIRouter(prefix="/performances", tags=["Performance"], route_class=MappingRoute)

@router.post("/{record_id}/process-temperature-samples", response_model=SuccessResponse,
    dependencies=[Depends(actor_context), Depends(require_permissions("performance-mapping-ingest"))])
async def receive_temperature(record_id: Annotated[int, Path(gt=0)], sample: ProcessTemperatureIn, request: Request,
        actor=Depends(get_current_active_admin), db=Depends(get_db), config: MappingConfig=Depends(get_mapping_config)):
    config.allowed_equipment(sample.equipment_id)
    return SuccessResponse(data=await receive_sample(db,sample,actor.id,record_id,'temperature'))

@router.post("/{record_id}/process-tension-samples", response_model=SuccessResponse,
    dependencies=[Depends(actor_context), Depends(require_permissions("performance-mapping-ingest"))])
async def receive_tension(record_id: Annotated[int, Path(gt=0)], sample: ProcessTensionIn, request: Request,
        actor=Depends(get_current_active_admin), db=Depends(get_db), config: MappingConfig=Depends(get_mapping_config)):
    config.allowed_equipment(sample.equipment_id)
    return SuccessResponse(data=await receive_sample(db,sample,actor.id,record_id,'tension'))

@router.post("/{record_id}/process-speed-samples", response_model=SuccessResponse,
    dependencies=[Depends(actor_context), Depends(require_permissions("performance-mapping-ingest"))])
async def receive_speed(record_id: Annotated[int, Path(gt=0)], sample: ProcessSpeedIn, request: Request,
        actor=Depends(get_current_active_admin), db=Depends(get_db), config: MappingConfig=Depends(get_mapping_config)):
    config.allowed_equipment(sample.equipment_id)
    return SuccessResponse(data=await receive_sample(db,sample,actor.id,record_id,'speed'))
