"""
文件路径: /backend/app/monitor/schemas/collector.py
功能描述: Monitor collector 状态响应 Schema
主要功能:
    - 定义 collector 健康与采集指标结构
"""
from typing import Optional

from common.schema_base import ApiSchema


class CollectorStatusOut(ApiSchema):
    collector_key: str
    status: str
    mode: Optional[str] = None
    device_id: Optional[int] = None
    target_interval_ms: Optional[int] = None
    last_heartbeat_at: Optional[str] = None
    last_sample_at: Optional[str] = None
    sample_count: int = 0
    failure_count: int = 0
    buffered_failure_count: int = 0
    last_collect_duration_ms: Optional[int] = None
    last_write_duration_ms: Optional[int] = None
    last_loop_delay_ms: Optional[int] = None
    last_error: Optional[str] = None
    stale: bool = True
