"""
文件路径: /backend/app/dashboard/models/__init__.py
功能描述: Dashboard 数据库模型导出
主要功能:
    - 导出每日生产统计模型
    - 导出质量、停机、生产状态和温度记录模型
"""
from app.dashboard.models.dashboard import (
    DailyProductionStats,
    DowntimeRecord,
    ProductionStatusRecord,
    QualityGradeStats,
    TemperatureZoneRecord,
)

__all__ = [
    "DailyProductionStats",
    "QualityGradeStats",
    "DowntimeRecord",
    "ProductionStatusRecord",
    "TemperatureZoneRecord",
]
