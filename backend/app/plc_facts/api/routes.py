"""只聚合三条匿名事实路由。"""
from fastapi import APIRouter
from . import batches,latest,history
router=APIRouter(prefix='/integration/plc-facts',tags=['plc-facts'])
for part in (batches,latest,history): router.include_router(part.router)
