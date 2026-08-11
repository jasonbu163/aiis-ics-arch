"""
File Path: /backend/tests/test_projection_mapping_models.py
Description: Projection mapping control-plane model contract tests.
Main Features:
    - Locks mapping set, revision, binding, and audit ownership in system
    - Preserves immutable published revisions and full point identity
    - Prevents mapping rows from carrying runtime CRUD or transform behavior
"""
import pytest

from app.system.models.projection_mapping import (
    ProjectionMappingAuditEvent,
    ProjectionMappingBinding,
    ProjectionMappingRevision,
    ProjectionMappingSet,
    ProjectionRuntimeAuditEvent,
    ProjectionRuntimeCursor,
)


pytestmark = pytest.mark.no_db


def _constraint_names(model) -> set[str]:
    return {constraint.name for constraint in model.__table__.constraints if constraint.name}


def test_projection_mapping_models_preserve_the_b6_3_identity_contract():
    assert ProjectionMappingSet.__tablename__ == "projection_mapping_sets"
    assert ProjectionMappingRevision.__tablename__ == "projection_mapping_revisions"
    assert ProjectionMappingBinding.__tablename__ == "projection_mapping_bindings"
    assert ProjectionMappingAuditEvent.__tablename__ == "projection_mapping_audit_events"
    assert ProjectionRuntimeCursor.__tablename__ == "projection_runtime_cursors"
    assert ProjectionRuntimeAuditEvent.__tablename__ == "projection_runtime_audit_events"

    assert {
        "plc_key",
        "db_number",
        "group_name",
        "handler_key",
        "active_published_revision_id",
    } <= set(ProjectionMappingSet.__table__.columns.keys())
    assert {"mapping_set_id", "revision_no", "handler_version", "status", "updated_at"} <= set(
        ProjectionMappingRevision.__table__.columns.keys()
    )
    assert {
        "revision_id",
        "plc_key",
        "db_number",
        "group_name",
        "point_name",
        "input_key",
    } <= set(ProjectionMappingBinding.__table__.columns.keys())

    assert "uq_projection_mapping_set_identity" in _constraint_names(ProjectionMappingSet)
    assert "uq_projection_mapping_revision_number" in _constraint_names(ProjectionMappingRevision)
    assert "ck_projection_mapping_revision_status" in _constraint_names(ProjectionMappingRevision)
    assert "uq_projection_mapping_binding_input" in _constraint_names(ProjectionMappingBinding)
    assert "uq_projection_mapping_binding_point" in _constraint_names(ProjectionMappingBinding)
    assert {"mapping_set_id", "last_raw_snapshot_id", "last_error_signature"} <= set(
        ProjectionRuntimeCursor.__table__.columns.keys()
    )
    assert {
        "mapping_set_id",
        "revision_id",
        "event_type",
        "first_raw_snapshot_id",
        "last_raw_snapshot_id",
        "processed_snapshot_count",
        "error_code",
        "source_quality",
    } <= set(ProjectionRuntimeAuditEvent.__table__.columns.keys())
    assert "uq_projection_runtime_cursor_set" in _constraint_names(ProjectionRuntimeCursor)
    assert "ck_projection_runtime_audit_event_type" in _constraint_names(
        ProjectionRuntimeAuditEvent
    )


def test_projection_mapping_binding_does_not_store_runtime_behavior():
    forbidden_columns = {
        "snapshot_source",
        "transform",
        "target_table",
        "target_field",
        "crud_mode",
        "create_update_mode",
        "python_path",
        "sql_expression",
        "idempotency_key",
    }

    assert forbidden_columns.isdisjoint(ProjectionMappingBinding.__table__.columns)
