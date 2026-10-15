"""
File Path: /backend/app/equipment/crud/sync_drive.py
Description: Synchronous persistence helpers for equipment drive Projection rows.
Main Features:
    - Locks drive rows by timestamp for r1 replay idempotency
    - Stages inserts without committing caller-owned transactions
    - Flushes generated identifiers for host-neutral sync results
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.equipment.models.equipment import EquipmentDrive


def get_by_timestamp_for_update(db: Session, *, timestamp: datetime) -> EquipmentDrive | None:
    """Lock one drive row by the r1 timestamp idempotency key."""
    result = db.execute(
        select(EquipmentDrive)
        .where(EquipmentDrive.timestamp == timestamp)
        .with_for_update()
    )
    return result.scalar_one_or_none()


def add_record(db: Session, record: EquipmentDrive) -> None:
    """Stage a new equipment drive row."""
    db.add(record)


def flush(db: Session) -> None:
    """Expose generated identifiers without committing or rolling back."""
    db.flush()
