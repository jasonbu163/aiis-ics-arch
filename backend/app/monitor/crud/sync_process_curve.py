"""
File Path: /backend/app/monitor/crud/sync_process_curve.py
Description: Synchronous persistence helpers for Monitor process curve Projection.
Main Features:
    - Appends process curve rows without committing transactions
    - Keeps ORM writes out of the monitor owner sync service
    - Flushes caller-owned transactions for deterministic record ids
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.monitor.models.business_history import HistoryProcessCurve


def add_process_curve(
    db: Session,
    *,
    device_id: int,
    coil_number: str | None,
    created_at: datetime,
    values: Mapping[str, Any],
) -> HistoryProcessCurve:
    """Add one process curve row to the caller-owned transaction."""
    record = HistoryProcessCurve(
        device_id=device_id,
        coil_number=coil_number,
        created_at=created_at,
        **dict(values),
    )
    db.add(record)
    return record


def flush(db: Session) -> None:
    """Flush pending writes without committing the caller-owned transaction."""
    db.flush()
