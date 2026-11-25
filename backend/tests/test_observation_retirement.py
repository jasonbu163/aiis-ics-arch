"""核对当前 schema revision、旧入口退出及冻结业务合同边界。"""

from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from httpx import ASGITransport, AsyncClient
import pytest

from app.equipment_observation.domain import ObservationError, identifier
from common.integration.canonical import canonical_bytes
from core.registrar import create_app
from database import Base, get_db

pytestmark = pytest.mark.no_db

RETIRED_TABLES = frozenset("""
    equipment_status_r8_archive process_monitor_r8_archive equipment_metric_configs_r8_archive
    equipment_metric_slot_bindings_r8_archive equipment_card_configs_r8_archive
    monitor_curve_group_configs_r8_archive equipment_drive equipment_temperature
    equipment_production_parameters equipment_temperature_samples equipment_temperature_sample_receipts
    equipment_mapping_receipts equipment_integration_receipts monitor_history_process_curves
    monitor_history_energy_consumptions monitor_mapping_receipts monitor_integration_receipts
    monitor_collector_states
""".split())
RETIRED_OPERATIONS = {
    ("GET", "/equipment/admin/r8-archive"),
    ("GET", "/equipment/admin/r8-archive/config"),
    ("GET", "/monitor/admin/r8-archive"),
    ("GET", "/equipment/drive"),
    ("GET", "/equipment/temperature-control"),
    ("GET", "/equipment/production-parameters"),
    ("GET", "/equipment/temperature-sample-dashboard"),
    ("GET", "/monitor/temperature"),
    ("GET", "/monitor/energy"),
    ("GET", "/monitor/collector/status"),
    ("POST", "/integration/equipment/temperature-samples"),
    ("POST", "/integration/equipment/drive-samples"),
    ("POST", "/integration/equipment/production-parameter-samples"),
    ("POST", "/integration/monitor/process-curve-samples"),
    *( (method, path) for method in ("GET", "POST") for path in (
        "/equipment/temperature-samples", "/equipment/drive-samples",
        "/equipment/production-parameter-samples", "/monitor/process-curve-samples",
    )),
}


@pytest.fixture(scope="module")
def retirement_graph():
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    return ScriptDirectory.from_config(config)


def test_single_forward_only_revision_with_precise_retirement_allowlist(retirement_graph):
    graph = retirement_graph
    assert graph.get_heads() == ["b52e9c416a07"]
    script = graph.get_revision("c9e1a3b5d720")
    assert script.down_revision == "ae20b4d6f831"
    assert set(script.module.RETIRED_TABLES) == RETIRED_TABLES
    assert len(script.module.RETIRED_TABLES) == 18
    with pytest.raises(RuntimeError, match="forward-only"):
        script.module.downgrade()


@pytest.mark.parametrize(("value", "limit", "accepted"), [
    ("设备 温区 ✈️", 64, True),
    ("设备\u3000温区", 64, True),
    ("process_monitor_r8_archive", 64, True),
    ("💡" + "区" * 63, 64, True),
    ("💡" + "区" * 64, 64, False),
    ("📋" + "任" * 127, 128, True),
    ("R" + "修" * 31, 32, True),
    ("R" + "修" * 32, 32, False),
    ("   ", 64, False),
    ("\u00a0设备", 64, False),
    ("设备\u3000", 64, False),
    ("a\u0000b", 64, False),
    ("a\u200bb", 64, False),
    ("👩\u200d🔧", 64, False),
    ("a\ud800b", 64, False),
    ("a\ue000b", 64, False),
    ("a\u0378b", 64, False),
])
def test_frozen_identifier_matches_current_writer(retirement_graph, value, limit, accepted):
    validate = retirement_graph.get_revision("c9e1a3b5d720").module._validate_identifier
    if accepted:
        assert identifier(value, limit) == value
        validate(value, limit)
    else:
        with pytest.raises(ObservationError):
            identifier(value, limit)
        with pytest.raises(ValueError, match="invalid identifier"):
            validate(value, limit)


def test_receipt_scan_rejects_non_utf8_bytes_and_closes_result(retirement_graph):
    migration = retirement_graph.get_revision("c9e1a3b5d720").module

    class FixtureConnection:
        closed = False

        @contextmanager
        def execute(self, statement, parameters):
            assert statement.get_execution_options()["stream_results"] is True
            assert parameters == {"first_id": 0, "page_size": 64}
            try:
                yield iter([(1, "energy", "meter-source", "event", None, None,
                             b'{"stored":["\x80"],"skipped":[]}', False, None)])
            finally:
                self.closed = True

    connection = FixtureConnection()
    with pytest.raises(RuntimeError, match="unknown observation receipt identifier") as error:
        migration._validate_receipt_identifiers(connection)
    assert connection.closed
    assert error.value.__suppress_context__


@pytest.mark.parametrize(("producer", "event"), [
    ("obs002-writer", "first"),
    ("设备 温区 ✈️", "事件💡"),
    ('来源 "甲"', r'事件\下一项"'),
])
def test_frozen_source_sample_key_matches_current_writer(retirement_graph, producer, event):
    migration = retirement_graph.get_revision("c9e1a3b5d720").module
    assert migration._source_sample_key(producer, event) == sha256(canonical_bytes([producer, event])).digest()


async def test_old_operations_absent_from_routes_openapi_and_metadata():
    app = create_app(testing=True)
    app.dependency_overrides[get_db] = lambda: pytest.fail("retired route entered database")
    paths = app.openapi()["paths"]
    assert len(RETIRED_OPERATIONS) == 22
    assert RETIRED_TABLES.isdisjoint(Base.metadata.tables)
    assert {"equipment_main", "monitor_main", "energy_consumption_main",
            "observation_ingest_receipts", "energy_ingest_receipts", "energy_prices", "energy_price_hours",
            "acq_plc_facts_latest", "acq_plc_facts_history", "acq_plc_source_registry"} <= set(Base.metadata.tables)
    for path in ("/integration/equipment/latest-snapshots", "/integration/monitor/history-samples",
                 "/integration/energy/samples"):
        assert "post" in paths["/api/v1" + path]
    for path in ("/equipment/latest-cards", "/monitor/observation-options", "/energy/consumption/samples"):
        assert "get" in paths["/api/v1" + path]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://fixture") as client:
        for method, path in sorted(RETIRED_OPERATIONS):
            assert method.lower() not in paths.get("/api/v1" + path, {})
            assert (await client.request(method, "/api/v1" + path)).status_code == 404
