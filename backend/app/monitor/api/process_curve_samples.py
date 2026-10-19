"""曲线独立HTTP写读，所有caller均受单设备scope约束。"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request
from common.response import SuccessResponse
from common.exceptions import BusinessException
from app.monitor.mapping_error_codes import MappingError
from core.deps import get_current_user, get_current_active_admin, require_permissions
from database import get_db
from app.monitor.api.mapping_http import MappingRoute
from app.monitor.mapping_config import MappingConfig, get_mapping_config
from app.monitor.schemas.process_curve_in import ProcessCurveIn
from app.monitor.schemas.process_curve_query import ProcessCurveQuery
from app.monitor.services import async_process_curve_sample as service
router = APIRouter(prefix="/monitor",tags=["Monitor"],route_class=MappingRoute)
async def actor_context(request: Request,actor=Depends(get_current_user)):
    request.state.monitor_mapping_actor_user_id = actor.id
    if actor.role not in {"admin", "supervisor", "operator"}:
        raise BusinessException(MappingError.FORBIDDEN, code=403)
@router.post("/process-curve-samples",response_model=SuccessResponse,
    dependencies=[Depends(actor_context),Depends(require_permissions("monitor-curve-ingest"))])
async def receive_sample(sample: ProcessCurveIn,request: Request,actor=Depends(get_current_active_admin),
        db=Depends(get_db),config: MappingConfig=Depends(get_mapping_config)):
    config.allowed_equipment(sample.equipment_id)
    request.state.monitor_mapping_equipment_id = sample.equipment_id
    return SuccessResponse(data=await service.receive_sample(db,sample,actor.id))
@router.get("/process-curve-samples",response_model=SuccessResponse,dependencies=[Depends(actor_context)])
async def read_samples(query: Annotated[ProcessCurveQuery,Query()],actor=Depends(require_permissions("monitor-curve-read")),
        db=Depends(get_db),config: MappingConfig=Depends(get_mapping_config)):
    config.allowed_equipment(query.equipment_id)
    return SuccessResponse(data=await service.read_samples(db,query.equipment_id,query.date,query.record_id,query.limit))
