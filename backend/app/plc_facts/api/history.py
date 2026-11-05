"""安全增量/范围历史薄入口。"""
from fastapi import APIRouter,Depends
from .http import FactsRoute,success,ERROR_RESPONSES
from .dependencies import history_query,history_session
from ..config import get_settings
from ..schemas.read_out import ReadOut
from ..services.async_query import read
router=APIRouter(route_class=FactsRoute)
@router.get('/history',response_model=ReadOut,responses=ERROR_RESPONSES,operation_id='plc_facts_history')
async def history(query=Depends(history_query),db=Depends(history_session)):
    return success(await read(db,query,get_settings()))
