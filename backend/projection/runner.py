"""
File Path: /backend/projection/runner.py
Description: Synchronous raw-fact Projection runner for the B6.4 pilot.
Main Features:
    - Reads only an active published mapping revision and registry descriptor
    - Applies owner handlers with cursor and runtime audit in one transaction
    - Fails closed on mapping, policy, provenance, or payload-contract errors
    - Bounds repeated audit-persistence failure observations within one process
"""
from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.monitor.models.monitor import PlcDbBlockRawSnapshot
from app.system.models.projection_mapping import (
    ProjectionMappingBinding,
    ProjectionMappingRevision,
    ProjectionMappingSet,
    ProjectionRuntimeAuditEvent,
    ProjectionRuntimeCursor,
)
from common.log import log_projection_event
from database import create_sync_session
from projection.failure_observability import ProjectionFailureObserver
from projection.input_resolver import (
    ProjectionInputResolverError,
    ProjectionInputUnavailable,
    ProjectionInputResolution,
    resolve_projection_inputs,
)
from projection.policy_catalog import SnapshotPolicyCatalog, SnapshotPolicyCatalogError
from projection.provenance_contract import get_expected_device_id
from projection.registry import (
    ProjectionHandlerDescriptor,
    ProjectionHandlerGroupIdentity,
    ProjectionInvocationContext,
    ProjectionRegistry,
)


RUNTIME_EVENT_PROCESSED = "processed"
RUNTIME_EVENT_SKIPPED = "skipped"
RUNTIME_EVENT_CONTRACT_REJECTED = "contract_rejected"
RUNTIME_EVENT_FAILED = "failed"
PUBLISHED_REVISION_STATUS = "published"
RAW_QUALITY_GOOD = "good"
NORMAL_SUMMARY_WINDOW_SECONDS = 60.0


@dataclass(frozen=True)
class ProjectionRunReport:
    """Aggregate result for one bounded runner pass."""

    processed_snapshot_count: int = 0
    processed_mapping_set_count: int = 0
    blocked_mapping_set_count: int = 0
    failed_mapping_set_count: int = 0


@dataclass(frozen=True)
class _MappingSetRunResult:
    """Committed result for one mapping set in a runner pass."""

    mapping_set_id: int
    revision_id: int
    first_raw_snapshot_id: int
    last_raw_snapshot_id: int
    processed_snapshot_count: int
    skipped_snapshot_count: int


@dataclass(frozen=True)
class _RecoveredRawSnapshot:
    """A committed invalid source fact that was skipped without owner invocation."""

    raw_snapshot_id: int
    source_quality: str
    reason_code: str


@dataclass(frozen=True)
class _UnavailableOptionalInput:
    """A committed primary raw whose optional input could not be resolved."""

    raw_snapshot_id: int
    item: ProjectionInputUnavailable


class ProjectionRunnerError(RuntimeError):
    """A controlled runner error that can safely become runtime audit evidence."""

    def __init__(
        self,
        error_code: str,
        *,
        event_type: str,
        revision_id: int | None = None,
        raw_snapshot_id: int | None = None,
        detail: str | None = None,
    ) -> None:
        super().__init__(detail or error_code)
        self.error_code = error_code
        self.event_type = event_type
        self.revision_id = revision_id
        self.raw_snapshot_id = raw_snapshot_id


