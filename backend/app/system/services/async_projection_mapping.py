"""
File Path: /backend/app/system/services/async_projection_mapping.py
Description: Projection mapping revision control-plane application service.
Main Features:
    - Orchestrates draft, validate, publish, copy, and rollback lifecycle changes
    - Validates policy identity, handler contract, and PLC-to-device evidence before activation
    - Commits durable audit evidence atomically without implementing a Projection runner
"""
from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.system.crud.async_projection_mapping import projection_mapping_crud
from app.system.models.projection_mapping import (
    ProjectionMappingAuditEvent,
    ProjectionMappingBinding,
    ProjectionMappingRevision,
    ProjectionMappingSet,
)
from app.system.schemas.projection_mapping import (
    ProjectionMappingBindingInput,
    ProjectionMappingBindingsReplace,
    ProjectionMappingRevisionCopy,
    ProjectionMappingRollback,
    ProjectionMappingSetCreate,
)
from common.error_codes import ErrorCode
from common.exceptions import BusinessException
from common.log import log_event
from projection.policy_catalog import SnapshotPolicyCatalog
from projection.provenance_contract import PILOT_PLC_DEVICE_IDENTITIES
from projection.registry import (
    ProjectionHandlerDescriptor,
    ProjectionHandlerGroupIdentity,
    ProjectionRegistry,
)


