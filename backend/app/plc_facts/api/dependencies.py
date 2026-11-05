"""默认关闭/精确scope先于DB；进程最多四在途操作，完整close后才发送。"""
from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import Depends,Request,Query
from database import get_db_session
from ..config import get_settings
from ..error_codes import FactsError
from ..source import prepare
from ..schemas.batch_in import BatchIn
from ..schemas.query import LatestQuery,HistoryQuery

_inflight=0

async def prepared_batch(request:Request,body:BatchIn):
    prepared=prepare(body)
    get_settings().admit({c.manifest.plc_id for c in prepared.cycles.values()})
    request.state.facts_prepared=prepared
    return prepared

async def latest_query(query:Annotated[LatestQuery,Query()]):
    get_settings().admit([query.plc_id]); return query

async def history_query(query:Annotated[HistoryQuery,Query()]):
    get_settings().admit([query.plc_id]); return query

@asynccontextmanager
async def session_for_request(request):
    global _inflight
    if _inflight>=4: raise FactsError('busy',429)
    _inflight+=1; session=None
    try:
        session=await get_db_session()
        yield session
    finally:
        try:
            if session is not None: await session.close()
        finally: _inflight-=1

async def batch_session(request:Request,prepared=Depends(prepared_batch)):
    async with session_for_request(request) as session: yield session
async def latest_session(request:Request,query=Depends(latest_query)):
    async with session_for_request(request) as session: yield session
async def history_session(request:Request,query=Depends(history_query)):
    async with session_for_request(request) as session: yield session
