"""monitor匿名typed入口；先准入及采用凭据，再调用真实async Service。"""
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Request
from starlette.responses import Response
from database import get_db_session
from common.integration.http import IntegrationRoute
from common.integration.receipt import receipt_response
from app.monitor.integration_config import IntegrationConfig, get_integration_config
from app.monitor.integration_error_codes import IntegrationError
from app.monitor.schemas import integration as dto
from app.monitor.services import async_integration as service

class ModuleIntegrationRoute(IntegrationRoute):
    owner = "monitor"
    error_type = IntegrationError


router = APIRouter(prefix="/integration/monitor", tags=["Business Integration"], route_class=ModuleIntegrationRoute)


async def ready_process_curve(sample: dto.ProcessCurveRequest, request: Request,
        config: IntegrationConfig = Depends(get_integration_config)):
    request.state.integration_context = {"producer_id":sample.producer_id,"event_id":sample.event_id,
        "resource":"process_curve","equipment_id":sample.data.equipment_id}
    adoption=config.require_ready(sample.data.equipment_id,sample.producer_id)
    async with await get_db_session() as db:
        yield sample,adoption,db


@router.post("/process-curve-samples", response_model=dto.ProcessCurveSuccess, responses=dto.error_responses("process_curve"), operation_id="business_monitor_process_curve_v1")
async def receive_process_curve(prepared=Depends(ready_process_curve)):
    sample,adoption,db=prepared
    result=await service.receive_sample(db,sample,adoption)
    return Response(receipt_response(result),media_type="application/json")
