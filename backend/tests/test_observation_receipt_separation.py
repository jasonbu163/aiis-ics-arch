"""观测与能耗回执分域后的模型、迁移链和运行合同检查。"""
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
import pytest

from app.equipment_observation.models import EnergyReceipt, EnergySample, HistorySample, LatestSnapshot, Receipt, SlotBinding
from app.equipment_observation.profile import REVISIONS

pytestmark = pytest.mark.no_db


def test_receipt_foreign_keys_follow_owning_domain():
    for sample, receipt in ((LatestSnapshot, Receipt), (HistorySample, Receipt), (EnergySample, EnergyReceipt)):
        constraint, = sample.__table__.c.ingest_receipt_id.foreign_keys
        assert constraint.column is receipt.__table__.c.id
        assert constraint.ondelete == "RESTRICT"
    binding, = SlotBinding.__table__.c.metric_key.foreign_keys
    assert binding.target_fullname == "observation_metric_configs.metric_key"
    assert list(Receipt.__table__.columns.keys()) == list(EnergyReceipt.__table__.columns.keys())


def test_single_linear_observation_migration_and_guard():
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "alembic"))
    graph = ScriptDirectory.from_config(config)
    assert graph.get_heads() == ["a1c307f8d2e4"]
    revision = graph.get_revision("d8f2a4c6b915")
    assert revision.down_revision == "da6c32f8a701"
    assert graph.get_revision(revision.down_revision).down_revision == "c9e1a3b5d720"
    assert graph.get_revision(REVISIONS[0]).down_revision == revision.revision
    with pytest.raises(RuntimeError, match="forward-only"):
        revision.module.downgrade()
