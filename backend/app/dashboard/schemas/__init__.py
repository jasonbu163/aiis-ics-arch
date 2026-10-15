"""
文件路径: /backend/app/dashboard/schemas/__init__.py
功能描述: Dashboard 响应模型导出
主要功能:
    - 导出看板统计响应模型
    - 导出趋势、分布、分析和状态响应模型
"""
from app.dashboard.schemas.dashboard_out import (
    DashboardStatsResponse,
    DowntimeAnalysisResponse,
    EnergyConsumptionResponse,
    OEEAnalysisResponse,
    OnlineCoilInfo,
    ProductionStatusResponse,
    ProductionTrendResponse,
    QualityDistributionResponse,
    ReadyCoilInfo,
    RecentPlanItem,
    RecentPlansResponse,
    TemperatureTrendResponse,
)

__all__ = [
    "DashboardStatsResponse",
    "ProductionTrendResponse",
    "QualityDistributionResponse",
    "OEEAnalysisResponse",
    "TemperatureTrendResponse",
    "EnergyConsumptionResponse",
    "DowntimeAnalysisResponse",
    "ProductionStatusResponse",
    "OnlineCoilInfo",
    "ReadyCoilInfo",
    "RecentPlanItem",
    "RecentPlansResponse",
]
