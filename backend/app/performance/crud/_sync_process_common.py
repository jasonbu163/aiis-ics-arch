"""
File Path: /backend/app/performance/crud/_sync_process_common.py
Description: Shared synchronous persistence helpers for process-data Projection handlers.
Main Features:
    - Locks the parent PLC-owned performance row by device and coil
    - Keeps process handler parent lookup out of HTTP and async paths
    - Leaves transaction commit and rollback to the Projection host
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.performance.models.performance import Performance


def get_parent_by_device_and_coil_for_update(
    db: Session,
    *,
    device_id: int,
    coil_no: str,
) -> Performance | None:
    """Lock the parent performance row for a process-data fact."""
    result = db.execute(
        select(Performance)
        .where(
            Performance.equipment_id.is_(None),
            Performance.device_id == device_id,
            Performance.coil_no == coil_no,
        )
        .with_for_update()
    )
    return result.scalar_one_or_none()
