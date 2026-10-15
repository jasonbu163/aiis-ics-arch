"""
File Path: /backend/app/performance/crud/sync_process_tension.py
Description: Synchronous persistence helpers for tension process Projection records.
Main Features:
    - Locks tension rows by performance, zone, and record_time
    - Stages inserts without committing caller-owned transactions
    - Flushes generated identifiers for host-neutral sync results
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.performance.models.performance import ProcessTension


def get_by_process_key_for_update(
    db: Session,
    *,
    performance_id: int,
    zone: str,
    record_time: datetime,
) -> ProcessTension | None:
    """Lock one tension process row by the r1 idempotency key."""
    result = db.execute(
        select(ProcessTension)
        .where(
            ProcessTension.performance_id == performance_id,
            ProcessTension.zone == zone,
            ProcessTension.record_time == record_time,
        )
        .with_for_update()
    )
    return result.scalar_one_or_none()


def add_record(db: Session, record: ProcessTension) -> None:
    """Stage a new tension process row."""
    db.add(record)


def flush(db: Session) -> None:
    """Expose generated identifiers without committing or rolling back."""
    db.flush()
