"""
File Path: /backend/projection/input_resolver.py
Description: Projection input assembly from primary raw facts and auxiliary latest facts.
Main Features:
    - Keeps primary raw trigger identity as the only cursor-driving source
    - Resolves optional handler inputs from descriptor-approved auxiliary latest groups
    - Reports unavailable optional inputs without turning them into handler failures
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.monitor.models.monitor import PlcDbBlockLatestSnapshot, PlcDbBlockRawSnapshot
from app.system.models.projection_mapping import ProjectionMappingBinding, ProjectionMappingSet
from projection.policy_catalog import SnapshotPolicyCatalog
from projection.registry import (
    ProjectionHandlerDescriptor,
    ProjectionHandlerGroupIdentity,
)


AUXILIARY_LATEST_FRESHNESS_SECONDS = 60.0
RAW_QUALITY_GOOD = "good"
ResolvedInputSource = Literal["raw", "latest"]


@dataclass(frozen=True)
class ProjectionInputUnavailable:
    """One optional binding that could not safely contribute an input value."""

    input_key: str
    plc_key: str
    db_number: int
    group_name: str
    point_name: str
    source: ResolvedInputSource
    reason_code: str


@dataclass(frozen=True)
class ProjectionInputResolution:
    """Handler inputs plus non-fatal optional input resolution evidence."""

    inputs: dict[str, object]
    unavailable_inputs: tuple[ProjectionInputUnavailable, ...]


class ProjectionInputResolverError(RuntimeError):
    """A fatal input assembly error that should reject or skip a primary raw fact."""

    def __init__(self, error_code: str) -> None:
        super().__init__(error_code)
        self.error_code = error_code


def resolve_projection_inputs(
    db: Session,
    *,
    mapping_set: ProjectionMappingSet,
    descriptor: ProjectionHandlerDescriptor,
    bindings: list[ProjectionMappingBinding],
    raw: PlcDbBlockRawSnapshot,
    expected_device_id: int,
    catalog: SnapshotPolicyCatalog,
    auxiliary_latest_freshness_seconds: float = AUXILIARY_LATEST_FRESHNESS_SECONDS,
) -> ProjectionInputResolution:
    """Assemble handler inputs for one primary raw trigger fact."""
    _validate_primary_raw(
        mapping_set=mapping_set,
        raw=raw,
        expected_device_id=expected_device_id,
    )
    primary_group_identity = ProjectionHandlerGroupIdentity(
        plc_key=mapping_set.plc_key,
        db_number=mapping_set.db_number,
        group_name=mapping_set.group_name,
    )
    latest_cache: dict[tuple[str, int, str], PlcDbBlockLatestSnapshot | None] = {}
    inputs: dict[str, object] = {}
    unavailable_inputs: list[ProjectionInputUnavailable] = []

    for binding in bindings:
        input_definition = descriptor.input_definition(binding.input_key)
        if input_definition is None:
            raise ProjectionInputResolverError("handler_input_not_declared")
        binding_snapshot_source = descriptor.binding_snapshot_source(
            input_key=binding.input_key,
            plc_key=binding.plc_key,
            db_number=binding.db_number,
            group_name=binding.group_name,
            primary_group_identity=primary_group_identity,
            catalog=catalog,
        )
        if binding_snapshot_source is None:
            raise ProjectionInputResolverError("binding_set_identity_mismatch")

        if binding_snapshot_source == "raw":
            if binding.point_name not in raw.decoded_payload:
                if input_definition.required:
                    raise ProjectionInputResolverError("payload_point_missing")
                unavailable_inputs.append(
                    _unavailable(binding, source="raw", reason_code="payload_point_missing")
                )
                continue
            inputs[binding.input_key] = raw.decoded_payload[binding.point_name]
            continue

        latest = _get_latest(
            db,
            cache=latest_cache,
            plc_key=binding.plc_key,
            db_number=binding.db_number,
            group_name=binding.group_name,
        )
        unavailable_reason = _get_latest_unavailable_reason(
            latest,
            binding=binding,
            expected_device_id=expected_device_id,
            primary_collected_at=raw.collected_at,
            freshness_seconds=auxiliary_latest_freshness_seconds,
        )
        if unavailable_reason is not None:
            unavailable_inputs.append(
                _unavailable(binding, source="latest", reason_code=unavailable_reason)
            )
            continue
        if latest is None:  # pragma: no cover - guarded by _get_latest_unavailable_reason
            continue
        inputs[binding.input_key] = latest.decoded_payload[binding.point_name]

    return ProjectionInputResolution(
        inputs=inputs,
        unavailable_inputs=tuple(unavailable_inputs),
    )


def _validate_primary_raw(
    *,
    mapping_set: ProjectionMappingSet,
    raw: PlcDbBlockRawSnapshot,
    expected_device_id: int,
) -> None:
    raw_identity = (raw.plc_key, raw.db_number, raw.group_name)
    set_identity = (
        mapping_set.plc_key,
        mapping_set.db_number,
        mapping_set.group_name,
    )
    if raw_identity != set_identity:
        raise ProjectionInputResolverError("raw_provenance_mismatch")
    if raw.device_id != expected_device_id:
        raise ProjectionInputResolverError("plc_device_identity_conflict")
    if not isinstance(raw.decoded_payload, dict):
        raise ProjectionInputResolverError("raw_payload_invalid")


def _get_latest(
    db: Session,
    *,
    cache: dict[tuple[str, int, str], PlcDbBlockLatestSnapshot | None],
    plc_key: str,
    db_number: int,
    group_name: str,
) -> PlcDbBlockLatestSnapshot | None:
    identity = (plc_key, db_number, group_name)
    if identity not in cache:
        cache[identity] = db.scalar(
            select(PlcDbBlockLatestSnapshot).where(
                PlcDbBlockLatestSnapshot.plc_key == plc_key,
                PlcDbBlockLatestSnapshot.db_number == db_number,
                PlcDbBlockLatestSnapshot.group_name == group_name,
            )
        )
    return cache[identity]


def _get_latest_unavailable_reason(
    latest: PlcDbBlockLatestSnapshot | None,
    *,
    binding: ProjectionMappingBinding,
    expected_device_id: int,
    primary_collected_at: datetime,
    freshness_seconds: float,
) -> str | None:
    if latest is None:
        return "latest_snapshot_missing"
    if latest.device_id != expected_device_id:
        return "latest_device_identity_conflict"
    if latest.quality != RAW_QUALITY_GOOD:
        return "latest_quality_not_good"
    if not isinstance(latest.decoded_payload, dict):
        return "latest_payload_invalid"
    if _is_stale(
        latest_collected_at=latest.collected_at,
        primary_collected_at=primary_collected_at,
        freshness_seconds=freshness_seconds,
    ):
        return "latest_snapshot_stale"
    if binding.point_name not in latest.decoded_payload:
        return "latest_point_missing"
    return None


def _is_stale(
    *,
    latest_collected_at: datetime,
    primary_collected_at: datetime,
    freshness_seconds: float,
) -> bool:
    return abs(
        (_normalize_datetime(latest_collected_at) - _normalize_datetime(primary_collected_at)).total_seconds()
    ) > freshness_seconds


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.replace(tzinfo=None)


def _unavailable(
    binding: ProjectionMappingBinding,
    *,
    source: ResolvedInputSource,
    reason_code: str,
) -> ProjectionInputUnavailable:
    return ProjectionInputUnavailable(
        input_key=binding.input_key,
        plc_key=binding.plc_key,
        db_number=binding.db_number,
        group_name=binding.group_name,
        point_name=binding.point_name,
        source=source,
        reason_code=reason_code,
    )
