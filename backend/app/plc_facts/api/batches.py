"""批量原子接收薄入口。"""
from fastapi import APIRouter,Depends,Request
from .http import FactsRoute,success,ERROR_RESPONSES
from .dependencies import prepared_batch,batch_session
from ..config import get_settings
from ..schemas.receipt_out import ReceiptOut
from ..services.async_ingest import ingest
router=APIRouter(route_class=FactsRoute)
@router.post('/batches',response_model=ReceiptOut,responses=ERROR_RESPONSES,operation_id='plc_facts_batches')
async def batches(request:Request,prepared=Depends(prepared_batch),db=Depends(batch_session)):
    return success(await ingest(db,prepared,get_settings(),request.state.facts_boundary))
