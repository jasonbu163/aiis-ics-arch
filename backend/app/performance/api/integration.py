"""performance匿名typed入口；先准入及采用凭据，再调用真实async Service。"""
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Request
from starlette.responses import Response
from database import get_db_session
from common.integration.http import IntegrationRoute
from common.integration.receipt import receipt_response
from app.performance.integration_config import IntegrationConfig, get_integration_config
from app.performance.integration_error_codes import IntegrationError
from app.performance.schemas import integration as dto
from app.performance.services import async_integration_observation as observation, async_integration_process as process

class ModuleIntegrationRoute(IntegrationRoute):
    owner = "performance"
    error_type = IntegrationError


router = APIRouter(prefix="/integration/performances", tags=["Business Integration"], route_class=ModuleIntegrationRoute)


async def ready_production_observation(sample: dto.ProductionObservationRequest, request: Request,
        config: IntegrationConfig = Depends(get_integration_config)):
    request.state.integration_context = {"producer_id":sample.producer_id,"event_id":sample.event_id,
        "resource":"production_observation","equipment_id":sample.data.equipment_id}
    adoption=config.require_ready(sample.data.equipment_id,sample.producer_id)
    async with await get_db_session() as db:
        yield sample,adoption,db


@router.post("/production-observations", response_model=dto.ProductionObservationSuccess, responses=dto.error_responses("production_observation"), operation_id="business_performance_production_observation_v1")
async def receive_production_observation(prepared=Depends(ready_production_observation)):
    sample,adoption,db=prepared
    result=await observation.receive_observation(db,sample,adoption)
    return Response(receipt_response(result),media_type="application/json")


async def ready_process_temperature(sample: dto.ProcessTemperatureRequest, request: Request, record_id: Annotated[int, Path(gt=0)],
        config: IntegrationConfig = Depends(get_integration_config)):
    request.state.integration_context = {"producer_id":sample.producer_id,"event_id":sample.event_id,
        "resource":"process_temperature","equipment_id":sample.data.equipment_id}
    adoption=config.require_ready(sample.data.equipment_id,sample.producer_id)
    async with await get_db_session() as db:
        yield sample,adoption,db,record_id


@router.post("/{record_id}/process-temperature-samples", response_model=dto.ProcessTemperatureSuccess, responses=dto.error_responses("process_temperature"), operation_id="business_performance_process_temperature_v1")
async def receive_process_temperature(prepared=Depends(ready_process_temperature)):
    sample,adoption,db,record_id=prepared
    result=await process.receive_sample(db,sample,adoption,record_id,"temperature")
    return Response(receipt_response(result),media_type="application/json")


async def ready_process_tension(sample: dto.ProcessTensionRequest, request: Request, record_id: Annotated[int, Path(gt=0)],
        config: IntegrationConfig = Depends(get_integration_config)):
    request.state.integration_context = {"producer_id":sample.producer_id,"event_id":sample.event_id,
        "resource":"process_tension","equipment_id":sample.data.equipment_id}
    adoption=config.require_ready(sample.data.equipment_id,sample.producer_id)
    async with await get_db_session() as db:
        yield sample,adoption,db,record_id


@router.post("/{record_id}/process-tension-samples", response_model=dto.ProcessTensionSuccess, responses=dto.error_responses("process_tension"), operation_id="business_performance_process_tension_v1")
async def receive_process_tension(prepared=Depends(ready_process_tension)):
    sample,adoption,db,record_id=prepared
    result=await process.receive_sample(db,sample,adoption,record_id,"tension")
    return Response(receipt_response(result),media_type="application/json")


async def ready_process_speed(sample: dto.ProcessSpeedRequest, request: Request, record_id: Annotated[int, Path(gt=0)],
        config: IntegrationConfig = Depends(get_integration_config)):
    request.state.integration_context = {"producer_id":sample.producer_id,"event_id":sample.event_id,
        "resource":"process_speed","equipment_id":sample.data.equipment_id}
    adoption=config.require_ready(sample.data.equipment_id,sample.producer_id)
    async with await get_db_session() as db:
        yield sample,adoption,db,record_id


@router.post("/{record_id}/process-speed-samples", response_model=dto.ProcessSpeedSuccess, responses=dto.error_responses("process_speed"), operation_id="business_performance_process_speed_v1")
async def receive_process_speed(prepared=Depends(ready_process_speed)):
    sample,adoption,db,record_id=prepared
    result=await process.receive_sample(db,sample,adoption,record_id,"speed")
    return Response(receipt_response(result),media_type="application/json")
