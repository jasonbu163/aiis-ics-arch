"""生产观察及明确设备的实绩读面，局部HTTP状态与独立权限。"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request, Path
from common.response import SuccessResponse
from common.exceptions import BusinessException
from app.performance.mapping_error_codes import MappingError
from core.deps import get_current_user, get_current_active_admin, require_permissions
from database import get_db
from app.performance.api.mapping_http import MappingRoute
from app.performance.mapping_config import MappingConfig, get_mapping_config
from app.performance.schemas.production_observation_in import ProductionObservationIn
from app.performance.schemas.mapping_query import MappingQuery
from app.performance.services import async_production_observation as service, async_mapping_query as queries
router = APIRouter(prefix="/performances", tags=["Performance"], route_class=MappingRoute)
async def actor_context(request: Request, actor=Depends(get_current_user)):
    request.state.performance_mapping_actor_user_id = actor.id
    if actor.role not in {"admin", "supervisor", "operator"}:
        raise BusinessException(MappingError.FORBIDDEN, code=403)
@router.post("/production-observations", response_model=SuccessResponse,
    dependencies=[Depends(actor_context), Depends(require_permissions("performance-mapping-ingest"))])
async def receive_observation(sample: ProductionObservationIn, request: Request, actor=Depends(get_current_active_admin),
        db=Depends(get_db), config: MappingConfig=Depends(get_mapping_config)):
    config.allowed_equipment(sample.equipment_id)
    request.state.performance_mapping_equipment_id = sample.equipment_id
    return SuccessResponse(data=await service.receive_observation(db,sample,actor.id))
@router.get("/mapping-records", response_model=SuccessResponse, dependencies=[Depends(actor_context)])
async def list_records(query: Annotated[MappingQuery, Query()], actor=Depends(require_permissions("performance-mapping-read")),
        db=Depends(get_db), config: MappingConfig=Depends(get_mapping_config)):
    config.allowed_equipment(query.equipment_id)
    return SuccessResponse(data=await queries.read_records(db,query))
@router.get("/mapping-records/{record_id}", response_model=SuccessResponse, dependencies=[Depends(actor_context)])
async def read_record(record_id: Annotated[int, Path(gt=0)], equipment_id: str=Query(...,alias="equipmentId"),
        actor=Depends(require_permissions("performance-mapping-read")), db=Depends(get_db), config: MappingConfig=Depends(get_mapping_config)):
    config.allowed_equipment(equipment_id)
    return SuccessResponse(data=await queries.read_record(db,equipment_id,record_id))
@router.get("/mapping-records/{record_id}/process-data", response_model=SuccessResponse, dependencies=[Depends(actor_context)])
async def read_process(record_id: Annotated[int, Path(gt=0)], equipment_id: str=Query(...,alias="equipmentId"),
        actor=Depends(require_permissions("performance-mapping-read")), db=Depends(get_db), config: MappingConfig=Depends(get_mapping_config)):
    config.allowed_equipment(equipment_id)
    return SuccessResponse(data=await queries.read_process_data(db,equipment_id,record_id))
