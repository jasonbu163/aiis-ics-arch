"""
File Path: /backend/app/monitor/services/sync_process_curve.py
Description: Host-neutral synchronization for Monitor process curve facts.
Main Features:
    - Declares monitor.sync_process_curve for Projection registry discovery
    - Converts typed Projection inputs into monitor_history_process_curves rows
    - Leaves transaction commit and rollback to the Projection host
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from math import isfinite

from sqlalchemy.orm import Session

from app.monitor.crud import sync_process_curve as sync_crud
from projection.provenance_contract import get_expected_device_id
from projection.registry import (
    ProjectionHandlerDescriptor,
    ProjectionHandlerGroupIdentity,
    ProjectionHandlerInput,
    ProjectionInvocationContext,
)


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

TEXT_INPUT_FIELDS = ("coil_number",)
INTEGER_INPUT_FIELDS = (
    "z1_temp_set",
    "z1_temp_act",
    "z2_temp_set",
    "z2_temp_act",
    "z3_temp_set",
    "z3_temp_act",
    "z4_temp_set",
    "z4_temp_act",
    "z5_temp_set",
    "z5_temp_act",
    "z6_temp_set",
    "z6_temp_act",
)
FLOAT_INPUT_FIELDS = (
    "line_speed_set",
    "line_speed_act",
    "unc_set_tension_p",
    "unc_act_tension_p",
    "unc_set_tension_kg",
    "rec_set_tension_p",
    "rec_act_tension_p",
    "rec_set_tension_kg",
    "furn_set_tension_kg",
    "furn_act_tension_kg",
    "cool_fan1_set_fre",
    "cool_fan1_act_fre",
    "cool_fan2_set_fre",
    "cool_fan2_act_fre",
    "n2_total",
    "elect_consum",
    "h2_flow",
    "n2_flow",
    "oxygen_content",
    "dew_point",
    "muffle_pressure",
)
MEASUREMENT_INPUT_FIELDS = (*INTEGER_INPUT_FIELDS, *FLOAT_INPUT_FIELDS)


@dataclass(frozen=True)
class ProcessCurveFact:
    """A decoded monitor process curve fact supplied by the Projection caller."""

    plc_key: str
    device_id: int
    db_number: int
    group_name: str
    raw_snapshot_id: int
    collected_at: datetime
    quality: str
    values: Mapping[str, object]


@dataclass(frozen=True)
class ProcessCurveSyncResult:
    """A stable, host-neutral result for one process curve fact."""

    action: str
    record_id: int | None = None
    skipped_reason: str | None = None


def run_projection_handler(
    db: Session,
    context: ProjectionInvocationContext,
    inputs: Mapping[str, object],
) -> ProcessCurveSyncResult:
    """Adapt one generic Projection invocation to a monitor process curve fact."""
    projection_handler.validate_inputs(inputs)
    return sync_process_curve(
        db,
        ProcessCurveFact(
            plc_key=context.plc_key,
            device_id=context.device_id,
            db_number=context.db_number,
            group_name=context.group_name,
            raw_snapshot_id=context.source_snapshot_id,
            collected_at=context.collected_at,
            quality=context.quality,
            values=inputs,
        ),
    )


projection_handler = ProjectionHandlerDescriptor(
    handler_key="monitor.sync_process_curve",
    owner_module="monitor",
    description="Append Monitor process curve history rows from PLC raw process observations.",
    snapshot_source="raw",
    handler_version="1",
    inputs=(
        ProjectionHandlerInput(
            input_key="coil_number",
            type="string",
            required=False,
            description="Optional observed coil number stored on the monitor process curve row.",
            accepted_plc_types=NUMBER_PLC_TYPES,
        ),
        *(
            ProjectionHandlerInput(
                input_key=input_key,
                type="integer",
                required=False,
                description=f"Optional integer process temperature field {input_key}.",
                accepted_plc_types=NUMBER_PLC_TYPES,
            )
            for input_key in INTEGER_INPUT_FIELDS
        ),
        *(
            ProjectionHandlerInput(
                input_key=input_key,
                type="decimal",
                required=False,
                description=f"Optional numeric process curve field {input_key}.",
                accepted_plc_types=NUMBER_PLC_TYPES,
            )
            for input_key in FLOAT_INPUT_FIELDS
        ),
    ),
    allowed_group_identities=PROCESS_ALLOWED_GROUP_IDENTITIES,
    invoke=run_projection_handler,
)


def sync_process_curve(
    db: Session,
    fact: ProcessCurveFact,
) -> ProcessCurveSyncResult:
    """Synchronize one monitor process curve fact without committing it."""
    _validate_process_provenance(fact)
    if fact.quality.strip().lower() != RAW_QUALITY_GOOD:
        return ProcessCurveSyncResult(
            action="skipped",
            skipped_reason="source_quality_not_good",
        )

    try:
        coil_number = _normalize_optional_text(
            fact.values.get("coil_number"),
            input_key="coil_number",
        )
        values = _normalize_measurements(fact.values)
    except ValueError as exc:
        return ProcessCurveSyncResult(
            action="skipped",
            skipped_reason=str(exc),
        )

    if not _has_measurement(values):
        return ProcessCurveSyncResult(
            action="skipped",
            skipped_reason="no_measurements",
        )

    record = sync_crud.add_process_curve(
        db,
        device_id=fact.device_id,
        coil_number=coil_number,
        created_at=_normalize_datetime(fact.collected_at, input_key="collected_at"),
        values=values,
    )
    sync_crud.flush(db)
    return ProcessCurveSyncResult(action="created", record_id=record.id)


def _validate_process_provenance(fact: ProcessCurveFact) -> None:
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
    if not isinstance(fact.values, Mapping):
        raise ValueError("values must be a mapping")


def _normalize_measurements(inputs: Mapping[str, object]) -> dict[str, float | int | None]:
    values: dict[str, float | int | None] = {}
    for input_key in INTEGER_INPUT_FIELDS:
        try:
            values[input_key] = _normalize_optional_int(inputs.get(input_key), input_key=input_key)
        except ValueError:
            raise ValueError(f"invalid_input:{input_key}") from None
    for input_key in FLOAT_INPUT_FIELDS:
        try:
            values[input_key] = _normalize_optional_float(inputs.get(input_key), input_key=input_key)
        except ValueError:
            raise ValueError(f"invalid_input:{input_key}") from None
    return values


def _normalize_optional_text(value: object | None, *, input_key: str) -> str | None:
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


def _normalize_optional_int(value: object | None, *, input_key: str) -> int | None:
    decimal_value = _normalize_optional_decimal(value, input_key=input_key)
    if decimal_value is None:
        return None
    integral_value = decimal_value.to_integral_value()
    if decimal_value != integral_value:
        raise ValueError(f"{input_key} must be integral")
    return int(integral_value)


def _normalize_optional_float(value: object | None, *, input_key: str) -> float | None:
    decimal_value = _normalize_optional_decimal(value, input_key=input_key)
    if decimal_value is None:
        return None
    float_value = float(decimal_value)
    if not isfinite(float_value):
        raise ValueError(f"{input_key} must be finite")
    return float_value


def _normalize_optional_decimal(value: object | None, *, input_key: str) -> Decimal | None:
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


def _normalize_datetime(value: datetime, *, input_key: str) -> datetime:
    if isinstance(value, bool) or not isinstance(value, datetime):
        raise ValueError(f"{input_key} must be a datetime")
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _has_measurement(values: Mapping[str, object | None]) -> bool:
    return any(values.get(input_key) is not None for input_key in MEASUREMENT_INPUT_FIELDS)
