"""
File Path: /backend/app/performance/services/sync_production_record.py
Description: Host-neutral synchronization for PLC-observed production records.
Main Features:
    - Accepts only the fixed B6.2 raw provenance contract
    - Creates, updates, reactivates and transitions unplanned PLC records
    - Leaves transaction commit and rollback to the Projection host
"""
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from math import isfinite

from sqlalchemy.orm import Session

from app.performance.crud import sync_production_record as sync_crud
from app.performance.domain import (
    CoilObservation,
    apply_performance_duration,
    classify_coil_no,
    normalize_parent_coil_no,
)
from app.performance.models.performance import Performance
from common.data_keys import (
    PerformanceEffectiveWeightSource,
    PerformanceObservationStatus,
    PerformanceRecordSource,
)
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


@dataclass(frozen=True)
class ProductionRecordFact:
    """A raw coil observation already decoded by the Projection caller."""

    plc_key: str
    device_id: int
    db_number: int
    group_name: str
    raw_snapshot_id: int
    collected_at: datetime
    quality: str
    coil_no_value: object
    grade_value: object | None = None
    weight_value: object | None = None
    total_length_value: object | None = None
    diameter_value: object | None = None
    density_value: object | None = None
    spec_value: object | None = None
    start_time_value: object | None = None
    end_time_value: object | None = None
    output_quantity_value: object | None = None
    qualified_quantity_value: object | None = None
    efficiency_rate_value: object | None = None
    quality_score_value: object | None = None
    remark_value: object | None = None


@dataclass(frozen=True)
class ProductionRecordSyncResult:
    """A stable, host-neutral result for one accepted or ignored raw fact."""

    action: str
    performance_id: int | None = None


def run_projection_handler(
    db: Session,
    context: ProjectionInvocationContext,
    inputs: Mapping[str, object],
) -> ProductionRecordSyncResult:
    """Adapt one generic raw Projection invocation to the B6.2 fact contract."""
    projection_handler.validate_inputs(inputs)
    return sync_production_record(
        db,
        ProductionRecordFact(
            plc_key=context.plc_key,
            device_id=context.device_id,
            db_number=context.db_number,
            group_name=context.group_name,
            raw_snapshot_id=context.source_snapshot_id,
            collected_at=context.collected_at,
            quality=context.quality,
            coil_no_value=inputs["coil_no"],
            grade_value=inputs.get("grade"),
            weight_value=inputs.get("weight"),
            total_length_value=inputs.get("total_length"),
            diameter_value=inputs.get("diameter"),
            density_value=inputs.get("density"),
            spec_value=inputs.get("spec"),
            start_time_value=inputs.get("start_time"),
            end_time_value=inputs.get("end_time"),
            output_quantity_value=inputs.get("output_quantity"),
            qualified_quantity_value=inputs.get("qualified_quantity"),
            efficiency_rate_value=inputs.get("efficiency_rate"),
            quality_score_value=inputs.get("quality_score"),
            remark_value=inputs.get("remark"),
        ),
    )


