"""
文件路径: /backend/app/monitor/services/collector/__init__.py
功能描述: Control Agent collector 状态查询入口
主要功能:
    - 导出 collector 状态查询 Service
    - 不承载 PLC 采集、重放或投影编排
"""
from app.monitor.services.collector.async_query import get_collector_status_data


__all__ = ["get_collector_status_data"]
