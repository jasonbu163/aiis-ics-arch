"""
File Path: /backend/app/performance/crud/sync_process_temperature.py
Description: Synchronous persistence helpers for temperature process Projection records.
Main Features:
    - Locks temperature rows by performance, zone, and record_time
    - Stages inserts without committing caller-owned transactions
    - Flushes generated identifiers for host-neutral sync results
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.performance.models.performance import ProcessTemperature


def get_by_process_key_for_update(
    db: Session,
    *,
    performance_id: int,
    zone: str,
    record_time: datetime,
) -> ProcessTemperature | None:
    """Lock one temperature process row by the r1 idempotency key."""
    result = db.execute(
        select(ProcessTemperature)
        .where(
            ProcessTemperature.performance_id == performance_id,
            ProcessTemperature.zone == zone,
            ProcessTemperature.record_time == record_time,
        )
        .with_for_update()
    )
    return result.scalar_one_or_none()


def add_record(db: Session, record: ProcessTemperature) -> None:
    """Stage a new temperature process row."""
    db.add(record)


def flush(db: Session) -> None:
    """Expose generated identifiers without committing or rolling back."""
    db.flush()
