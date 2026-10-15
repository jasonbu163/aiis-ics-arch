"""
文件路径: /backend/app/monitor/services/async_temperature.py
功能描述: Monitor 温度与过程曲线查询 Service
主要功能:
    - 查询指定日期的生产过程曲线
    - 普通查询不生成或写入样本
"""
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.crud import async_temperature as temperature_crud


async def get_curve_dashboard_data(
    db: AsyncSession,
    curve_type: str,
    date_str: str,
) -> Dict[str, Any]:
    """获取生产过程曲线数据。"""
    records = await temperature_crud.list_curves_by_date(db, date_str)
    if not records:
        return {"trends": [], "latest": {}}

    trends = []
    for record in records:
        trends.append(
            {
                "time": record.created_at.strftime("%H:%M:%S"),
                "lineSpeedSet": record.line_speed_set,
                "lineSpeedAct": record.line_speed_act,
                "z1TempSet": record.z1_temp_set,
                "z1TempAct": record.z1_temp_act,
                "z2TempSet": record.z2_temp_set,
                "z2TempAct": record.z2_temp_act,
                "z3TempSet": record.z3_temp_set,
                "z3TempAct": record.z3_temp_act,
                "z4TempSet": record.z4_temp_set,
                "z4TempAct": record.z4_temp_act,
                "z5TempSet": record.z5_temp_set,
                "z5TempAct": record.z5_temp_act,
                "z6TempSet": record.z6_temp_set,
                "z6TempAct": record.z6_temp_act,
                "uncTension": record.unc_act_tension_p,
                "recTension": record.rec_act_tension_p,
                "furnTension": record.furn_act_tension_kg,
                "h2Flow": record.h2_flow,
                "n2Flow": record.n2_flow,
                "oxygen": record.oxygen_content,
                "dewPoint": record.dew_point,
                "pressure": record.muffle_pressure,
            }
        )

    return {"trends": trends, "latest": trends[-1] if trends else {}}
