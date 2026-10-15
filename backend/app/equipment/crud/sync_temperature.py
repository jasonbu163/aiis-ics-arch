"""
File Path: /backend/app/equipment/crud/sync_temperature.py
Description: Synchronous persistence helpers for equipment temperature Projection rows.
Main Features:
    - Locks temperature rows by timestamp for r1 replay idempotency
    - Stages inserts without committing caller-owned transactions
    - Flushes generated identifiers for host-neutral sync results
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.equipment.models.equipment import EquipmentTemperature


def get_by_timestamp_for_update(db: Session, *, timestamp: datetime) -> EquipmentTemperature | None:
    """Lock one equipment temperature row by the r1 timestamp idempotency key."""
    result = db.execute(
        select(EquipmentTemperature)
        .where(EquipmentTemperature.timestamp == timestamp)
        .with_for_update()
    )
    return result.scalar_one_or_none()


def add_record(db: Session, record: EquipmentTemperature) -> None:
    """Stage a new equipment temperature row."""
    db.add(record)


def flush(db: Session) -> None:
    """Expose generated identifiers without committing or rolling back."""
    db.flush()
