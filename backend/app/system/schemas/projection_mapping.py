"""
File Path: /backend/app/system/schemas/projection_mapping.py
Description: Projection mapping revision control-plane API schemas.
Main Features:
    - Defines read-only handler and policy candidate catalog contracts
    - Accepts only mapping set identity and point-to-input bindings
    - Exposes draft, validation, publication, and rollback state without runtime behavior fields
"""
from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field

from common.schema_base import ApiSchema, to_camel


class ProjectionHandlerInputOut(ApiSchema):
    input_key: str
    type: str
    required: bool
    description: str
    accepted_plc_types: list[str]


class ProjectionHandlerGroupIdentityOut(ApiSchema):
    plc_key: str
    db_number: int
    group_name: str


class ProjectionHandlerOut(ApiSchema):
    handler_key: str
    owner_module: str
    description: str
    snapshot_source: str
    handler_version: str
    allowed_group_identities: list[ProjectionHandlerGroupIdentityOut]
    auxiliary_group_identities: list[ProjectionHandlerGroupIdentityOut]
    inputs: list[ProjectionHandlerInputOut]


class ProjectionHandlerCatalogOut(ApiSchema):
    items: list[ProjectionHandlerOut]


class SnapshotPolicyPointOut(ApiSchema):
    plc_key: str
    db_number: int
    group_name: str
    point_name: str
    plc_data_type: str
    source_name: str | None = None
    description: str | None = None


class SnapshotPolicyCandidateCatalogOut(ApiSchema):
    items: list[SnapshotPolicyPointOut]


class ProjectionMappingInputSchema(ApiSchema):
    """Reject fields that could widen a mapping into a runtime behavior surface."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra="forbid",
    )


class ProjectionMappingSetCreate(ProjectionMappingInputSchema):
    plc_key: str = Field(..., min_length=1, max_length=80)
    db_number: int = Field(..., ge=1)
    group_name: str = Field(..., min_length=1, max_length=120)
    handler_key: str = Field(..., min_length=1, max_length=160)
    change_note: str | None = Field(default=None, max_length=2000)


class ProjectionMappingBindingInput(ProjectionMappingInputSchema):
    plc_key: str = Field(..., min_length=1, max_length=80)
    db_number: int = Field(..., ge=1)
    group_name: str = Field(..., min_length=1, max_length=120)
    point_name: str = Field(..., min_length=1, max_length=180)
    input_key: str = Field(..., min_length=1, max_length=100)


class ProjectionMappingBindingsReplace(ProjectionMappingInputSchema):
    bindings: list[ProjectionMappingBindingInput] = Field(default_factory=list, max_length=100)


class ProjectionMappingRevisionCopy(ProjectionMappingInputSchema):
    change_note: str | None = Field(default=None, max_length=2000)


class ProjectionMappingRollback(ProjectionMappingInputSchema):
    revision_id: int = Field(..., ge=1)
    change_note: str | None = Field(default=None, max_length=2000)


class ProjectionMappingBindingOut(ApiSchema):
    plc_key: str
    db_number: int
    group_name: str
    point_name: str
    input_key: str


class ProjectionMappingRevisionOut(ApiSchema):
    id: int
    mapping_set_id: int
    revision_no: int
    handler_version: str
    status: str
    change_note: str | None = None
    validation_report: dict[str, Any] | None = None
    created_by_user_id: int | None = None
    validated_by_user_id: int | None = None
    published_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime
    validated_at: datetime | None = None
    published_at: datetime | None = None
    bindings: list[ProjectionMappingBindingOut] = Field(default_factory=list)


class ProjectionMappingSetOut(ApiSchema):
    id: int
    plc_key: str
    db_number: int
    group_name: str
    handler_key: str
    active_published_revision_id: int | None = None
    created_at: datetime
    updated_at: datetime


class ProjectionMappingSetDetailOut(ProjectionMappingSetOut):
    revisions: list[ProjectionMappingRevisionOut] = Field(default_factory=list)


class ProjectionMappingSetListOut(ApiSchema):
    items: list[ProjectionMappingSetOut]


class ProjectionMappingOperationOut(ApiSchema):
    mapping_set: ProjectionMappingSetOut
    revision: ProjectionMappingRevisionOut


class ProjectionMappingCurrentOut(ApiSchema):
    mapping_set: ProjectionMappingSetOut
    revision: ProjectionMappingRevisionOut | None = None
