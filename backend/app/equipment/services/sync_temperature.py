"""
File Path: /backend/app/equipment/services/sync_temperature.py
Description: Host-neutral synchronization for equipment temperature facts.
Main Features:
    - Declares equipment.sync_temperature for Projection registry discovery
    - Upserts temperature rows by timestamp for replay idempotency
    - Leaves transaction commit and rollback to the Projection host
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.equipment.crud import sync_temperature as sync_crud
from app.equipment.models.equipment import EquipmentTemperature
from app.equipment.services._sync_common import (
    NUMBER_PLC_TYPES,
    PROCESS_ALLOWED_GROUP_IDENTITIES,
    EquipmentSyncResult,
    has_measurement,
    is_good_quality,
    normalize_optional_float,
    normalize_timestamp,
    validate_equipment_provenance,
)
from projection.registry import (
    ProjectionHandlerDescriptor,
    ProjectionHandlerInput,
    ProjectionInvocationContext,
)


TEMPERATURE_MEASUREMENT_INPUTS = (
    "zone1_set",
    "zone1_act",
    "zone2_set",
    "zone2_act",
    "zone3_set",
    "zone3_act",
    "zone4_set",
    "zone4_act",
    "zone5_set",
    "zone5_act",
)


@dataclass(frozen=True)
class EquipmentTemperatureFact:
    """A decoded equipment temperature fact supplied by the Projection caller."""

    plc_key: str
    device_id: int
    db_number: int
    group_name: str
    raw_snapshot_id: int
    collected_at: datetime
    quality: str
    values: Mapping[str, object]


def run_projection_handler(
    db: Session,
    context: ProjectionInvocationContext,
    inputs: Mapping[str, object],
) -> EquipmentSyncResult:
    """Adapt one generic Projection invocation to an equipment temperature fact."""
    projection_handler.validate_inputs(inputs)
    return sync_temperature(
        db,
        EquipmentTemperatureFact(
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
    handler_key="equipment.sync_temperature",
    owner_module="equipment",
    description="Create or update equipment temperature dashboard rows from PLC raw observations.",
    snapshot_source="raw",
    handler_version="1",
    inputs=(
        ProjectionHandlerInput(
            input_key="timestamp",
            type="datetime",
            required=False,
            description="Optional sample timestamp; defaults to the source collection time.",
            accepted_plc_types=("String",),
        ),
        *(
            ProjectionHandlerInput(
                input_key=input_key,
                type="decimal",
                required=False,
                description=f"Optional equipment temperature numeric field {input_key}.",
                accepted_plc_types=NUMBER_PLC_TYPES,
            )
            for input_key in TEMPERATURE_MEASUREMENT_INPUTS
        ),
    ),
    allowed_group_identities=PROCESS_ALLOWED_GROUP_IDENTITIES,
    policy_derived_auxiliary_latest_groups=True,
    invoke=run_projection_handler,
)


def sync_temperature(db: Session, fact: EquipmentTemperatureFact) -> EquipmentSyncResult:
    """Synchronize one equipment temperature fact without committing it."""
    validate_equipment_provenance(fact)
    if not is_good_quality(fact):
        return EquipmentSyncResult(action="skipped", skipped_reason="source_quality_not_good")

    try:
        timestamp = normalize_timestamp(fact.values.get("timestamp"), collected_at=fact.collected_at)
        values = _normalize_measurements(fact.values)
    except ValueError as exc:
        return EquipmentSyncResult(action="skipped", skipped_reason=str(exc))

    if not has_measurement(values):
        return EquipmentSyncResult(action="skipped", skipped_reason="no_measurements")

    record = sync_crud.get_by_timestamp_for_update(db, timestamp=timestamp)
    action = "updated"
    if record is None:
        record = EquipmentTemperature(timestamp=timestamp)
        sync_crud.add_record(db, record)
        action = "created"

    _write_values(record, values)
    sync_crud.flush(db)
    return EquipmentSyncResult(action=action, record_id=record.id)


def _normalize_measurements(inputs: Mapping[str, object]) -> dict[str, float | None]:
    values: dict[str, float | None] = {}
    for input_key in TEMPERATURE_MEASUREMENT_INPUTS:
        try:
            values[input_key] = normalize_optional_float(inputs.get(input_key), input_key=input_key)
        except ValueError:
            raise ValueError(f"invalid_input:{input_key}") from None
    return values


def _write_values(record: EquipmentTemperature, values: Mapping[str, float | None]) -> None:
    for field_name, value in values.items():
        if value is not None:
            setattr(record, field_name, value)
