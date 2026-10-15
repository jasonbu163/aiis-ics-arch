"""
File Path: /backend/app/equipment/crud/sync_production_parameters.py
Description: Synchronous persistence helpers for equipment production-parameter Projection rows.
Main Features:
    - Locks production-parameter rows by coil number and timestamp
    - Stages inserts without committing caller-owned transactions
    - Flushes generated identifiers for host-neutral sync results
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.equipment.models.equipment import EquipmentProductionParameters


def get_by_business_key_for_update(
    db: Session,
    *,
    coil_no: str,
    timestamp: datetime,
) -> EquipmentProductionParameters | None:
    """Lock one production-parameter row by the r1 business idempotency key."""
    result = db.execute(
        select(EquipmentProductionParameters)
        .where(
            EquipmentProductionParameters.coil_no == coil_no,
            EquipmentProductionParameters.timestamp == timestamp,
        )
        .with_for_update()
    )
    return result.scalar_one_or_none()


def add_record(db: Session, record: EquipmentProductionParameters) -> None:
    """Stage a new equipment production-parameter row."""
    db.add(record)


def flush(db: Session) -> None:
    """Expose generated identifiers without committing or rolling back."""
    db.flush()
