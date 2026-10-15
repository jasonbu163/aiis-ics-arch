"""
File Path: /backend/app/performance/services/sync_process_speed.py
Description: Host-neutral synchronization for Performance speed process data.
Main Features:
    - Declares performance.sync_process_speed for Projection registry discovery
    - Upserts speed rows by performance, zone, and record_time
    - Leaves transaction commit and rollback to the Projection host
"""
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.performance.crud import sync_process_speed as sync_crud
from app.performance.models.performance import ProcessSpeed
from app.performance.services._sync_process_common import (
    NUMBER_PLC_TYPES,
    PROCESS_ALLOWED_GROUP_IDENTITIES,
    ProcessRecordSyncResult,
    ensure_observed_measurement,
    normalize_optional_decimal,
    normalize_record_time,
    normalize_required_zone,
    resolve_parent_performance,
)
from projection.registry import (
    ProjectionHandlerDescriptor,
    ProjectionHandlerInput,
    ProjectionInvocationContext,
)


@dataclass(frozen=True)
class ProcessSpeedFact:
    """A decoded speed process fact supplied by the Projection caller."""

    plc_key: str
    device_id: int
    db_number: int
    group_name: str
    raw_snapshot_id: int
    collected_at: datetime
    quality: str
    coil_no_value: object
    zone_value: object
    set_speed_value: object | None = None
    avg_speed_value: object | None = None
    max_speed_value: object | None = None
    record_time_value: object | None = None


def run_projection_handler(
    db: Session,
    context: ProjectionInvocationContext,
    inputs: Mapping[str, object],
) -> ProcessRecordSyncResult:
    """Adapt one generic Projection invocation to a speed process fact."""
    projection_handler.validate_inputs(inputs)
    return sync_process_speed(
        db,
        ProcessSpeedFact(
            plc_key=context.plc_key,
            device_id=context.device_id,
            db_number=context.db_number,
            group_name=context.group_name,
            raw_snapshot_id=context.source_snapshot_id,
            collected_at=context.collected_at,
            quality=context.quality,
            coil_no_value=inputs["coil_no"],
            zone_value=inputs["zone"],
            set_speed_value=inputs.get("set_speed"),
            avg_speed_value=inputs.get("avg_speed"),
            max_speed_value=inputs.get("max_speed"),
            record_time_value=inputs.get("record_time"),
        ),
    )


projection_handler = ProjectionHandlerDescriptor(
    handler_key="performance.sync_process_speed",
    owner_module="performance",
    description="Create or update speed process rows for an existing performance record.",
    snapshot_source="raw",
    handler_version="1",
    inputs=(
        ProjectionHandlerInput(
            input_key="coil_no",
            type="string",
            required=True,
            description="Observed coil number used to resolve the parent performance row.",
            accepted_plc_types=NUMBER_PLC_TYPES,
        ),
        ProjectionHandlerInput(
            input_key="zone",
            type="string",
            required=True,
            description="Speed zone key stored on the process row.",
            accepted_plc_types=NUMBER_PLC_TYPES,
        ),
        ProjectionHandlerInput(
            input_key="set_speed",
            type="decimal",
            required=False,
            description="Optional set speed for the process row.",
            accepted_plc_types=NUMBER_PLC_TYPES,
        ),
        ProjectionHandlerInput(
            input_key="avg_speed",
            type="decimal",
            required=False,
            description="Optional average speed for the process row.",
            accepted_plc_types=NUMBER_PLC_TYPES,
        ),
        ProjectionHandlerInput(
            input_key="max_speed",
            type="decimal",
            required=False,
            description="Optional maximum speed for the process row.",
            accepted_plc_types=NUMBER_PLC_TYPES,
        ),
        ProjectionHandlerInput(
            input_key="record_time",
            type="datetime",
            required=False,
            description="Optional process record time; defaults to the source collection time.",
            accepted_plc_types=("String",),
        ),
    ),
    allowed_group_identities=PROCESS_ALLOWED_GROUP_IDENTITIES,
    invoke=run_projection_handler,
    policy_derived_auxiliary_latest_groups=True,
)


def sync_process_speed(
    db: Session,
    fact: ProcessSpeedFact,
) -> ProcessRecordSyncResult:
    """Synchronize one speed process fact without committing it."""
    performance = resolve_parent_performance(db, fact)
    zone = normalize_required_zone(fact.zone_value)
    record_time = normalize_record_time(
        fact.record_time_value,
        collected_at=fact.collected_at,
    )
    values = {
        "set_speed": normalize_optional_decimal(fact.set_speed_value, input_key="set_speed"),
        "avg_speed": normalize_optional_decimal(fact.avg_speed_value, input_key="avg_speed"),
        "max_speed": normalize_optional_decimal(fact.max_speed_value, input_key="max_speed"),
    }
    ensure_observed_measurement(values)

    record = sync_crud.get_by_process_key_for_update(
        db,
        performance_id=performance.id,
        zone=zone,
        record_time=record_time,
    )
    action = "updated"
    if record is None:
        record = ProcessSpeed(
            performance_id=performance.id,
            zone=zone,
            record_time=record_time,
        )
        sync_crud.add_record(db, record)
        action = "created"

    _write_values(record, values)
    sync_crud.flush(db)
    return ProcessRecordSyncResult(
        action=action,
        performance_id=performance.id,
        record_id=record.id,
    )


def _write_values(
    record: ProcessSpeed,
    values: dict[str, Decimal | None],
) -> None:
    for field_name, value in values.items():
        if value is not None:
            setattr(record, field_name, value)