projection_handler = ProjectionHandlerDescriptor(
    handler_key="performance.sync_production_record",
    owner_module="performance",
    description="Create or update PLC-observed production records from one coil observation.",
    snapshot_source="raw",
    handler_version="1",
    inputs=(
        ProjectionHandlerInput(
            input_key="coil_no",
            type="string",
            required=True,
            description="Observed coil number stored as a canonical string by the performance service.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
        ProjectionHandlerInput(
            input_key="grade",
            type="string",
            required=False,
            description="Optional observed material grade. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
        ProjectionHandlerInput(
            input_key="weight",
            type="decimal",
            required=False,
            description="Optional observed coil weight in tons. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
        ProjectionHandlerInput(
            input_key="total_length",
            type="decimal",
            required=False,
            description="Optional observed total length in meters. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
        ProjectionHandlerInput(
            input_key="diameter",
            type="decimal",
            required=False,
            description="Optional observed diameter in millimeters. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
        ProjectionHandlerInput(
            input_key="density",
            type="decimal",
            required=False,
            description="Optional observed density. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
        ProjectionHandlerInput(
            input_key="spec",
            type="string",
            required=False,
            description="Optional observed product specification. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
        ProjectionHandlerInput(
            input_key="start_time",
            type="datetime",
            required=False,
            description="Optional manual production start time as an ISO string. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("String",),
        ),
        ProjectionHandlerInput(
            input_key="end_time",
            type="datetime",
            required=False,
            description="Optional manual production end time as an ISO string. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("String",),
        ),
        ProjectionHandlerInput(
            input_key="output_quantity",
            type="decimal",
            required=False,
            description="Optional observed output quantity. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
        ProjectionHandlerInput(
            input_key="qualified_quantity",
            type="decimal",
            required=False,
            description="Optional observed qualified quantity. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
        ProjectionHandlerInput(
            input_key="efficiency_rate",
            type="decimal",
            required=False,
            description="Optional observed efficiency rate. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
        ProjectionHandlerInput(
            input_key="quality_score",
            type="decimal",
            required=False,
            description="Optional observed quality score. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
        ProjectionHandlerInput(
            input_key="remark",
            type="string",
            required=False,
            description="Optional observed production remark. Blank or invalid values do not overwrite existing data.",
            accepted_plc_types=("Real", "Int", "String"),
        ),
    ),
    allowed_group_identities=(
        ProjectionHandlerGroupIdentity(
            plc_key=PILOT_PLC_KEY,
            db_number=PILOT_DB_NUMBER,
            group_name=PILOT_GROUP_NAME,
        ),
    ),
    invoke=run_projection_handler,
    policy_derived_auxiliary_latest_groups=True,
)


def sync_production_record(
    db: Session,
    fact: ProductionRecordFact,
) -> ProductionRecordSyncResult:
    """Synchronize a fixed-provenance PLC coil fact without committing it."""
    _validate_provenance(fact)
    observation = _classify_fact(fact)
    latest_raw_snapshot_id = sync_crud.get_latest_raw_snapshot_id_for_device(
        db,
        device_id=fact.device_id,
    )
    if (
        latest_raw_snapshot_id is not None
        and fact.raw_snapshot_id <= latest_raw_snapshot_id
    ):
        return ProductionRecordSyncResult(
            action="noop",
            performance_id=_find_existing_performance_id(db, fact, observation),
        )

    if observation.status is PerformanceObservationStatus.IN_PRODUCTION:
        return _sync_in_production(db, fact, observation)
    if observation.status is PerformanceObservationStatus.NOT_IN_PRODUCTION:
        return _sync_active_rows(
            db,
            fact,
            PerformanceObservationStatus.NOT_IN_PRODUCTION,
        )
    return _sync_active_rows(db, fact, PerformanceObservationStatus.UNKNOWN)


def _validate_provenance(fact: ProductionRecordFact) -> None:
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


def _classify_fact(fact: ProductionRecordFact) -> CoilObservation:
    if not isinstance(fact.quality, str) or fact.quality.strip().lower() != "good":
        return CoilObservation(PerformanceObservationStatus.UNKNOWN, None)
    return classify_coil_no(fact.coil_no_value)


def _sync_in_production(
    db: Session,
    fact: ProductionRecordFact,
    observation: CoilObservation,
) -> ProductionRecordSyncResult:
    if observation.coil_no is None:
        raise ValueError("in_production observations require a canonical coil number")

    performance = sync_crud.get_by_device_and_coil_for_update(
        db,
        device_id=fact.device_id,
        coil_no=observation.coil_no,
    )
    active_rows = sync_crud.list_active_for_device_for_update(
        db,
        device_id=fact.device_id,
    )
    if _has_newer_or_equal_raw_snapshot(active_rows, fact.raw_snapshot_id):
        return ProductionRecordSyncResult(
            action="noop",
            performance_id=performance.id if performance else None,
        )
    if performance and _is_newer_or_equal(performance, fact.raw_snapshot_id):
        return ProductionRecordSyncResult(action="noop", performance_id=performance.id)

    if performance is None:
        performance = _new_performance(fact, observation.coil_no)
        _write_optional_main_fields(performance, fact)
        apply_performance_duration(performance)
        sync_crud.add_performance(db, performance)
        action = "created"
    else:
        action = (
            "reactivated"
            if performance.observation_status == PerformanceObservationStatus.NOT_IN_PRODUCTION.value
            else "updated"
        )
        _write_last_observation(
            performance,
            fact,
            PerformanceObservationStatus.IN_PRODUCTION,
        )
        _write_optional_main_fields(performance, fact)
        apply_performance_duration(performance)

    for active_row in active_rows:
        if performance.id is not None and active_row.id == performance.id:
            continue
        _write_last_observation(
            active_row,
            fact,
            PerformanceObservationStatus.NOT_IN_PRODUCTION,
        )
        apply_performance_duration(active_row)

    sync_crud.flush(db)
    return ProductionRecordSyncResult(action=action, performance_id=performance.id)


def _sync_active_rows(
    db: Session,
    fact: ProductionRecordFact,
    target_status: PerformanceObservationStatus,
) -> ProductionRecordSyncResult:
    active_rows = sync_crud.list_active_for_device_for_update(
        db,
        device_id=fact.device_id,
    )
    if _has_newer_or_equal_raw_snapshot(active_rows, fact.raw_snapshot_id):
        return ProductionRecordSyncResult(action="noop")

    for performance in active_rows:
        _write_last_observation(performance, fact, target_status)
        apply_performance_duration(performance)

    if active_rows:
        sync_crud.flush(db)
    return ProductionRecordSyncResult(
        action=target_status.value,
        performance_id=active_rows[0].id if len(active_rows) == 1 else None,
    )


def _new_performance(fact: ProductionRecordFact, coil_no: str) -> Performance:
    return Performance(
        plan_id=None,
        coil_no=coil_no,
        parent_coil_no=normalize_parent_coil_no(coil_no, None),
        grade=None,
        weight=None,
        production_date=fact.collected_at.date(),
        output_quantity=Decimal("0"),
        qualified_quantity=Decimal("0"),
        device_id=fact.device_id,
        observation_status=PerformanceObservationStatus.IN_PRODUCTION.value,
        record_source=PerformanceRecordSource.UNPLANNED_PLC.value,
        first_observed_at=fact.collected_at,
        last_observed_at=fact.collected_at,
        first_raw_snapshot_id=fact.raw_snapshot_id,
        last_raw_snapshot_id=fact.raw_snapshot_id,
        plc_key=fact.plc_key,
        db_number=fact.db_number,
        group_name=fact.group_name,
    )


def _find_existing_performance_id(
    db: Session,
    fact: ProductionRecordFact,
    observation: CoilObservation,
) -> int | None:
    if observation.coil_no is None:
        return None
    performance = sync_crud.get_by_device_and_coil_for_update(
        db,
        device_id=fact.device_id,
        coil_no=observation.coil_no,
    )
    return performance.id if performance else None


def _write_last_observation(
    performance: Performance,
    fact: ProductionRecordFact,
    status: PerformanceObservationStatus,
) -> None:
    performance.observation_status = status.value
    performance.last_observed_at = fact.collected_at
    performance.last_raw_snapshot_id = fact.raw_snapshot_id


def _write_optional_main_fields(
    performance: Performance,
    fact: ProductionRecordFact,
) -> None:
    grade = _normalize_optional_text(fact.grade_value)
    if grade is not None:
        performance.grade = grade

    spec = _normalize_optional_text(fact.spec_value)
    if spec is not None:
        performance.spec = spec

    remark = _normalize_optional_text(fact.remark_value)
    if remark is not None:
        performance.remark = remark

    collected_weight = _normalize_optional_decimal(fact.weight_value)
    if collected_weight is not None:
        performance.collected_weight = collected_weight
        if (
            performance.effective_weight_source
            != PerformanceEffectiveWeightSource.MANUAL_OVERRIDE_WEIGHT.value
        ):
            performance.weight = collected_weight
            performance.effective_weight = collected_weight
            performance.effective_weight_source = PerformanceEffectiveWeightSource.COLLECTED_WEIGHT.value

    decimal_fields = {
        "total_length": fact.total_length_value,
        "diameter": fact.diameter_value,
        "density": fact.density_value,
        "output_quantity": fact.output_quantity_value,
        "qualified_quantity": fact.qualified_quantity_value,
        "efficiency_rate": fact.efficiency_rate_value,
        "quality_score": fact.quality_score_value,
    }
    for field_name, value in decimal_fields.items():
        decimal_value = _normalize_optional_decimal(value)
        if decimal_value is not None:
            setattr(performance, field_name, decimal_value)

    start_time = _normalize_optional_datetime(fact.start_time_value)
    if start_time is not None:
        performance.start_time = start_time

    end_time = _normalize_optional_datetime(fact.end_time_value)
    if end_time is not None:
        performance.end_time = end_time


def _normalize_optional_text(value: object | None) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, Decimal):
        if not value.is_finite():
            return None
        return str(value.normalize())
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not isfinite(value):
            return None
        return str(Decimal(str(value)).normalize())
    return None


def _normalize_optional_decimal(value: object | None) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
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
        return None
    if not decimal_value.is_finite():
        return None
    return decimal_value


def _normalize_optional_datetime(value: object | None) -> datetime | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _has_newer_or_equal_raw_snapshot(
    performances: list[Performance],
    raw_snapshot_id: int,
) -> bool:
    return any(_is_newer_or_equal(performance, raw_snapshot_id) for performance in performances)


def _is_newer_or_equal(performance: Performance, raw_snapshot_id: int) -> bool:
    return (
        performance.last_raw_snapshot_id is not None
        and performance.last_raw_snapshot_id >= raw_snapshot_id
    )
