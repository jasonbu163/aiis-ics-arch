"""equipment匿名typed入口；先准入及采用凭据，再调用真实async Service。"""
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Request
from starlette.responses import Response
from database import get_db_session
from common.integration.http import IntegrationRoute
from common.integration.receipt import receipt_response
from app.equipment.integration_config import IntegrationConfig, get_integration_config
from app.equipment.integration_error_codes import IntegrationError
from app.equipment.schemas import integration as dto
from app.equipment.services import async_integration as service

class ModuleIntegrationRoute(IntegrationRoute):
    owner = "equipment"
    error_type = IntegrationError


router = APIRouter(prefix="/integration/equipment", tags=["Business Integration"], route_class=ModuleIntegrationRoute)


async def ready_temperature(sample: dto.TemperatureRequest, request: Request,
        config: IntegrationConfig = Depends(get_integration_config)):
    request.state.integration_context = {"producer_id":sample.producer_id,"event_id":sample.event_id,
        "resource":"temperature","equipment_id":sample.data.equipment_id}
    adoption=config.require_ready(sample.data.equipment_id,sample.producer_id)
    async with await get_db_session() as db:
        yield sample,adoption,db


@router.post("/temperature-samples", response_model=dto.TemperatureSuccess, responses=dto.error_responses("temperature"), operation_id="business_equipment_temperature_v1")
async def receive_temperature(prepared=Depends(ready_temperature)):
    sample,adoption,db=prepared
    result=await service.receive_sample(db,sample,adoption,"temperature")
    return Response(receipt_response(result),media_type="application/json")


async def ready_drive(sample: dto.DriveRequest, request: Request,
        config: IntegrationConfig = Depends(get_integration_config)):
    request.state.integration_context = {"producer_id":sample.producer_id,"event_id":sample.event_id,
        "resource":"drive","equipment_id":sample.data.equipment_id}
    adoption=config.require_ready(sample.data.equipment_id,sample.producer_id)
    async with await get_db_session() as db:
        yield sample,adoption,db


@router.post("/drive-samples", response_model=dto.DriveSuccess, responses=dto.error_responses("drive"), operation_id="business_equipment_drive_v1")
async def receive_drive(prepared=Depends(ready_drive)):
    sample,adoption,db=prepared
    result=await service.receive_sample(db,sample,adoption,"drive")
    return Response(receipt_response(result),media_type="application/json")


async def ready_production_parameters(sample: dto.ProductionParameterRequest, request: Request,
        config: IntegrationConfig = Depends(get_integration_config)):
    request.state.integration_context = {"producer_id":sample.producer_id,"event_id":sample.event_id,
        "resource":"production_parameters","equipment_id":sample.data.equipment_id}
    adoption=config.require_ready(sample.data.equipment_id,sample.producer_id)
    async with await get_db_session() as db:
        yield sample,adoption,db


@router.post("/production-parameter-samples", response_model=dto.ProductionParameterSuccess, responses=dto.error_responses("production_parameters"), operation_id="business_equipment_production_parameters_v1")
async def receive_production_parameters(prepared=Depends(ready_production_parameters)):
    sample,adoption,db=prepared
    result=await service.receive_sample(db,sample,adoption,"production_parameters")
    return Response(receipt_response(result),media_type="application/json")
