"""
文件路径: /backend/app/monitor/services/collector/async_query.py
功能描述: Monitor collector 状态查询
主要功能:
    - 读取 collector 状态与采集指标
    - 计算 collector stale 状态
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.crud import async_collector as collector_crud
from app.monitor.services._shared import is_stale, iso_datetime


async def get_collector_status_data(
    db: AsyncSession,
    collector_key: str = "control-agent-plc",
) -> dict[str, Any]:
    """读取 collector 运行状态，供前端判断采集链路是否健康。"""
    state = await collector_crud.get_state_async(db, collector_key)
    if not state:
        return {
            "collectorKey": collector_key,
            "status": "stopped",
            "mode": None,
            "deviceId": None,
            "targetIntervalMs": None,
            "lastHeartbeatAt": None,
            "lastSampleAt": None,
            "sampleCount": 0,
            "failureCount": 0,
            "lastError": None,
            "stale": True,
        }

    heartbeat_at = state.last_heartbeat_at or state.started_at
    return {
        "collectorKey": state.collector_key,
        "status": state.status,
        "mode": state.mode,
        "deviceId": state.device_id,
        "targetIntervalMs": state.target_interval_ms,
        "lastHeartbeatAt": iso_datetime(state.last_heartbeat_at),
        "lastSampleAt": iso_datetime(state.last_sample_at),
        "sampleCount": state.sample_count,
        "failureCount": state.failure_count,
        "bufferedFailureCount": state.buffered_failure_count,
        "lastCollectDurationMs": state.last_collect_duration_ms,
        "lastWriteDurationMs": state.last_write_duration_ms,
        "lastLoopDelayMs": state.last_loop_delay_ms,
        "lastError": state.last_error,
        "stale": is_stale(
            heartbeat_at,
            stale_seconds=max((state.target_interval_ms or 1000) // 1000 * 5, 10),
        ),
    }
