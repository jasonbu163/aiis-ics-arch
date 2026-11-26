"""在能源模块聚合原三价和逐项目价格 API。"""
from fastapi import APIRouter

from . import energy_price, energy_pricing

router = APIRouter()
router.include_router(energy_price.router)
router.include_router(energy_pricing.router)
