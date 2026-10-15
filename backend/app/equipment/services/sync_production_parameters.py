"""
File Path: /backend/app/equipment/services/sync_production_parameters.py
Description: Host-neutral synchronization for equipment production-parameter facts.
Main Features:
    - Declares equipment.sync_production_parameters for Projection registry discovery
    - Upserts production-parameter rows by coil number and timestamp
    - Leaves transaction commit and rollback to the Projection host
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.equipment.crud import sync_production_parameters as sync_crud
from app.equipment.models.equipment import EquipmentProductionParameters
from app.equipment.services._sync_common import (
    NUMBER_PLC_TYPES,
    PROCESS_ALLOWED_GROUP_IDENTITIES,
    EquipmentSyncResult,
    has_measurement,
    is_good_quality,
    normalize_optional_float,
    normalize_optional_text,
    normalize_required_text,
    normalize_timestamp,
    validate_equipment_provenance,
)
from projection.registry import (
    ProjectionHandlerDescriptor,
    ProjectionHandlerInput,
    ProjectionInvocationContext,
)


TEXT_INPUTS = ("grade",)
NUMERIC_INPUTS = ("thickness", "width", "total_time", "weight", "speed")


@dataclass(frozen=True)
class EquipmentProductionParametersFact:
    """A decoded equipment production-parameter fact supplied by the Projection caller."""

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
    """Adapt one generic Projection invocation to equipment production parameters."""
    projection_handler.validate_inputs(inputs)
    return sync_production_parameters(
        db,
        EquipmentProductionParametersFact(
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
    handler_key="equipment.sync_production_parameters",
    owner_module="equipment",
    description="Create or update equipment production parameter rows from PLC raw observations.",
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
        ProjectionHandlerInput(
            input_key="coil_no",
            type="string",
            required=True,
            description="Required current equipment coil number.",
            accepted_plc_types=NUMBER_PLC_TYPES,
        ),
        ProjectionHandlerInput(
            input_key="grade",
            type="string",
            required=False,
            description="Optional material grade.",
            accepted_plc_types=NUMBER_PLC_TYPES,
        ),
        ProjectionHandlerInput(
            input_key="entry_time",
            type="datetime",
            required=False,
            description="Optional equipment entry time.",
            accepted_plc_types=("String",),
        ),
        *(
            ProjectionHandlerInput(
                input_key=input_key,
                type="decimal",
                required=False,
                description=f"Optional equipment production numeric field {input_key}.",
                accepted_plc_types=NUMBER_PLC_TYPES,
            )
            for input_key in NUMERIC_INPUTS
        ),
    ),
    allowed_group_identities=PROCESS_ALLOWED_GROUP_IDENTITIES,
    policy_derived_auxiliary_latest_groups=True,
    invoke=run_projection_handler,
)


def sync_production_parameters(
    db: Session,
    fact: EquipmentProductionParametersFact,
) -> EquipmentSyncResult:
    """Synchronize one equipment production-parameter fact without committing it."""
    validate_equipment_provenance(fact)
    if not is_good_quality(fact):
        return EquipmentSyncResult(action="skipped", skipped_reason="source_quality_not_good")

    try:
        timestamp = normalize_timestamp(fact.values.get("timestamp"), collected_at=fact.collected_at)
        coil_no = normalize_required_text(fact.values.get("coil_no"), input_key="coil_no")
        entry_time = normalize_timestamp(
            fact.values.get("entry_time"),
            collected_at=fact.collected_at,
            input_key="entry_time",
        ) if fact.values.get("entry_time") is not None else None
        text_values = _normalize_text_values(fact.values)
        numeric_values = _normalize_numeric_values(fact.values)
    except ValueError as exc:
        return EquipmentSyncResult(action="skipped", skipped_reason=str(exc))

    if not has_measurement({**text_values, **numeric_values, "entry_time": entry_time}):
        return EquipmentSyncResult(action="skipped", skipped_reason="no_measurements")

    record = sync_crud.get_by_business_key_for_update(
        db,
        coil_no=coil_no,
        timestamp=timestamp,
    )
    action = "updated"
    if record is None:
        record = EquipmentProductionParameters(
            timestamp=timestamp,
            coil_no=coil_no,
            process_steps=[],
        )
        sync_crud.add_record(db, record)
        action = "created"

    _write_values(record, text_values)
    _write_values(record, numeric_values)
    if entry_time is not None:
        record.entry_time = entry_time
    sync_crud.flush(db)
    return EquipmentSyncResult(action=action, record_id=record.id)


def _normalize_text_values(inputs: Mapping[str, object]) -> dict[str, str | None]:
    values: dict[str, str | None] = {}
    for input_key in TEXT_INPUTS:
        try:
            values[input_key] = normalize_optional_text(inputs.get(input_key), input_key=input_key)
        except ValueError:
            raise ValueError(f"invalid_input:{input_key}") from None
    return values


def _normalize_numeric_values(inputs: Mapping[str, object]) -> dict[str, float | None]:
    values: dict[str, float | None] = {}
    for input_key in NUMERIC_INPUTS:
        try:
            values[input_key] = normalize_optional_float(inputs.get(input_key), input_key=input_key)
        except ValueError:
            raise ValueError(f"invalid_input:{input_key}") from None
    return values


def _write_values(
    record: EquipmentProductionParameters,
    values: Mapping[str, str | float | None],
) -> None:
    for field_name, value in values.items():
        if value is not None:
            setattr(record, field_name, value)
