"""两类equipment映射POST/GET；认证/scope先于任何业务SQL。"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from common.response import SuccessResponse
from common.exceptions import BusinessException
from app.equipment.mapping_error_codes import MappingError
from core.deps import get_current_user, get_current_active_admin, require_permissions
from database import get_db
from app.equipment.mapping_config import MappingConfig, get_mapping_config
from app.equipment.api.mapping_http import MappingRoute
from app.equipment.schemas.drive_sample_in import DriveSampleIn
from app.equipment.schemas.production_parameter_sample_in import ProductionParameterSampleIn
from app.equipment.schemas.mapping_sample_query import MappingSampleQuery
from app.equipment.services import async_drive_sample as drive, async_production_parameter_sample as parameters
router = APIRouter(prefix="/equipment", tags=["Equipment"], route_class=MappingRoute)
async def actor_context(request: Request, actor=Depends(get_current_user)):
    request.state.equipment_mapping_actor_user_id = actor.id
    if actor.role not in {"admin", "supervisor", "operator"}:
        raise BusinessException(MappingError.FORBIDDEN, code=403)

@router.post("/drive-samples", response_model=SuccessResponse, dependencies=[Depends(actor_context), Depends(require_permissions("equipment-mapping-ingest"))])
async def receive_drive(sample: DriveSampleIn, request: Request, actor=Depends(get_current_active_admin),
        db: AsyncSession=Depends(get_db), config: MappingConfig=Depends(get_mapping_config)):
    request.state.equipment_mapping_equipment_id = sample.equipment_id
    config.allowed_equipment(sample.equipment_id)
    return SuccessResponse(data=await drive.receive_sample(db, sample, actor.id))
@router.get("/drive-samples", response_model=SuccessResponse, dependencies=[Depends(actor_context)])
async def read_drive(query: Annotated[MappingSampleQuery, Query()], request: Request,
        actor=Depends(require_permissions("equipment-mapping-read")), db: AsyncSession=Depends(get_db),
        config: MappingConfig=Depends(get_mapping_config)):
    config.allowed_equipment(query.equipment_id)
    return SuccessResponse(data=await drive.read_samples(db, query.equipment_id, query.record_id, query.limit))

@router.post("/production-parameter-samples", response_model=SuccessResponse, dependencies=[Depends(actor_context), Depends(require_permissions("equipment-mapping-ingest"))])
async def receive_parameters(sample: ProductionParameterSampleIn, request: Request, actor=Depends(get_current_active_admin),
        db: AsyncSession=Depends(get_db), config: MappingConfig=Depends(get_mapping_config)):
    request.state.equipment_mapping_equipment_id = sample.equipment_id
    config.allowed_equipment(sample.equipment_id)
    return SuccessResponse(data=await parameters.receive_sample(db, sample, actor.id))
@router.get("/production-parameter-samples", response_model=SuccessResponse, dependencies=[Depends(actor_context)])
async def read_parameters(query: Annotated[MappingSampleQuery, Query()], request: Request,
        actor=Depends(require_permissions("equipment-mapping-read")), db: AsyncSession=Depends(get_db),
        config: MappingConfig=Depends(get_mapping_config)):
    config.allowed_equipment(query.equipment_id)
    return SuccessResponse(data=await parameters.read_samples(db, query.equipment_id, query.record_id, query.limit))
