"""
文件路径: /backend/app/dashboard/services/async_dashboard.py
功能描述: Dashboard 异步业务服务
主要功能:
    - 编排看板统计、趋势、分布和状态查询
    - 统一处理后端业务 mock 开关和数据库数据组装
    - 为 API 层提供可直接包装的字典数据
"""
import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.dashboard.mocks import dashboard as dashboard_mock
from app.dashboard.crud.async_dashboard import DashboardCRUD
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
    TemperatureTrendResponse,
)
from settings import settings


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


class DashboardService:
    """Dashboard 业务编排层。"""

    @staticmethod
    def crud(db: AsyncSession) -> DashboardCRUD:
        return DashboardCRUD(db)

    async def get_dashboard_stats(self, db: AsyncSession) -> dict:
        if settings.BACKEND_MOCK_ENABLED:
            return dashboard_mock.get_stats().model_dump()

        today = datetime.date.today()

        crud = self.crud(db)
        today_stats = await crud.get_daily_stats_by_date(today)
        pending_plans = await crud.count_pending_plans()

        if today_stats:
            return DashboardStatsResponse(
                today_production=float(today_stats.production_weight or 0),
                pending_plans=pending_plans,
                completed_coils=today_stats.completed_coils or 0,
                oee=float(today_stats.oee_rate or 0),
                energy_consumption=float(today_stats.energy_electricity or 0),
            ).model_dump()

        return DashboardStatsResponse(
            today_production=0,
            pending_plans=pending_plans,
            completed_coils=0,
            oee=0,
            energy_consumption=0,
        ).model_dump()

    async def get_production_trend(self, db: AsyncSession) -> dict:
        if settings.BACKEND_MOCK_ENABLED:
            return dashboard_mock.get_production_trend().model_dump()

        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=6)

        stats_list = await self.crud(db).list_daily_stats_from(start_date)
        stats_dict = {s.stats_date: s for s in stats_list}

        days = []
        actual = []
        target = []

        for i in range(7):
            current_date = start_date + datetime.timedelta(days=i)
            days.append(WEEKDAY_KEYS[current_date.weekday()])

            if current_date in stats_dict:
                stats = stats_dict[current_date]
                actual.append(float(stats.production_weight or 0))
                target.append(float(stats.target_weight or 120))
            else:
                actual.append(0)
                target.append(120)

        return ProductionTrendResponse(days=days, actual=actual, target=target).model_dump()

    async def get_quality_distribution(self, db: AsyncSession) -> dict:
        if settings.BACKEND_MOCK_ENABLED:
            return dashboard_mock.get_quality_distribution().model_dump()

        today = datetime.date.today()

        grade_stats = await self.crud(db).list_quality_grade_stats(today)

        grade_key_map = {
            "优等品": "excellent",
            "一等品": "firstClass",
            "合格品": "qualified",
            "待复检": "pending",
        }

        if grade_stats:
            grades = [
                {
                    "value": g.grade_count,
                    "name": grade_key_map.get(g.grade_name, g.grade_name),
                    "itemStyle": {"color": g.grade_color},
                }
                for g in grade_stats
            ]
        else:
            grades = [
                {"value": 0, "name": "excellent", "itemStyle": {"color": QUALITY_GRADE_KEYS["excellent"]}},
                {"value": 0, "name": "firstClass", "itemStyle": {"color": QUALITY_GRADE_KEYS["firstClass"]}},
                {"value": 0, "name": "qualified", "itemStyle": {"color": QUALITY_GRADE_KEYS["qualified"]}},
                {"value": 0, "name": "pending", "itemStyle": {"color": QUALITY_GRADE_KEYS["pending"]}},
            ]

        return QualityDistributionResponse(grades=grades).model_dump()

    async def get_oee_analysis(self, db: AsyncSession) -> dict:
        if settings.BACKEND_MOCK_ENABLED:
            return dashboard_mock.get_oee_analysis().model_dump()

        today = datetime.date.today()
        week_start = today - datetime.timedelta(days=today.weekday())
        last_week_start = week_start - datetime.timedelta(days=7)

        crud = self.crud(db)
        current_week_stats = await crud.list_daily_stats_from(week_start)
        last_week_stats = await crud.list_daily_stats_between(last_week_start, week_start)

        def calc_avg(stats_list, field_name):
            if not stats_list:
                return 0
            values = [getattr(s, field_name, 0) or 0 for s in stats_list]
            return round(sum(values) / len(values), 1) if values else 0

        current_week = [
            calc_avg(current_week_stats, "availability_rate"),
            calc_avg(current_week_stats, "performance_rate"),
            calc_avg(current_week_stats, "quality_rate"),
            0,
            0,
        ]

        last_week = [
            calc_avg(last_week_stats, "availability_rate"),
            calc_avg(last_week_stats, "performance_rate"),
            calc_avg(last_week_stats, "quality_rate"),
            0,
            0,
        ]

        return OEEAnalysisResponse(
            indicators=OEE_INDICATOR_KEYS,
            current_week=current_week,
            last_week=last_week,
        ).model_dump()

    async def get_temperature_trend(self, db: AsyncSession) -> dict:
        if settings.BACKEND_MOCK_ENABLED:
            return dashboard_mock.get_temperature_trend().model_dump()

        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        records = await self.crud(db).list_temperature_records_from(today)

        zone_key_map = {
            "加热区1": "rtf1",
            "加热区2": "rtf2",
            "加热区3": "rtf3",
            "均热区": "sf",
            "冷却区1": "cf1",
            "冷却区2": "cf2",
        }

        zones = FURNACE_ZONE_KEYS
        hours = [f"{i}:00" for i in range(24)]
        zone_data_map = {zone: [None] * 24 for zone in zones}

        for record in records:
            hour = record.record_time.hour
            zone_key = zone_key_map.get(record.zone_name, record.zone_name)
            if zone_key in zone_data_map:
                zone_data_map[zone_key][hour] = float(record.temperature or 0)

        data = []
        for zone in zones:
            zone_data = []
            for h in range(24):
                if zone_data_map[zone][h] is not None:
                    zone_data.append(zone_data_map[zone][h])
                else:
                    zone_data.append(0)
            data.append(zone_data)

        return TemperatureTrendResponse(zones=zones, hours=hours, data=data).model_dump()

    async def get_energy_consumption(self, db: AsyncSession) -> dict:
        if settings.BACKEND_MOCK_ENABLED:
            return dashboard_mock.get_energy_consumption().model_dump()

        today = datetime.date.today()

        stats_list = await self.crud(db).list_daily_stats_from(today - datetime.timedelta(days=1))
        hours = [f"{i}:00" for i in range(24)]

        if stats_list:
            total_electricity = float(stats_list[0].energy_electricity or 0)
            total_gas = float(stats_list[0].energy_gas or 0)
            electricity = [round(total_electricity / 24, 2)] * 24
            gas = [round(total_gas / 24, 2)] * 24
        else:
            electricity = [0] * 24
            gas = [0] * 24

        return EnergyConsumptionResponse(hours=hours, electricity=electricity, gas=gas).model_dump()

    async def get_downtime_analysis(self, db: AsyncSession) -> dict:
        if settings.BACKEND_MOCK_ENABLED:
            return dashboard_mock.get_downtime_analysis().model_dump()

        today = datetime.date.today()

        records = await self.crud(db).list_downtime_records(today)

        reason_key_map = {
            "计划停机": "scheduled",
            "换卷时间": "coilChange",
            "设备故障": "equipment",
            "原料不足": "material",
            "其他": "other",
        }

        if records:
            reasons = [reason_key_map.get(r.reason, r.reason) for r in records]
            duration = [r.duration_minutes for r in records]
            colors = [r.color for r in records]
        else:
            reasons = DOWNTIME_REASON_KEYS
            duration = [0, 0, 0, 0, 0]
            colors = [DOWNTIME_COLORS[key] for key in DOWNTIME_REASON_KEYS]

        return DowntimeAnalysisResponse(reasons=reasons, duration=duration, colors=colors).model_dump()

    async def get_production_status(self, db: AsyncSession) -> dict:
        if settings.BACKEND_MOCK_ENABLED:
            return dashboard_mock.get_production_status().model_dump()

        latest_record = await self.crud(db).get_latest_production_status()

        status_key_map = {
            "生产中": "producing",
            "待机": "standby",
            "停机": "stopped",
        }

        if latest_record:
            status = ProductionStatusResponse(
                online_coil=OnlineCoilInfo(
                    id=latest_record.online_coil_id or "",
                    progress=latest_record.online_coil_progress or 0,
                    status=status_key_map.get(latest_record.online_coil_status, latest_record.online_coil_status),
                ),
                ready_coil=ReadyCoilInfo(
                    id=latest_record.ready_coil_id or "",
                    grade=latest_record.ready_coil_grade or "",
                    weight=float(latest_record.ready_coil_weight or 0),
                ),
                current_speed=float(latest_record.current_speed or 0),
                furnace_temp=float(latest_record.furnace_temp or 0),
            )
        else:
            status = ProductionStatusResponse(
                online_coil=OnlineCoilInfo(id="", progress=0, status=""),
                ready_coil=ReadyCoilInfo(id="", grade="", weight=0),
                current_speed=0,
                furnace_temp=0,
            )

        return status.model_dump()

    async def get_recent_plans(self, db: AsyncSession) -> dict:
        plans = await self.crud(db).list_recent_plans(limit=5)

        plan_items = [
            RecentPlanItem(
                coil_no=plan.coil_no,
                grade=plan.grade,
                weight=float(plan.weight),
                status=plan.status,
            )
            for plan in plans
        ]
        return {"plans": [p.model_dump() for p in plan_items]}


dashboard_service = DashboardService()
