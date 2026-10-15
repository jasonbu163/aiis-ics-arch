"""
文件路径: /backend/app/equipment/services/async_equipment.py
功能描述: 设备模块异步业务服务
主要功能:
    - 编排设备看板数据查询
    - 组装前端设备看板响应结构
"""
from datetime import datetime, timedelta
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.equipment.models.equipment import EquipmentDrive, EquipmentProductionParameters, EquipmentTemperature
from app.equipment.crud.async_equipment import equipment_crud
from settings import settings


class EquipmentService:
    """设备看板业务编排层。"""

    async def get_drive_dashboard_data(self, db: AsyncSession) -> Dict[str, Any]:
        if settings.BACKEND_MOCK_ENABLED:
            await self.ensure_drive_sample_data(db)
        record = await equipment_crud.get_latest_drive(db)
        if not record:
            return {
                "process_params": {},
                "tension_params": {},
                "process_items": [],
                "tension_items": [],
            }

        process_items = [
            self.build_single_metric("tv", record.tv, "", 0),
            self.build_single_metric("km", record.km, "", 2),
            self.build_single_metric("oxygen", record.oxygen, "ppm", 0),
            self.build_single_metric("muffle_pressure", record.muffle_pressure, "Pa", 0),
            self.build_compare_metric("dew_point", record.dew_point_set, record.dew_point_actual, "℃", 2, 5),
            self.build_compare_metric("nh3_flow", record.nh3_flow_set, record.nh3_flow_actual, "m³/h", 2, 10),
            self.build_compare_metric("ng_flow", record.ng_flow_set, record.ng_flow_actual, "m³/h", 2, 10),
        ]

        tension_items = [
            self.build_compare_metric("uncoiler", record.uncoiler_set, record.uncoiler_actual, "kN", 2, 2),
            self.build_compare_metric("entry_looper", record.entry_looper_set, record.entry_looper_actual, "kN", 2, 2),
            self.build_compare_metric("furnace", record.furnace_set, record.furnace_actual, "kN", 2, 2),
            self.build_compare_metric("exit_looper", record.exit_looper_set, record.exit_looper_actual, "kN", 2, 2),
            self.build_compare_metric("recoiler", record.recoiler_set, record.recoiler_actual, "kN", 2, 2),
        ]

        return {
            "process_params": {
                "tv": record.tv,
                "km": record.km,
                "dew_point_set": record.dew_point_set,
                "dew_point_actual": record.dew_point_actual,
                "oxygen": record.oxygen,
                "muffle_pressure": record.muffle_pressure,
                "nh3_flow_set": record.nh3_flow_set,
                "nh3_flow_actual": record.nh3_flow_actual,
                "ng_flow_set": record.ng_flow_set,
                "ng_flow_actual": record.ng_flow_actual,
            },
            "tension_params": {
                "uncoiler_set": record.uncoiler_set,
                "uncoiler_actual": record.uncoiler_actual,
                "entry_looper_set": record.entry_looper_set,
                "entry_looper_actual": record.entry_looper_actual,
                "furnace_set": record.furnace_set,
                "furnace_actual": record.furnace_actual,
                "exit_looper_set": record.exit_looper_set,
                "exit_looper_actual": record.exit_looper_actual,
                "recoiler_set": record.recoiler_set,
                "recoiler_actual": record.recoiler_actual,
            },
            "process_items": process_items,
            "tension_items": tension_items,
        }

    def build_single_metric(self, metric_id: str, value: float, unit: str, decimals: int) -> Dict[str, Any]:
        return {
            "id": metric_id,
            "kind": "single",
            "value": value,
            "unit": unit,
            "decimals": decimals,
        }

    def build_compare_metric(
        self,
        metric_id: str,
        set_value: float,
        actual_value: float,
        unit: str,
        decimals: int,
        tolerance: float,
    ) -> Dict[str, Any]:
        deviation = actual_value - set_value
        return {
            "id": metric_id,
            "kind": "compare",
            "set": set_value,
            "actual": actual_value,
            "deviation": deviation,
            "status": self.resolve_metric_status(deviation, tolerance),
            "unit": unit,
            "decimals": decimals,
        }

    def resolve_metric_status(self, deviation: float, tolerance: float) -> str:
        diff = abs(deviation)
        if diff <= tolerance:
            return "normal"
        if diff <= tolerance * 2:
            return "warning"
        return "danger"

    async def get_temperature_control_dashboard_data(self, db: AsyncSession, limit: int = 10) -> Dict[str, Any]:
        if settings.BACKEND_MOCK_ENABLED:
            await self.ensure_temperature_sample_data(db)
        records = await equipment_crud.get_temperature_history(db, limit)
        if not records:
            return {"heating_zones": [], "temperature_history": []}

        latest = records[0]
        heating_zones = [
            {"set_temp": latest.zone1_set, "actual_temp": latest.zone1_act},
            {"set_temp": latest.zone2_set, "actual_temp": latest.zone2_act},
            {"set_temp": latest.zone3_set, "actual_temp": latest.zone3_act},
            {"set_temp": latest.zone4_set, "actual_temp": latest.zone4_act},
            {"set_temp": latest.zone5_set, "actual_temp": latest.zone5_act},
        ]

        temperature_history = []
        for record in reversed(records):
            temperature_history.append({
                "time": record.timestamp.strftime("%H:%M:%S") if record.timestamp else "",
                "zone1": record.zone1_act,
                "zone2": record.zone2_act,
                "zone3": record.zone3_act,
                "zone4": record.zone4_act,
                "zone5": record.zone5_act,
            })

        return {
            "heating_zones": heating_zones,
            "temperature_history": temperature_history,
        }

    async def get_production_parameters_dashboard_data(self, db: AsyncSession) -> Dict[str, Any]:
        if settings.BACKEND_MOCK_ENABLED:
            await self.ensure_production_parameters_sample_data(db)
        record = await equipment_crud.get_latest_production_parameters(db)
        if not record:
            return {"production_parameters": {}, "process_steps": []}

        production_parameters = {
            "coil_no": record.coil_no,
            "grade": record.grade,
            "status": "producing",
            "last_update": record.timestamp.strftime("%Y-%m-%d %H:%M:%S") if record.timestamp else "",
            "thickness": record.thickness,
            "width": record.width,
            "entry_time": record.entry_time.strftime("%Y-%m-%d %H:%M:%S") if record.entry_time else "",
            "total_time": record.total_time,
            "weight": record.weight,
            "speed": record.speed,
        }

        return {
            "production_parameters": production_parameters,
            "process_steps": record.process_steps or [],
        }

    async def ensure_production_parameters_sample_data(self, db: AsyncSession) -> None:
        """生产参数表无数据时，生成一条后端测试数据。"""
        record = await equipment_crud.get_latest_production_parameters(db)
        if record:
            return

        now = datetime.now()
        db.add(EquipmentProductionParameters(
            coil_no="COIL000001",
            grade="TA1",
            thickness=2.5,
            width=1000,
            entry_time=now - timedelta(minutes=126),
            total_time=126,
            weight=15.8,
            speed=12.4,
            process_steps=[
                {"step": "uncoiling", "status": "completed", "start_time": "08:30:00", "end_time": "08:35:00", "duration": 5, "temperature": "-", "remark": ""},
                {"step": "heating1", "status": "completed", "start_time": "08:35:00", "end_time": "09:05:00", "duration": 30, "temperature": "825", "remark": ""},
                {"step": "heating2", "status": "completed", "start_time": "09:05:00", "end_time": "09:35:00", "duration": 30, "temperature": "875", "remark": ""},
                {"step": "soaking", "status": "processing", "start_time": "09:35:00", "end_time": "-", "duration": "-", "temperature": "910", "remark": ""},
                {"step": "cooling1", "status": "pending", "start_time": "-", "end_time": "-", "duration": "-", "temperature": "-", "remark": ""},
                {"step": "cooling2", "status": "pending", "start_time": "-", "end_time": "-", "duration": "-", "temperature": "-", "remark": ""},
                {"step": "recoiling", "status": "pending", "start_time": "-", "end_time": "-", "duration": "-", "temperature": "-", "remark": ""},
            ],
        ))
        await db.commit()

    async def ensure_drive_sample_data(self, db: AsyncSession) -> None:
        """传动参数表无数据时，生成一组后端测试数据。"""
        record = await equipment_crud.get_latest_drive(db)
        if record:
            return

        now = datetime.now()
        for index in range(6):
            wave = index - 2
            db.add(EquipmentDrive(
                timestamp=now - timedelta(seconds=(5 - index) * 30),
                tv=1250 + wave * 4,
                km=0.85 + wave * 0.01,
                dew_point_set=-45,
                dew_point_actual=-45 + wave * 0.65,
                oxygen=8 + (index % 2),
                muffle_pressure=150 + wave * 2,
                nh3_flow_set=50,
                nh3_flow_actual=50 + wave * 0.25,
                ng_flow_set=120,
                ng_flow_actual=120 + wave * 0.27,
                uncoiler_set=15,
                uncoiler_actual=15 + wave * 0.15,
                entry_looper_set=12,
                entry_looper_actual=12 - wave * 0.1,
                furnace_set=10,
                furnace_actual=10 + wave * 0.08,
                exit_looper_set=12,
                exit_looper_actual=12 + wave * 0.12,
                recoiler_set=18,
                recoiler_actual=18 + wave * 0.09,
            ))
        await db.commit()

    async def ensure_temperature_sample_data(self, db: AsyncSession) -> None:
        """温控参数表无数据时，生成一组后端测试数据。"""
        records = await equipment_crud.get_temperature_history(db, 1)
        if records:
            return

        now = datetime.now()
        set_values = [820, 860, 900, 920, 880]
        for index in range(12):
            wave = index % 5
            values = {
                f"zone{zone_index}_set": set_value
                for zone_index, set_value in enumerate(set_values, start=1)
            }
            for zone_index, set_value in enumerate(set_values, start=1):
                offset = ((wave + zone_index) % 5) - 2
                values[f"zone{zone_index}_act"] = set_value + offset * 2.5

            db.add(EquipmentTemperature(
                timestamp=now - timedelta(minutes=(11 - index) * 5),
                **values,
            ))

        await db.commit()


equipment_service = EquipmentService()