DRAFT = "draft"
VALIDATED = "validated"
PUBLISHED = "published"
RETIRED = "retired"
EDITABLE_STATUSES = {DRAFT}
ROLLBACK_TARGET_STATUSES = {VALIDATED, RETIRED}
class ProjectionMappingService:
    """Application service for the database-backed Projection mapping truth."""

    def list_handlers(self, registry: ProjectionRegistry) -> tuple[ProjectionHandlerDescriptor, ...]:
        return registry.handlers

    def list_candidates(
        self,
        *,
        registry: ProjectionRegistry,
        catalog: SnapshotPolicyCatalog,
        plc_key: str,
        db_number: int,
        group_name: str,
        handler_key: str,
    ):
        descriptor = self._require_handler(registry, handler_key)
        snapshot_source = self._candidate_snapshot_source(
            descriptor,
            plc_key=plc_key,
            db_number=db_number,
            group_name=group_name,
            catalog=catalog,
        )
        return catalog.list_group_points(
            plc_key=plc_key,
            db_number=db_number,
            group_name=group_name,
            snapshot_source=snapshot_source,
        )

    async def list_mapping_sets(self, db: AsyncSession) -> list[ProjectionMappingSet]:
        return await projection_mapping_crud.list_sets(db)

    async def get_mapping_set_detail(
        self,
        db: AsyncSession,
        mapping_set_id: int,
    ) -> ProjectionMappingSet:
        mapping_set = await projection_mapping_crud.get_set(
            db,
            mapping_set_id,
            include_revisions=True,
        )
        if mapping_set is None:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_SET_NOT_FOUND)
        mapping_set.revisions.sort(key=lambda revision: revision.revision_no)
        return mapping_set

    async def get_current_revision(
        self,
        db: AsyncSession,
        mapping_set_id: int,
    ) -> tuple[ProjectionMappingSet, ProjectionMappingRevision | None]:
        mapping_set = await projection_mapping_crud.get_set(db, mapping_set_id)
        if mapping_set is None:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_SET_NOT_FOUND)
        if mapping_set.active_published_revision_id is None:
            return mapping_set, None
        revision = await projection_mapping_crud.get_revision(
            db,
            mapping_set.active_published_revision_id,
        )
        if revision is None or revision.mapping_set_id != mapping_set.id or revision.status != PUBLISHED:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_INVALID_TRANSITION)
        return mapping_set, revision

    async def create_mapping_set(
        self,
        db: AsyncSession,
        request: ProjectionMappingSetCreate,
        *,
        actor_user_id: int,
        registry: ProjectionRegistry,
        catalog: SnapshotPolicyCatalog,
    ) -> tuple[ProjectionMappingSet, ProjectionMappingRevision]:
        descriptor = self._require_handler(registry, request.handler_key)
        self._ensure_handler_allows_group(
            descriptor,
            plc_key=request.plc_key,
            db_number=request.db_number,
            group_name=request.group_name,
        )
        candidates = catalog.list_group_points(
            plc_key=request.plc_key,
            db_number=request.db_number,
            group_name=request.group_name,
            snapshot_source=descriptor.snapshot_source,
        )
        if not candidates:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_VALIDATION_FAILED)
        existing = await projection_mapping_crud.get_set_by_identity(
            db,
            plc_key=request.plc_key,
            db_number=request.db_number,
            group_name=request.group_name,
            handler_key=request.handler_key,
        )
        if existing is not None:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_SET_ALREADY_EXISTS)

        mapping_set = ProjectionMappingSet(
            plc_key=request.plc_key,
            db_number=request.db_number,
            group_name=request.group_name,
            handler_key=request.handler_key,
        )
        revision = ProjectionMappingRevision(
            mapping_set=mapping_set,
            revision_no=1,
            handler_version=descriptor.handler_version,
            status=DRAFT,
            change_note=request.change_note,
            created_by_user_id=actor_user_id,
        )
        try:
            await projection_mapping_crud.add(db, mapping_set)
            await projection_mapping_crud.add(db, revision)
            await self._add_audit(
                db,
                mapping_set_id=mapping_set.id,
                revision_id=revision.id,
                action="draft_created",
                actor_user_id=actor_user_id,
                note=request.change_note,
                details={
                    "handler_key": descriptor.handler_key,
                    "handler_version": descriptor.handler_version,
                },
            )
            await self._commit(db)
        except IntegrityError as exc:
            await db.rollback()
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_SET_ALREADY_EXISTS) from exc

        log_event(
            "info",
            "projection_mapping_draft_created",
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            actor_user_id=actor_user_id,
            handler_key=descriptor.handler_key,
            handler_version=descriptor.handler_version,
        )

        return await self._operation_result(db, mapping_set.id, revision.id)

    async def replace_bindings(
        self,
        db: AsyncSession,
        revision_id: int,
        request: ProjectionMappingBindingsReplace,
        *,
        actor_user_id: int,
    ) -> tuple[ProjectionMappingSet, ProjectionMappingRevision]:
        mapping_set, revision = await self._lock_set_and_revision(db, revision_id)
        if revision.status not in EDITABLE_STATUSES:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_REVISION_IMMUTABLE)
        self._ensure_binding_request_is_unique(request.bindings)

        bindings = [
            ProjectionMappingBinding(
                revision_id=revision.id,
                plc_key=item.plc_key,
                db_number=item.db_number,
                group_name=item.group_name,
                point_name=item.point_name,
                input_key=item.input_key,
            )
            for item in request.bindings
        ]
        try:
            await projection_mapping_crud.replace_bindings(db, revision, bindings)
            await self._add_audit(
                db,
                mapping_set_id=mapping_set.id,
                revision_id=revision.id,
                action="bindings_replaced",
                actor_user_id=actor_user_id,
                details={"binding_count": len(bindings)},
            )
            await self._commit(db)
        except IntegrityError as exc:
            await db.rollback()
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_VALIDATION_FAILED) from exc
        log_event(
            "info",
            "projection_mapping_bindings_replaced",
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            actor_user_id=actor_user_id,
            binding_count=len(bindings),
        )
        return await self._operation_result(db, mapping_set.id, revision.id)

    async def validate_revision(
        self,
        db: AsyncSession,
        revision_id: int,
        *,
        actor_user_id: int,
        registry: ProjectionRegistry,
        catalog: SnapshotPolicyCatalog,
    ) -> tuple[ProjectionMappingSet, ProjectionMappingRevision]:
        mapping_set, revision = await self._lock_set_and_revision(db, revision_id)
        if revision.status != DRAFT:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_REVISION_IMMUTABLE)

        report = await self._validate_revision_data(
            db,
            mapping_set,
            revision,
            registry=registry,
            catalog=catalog,
        )
        revision.validation_report = report
        if report["valid"]:
            revision.status = VALIDATED
            revision.validated_at = func.now()
            revision.validated_by_user_id = actor_user_id
            action = "validated"
            log_level = "info"
            event_name = "projection_mapping_validation_succeeded"
        else:
            action = "validation_failed"
            log_level = "warning"
            event_name = "projection_mapping_validation_failed"
        await self._add_audit(
            db,
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            action=action,
            actor_user_id=actor_user_id,
            details=report,
        )
        await self._commit(db)
        log_event(
            log_level,
            event_name,
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            actor_user_id=actor_user_id,
            observed_device_ids=report["observed_device_ids"],
            error_codes=report["errors"],
        )
        return await self._operation_result(db, mapping_set.id, revision.id)

    async def publish_revision(
        self,
        db: AsyncSession,
        revision_id: int,
        *,
        actor_user_id: int,
        registry: ProjectionRegistry,
        catalog: SnapshotPolicyCatalog,
    ) -> tuple[ProjectionMappingSet, ProjectionMappingRevision]:
        mapping_set, revision = await self._lock_set_and_revision(db, revision_id)
        if revision.status != VALIDATED:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_INVALID_TRANSITION)
        current_revision = await self._lock_current_revision(db, mapping_set)
        report = await self._validate_revision_data(
            db,
            mapping_set,
            revision,
            registry=registry,
            catalog=catalog,
        )
        if not report["valid"]:
            await self._record_activation_rejection(
                db,
                mapping_set=mapping_set,
                revision=revision,
                actor_user_id=actor_user_id,
                action="publish_rejected",
                report=report,
            )
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_VALIDATION_FAILED)

        old_active_revision_id = current_revision.id if current_revision else None
        if current_revision is not None:
            current_revision.status = RETIRED
        revision.status = PUBLISHED
        revision.published_at = func.now()
        revision.published_by_user_id = actor_user_id
        revision.validation_report = report
        mapping_set.active_published_revision_id = revision.id
        await self._add_audit(
            db,
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            action="published",
            actor_user_id=actor_user_id,
            details={"previous_active_revision_id": old_active_revision_id},
        )
        await self._commit(db)
        log_event(
            "info",
            "projection_mapping_published",
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            actor_user_id=actor_user_id,
            previous_active_revision_id=old_active_revision_id,
        )
        return await self._operation_result(db, mapping_set.id, revision.id)

    async def copy_revision(
        self,
        db: AsyncSession,
        source_revision_id: int,
        request: ProjectionMappingRevisionCopy,
        *,
        actor_user_id: int,
        registry: ProjectionRegistry,
    ) -> tuple[ProjectionMappingSet, ProjectionMappingRevision]:
        mapping_set, source_revision = await self._lock_set_and_revision(db, source_revision_id)
        if source_revision.status == DRAFT:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_INVALID_TRANSITION)
        descriptor = self._require_handler(registry, mapping_set.handler_key)
        revision = ProjectionMappingRevision(
            mapping_set_id=mapping_set.id,
            revision_no=await projection_mapping_crud.get_next_revision_no(db, mapping_set.id),
            handler_version=descriptor.handler_version,
            status=DRAFT,
            change_note=request.change_note,
            created_by_user_id=actor_user_id,
        )
        await projection_mapping_crud.add(db, revision)
        copied_bindings = [
            ProjectionMappingBinding(
                revision_id=revision.id,
                plc_key=binding.plc_key,
                db_number=binding.db_number,
                group_name=binding.group_name,
                point_name=binding.point_name,
                input_key=binding.input_key,
            )
            for binding in source_revision.bindings
        ]
        try:
            await projection_mapping_crud.replace_bindings(db, revision, copied_bindings)
            await self._add_audit(
                db,
                mapping_set_id=mapping_set.id,
                revision_id=revision.id,
                action="revision_copied",
                actor_user_id=actor_user_id,
                note=request.change_note,
                details={"source_revision_id": source_revision.id},
            )
            await self._commit(db)
        except IntegrityError as exc:
            await db.rollback()
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_VALIDATION_FAILED) from exc
        log_event(
            "info",
            "projection_mapping_revision_copied",
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            source_revision_id=source_revision.id,
            actor_user_id=actor_user_id,
        )
        return await self._operation_result(db, mapping_set.id, revision.id)

    async def rollback_revision(
        self,
        db: AsyncSession,
        mapping_set_id: int,
        request: ProjectionMappingRollback,
        *,
        actor_user_id: int,
        registry: ProjectionRegistry,
        catalog: SnapshotPolicyCatalog,
    ) -> tuple[ProjectionMappingSet, ProjectionMappingRevision]:
        mapping_set = await projection_mapping_crud.get_set(db, mapping_set_id, for_update=True)
        if mapping_set is None:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_SET_NOT_FOUND)
        revision = await projection_mapping_crud.get_revision(db, request.revision_id, for_update=True)
        if revision is None:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_REVISION_NOT_FOUND)
        if revision.mapping_set_id != mapping_set.id:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_INVALID_TRANSITION)
        if revision.status not in ROLLBACK_TARGET_STATUSES:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_INVALID_TRANSITION)
        current_revision = await self._lock_current_revision(db, mapping_set, required=True)
        report = await self._validate_revision_data(
            db,
            mapping_set,
            revision,
            registry=registry,
            catalog=catalog,
        )
        if not report["valid"]:
            await self._record_activation_rejection(
                db,
                mapping_set=mapping_set,
                revision=revision,
                actor_user_id=actor_user_id,
                action="rollback_rejected",
                report=report,
            )
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_VALIDATION_FAILED)

        current_revision.status = RETIRED
        revision.status = PUBLISHED
        revision.published_at = func.now()
        revision.published_by_user_id = actor_user_id
        revision.validation_report = report
        mapping_set.active_published_revision_id = revision.id
        await self._add_audit(
            db,
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            action="rolled_back",
            actor_user_id=actor_user_id,
            note=request.change_note,
            details={"previous_active_revision_id": current_revision.id},
        )
        await self._commit(db)
        log_event(
            "info",
            "projection_mapping_rolled_back",
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            actor_user_id=actor_user_id,
            previous_active_revision_id=current_revision.id,
        )
        return await self._operation_result(db, mapping_set.id, revision.id)

    async def _lock_set_and_revision(
        self,
        db: AsyncSession,
        revision_id: int,
    ) -> tuple[ProjectionMappingSet, ProjectionMappingRevision]:
        initial_revision = await projection_mapping_crud.get_revision(db, revision_id)
        if initial_revision is None:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_REVISION_NOT_FOUND)
        mapping_set = await projection_mapping_crud.get_set(
            db,
            initial_revision.mapping_set_id,
            for_update=True,
        )
        if mapping_set is None:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_SET_NOT_FOUND)
        revision = await projection_mapping_crud.get_revision(db, revision_id, for_update=True)
        if revision is None or revision.mapping_set_id != mapping_set.id:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_INVALID_TRANSITION)
        return mapping_set, revision

    async def _lock_current_revision(
        self,
        db: AsyncSession,
        mapping_set: ProjectionMappingSet,
        *,
        required: bool = False,
    ) -> ProjectionMappingRevision | None:
        if mapping_set.active_published_revision_id is None:
            if required:
                raise BusinessException(ErrorCode.PROJECTION_MAPPING_INVALID_TRANSITION)
            return None
        revision = await projection_mapping_crud.get_revision(
            db,
            mapping_set.active_published_revision_id,
            for_update=True,
        )
        if revision is None or revision.mapping_set_id != mapping_set.id or revision.status != PUBLISHED:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_INVALID_TRANSITION)
        return revision

    async def _validate_revision_data(
        self,
        db: AsyncSession,
        mapping_set: ProjectionMappingSet,
        revision: ProjectionMappingRevision,
        *,
        registry: ProjectionRegistry,
        catalog: SnapshotPolicyCatalog,
    ) -> dict[str, object]:
        errors: list[str] = []
        descriptor = registry.get_optional(mapping_set.handler_key)
        raw_fact_count, observed_device_ids = await projection_mapping_crud.get_raw_device_identity(
            db,
            plc_key=mapping_set.plc_key,
            db_number=mapping_set.db_number,
            group_name=mapping_set.group_name,
        )
        report: dict[str, object] = {
            "valid": False,
            "errors": errors,
            "handler_key": mapping_set.handler_key,
            "handler_version": revision.handler_version,
            "snapshot_source": descriptor.snapshot_source if descriptor else None,
            "bound_inputs": sorted(binding.input_key for binding in revision.bindings),
            "observed_device_ids": observed_device_ids,
            "raw_fact_count": raw_fact_count,
        }
        if descriptor is None:
            self._append_error(errors, "handler_not_found")
        else:
            report["required_inputs"] = sorted(
                input_definition.input_key
                for input_definition in descriptor.inputs
                if input_definition.required
            )
            if revision.handler_version != descriptor.handler_version:
                self._append_error(errors, "handler_version_mismatch")
            if not descriptor.allows_group(
                plc_key=mapping_set.plc_key,
                db_number=mapping_set.db_number,
                group_name=mapping_set.group_name,
            ):
                self._append_error(errors, "handler_provenance_not_allowed")
            if not catalog.list_group_points(
                plc_key=mapping_set.plc_key,
                db_number=mapping_set.db_number,
                group_name=mapping_set.group_name,
                snapshot_source=descriptor.snapshot_source,
            ):
                self._append_error(errors, "policy_group_not_available")
            self._validate_bindings(mapping_set, revision, descriptor, catalog, errors)

        expected_device_id = PILOT_PLC_DEVICE_IDENTITIES.get(mapping_set.plc_key)
        report["expected_device_id"] = expected_device_id
        if expected_device_id is None:
            self._append_error(errors, "plc_device_identity_not_supported")
        elif raw_fact_count == 0:
            self._append_error(errors, "plc_device_identity_missing")
        elif observed_device_ids != [expected_device_id]:
            self._append_error(errors, "plc_device_identity_conflict")

        report["valid"] = not errors
        return report

    def _validate_bindings(
        self,
        mapping_set: ProjectionMappingSet,
        revision: ProjectionMappingRevision,
        descriptor: ProjectionHandlerDescriptor,
        catalog: SnapshotPolicyCatalog,
        errors: list[str],
    ) -> None:
        declared_inputs = {item.input_key: item for item in descriptor.inputs}
        bound_input_keys: list[str] = []
        bound_point_identities: set[tuple[str, int, str, str]] = set()
        primary_group_identity = ProjectionHandlerGroupIdentity(
            plc_key=mapping_set.plc_key,
            db_number=mapping_set.db_number,
            group_name=mapping_set.group_name,
        )
        for binding in revision.bindings:
            binding_identity = (
                binding.plc_key,
                binding.db_number,
                binding.group_name,
            )
            point_identity = (*binding_identity, binding.point_name)
            if binding.input_key not in declared_inputs:
                self._append_error(errors, "handler_input_not_declared")
                continue
            binding_snapshot_source = descriptor.binding_snapshot_source(
                input_key=binding.input_key,
                plc_key=binding.plc_key,
                db_number=binding.db_number,
                group_name=binding.group_name,
                primary_group_identity=primary_group_identity,
                catalog=catalog,
            )
            if binding_snapshot_source is None:
                self._append_error(errors, "binding_set_identity_mismatch")
                continue
            bound_input_keys.append(binding.input_key)
            if point_identity in bound_point_identities:
                self._append_error(errors, "binding_point_duplicate")
            bound_point_identities.add(point_identity)
            try:
                point = catalog.get_point(
                    plc_key=binding.plc_key,
                    db_number=binding.db_number,
                    group_name=binding.group_name,
                    point_name=binding.point_name,
                )
            except ValueError:
                self._append_error(errors, "policy_point_not_found")
                continue
            if not point.allows_source(binding_snapshot_source):
                self._append_error(errors, "policy_source_not_allowed")
            input_definition = declared_inputs[binding.input_key]
            if point.plc_data_type not in input_definition.accepted_plc_types:
                self._append_error(errors, "input_type_incompatible")

        if len(set(bound_input_keys)) != len(bound_input_keys):
            self._append_error(errors, "binding_input_duplicate")
        for input_definition in descriptor.inputs:
            if input_definition.required and input_definition.input_key not in bound_input_keys:
                self._append_error(errors, "required_input_missing")

    async def _record_activation_rejection(
        self,
        db: AsyncSession,
        *,
        mapping_set: ProjectionMappingSet,
        revision: ProjectionMappingRevision,
        actor_user_id: int,
        action: str,
        report: dict[str, object],
    ) -> None:
        revision.validation_report = report
        await self._add_audit(
            db,
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            action=action,
            actor_user_id=actor_user_id,
            details=report,
        )
        await self._commit(db)
        log_event(
            "warning",
            "projection_mapping_activation_rejected",
            mapping_set_id=mapping_set.id,
            revision_id=revision.id,
            actor_user_id=actor_user_id,
            action=action,
            error_codes=report["errors"],
        )

    async def _operation_result(
        self,
        db: AsyncSession,
        mapping_set_id: int,
        revision_id: int,
    ) -> tuple[ProjectionMappingSet, ProjectionMappingRevision]:
        mapping_set = await projection_mapping_crud.get_set(db, mapping_set_id)
        revision = await projection_mapping_crud.get_revision(db, revision_id)
        if mapping_set is None or revision is None:
            raise RuntimeError("Projection mapping rows disappeared after a committed mutation")
        return mapping_set, revision

    def _require_handler(
        self,
        registry: ProjectionRegistry,
        handler_key: str,
    ) -> ProjectionHandlerDescriptor:
        descriptor = registry.get_optional(handler_key)
        if descriptor is None:
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_HANDLER_NOT_FOUND)
        return descriptor

    def _ensure_handler_allows_group(
        self,
        descriptor: ProjectionHandlerDescriptor,
        *,
        plc_key: str,
        db_number: int,
        group_name: str,
    ) -> None:
        if not descriptor.allows_group(
            plc_key=plc_key,
            db_number=db_number,
            group_name=group_name,
        ):
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_HANDLER_PROVENANCE_NOT_ALLOWED)

    def _candidate_snapshot_source(
        self,
        descriptor: ProjectionHandlerDescriptor,
        *,
        plc_key: str,
        db_number: int,
        group_name: str,
        catalog: SnapshotPolicyCatalog,
    ) -> str:
        if descriptor.allows_group(
            plc_key=plc_key,
            db_number=db_number,
            group_name=group_name,
        ):
            return descriptor.snapshot_source
        if descriptor.allows_auxiliary_group(
            plc_key=plc_key,
            db_number=db_number,
            group_name=group_name,
            catalog=catalog,
        ):
            return "latest"
        raise BusinessException(ErrorCode.PROJECTION_MAPPING_HANDLER_PROVENANCE_NOT_ALLOWED)

    def _ensure_binding_request_is_unique(
        self,
        bindings: list[ProjectionMappingBindingInput],
    ) -> None:
        input_keys = [binding.input_key for binding in bindings]
        point_identities = [
            (binding.plc_key, binding.db_number, binding.group_name, binding.point_name)
            for binding in bindings
        ]
        if len(set(input_keys)) != len(input_keys) or len(set(point_identities)) != len(point_identities):
            raise BusinessException(ErrorCode.PROJECTION_MAPPING_VALIDATION_FAILED)

    async def _add_audit(
        self,
        db: AsyncSession,
        *,
        mapping_set_id: int,
        revision_id: int | None,
        action: str,
        actor_user_id: int,
        note: str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        await projection_mapping_crud.add_audit_event(
            db,
            ProjectionMappingAuditEvent(
                mapping_set_id=mapping_set_id,
                revision_id=revision_id,
                action=action,
                actor_user_id=actor_user_id,
                note=note,
                details=details,
            ),
        )

    async def _commit(self, db: AsyncSession) -> None:
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    def _append_error(errors: list[str], error_code: str) -> None:
        if error_code not in errors:
            errors.append(error_code)


projection_mapping_service = ProjectionMappingService()