class ProjectionRunner:
    """Run the accepted single-process raw Projection slice without PLC access."""

    def __init__(
        self,
        *,
        registry: ProjectionRegistry,
        catalog: SnapshotPolicyCatalog,
        session_factory: Callable[[], Session] = create_sync_session,
        batch_size: int = 100,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("Projection runner batch_size must be positive")
        self._registry = registry
        self._catalog = catalog
        self._session_factory = session_factory
        self._batch_size = batch_size
        self._clock = clock
        self._summary_window_started_at = clock()
        self._summary_tick_count = 0
        self._summary_batch_count = 0
        self._summary_processed_snapshot_count = 0
        self._summary_rejected_mapping_set_count = 0
        self._summary_skipped_snapshot_count = 0
        self._summary_first_raw_snapshot_id: int | None = None
        self._summary_last_raw_snapshot_id: int | None = None
        self._failure_observer = ProjectionFailureObserver(clock=clock)

    def run_once(self) -> ProjectionRunReport:
        """Synchronously process at most one bounded raw batch per mapping set."""
        mapping_set_ids = self._list_mapping_set_ids()
        processed_snapshot_count = 0
        processed_mapping_set_count = 0
        blocked_mapping_set_count = 0
        failed_mapping_set_count = 0
        skipped_snapshot_count = 0
        first_raw_snapshot_id: int | None = None
        last_raw_snapshot_id: int | None = None

        for mapping_set_id in mapping_set_ids:
            try:
                result = self._run_mapping_set(mapping_set_id)
            except ProjectionRunnerError as exc:
                self._record_failure(
                    mapping_set_id=mapping_set_id,
                    revision_id=exc.revision_id,
                    raw_snapshot_id=exc.raw_snapshot_id,
                    event_type=exc.event_type,
                    error_code=exc.error_code,
                    error_summary=self._safe_error_summary(exc),
                )
                if exc.event_type == RUNTIME_EVENT_CONTRACT_REJECTED:
                    blocked_mapping_set_count += 1
                else:
                    failed_mapping_set_count += 1
                continue
            except Exception as exc:  # pragma: no cover - defensive conversion for unknown runtime failures
                self._record_failure(
                    mapping_set_id=mapping_set_id,
                    revision_id=None,
                    raw_snapshot_id=None,
                    event_type=RUNTIME_EVENT_FAILED,
                    error_code="runner_unexpected_failure",
                    error_summary=self._safe_error_summary(exc),
                )
                failed_mapping_set_count += 1
                continue

            if result is None:
                continue
            processed_snapshot_count += result.processed_snapshot_count
            processed_mapping_set_count += 1
            skipped_snapshot_count += result.skipped_snapshot_count
            self._failure_observer.record_recovery(
                scope=self._failure_scope(mapping_set_id)
            )
            first_raw_snapshot_id = self._min_snapshot_id(
                first_raw_snapshot_id,
                result.first_raw_snapshot_id,
            )
            last_raw_snapshot_id = self._max_snapshot_id(
                last_raw_snapshot_id,
                result.last_raw_snapshot_id,
            )

        report = ProjectionRunReport(
            processed_snapshot_count=processed_snapshot_count,
            processed_mapping_set_count=processed_mapping_set_count,
            blocked_mapping_set_count=blocked_mapping_set_count,
            failed_mapping_set_count=failed_mapping_set_count,
        )
        self._record_normal_summary(
            report,
            skipped_snapshot_count=skipped_snapshot_count,
            first_raw_snapshot_id=first_raw_snapshot_id,
            last_raw_snapshot_id=last_raw_snapshot_id,
        )
        return report

    def _list_mapping_set_ids(self) -> list[int]:
        db = self._session_factory()
        try:
            return list(
                db.scalars(
                    select(ProjectionMappingSet.id).order_by(ProjectionMappingSet.id)
                )
            )
        finally:
            db.close()

    def _run_mapping_set(self, mapping_set_id: int) -> _MappingSetRunResult | None:
        db = self._session_factory()
        revision_id: int | None = None
        raw_snapshot_id: int | None = None
        recovered_raw_snapshots: list[_RecoveredRawSnapshot] = []
        unavailable_optional_inputs: list[_UnavailableOptionalInput] = []
        try:
            mapping_set = db.scalar(
                select(ProjectionMappingSet)
                .where(ProjectionMappingSet.id == mapping_set_id)
                .with_for_update()
            )
            if mapping_set is None:
                db.rollback()
                return None

            revision, descriptor, bindings, expected_device_id = self._load_runtime_contract(
                db,
                mapping_set,
            )
            revision_id = revision.id
            cursor = db.scalar(
                select(ProjectionRuntimeCursor)
                .where(ProjectionRuntimeCursor.mapping_set_id == mapping_set.id)
                .with_for_update()
            )
            raw_rows = self._read_raw_batch(
                db,
                mapping_set=mapping_set,
                last_raw_snapshot_id=cursor.last_raw_snapshot_id if cursor else None,
            )
            if not raw_rows:
                db.rollback()
                return None
            if cursor is None:
                cursor = ProjectionRuntimeCursor(mapping_set_id=mapping_set.id)
                db.add(cursor)
                db.flush()

            first_raw_snapshot_id = raw_rows[0].id
            for raw in raw_rows:
                raw_snapshot_id = raw.id
                recovery_reason = self._get_recovery_reason(raw)
                if recovery_reason is not None:
                    self._record_recovery_skip(
                        db,
                        mapping_set_id=mapping_set.id,
                        revision_id=revision.id,
                        raw=raw,
                        reason_code=recovery_reason,
                    )
                    recovered_raw_snapshots.append(
                        _RecoveredRawSnapshot(
                            raw_snapshot_id=raw.id,
                            source_quality=raw.quality,
                            reason_code=recovery_reason,
                        )
                    )
                    continue

                try:
                    input_resolution = self._build_inputs(
                        db=db,
                        mapping_set=mapping_set,
                        descriptor=descriptor,
                        revision_id=revision.id,
                        expected_device_id=expected_device_id,
                        bindings=bindings,
                        raw=raw,
                    )
                except ProjectionRunnerError as exc:
                    if exc.error_code != "payload_point_missing":
                        raise
                    self._record_recovery_skip(
                        db,
                        mapping_set_id=mapping_set.id,
                        revision_id=revision.id,
                        raw=raw,
                        reason_code=exc.error_code,
                    )
                    recovered_raw_snapshots.append(
                        _RecoveredRawSnapshot(
                            raw_snapshot_id=raw.id,
                            source_quality=raw.quality,
                            reason_code=exc.error_code,
                        )
                    )
                    continue

                unavailable_optional_inputs.extend(
                    _UnavailableOptionalInput(raw_snapshot_id=raw.id, item=item)
                    for item in input_resolution.unavailable_inputs
                )
                context = ProjectionInvocationContext(
                    plc_key=raw.plc_key,
                    device_id=raw.device_id,
                    db_number=raw.db_number,
                    group_name=raw.group_name,
                    source_snapshot_id=raw.id,
                    collected_at=raw.collected_at,
                    quality=raw.quality,
                )
                try:
                    descriptor.invoke(db, context, input_resolution.inputs)
                except Exception as exc:
                    log_projection_event(
                        "error",
                        "projection_runtime_handler_invocation_failed",
                        mapping_set_id=mapping_set.id,
                        revision_id=revision.id,
                        raw_snapshot_id=raw.id,
                        exception_type=type(exc).__name__,
                    )
                    raise ProjectionRunnerError(
                        "handler_failed",
                        event_type=RUNTIME_EVENT_FAILED,
                        revision_id=revision.id,
                        raw_snapshot_id=raw.id,
                        detail=type(exc).__name__,
                    ) from exc

            cursor.last_raw_snapshot_id = raw_rows[-1].id
            cursor.last_success_at = func.now()
            cursor.last_error_signature = None
            cursor.last_error_at = None
            db.add(
                ProjectionRuntimeAuditEvent(
                    mapping_set_id=mapping_set.id,
                    revision_id=revision.id,
                    event_type=RUNTIME_EVENT_PROCESSED,
                    first_raw_snapshot_id=first_raw_snapshot_id,
                    last_raw_snapshot_id=raw_rows[-1].id,
                    processed_snapshot_count=len(raw_rows),
                )
            )
            db.commit()
        except ProjectionRunnerError:
            db.rollback()
            raise
        except Exception as exc:
            db.rollback()
            raise ProjectionRunnerError(
                "runner_transaction_failed",
                event_type=RUNTIME_EVENT_FAILED,
                revision_id=revision_id,
                raw_snapshot_id=raw_snapshot_id,
                detail=str(exc),
            ) from exc
        finally:
            db.close()

        for recovered_raw in recovered_raw_snapshots:
            log_projection_event(
                "warning",
                "projection_runtime_raw_skipped",
                mapping_set_id=mapping_set_id,
                revision_id=revision.id,
                plc_key=mapping_set.plc_key,
                db_number=mapping_set.db_number,
                group_name=mapping_set.group_name,
                raw_snapshot_id=recovered_raw.raw_snapshot_id,
                source_quality=recovered_raw.source_quality,
                recovery_action="skipped",
                reason_code=recovered_raw.reason_code,
            )
        for unavailable_input in unavailable_optional_inputs:
            item = unavailable_input.item
            log_projection_event(
                "warning",
                "projection_runtime_optional_input_unavailable",
                mapping_set_id=mapping_set_id,
                revision_id=revision.id,
                raw_snapshot_id=unavailable_input.raw_snapshot_id,
                input_key=item.input_key,
                plc_key=item.plc_key,
                db_number=item.db_number,
                group_name=item.group_name,
                point_name=item.point_name,
                source=item.source,
                reason_code=item.reason_code,
            )
        return _MappingSetRunResult(
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            first_raw_snapshot_id=first_raw_snapshot_id,
            last_raw_snapshot_id=raw_rows[-1].id,
            processed_snapshot_count=len(raw_rows),
            skipped_snapshot_count=len(recovered_raw_snapshots),
        )

    def _record_normal_summary(
        self,
        report: ProjectionRunReport,
        *,
        skipped_snapshot_count: int,
        first_raw_snapshot_id: int | None,
        last_raw_snapshot_id: int | None,
    ) -> None:
        self._summary_tick_count += 1
        self._summary_batch_count += report.processed_mapping_set_count
        self._summary_processed_snapshot_count += report.processed_snapshot_count
        self._summary_rejected_mapping_set_count += report.blocked_mapping_set_count
        self._summary_skipped_snapshot_count += skipped_snapshot_count

        self._summary_first_raw_snapshot_id = self._min_snapshot_id(
            self._summary_first_raw_snapshot_id,
            first_raw_snapshot_id,
        )
        self._summary_last_raw_snapshot_id = self._max_snapshot_id(
            self._summary_last_raw_snapshot_id,
            last_raw_snapshot_id,
        )

        now = self._clock()
        if now - self._summary_window_started_at < NORMAL_SUMMARY_WINDOW_SECONDS:
            return

        if self._summary_has_work():
            log_projection_event(
                "info",
                "projection_runtime_summary",
                tick_count=self._summary_tick_count,
                batch_count=self._summary_batch_count,
                processed_snapshot_count=self._summary_processed_snapshot_count,
                rejected_mapping_set_count=self._summary_rejected_mapping_set_count,
                skipped_snapshot_count=self._summary_skipped_snapshot_count,
                first_raw_snapshot_id=self._summary_first_raw_snapshot_id,
                last_raw_snapshot_id=self._summary_last_raw_snapshot_id,
            )
        self._reset_normal_summary(now)

    def _summary_has_work(self) -> bool:
        return any(
            (
                self._summary_batch_count,
                self._summary_rejected_mapping_set_count,
                self._summary_skipped_snapshot_count,
            )
        )

    def _reset_normal_summary(self, now: float) -> None:
        self._summary_window_started_at = now
        self._summary_tick_count = 0
        self._summary_batch_count = 0
        self._summary_processed_snapshot_count = 0
        self._summary_rejected_mapping_set_count = 0
        self._summary_skipped_snapshot_count = 0
        self._summary_first_raw_snapshot_id = None
        self._summary_last_raw_snapshot_id = None

    @staticmethod
    def _min_snapshot_id(current: int | None, candidate: int | None) -> int | None:
        if candidate is None:
            return current
        return candidate if current is None else min(current, candidate)

    @staticmethod
    def _max_snapshot_id(current: int | None, candidate: int | None) -> int | None:
        if candidate is None:
            return current
        return candidate if current is None else max(current, candidate)

    def _load_runtime_contract(
        self,
        db: Session,
        mapping_set: ProjectionMappingSet,
    ) -> tuple[
        ProjectionMappingRevision,
        ProjectionHandlerDescriptor,
        list[ProjectionMappingBinding],
        int,
    ]:
        if mapping_set.active_published_revision_id is None:
            raise ProjectionRunnerError(
                "no_active_published_revision",
                event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
            )
        revision = db.scalar(
            select(ProjectionMappingRevision)
            .where(ProjectionMappingRevision.id == mapping_set.active_published_revision_id)
            .with_for_update()
        )
        if (
            revision is None
            or revision.mapping_set_id != mapping_set.id
            or revision.status != PUBLISHED_REVISION_STATUS
        ):
            raise ProjectionRunnerError(
                "active_published_revision_invalid",
                event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                revision_id=mapping_set.active_published_revision_id,
            )

        descriptor = self._registry.get_optional(mapping_set.handler_key)
        if descriptor is None:
            raise ProjectionRunnerError(
                "handler_not_found",
                event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                revision_id=revision.id,
            )
        if descriptor.snapshot_source != "raw":
            raise ProjectionRunnerError(
                "snapshot_source_not_supported",
                event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                revision_id=revision.id,
            )
        if revision.handler_version != descriptor.handler_version:
            raise ProjectionRunnerError(
                "handler_version_mismatch",
                event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                revision_id=revision.id,
            )
        if not descriptor.allows_group(
            plc_key=mapping_set.plc_key,
            db_number=mapping_set.db_number,
            group_name=mapping_set.group_name,
        ):
            raise ProjectionRunnerError(
                "handler_provenance_not_allowed",
                event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                revision_id=revision.id,
            )

        expected_device_id = get_expected_device_id(mapping_set.plc_key)
        if expected_device_id is None:
            raise ProjectionRunnerError(
                "plc_device_identity_not_supported",
                event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                revision_id=revision.id,
            )

        bindings = list(
            db.scalars(
                select(ProjectionMappingBinding)
                .where(ProjectionMappingBinding.revision_id == revision.id)
                .order_by(ProjectionMappingBinding.id)
            )
        )
        self._validate_bindings(
            mapping_set=mapping_set,
            revision=revision,
            descriptor=descriptor,
            bindings=bindings,
        )
        return revision, descriptor, bindings, expected_device_id

    def _validate_bindings(
        self,
        *,
        mapping_set: ProjectionMappingSet,
        revision: ProjectionMappingRevision,
        descriptor: ProjectionHandlerDescriptor,
        bindings: list[ProjectionMappingBinding],
    ) -> None:
        declared_inputs = {item.input_key: item for item in descriptor.inputs}
        bound_input_keys: set[str] = set()
        primary_group_identity = ProjectionHandlerGroupIdentity(
            plc_key=mapping_set.plc_key,
            db_number=mapping_set.db_number,
            group_name=mapping_set.group_name,
        )
        for binding in bindings:
            input_definition = declared_inputs.get(binding.input_key)
            if input_definition is None:
                raise ProjectionRunnerError(
                    "handler_input_not_declared",
                    event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                    revision_id=revision.id,
                )
            if binding.input_key in bound_input_keys:
                raise ProjectionRunnerError(
                    "binding_input_duplicate",
                    event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                    revision_id=revision.id,
                )
            bound_input_keys.add(binding.input_key)
            binding_snapshot_source = descriptor.binding_snapshot_source(
                input_key=binding.input_key,
                plc_key=binding.plc_key,
                db_number=binding.db_number,
                group_name=binding.group_name,
                primary_group_identity=primary_group_identity,
                catalog=self._catalog,
            )
            if binding_snapshot_source is None:
                raise ProjectionRunnerError(
                    "binding_set_identity_mismatch",
                    event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                    revision_id=revision.id,
                )
            try:
                point = self._catalog.get_point(
                    plc_key=binding.plc_key,
                    db_number=binding.db_number,
                    group_name=binding.group_name,
                    point_name=binding.point_name,
                )
            except SnapshotPolicyCatalogError as exc:
                raise ProjectionRunnerError(
                    "policy_point_not_found",
                    event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                    revision_id=revision.id,
                ) from exc
            if not point.allows_source(binding_snapshot_source):
                raise ProjectionRunnerError(
                    "policy_source_not_allowed",
                    event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                    revision_id=revision.id,
                )
            if point.plc_data_type not in input_definition.accepted_plc_types:
                raise ProjectionRunnerError(
                    "input_type_incompatible",
                    event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                    revision_id=revision.id,
                )

        for input_definition in descriptor.inputs:
            if input_definition.required and input_definition.input_key not in bound_input_keys:
                raise ProjectionRunnerError(
                    "required_input_missing",
                    event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                    revision_id=revision.id,
                )

    def _read_raw_batch(
        self,
        db: Session,
        *,
        mapping_set: ProjectionMappingSet,
        last_raw_snapshot_id: int | None,
    ) -> list[PlcDbBlockRawSnapshot]:
        statement = (
            select(PlcDbBlockRawSnapshot)
            .where(
                PlcDbBlockRawSnapshot.plc_key == mapping_set.plc_key,
                PlcDbBlockRawSnapshot.db_number == mapping_set.db_number,
                PlcDbBlockRawSnapshot.group_name == mapping_set.group_name,
            )
            .order_by(PlcDbBlockRawSnapshot.id)
            .limit(self._batch_size)
        )
        if last_raw_snapshot_id is not None:
            statement = statement.where(PlcDbBlockRawSnapshot.id > last_raw_snapshot_id)
        return list(db.scalars(statement))

    def _build_inputs(
        self,
        *,
        db: Session,
        mapping_set: ProjectionMappingSet,
        descriptor: ProjectionHandlerDescriptor,
        revision_id: int,
        expected_device_id: int,
        bindings: list[ProjectionMappingBinding],
        raw: PlcDbBlockRawSnapshot,
    ) -> ProjectionInputResolution:
        try:
            return resolve_projection_inputs(
                db=db,
                mapping_set=mapping_set,
                descriptor=descriptor,
                bindings=bindings,
                raw=raw,
                expected_device_id=expected_device_id,
                catalog=self._catalog,
            )
        except ProjectionInputResolverError as exc:
            raise ProjectionRunnerError(
                exc.error_code,
                event_type=RUNTIME_EVENT_CONTRACT_REJECTED,
                revision_id=revision_id,
                raw_snapshot_id=raw.id,
            ) from exc

    @staticmethod
    def _get_recovery_reason(raw: PlcDbBlockRawSnapshot) -> str | None:
        if raw.quality != RAW_QUALITY_GOOD:
            return "source_quality_not_good"
        return None

    @staticmethod
    def _record_recovery_skip(
        db: Session,
        *,
        mapping_set_id: int,
        revision_id: int,
        raw: PlcDbBlockRawSnapshot,
        reason_code: str,
    ) -> None:
        """Persist one terminal skip before this batch can advance its cursor."""
        db.add(
            ProjectionRuntimeAuditEvent(
                mapping_set_id=mapping_set_id,
                revision_id=revision_id,
                event_type=RUNTIME_EVENT_SKIPPED,
                first_raw_snapshot_id=raw.id,
                last_raw_snapshot_id=raw.id,
                processed_snapshot_count=0,
                error_code=reason_code,
                error_summary="raw snapshot skipped without owner invocation",
                source_quality=raw.quality,
            )
        )
        db.flush()

    def _record_failure(
        self,
        *,
        mapping_set_id: int,
        revision_id: int | None,
        raw_snapshot_id: int | None,
        event_type: str,
        error_code: str,
        error_summary: str,
    ) -> None:
        db = self._session_factory()
        try:
            cursor = db.scalar(
                select(ProjectionRuntimeCursor)
                .where(ProjectionRuntimeCursor.mapping_set_id == mapping_set_id)
                .with_for_update()
            )
            if cursor is None:
                cursor = ProjectionRuntimeCursor(mapping_set_id=mapping_set_id)
                db.add(cursor)
                db.flush()

            error_signature = ":".join(
                str(value)
                for value in (event_type, error_code, revision_id, raw_snapshot_id)
            )
            if cursor.last_error_signature == error_signature:
                db.rollback()
                return

            cursor.last_error_signature = error_signature
            cursor.last_error_at = func.now()
            db.add(
                ProjectionRuntimeAuditEvent(
                    mapping_set_id=mapping_set_id,
                    revision_id=revision_id,
                    event_type=event_type,
                    first_raw_snapshot_id=raw_snapshot_id,
                    last_raw_snapshot_id=raw_snapshot_id,
                    processed_snapshot_count=0,
                    error_code=error_code,
                    error_summary=error_summary,
                )
            )
            db.commit()
        except Exception as exc:  # pragma: no cover - audit failures must not terminate the API lifecycle loop
            db.rollback()
            self._failure_observer.record_failure(
                scope=self._failure_scope(mapping_set_id),
                failure_category="runtime_audit_persistence",
                exc=exc,
            )
            return
        finally:
            db.close()

        log_projection_event(
            "warning" if event_type == RUNTIME_EVENT_CONTRACT_REJECTED else "error",
            "projection_runtime_mapping_failed",
            mapping_set_id=mapping_set_id,
            revision_id=revision_id,
            raw_snapshot_id=raw_snapshot_id,
            event_type=event_type,
            error_code=error_code,
        )

    @staticmethod
    def _safe_error_summary(exc: BaseException) -> str:
        if isinstance(exc, ProjectionRunnerError):
            return f"{type(exc).__name__}: {exc.error_code}"
        return type(exc).__name__

    @staticmethod
    def _failure_scope(mapping_set_id: int) -> str:
        return f"mapping_set:{mapping_set_id}"
