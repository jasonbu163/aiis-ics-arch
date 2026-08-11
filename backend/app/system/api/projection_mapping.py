"""
File Path: /backend/app/system/api/projection_mapping.py
Description: Projection mapping revision control-plane HTTP adapters.
Main Features:
    - Exposes read-only handler and PLC policy candidate catalogs
    - Delegates admin draft, validation, publication, copy, and rollback intents to the Service
    - Keeps runtime execution, PLC polling, and mapping transforms outside the API surface
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.system.schemas.projection_mapping import (
    ProjectionHandlerCatalogOut,
    ProjectionHandlerGroupIdentityOut,
    ProjectionHandlerInputOut,
    ProjectionHandlerOut,
    ProjectionMappingBindingsReplace,
    ProjectionMappingCurrentOut,
    ProjectionMappingOperationOut,
    ProjectionMappingRevisionCopy,
    ProjectionMappingRevisionOut,
    ProjectionMappingRollback,
    ProjectionMappingSetCreate,
    ProjectionMappingSetDetailOut,
    ProjectionMappingSetListOut,
    ProjectionMappingSetOut,
    SnapshotPolicyCandidateCatalogOut,
    SnapshotPolicyPointOut,
)
from app.system.services.async_projection_mapping import projection_mapping_service
from app.user.models.user import User
from common.response import StandardResponse
from core.deps import require_permissions
from database import get_db
from projection.policy_catalog import SnapshotPolicyCatalog
from projection.registry import ProjectionRegistry


router = APIRouter(prefix="/projection-mappings", tags=["System - Projection Mapping"])


def _projection_registry(request: Request) -> ProjectionRegistry:
    return request.app.state.projection_registry


def _snapshot_policy_catalog(request: Request) -> SnapshotPolicyCatalog:
    return request.app.state.snapshot_policy_catalog


def _handler_out(handler, catalog: SnapshotPolicyCatalog) -> ProjectionHandlerOut:
    return ProjectionHandlerOut(
        handler_key=handler.handler_key,
        owner_module=handler.owner_module,
        description=handler.description,
        snapshot_source=handler.snapshot_source,
        handler_version=handler.handler_version,
        allowed_group_identities=[
            ProjectionHandlerGroupIdentityOut(
                plc_key=identity.plc_key,
                db_number=identity.db_number,
                group_name=identity.group_name,
            )
            for identity in handler.allowed_group_identities
        ],
        auxiliary_group_identities=[
            ProjectionHandlerGroupIdentityOut(
                plc_key=identity.plc_key,
                db_number=identity.db_number,
                group_name=identity.group_name,
            )
            for identity in handler.resolved_auxiliary_group_identities(catalog=catalog)
        ],
        inputs=[
            ProjectionHandlerInputOut(
                input_key=input_definition.input_key,
                type=input_definition.type,
                required=input_definition.required,
                description=input_definition.description,
                accepted_plc_types=list(input_definition.accepted_plc_types),
            )
            for input_definition in handler.inputs
        ],
    )


def _operation_out(mapping_set, revision) -> ProjectionMappingOperationOut:
    return ProjectionMappingOperationOut(
        mapping_set=ProjectionMappingSetOut.model_validate(mapping_set),
        revision=ProjectionMappingRevisionOut.model_validate(revision),
    )


@router.get(
    "/handlers",
    response_model=StandardResponse[ProjectionHandlerCatalogOut],
)
async def list_projection_handlers(
    request: Request,
    current_user: User = Depends(require_permissions("projection-mapping")),
):
    """Return only explicitly registered Projection handler metadata."""
    registry = _projection_registry(request)
    catalog = _snapshot_policy_catalog(request)
    return StandardResponse(
        data=ProjectionHandlerCatalogOut(
            items=[
                _handler_out(handler, catalog)
                for handler in projection_mapping_service.list_handlers(registry)
            ]
        )
    )


@router.get(
    "/candidates",
    response_model=StandardResponse[SnapshotPolicyCandidateCatalogOut],
)
async def list_projection_mapping_candidates(
    request: Request,
    plc_key: str = Query(..., alias="plcKey", min_length=1, max_length=80),
    db_number: int = Query(..., alias="dbNumber", ge=1),
    group_name: str = Query(..., alias="groupName", min_length=1, max_length=120),
    handler_key: str = Query(..., alias="handlerKey", min_length=1, max_length=160),
    current_user: User = Depends(require_permissions("projection-mapping")),
):
    """Return policy points that match the handler's immutable snapshot source."""
    candidates = projection_mapping_service.list_candidates(
        registry=_projection_registry(request),
        catalog=_snapshot_policy_catalog(request),
        plc_key=plc_key,
        db_number=db_number,
        group_name=group_name,
        handler_key=handler_key,
    )
    return StandardResponse(
        data=SnapshotPolicyCandidateCatalogOut(
            items=[SnapshotPolicyPointOut.model_validate(point) for point in candidates]
        )
    )


