"""
File Path: /backend/app/performance/crud/sync_production_record.py
Description: Synchronous persistence helpers for PLC-observed production records.
Main Features:
    - Locks performance rows by the fixed device/coil business key
    - Lists active PLC observation rows for a device
    - Flushes changes without committing the caller transaction
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.performance.models.performance import Performance
from common.data_keys import PerformanceObservationStatus


ACTIVE_OBSERVATION_STATUSES = (
    PerformanceObservationStatus.IN_PRODUCTION.value,
    PerformanceObservationStatus.UNKNOWN.value,
)


def get_by_device_and_coil_for_update(
    db: Session,
    *,
    device_id: int,
    coil_no: str,
) -> Performance | None:
    """Lock one PLC-owned performance row by its stable business key."""
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


def list_active_for_device_for_update(
    db: Session,
    *,
    device_id: int,
) -> list[Performance]:
    """Lock the device's rows that can still be transitioned by a raw fact."""
    result = db.execute(
        select(Performance)
        .where(
            Performance.equipment_id.is_(None),
            Performance.device_id == device_id,
            Performance.observation_status.in_(ACTIVE_OBSERVATION_STATUSES),
        )
        .order_by(Performance.id)
        .with_for_update()
    )
    return list(result.scalars())


def get_latest_raw_snapshot_id_for_device(
    db: Session,
    *,
    device_id: int,
) -> int | None:
    """Return the latest accepted raw fact for device-level replay protection."""
    result = db.execute(
        select(func.max(Performance.last_raw_snapshot_id)).where(
            Performance.equipment_id.is_(None),
            Performance.device_id == device_id,
        )
    )
    return result.scalar_one()


def add_performance(db: Session, performance: Performance) -> None:
    """Stage a new record in the caller-owned transaction."""
    db.add(performance)


def flush(db: Session) -> None:
    """Expose generated identifiers without committing or rolling back."""
    db.flush()
