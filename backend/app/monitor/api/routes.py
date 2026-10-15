"""
文件路径: /backend/app/monitor/api/routes.py
功能描述: Monitor Core 事实层路由聚合入口

只暴露 collector 状态和 raw/latest 现场事实查询。
项目 HMI、温度、能耗和过程业务路由由消费方项目模块提供。
"""
from fastapi import APIRouter, Depends

from app.monitor.api.collector import router as collector_router
from app.monitor.api.realtime import router as realtime_router
from core.deps import require_permissions


router = APIRouter(
    prefix="/monitor",
)
router.include_router(collector_router, dependencies=[Depends(require_permissions("monitor"))])
router.include_router(realtime_router, dependencies=[Depends(require_permissions("monitor"))])

from .temperature import router as temperature_router
from .energy import router as energy_router
router.include_router(temperature_router, dependencies=[Depends(require_permissions("monitor-business-read"))])
router.include_router(energy_router, dependencies=[Depends(require_permissions("monitor-business-read"))])
