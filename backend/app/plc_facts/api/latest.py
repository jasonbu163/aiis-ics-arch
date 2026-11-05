"""逐点latest薄查询入口。"""
from fastapi import APIRouter,Depends
from .http import FactsRoute,success,ERROR_RESPONSES
from .dependencies import latest_query,latest_session
from ..config import get_settings
from ..schemas.read_out import ReadOut
from ..services.async_query import read
router=APIRouter(route_class=FactsRoute)
@router.get('/latest',response_model=ReadOut,responses=ERROR_RESPONSES,operation_id='plc_facts_latest')
async def latest(query=Depends(latest_query),db=Depends(latest_session)):
    return success(await read(db,query,get_settings()))
