"""
文件路径: /backend/app/dashboard/schemas/dashboard_out.py
功能描述: Dashboard 看板数据模型定义
主要功能:
    - 定义看板各类数据的请求/响应模型
"""
from typing import Optional, List

from common.schema_base import ApiSchema


class DashboardStatsResponse(ApiSchema):
    today_production: float = 0.0
    pending_plans: int = 0
    completed_coils: int = 0
    oee: float = 0.0
    energy_consumption: float = 0.0


class ProductionTrendResponse(ApiSchema):
    days: List[str]
    actual: List[float]
    target: List[float]


class QualityDistributionResponse(ApiSchema):
    grades: List[dict]


class OEEAnalysisResponse(ApiSchema):
    indicators: List[str]
    current_week: List[float]
    last_week: List[float]


class TemperatureTrendResponse(ApiSchema):
    zones: List[str]
    hours: List[str]
    data: List[List[float]]


class EnergyConsumptionResponse(ApiSchema):
    hours: List[str]
    electricity: List[float]
    gas: List[float]


class DowntimeAnalysisResponse(ApiSchema):
    reasons: List[str]
    duration: List[int]
    colors: List[str]


class OnlineCoilInfo(ApiSchema):
    id: str
    progress: int
    status: str


class ReadyCoilInfo(ApiSchema):
    id: str
    grade: str
    weight: float


class ProductionStatusResponse(ApiSchema):
    online_coil: OnlineCoilInfo
    ready_coil: ReadyCoilInfo
    current_speed: float
    furnace_temp: float


class RecentPlanItem(ApiSchema):
    coil_no: str
    grade: str
    weight: float
    status: str


class RecentPlansResponse(ApiSchema):
    plans: List[RecentPlanItem]
