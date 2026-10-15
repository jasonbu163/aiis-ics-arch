"""
文件路径: /backend/app/reports/api/__init__.py
功能描述: 报表 API 导出
主要功能:
    - 导出报表相关路由
"""
from app.reports.api.routes import (
    assessment_router,
    efficiency_router,
    print_router,
    quality_router,
    router,
    target_router,
)

report_router = router

__all__ = [
    "router",
    "report_router",
    "assessment_router",
    "efficiency_router",
    "print_router",
    "quality_router",
    "target_router",
]
