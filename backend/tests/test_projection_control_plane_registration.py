"""
File Path: /backend/tests/test_projection_control_plane_registration.py
Description: Projection control-plane startup registration tests.
Main Features:
    - Builds the handler registry once during FastAPI composition
    - Loads the read-only snapshot-policy catalog before API requests
    - Avoids request-time filesystem discovery for mapping endpoints
"""
import pytest

from core.registrar import create_app
from projection.policy_catalog import SnapshotPolicyCatalog
from projection.registry import ProjectionRegistry


pytestmark = pytest.mark.no_db


def test_application_composition_builds_projection_control_plane_catalogs_once():
    app = create_app(testing=True)

    assert isinstance(app.state.projection_registry, ProjectionRegistry)
    assert isinstance(app.state.snapshot_policy_catalog, SnapshotPolicyCatalog)
    assert len(app.state.projection_registry.handlers) >= 8
    assert len({handler.handler_key for handler in app.state.projection_registry.handlers}) == len(app.state.projection_registry.handlers)
    assert {handler.owner_module for handler in app.state.projection_registry.handlers} .issuperset({"equipment", "performance", "monitor"})
    assert app.state.snapshot_policy_catalog.get_point(
        plc_key="example_plc",
        db_number=1,
        group_name="example_group",
        point_name="example_value",
    ).raw_enabled is False
