"""
File Path: /backend/app/equipment/services/_sync_common.py
Description: Shared helpers for Equipment Projection synchronization services.
Main Features:
    - Validates the fixed pilot PLC provenance contract
    - Normalizes Projection input values for equipment target tables
    - Provides stable caller-owned transaction result types
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from math import isfinite
from typing import Protocol

from projection.provenance_contract import get_expected_device_id
from projection.registry import ProjectionHandlerGroupIdentity


PILOT_PLC_KEY = "PLC_1"
PILOT_DB_NUMBER = 28
PILOT_GROUP_NAME = "CD_HMI_Read_Data"
RAW_QUALITY_GOOD = "good"
NUMBER_PLC_TYPES = ("Real", "Int", "String")

PROCESS_ALLOWED_GROUP_IDENTITIES = (
    ProjectionHandlerGroupIdentity(
        plc_key=PILOT_PLC_KEY,
        db_number=PILOT_DB_NUMBER,
        group_name=PILOT_GROUP_NAME,
    ),
)


class EquipmentFact(Protocol):
    """Common provenance carried by Equipment Projection facts."""

    plc_key: str
    device_id: int
    db_number: int
    group_name: str
    raw_snapshot_id: int
    collected_at: datetime
    quality: str


@dataclass(frozen=True)
class EquipmentSyncResult:
    """A stable, host-neutral result for one equipment sync invocation."""

    action: str
    record_id: int | None = None
    skipped_reason: str | None = None


def validate_equipment_provenance(fact: EquipmentFact) -> None:
    """Reject facts outside the approved pilot PLC provenance."""
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
    if not isinstance(fact.quality, str):
        raise ValueError("quality must be a string")


def is_good_quality(fact: EquipmentFact) -> bool:
    """Return whether the source fact passes the approved r1 quality gate."""
    return fact.quality.strip().lower() == RAW_QUALITY_GOOD


def normalize_timestamp(value: object | None, *, collected_at: datetime, input_key: str = "timestamp") -> datetime:
    """Normalize an optional timestamp, defaulting to the source collection time."""
    if value is None:
        return _normalize_datetime(collected_at, input_key="collected_at")
    if isinstance(value, str) and not value.strip():
        return _normalize_datetime(collected_at, input_key="collected_at")
    return _normalize_datetime(value, input_key=input_key)


def normalize_required_text(value: object | None, *, input_key: str) -> str:
    """Normalize a required stable text input."""
    text = normalize_optional_text(value, input_key=input_key)
    if text is None:
        raise ValueError(f"{input_key} is required")
    return text


def normalize_optional_text(value: object | None, *, input_key: str) -> str | None:
    """Normalize an optional text input without accepting booleans or unknown objects."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"invalid_input:{input_key}")
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError(f"invalid_input:{input_key}")
        return str(value.normalize())
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError(f"invalid_input:{input_key}")
        return str(Decimal(str(value)).normalize())
    raise ValueError(f"invalid_input:{input_key}")


def normalize_optional_float(value: object | None, *, input_key: str) -> float | None:
    """Normalize an optional numeric input to a finite float."""
    decimal_value = _normalize_optional_decimal(value, input_key=input_key)
    if decimal_value is None:
        return None
    float_value = float(decimal_value)
    if not isfinite(float_value):
        raise ValueError(f"invalid_input:{input_key}")
    return float_value


def has_measurement(values: Mapping[str, object | None]) -> bool:
    """Return whether at least one business measurement was observed."""
    return any(value is not None for value in values.values())


def _normalize_optional_decimal(value: object | None, *, input_key: str) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"invalid_input:{input_key}")
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
        raise ValueError(f"invalid_input:{input_key}") from None
    if not decimal_value.is_finite():
        raise ValueError(f"invalid_input:{input_key}")
    return decimal_value


def _normalize_datetime(value: object, *, input_key: str) -> datetime:
    if isinstance(value, bool):
        raise ValueError(f"invalid_input:{input_key}")
    if isinstance(value, datetime):
        return _to_naive_utc(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError(f"invalid_input:{input_key}")
        try:
            return _to_naive_utc(datetime.fromisoformat(text.replace("Z", "+00:00")))
        except ValueError:
            raise ValueError(f"invalid_input:{input_key}") from None
    raise ValueError(f"invalid_input:{input_key}")


def _to_naive_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)
