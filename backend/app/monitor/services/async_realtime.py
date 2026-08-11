"""
文件路径: /backend/app/monitor/services/async_realtime.py
功能描述: Monitor Core latest 现场事实查询 Service

该 Service 只合并 raw/latest 事实元数据和 payload，不解释项目业务语义。
"""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.monitor.crud import async_realtime as realtime_crud
from app.monitor.services._shared import is_stale, iso_datetime


async def get_realtime_latest_data(db: AsyncSession, device_id: int = 1) -> dict[str, Any]:
    """返回一个设备的 latest field facts，保持项目无关的结构。"""
    snapshots = await realtime_crud.list_latest_snapshots(db, device_id)
    rows = [
        {
            "plcKey": snapshot.plc_key,
            "deviceId": snapshot.device_id,
            "dbNumber": snapshot.db_number,
            "groupName": snapshot.group_name,
            "contractVersion": snapshot.contract_version,
            "collectedAt": iso_datetime(snapshot.collected_at),
            "driver": snapshot.driver,
            "quality": snapshot.quality,
            "readDurationMs": snapshot.read_duration_ms,
            "rawSnapshotId": snapshot.raw_snapshot_id,
            "decodedPayload": snapshot.decoded_payload or {},
            "unsupportedPayload": snapshot.unsupported_payload,
            "errorMessage": snapshot.error_message,
            "updatedAt": iso_datetime(snapshot.updated_at),
        }
        for snapshot in snapshots
    ]
    freshness_watermark = min(
        (snapshot.collected_at for snapshot in snapshots),
        default=None,
    )
    contract_versions = {snapshot.contract_version for snapshot in snapshots}
    return {
        "deviceId": device_id,
        "hasSnapshot": bool(rows),
        "updatedAt": iso_datetime(freshness_watermark),
        "stale": is_stale(freshness_watermark) or len(contract_versions) > 1,
        "snapshots": rows,
    }