@router.get(
    "/sets",
    response_model=StandardResponse[ProjectionMappingSetListOut],
)
async def list_projection_mapping_sets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("projection-mapping")),
):
    """List persisted mapping identities and their currently active revision pointer."""
    mapping_sets = await projection_mapping_service.list_mapping_sets(db)
    return StandardResponse(
        data=ProjectionMappingSetListOut(
            items=[ProjectionMappingSetOut.model_validate(mapping_set) for mapping_set in mapping_sets]
        )
    )


@router.get(
    "/sets/{mapping_set_id}",
    response_model=StandardResponse[ProjectionMappingSetDetailOut],
)
async def get_projection_mapping_set(
    mapping_set_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("projection-mapping")),
):
    """Return revision history for one stable mapping set identity."""
    mapping_set = await projection_mapping_service.get_mapping_set_detail(db, mapping_set_id)
    return StandardResponse(data=ProjectionMappingSetDetailOut.model_validate(mapping_set))


@router.get(
    "/sets/{mapping_set_id}/current",
    response_model=StandardResponse[ProjectionMappingCurrentOut],
)
async def get_projection_mapping_current_revision(
    mapping_set_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("projection-mapping")),
):
    """Return the active published revision without executing it."""
    mapping_set, revision = await projection_mapping_service.get_current_revision(db, mapping_set_id)
    return StandardResponse(
        data=ProjectionMappingCurrentOut(
            mapping_set=ProjectionMappingSetOut.model_validate(mapping_set),
            revision=ProjectionMappingRevisionOut.model_validate(revision) if revision else None,
        )
    )


@router.post(
    "/sets",
    response_model=StandardResponse[ProjectionMappingOperationOut],
)
async def create_projection_mapping_set(
    request: Request,
    data: ProjectionMappingSetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("projection-mapping-manage")),
):
    """Create a stable mapping set and its initial editable draft revision."""
    mapping_set, revision = await projection_mapping_service.create_mapping_set(
        db,
        data,
        actor_user_id=current_user.id,
        registry=_projection_registry(request),
        catalog=_snapshot_policy_catalog(request),
    )
    return StandardResponse(data=_operation_out(mapping_set, revision))


@router.put(
    "/revisions/{revision_id}/bindings",
    response_model=StandardResponse[ProjectionMappingOperationOut],
)
async def replace_projection_mapping_bindings(
    revision_id: int,
    data: ProjectionMappingBindingsReplace,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("projection-mapping-manage")),
):
    """Replace one draft's point-to-input identity bindings."""
    mapping_set, revision = await projection_mapping_service.replace_bindings(
        db,
        revision_id,
        data,
        actor_user_id=current_user.id,
    )
    return StandardResponse(data=_operation_out(mapping_set, revision))


@router.post(
    "/revisions/{revision_id}/validate",
    response_model=StandardResponse[ProjectionMappingOperationOut],
)
async def validate_projection_mapping_revision(
    request: Request,
    revision_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("projection-mapping-manage")),
):
    """Persist a non-runtime validation report for one editable draft."""
    mapping_set, revision = await projection_mapping_service.validate_revision(
        db,
        revision_id,
        actor_user_id=current_user.id,
        registry=_projection_registry(request),
        catalog=_snapshot_policy_catalog(request),
    )
    return StandardResponse(data=_operation_out(mapping_set, revision))


@router.post(
    "/revisions/{revision_id}/publish",
    response_model=StandardResponse[ProjectionMappingOperationOut],
)
async def publish_projection_mapping_revision(
    request: Request,
    revision_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("projection-mapping-manage")),
):
    """Atomically retire the old active revision and publish a validated target."""
    mapping_set, revision = await projection_mapping_service.publish_revision(
        db,
        revision_id,
        actor_user_id=current_user.id,
        registry=_projection_registry(request),
        catalog=_snapshot_policy_catalog(request),
    )
    return StandardResponse(data=_operation_out(mapping_set, revision))


@router.post(
    "/revisions/{revision_id}/copy",
    response_model=StandardResponse[ProjectionMappingOperationOut],
)
async def copy_projection_mapping_revision(
    request: Request,
    revision_id: int,
    data: ProjectionMappingRevisionCopy,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("projection-mapping-manage")),
):
    """Copy an immutable revision into a new editable draft revision."""
    mapping_set, revision = await projection_mapping_service.copy_revision(
        db,
        revision_id,
        data,
        actor_user_id=current_user.id,
        registry=_projection_registry(request),
    )
    return StandardResponse(data=_operation_out(mapping_set, revision))


@router.post(
    "/sets/{mapping_set_id}/rollback",
    response_model=StandardResponse[ProjectionMappingOperationOut],
)
async def rollback_projection_mapping_revision(
    request: Request,
    mapping_set_id: int,
    data: ProjectionMappingRollback,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permissions("projection-mapping-manage")),
):
    """Atomically reactivate one historical validated revision for its own mapping set."""
    mapping_set, revision = await projection_mapping_service.rollback_revision(
        db,
        mapping_set_id,
        data,
        actor_user_id=current_user.id,
        registry=_projection_registry(request),
        catalog=_snapshot_policy_catalog(request),
    )
    return StandardResponse(data=_operation_out(mapping_set, revision))
