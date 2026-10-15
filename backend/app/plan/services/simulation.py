"""
文件路径: /backend/app/plan/simulation.py
功能描述: 仿真数据生成服务
主要功能:
    - 为设备提供模拟参数与质量实绩脱离业务主流程的硬编码耦合
"""
import random
from typing import Dict, Any

class SimulationDataService:
    """模拟数据生成服务，预留后续真实 PLC 接口等效替换能力"""
    
    @staticmethod
    def generate_performance_data(plan_weight: float) -> Dict[str, Any]:
        """生成生产实绩随机数据"""
        yield_weight = float(plan_weight) * random.uniform(0.95, 0.99)
        return {
            "yield_weight": yield_weight,
            "defect_weight": float(plan_weight) - yield_weight,
            "energy_consumed": random.uniform(100.0, 500.0),
            "quality_grade": random.choices(["A", "B", "C"], weights=[0.8, 0.15, 0.05])[0]
        }
        
    @staticmethod
    def generate_temperature_data(plan_id: int) -> list:
        """生成模拟温度过程数据"""
        return [
            {
                "plan_id": plan_id,
                "zone_name": f"H{i}",
                "pv_val": random.uniform(850.0, 950.0),
                "sv_val": 900.0,
                "status": "normal"
            }
            for i in range(1, 4)
        ]
