"""
文件路径: /backend/app/dashboard/mocks/dashboard.py
功能描述: Dashboard 后端业务 mock provider
主要功能:
    - 提供 BACKEND_MOCK_ENABLED=true 时使用的 dashboard 诊断响应
    - 与真实 Service 查询路径分离
"""
import random

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
    TemperatureTrendResponse,
)


WEEKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
QUALITY_GRADE_KEYS = {
    "excellent": "#52c41a",
    "firstClass": "#1890ff",
    "qualified": "#faad14",
    "pending": "#ff4d4f",
}
OEE_INDICATOR_KEYS = ["availability", "performance", "quality", "equipmentStability", "planAchievement"]
FURNACE_ZONE_KEYS = ["rtf1", "rtf2", "rtf3", "sf", "cf1", "cf2"]
DOWNTIME_REASON_KEYS = ["scheduled", "coilChange", "equipment", "material", "other"]
DOWNTIME_COLORS = {
    "scheduled": "#1890ff",
    "coilChange": "#52c41a",
    "equipment": "#ff4d4f",
    "material": "#faad14",
    "other": "#722ed1",
}


def get_stats() -> DashboardStatsResponse:
    return DashboardStatsResponse(
        today_production=125.8,
        pending_plans=8,
        completed_coils=12,
        oee=85.6,
        energy_consumption=15280,
    )


def get_production_trend() -> ProductionTrendResponse:
    return ProductionTrendResponse(
        days=WEEKDAY_KEYS,
        actual=[125, 132, 118, 145, 138, 142, 135],
        target=[120, 120, 120, 120, 120, 120, 120],
    )


def get_quality_distribution() -> QualityDistributionResponse:
    return QualityDistributionResponse(
        grades=[
            {"value": 85, "name": "excellent", "itemStyle": {"color": QUALITY_GRADE_KEYS["excellent"]}},
            {"value": 32, "name": "firstClass", "itemStyle": {"color": QUALITY_GRADE_KEYS["firstClass"]}},
            {"value": 8, "name": "qualified", "itemStyle": {"color": QUALITY_GRADE_KEYS["qualified"]}},
            {"value": 2, "name": "pending", "itemStyle": {"color": QUALITY_GRADE_KEYS["pending"]}},
        ]
    )


def get_oee_analysis() -> OEEAnalysisResponse:
    return OEEAnalysisResponse(
        indicators=OEE_INDICATOR_KEYS,
        current_week=[92.5, 95.2, 97.3, 88.6, 91.2],
        last_week=[88.3, 92.8, 95.6, 85.4, 87.8],
    )


def get_temperature_trend() -> TemperatureTrendResponse:
    hours = [f"{i}:00" for i in range(24)]
    data = []
    for i, _zone in enumerate(FURNACE_ZONE_KEYS):
        base_temp = 900 if i < 4 else 300
        data.append([base_temp + random.randint(-20, 20) for _ in range(24)])
    return TemperatureTrendResponse(zones=FURNACE_ZONE_KEYS, hours=hours, data=data)


def get_energy_consumption() -> EnergyConsumptionResponse:
    hours = [f"{i}:00" for i in range(24)]
    electricity = [random.randint(400, 700) for _ in range(24)]
    gas = [random.randint(80, 130) for _ in range(24)]
    return EnergyConsumptionResponse(hours=hours, electricity=electricity, gas=gas)


def get_downtime_analysis() -> DowntimeAnalysisResponse:
    return DowntimeAnalysisResponse(
        reasons=DOWNTIME_REASON_KEYS,
        duration=[45, 38, 25, 18, 12],
        colors=[DOWNTIME_COLORS[key] for key in DOWNTIME_REASON_KEYS],
    )


def get_production_status() -> ProductionStatusResponse:
    return ProductionStatusResponse(
        online_coil=OnlineCoilInfo(id="COIL000001", progress=75, status="producing"),
        ready_coil=ReadyCoilInfo(id="COIL000002", grade="TA1", weight=15.2),
        current_speed=12.5,
        furnace_temp=910,
    )
