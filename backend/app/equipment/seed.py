import asyncio
from datetime import datetime, timedelta
import random

from database import async_session_maker
from app.equipment.models.equipment import EquipmentDrive, EquipmentProductionParameters, EquipmentTemperature

async def seed_equipment_data():
    async with async_session_maker() as db:
        # Create a single EquipmentDrive record
        drive = EquipmentDrive(
            tv=1250, km=0.85,
            dew_point_set=-45, dew_point_actual=round(-45 + random.uniform(-2, 2), 1),
            oxygen=8, muffle_pressure=150,
            nh3_flow_set=50, nh3_flow_actual=round(50 + random.uniform(-1, 1), 2),
            ng_flow_set=120, ng_flow_actual=round(120 + random.uniform(-2, 2), 2),
            
            uncoiler_set=15.0, uncoiler_actual=round(15.0 + random.uniform(-0.5, 0.5), 2),
            entry_looper_set=12.0, entry_looper_actual=round(12.0 + random.uniform(-0.5, 0.5), 2),
            furnace_set=10.0, furnace_actual=round(10.0 + random.uniform(-0.5, 0.5), 2),
            exit_looper_set=12.0, exit_looper_actual=round(12.0 + random.uniform(-0.5, 0.5), 2),
            recoiler_set=18.0, recoiler_actual=round(18.0 + random.uniform(-0.5, 0.5), 2)
        )
        db.add(drive)
        
        # Create multiple EquipmentTemperature records (e.g. 10 history points)
        base_temps = [800, 850, 900, 880, 820]
        now = datetime.now()
        for i in range(10, -1, -1):
            t_time = now - timedelta(minutes=i)
            t_record = EquipmentTemperature(
                timestamp=t_time,
                zone1_set=base_temps[0], zone1_act=round(base_temps[0] + random.uniform(-15, 15), 1),
                zone2_set=base_temps[1], zone2_act=round(base_temps[1] + random.uniform(-15, 15), 1),
                zone3_set=base_temps[2], zone3_act=round(base_temps[2] + random.uniform(-15, 15), 1),
                zone4_set=base_temps[3], zone4_act=round(base_temps[3] + random.uniform(-15, 15), 1),
                zone5_set=base_temps[4], zone5_act=round(base_temps[4] + random.uniform(-15, 15), 1)
            )
            db.add(t_record)
            
        # Create a single EquipmentProductionParameters record
        production_parameters = EquipmentProductionParameters(
            coil_no="COIL000001",
            grade="TA1",
            thickness=2.5,
            width=1000,
            entry_time=now - timedelta(minutes=120),
            total_time=120,
            weight=15.8,
            speed=round(12.5 + random.uniform(-0.5, 0.5), 1),
            process_steps=[
                {"step": "uncoiling", "status": "completed", "start_time": "08:30:00", "end_time": "08:35:00", "duration": 5, "temperature": "-", "remark": ""},
                {"step": "heating1", "status": "completed", "start_time": "08:35:00", "end_time": "09:05:00", "duration": 30, "temperature": "825", "remark": ""},
                {"step": "heating2", "status": "completed", "start_time": "09:05:00", "end_time": "09:35:00", "duration": 30, "temperature": "875", "remark": ""},
                {"step": "soaking", "status": "processing", "start_time": "09:35:00", "end_time": "-", "duration": "-", "temperature": "910", "remark": ""},
                {"step": "cooling1", "status": "pending", "start_time": "-", "end_time": "-", "duration": "-", "temperature": "-", "remark": ""},
                {"step": "cooling2", "status": "pending", "start_time": "-", "end_time": "-", "duration": "-", "temperature": "-", "remark": ""},
                {"step": "recoiling", "status": "pending", "start_time": "-", "end_time": "-", "duration": "-", "temperature": "-", "remark": ""}
            ]
        )
        db.add(production_parameters)
        
        await db.commit()

if __name__ == "__main__":
    asyncio.run(seed_equipment_data())
    print("Seeding completed.")
