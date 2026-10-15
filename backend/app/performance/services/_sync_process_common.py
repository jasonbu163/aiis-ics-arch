"""
File Path: /backend/app/performance/services/_sync_process_common.py
Description: Shared host-neutral helpers for process-data Projection services.
Main Features:
    - Validates the fixed pilot PLC provenance contract
    - Resolves parent Performance rows from canonical coil observations
    - Normalizes process keys and optional numeric inputs without committing
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from math import isfinite
from typing import Protocol

from sqlalchemy.orm import Session

from app.performance.crud import _sync_process_common as sync_common_crud
from app.performance.domain import classify_coil_no
from app.performance.models.performance import Performance
from common.data_keys import PerformanceObservationStatus
from projection.provenance_contract import get_expected_device_id
from projection.registry import ProjectionHandlerGroupIdentity


PILOT_PLC_KEY = "PLC_1"
PILOT_DB_NUMBER = 28
PILOT_GROUP_NAME = "CD_HMI_Read_Data"
PROCESS_ALLOWED_GROUP_IDENTITIES = (
    ProjectionHandlerGroupIdentity(
        plc_key=PILOT_PLC_KEY,
        db_number=PILOT_DB_NUMBER,
        group_name=PILOT_GROUP_NAME,
    ),
)
NUMBER_PLC_TYPES = ("Real", "Int", "String")


class ProcessFact(Protocol):
    """Common fact attributes shared by the three process sync services."""

    plc_key: str
    device_id: int
    db_number: int
    group_name: str
    raw_snapshot_id: int
    collected_at: datetime
    quality: str
    coil_no_value: object


@dataclass(frozen=True)
class ProcessRecordSyncResult:
    """A stable, host-neutral result for one process-data fact."""

    action: str
    performance_id: int
    record_id: int | None = None


def validate_process_provenance(fact: ProcessFact) -> None:
    """Reject process facts outside the approved pilot PLC provenance."""
    if fact.plc_key != PILOT_PLC_KEY:
        raise ValueError(f"Unsupported PLC provenance: plc_key={fact.plc_key!r}")
    expected_device_id = get_expected_device_id(fact.plc_key)
    if (
        expected_device_id is None
        or type(fact.device_id) is not int
        or fact.device_id != expected_device_id
    ):
        raise ValueError(f"Unsupported PLC provenance: device_id={fact.device_id!r}")
    if type(fact.db_number) is not int or fact.db_number != PILOT_DB_NUMBER:
        raise ValueError(f"Unsupported PLC provenance: db_number={fact.db_number!r}")
    if fact.group_name != PILOT_GROUP_NAME:
        raise ValueError(f"Unsupported PLC provenance: group_name={fact.group_name!r}")
    if type(fact.raw_snapshot_id) is not int or fact.raw_snapshot_id <= 0:
        raise ValueError(f"raw_snapshot_id must be a positive integer: {fact.raw_snapshot_id!r}")
    if not isinstance(fact.collected_at, datetime):
        raise ValueError("collected_at must be a datetime")
    if not isinstance(fact.quality, str) or fact.quality.strip().lower() != "good":
        raise ValueError(f"Unsupported process fact quality: {fact.quality!r}")


def resolve_parent_performance(
    db: Session,
    fact: ProcessFact,
) -> Performance:
    """Resolve and lock the parent performance row for one process fact."""
    validate_process_provenance(fact)
    observation = classify_coil_no(fact.coil_no_value)
    if (
        observation.status is not PerformanceObservationStatus.IN_PRODUCTION
        or observation.coil_no is None
    ):
        raise ValueError("coil_no must identify an in-production parent Performance")
    performance = sync_common_crud.get_parent_by_device_and_coil_for_update(
        db,
        device_id=fact.device_id,
        coil_no=observation.coil_no,
    )
    if performance is None:
        raise ValueError(
            "parent Performance not found for "
            f"device_id={fact.device_id!r}, coil_no={observation.coil_no!r}"
        )
    return performance


def normalize_required_zone(value: object) -> str:
    """Normalize a required process zone key to a stable nonblank string."""
    if value is None or isinstance(value, bool):
        raise ValueError("zone is required")
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("zone is required")
        return text
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError(f"zone must be finite: {value!r}")
        return str(value.normalize())
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError(f"zone must be finite: {value!r}")
        return str(Decimal(str(value)).normalize())
    raise ValueError(f"zone has unsupported type: {type(value).__name__}")


def normalize_optional_decimal(value: object | None, *, input_key: str) -> Decimal | None:
    """Normalize an optional process numeric value, rejecting invalid values."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{input_key} must be numeric")
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        candidate = text
    else:
        candidate = value
    try:
        decimal_value = Decimal(str(candidate))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{input_key} must be numeric") from None
    if not decimal_value.is_finite():
        raise ValueError(f"{input_key} must be finite")
    return decimal_value


def normalize_record_time(value: object | None, *, collected_at: datetime) -> datetime:
    """Normalize an optional record_time, defaulting to the source collection time."""
    if value is None:
        return _normalize_datetime(collected_at, input_key="collected_at")
    if isinstance(value, str) and not value.strip():
        return _normalize_datetime(collected_at, input_key="collected_at")
    return _normalize_datetime(value, input_key="record_time")


def ensure_observed_measurement(values: dict[str, Decimal | None]) -> None:
    """Reject rows that contain only parent and process key metadata."""
    if not any(value is not None for value in values.values()):
        raise ValueError("at least one process measurement input is required")


def _normalize_datetime(value: object, *, input_key: str) -> datetime:
    if isinstance(value, bool):
        raise ValueError(f"{input_key} must be a datetime")
    if isinstance(value, datetime):
        return _to_naive_utc(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError(f"{input_key} must be a datetime")
        try:
            return _to_naive_utc(datetime.fromisoformat(text.replace("Z", "+00:00")))
        except ValueError:
            raise ValueError(f"{input_key} must be a datetime") from None
    raise ValueError(f"{input_key} must be a datetime")


def _to_naive_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)
