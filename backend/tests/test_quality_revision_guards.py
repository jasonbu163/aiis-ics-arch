"""验证质量迁移版本继承原共库版本门卫。"""
import json
from types import SimpleNamespace

import pytest

from app.equipment_observation import profile as observation
from app.equipment_observation.services.guard import EvidenceUnavailable, probe_target
from app.equipment_observation.services.write_sources import registry_available
from app.plc_facts import v2_config
from app.plc_facts.crud import sync_v2_maintenance
from app.plc_facts.v2_domain import V2Error
from common.integration.storage import ALLOWED_SCHEMA_REVISIONS, validate_target
from tests.test_generic_task_revision_guards import AsyncProbe, NOW, SUCCESSOR, SyncProbe, observation_document, target

pytestmark = pytest.mark.no_db
NEW = 'f0a2b4c6d8e1'


@pytest.mark.asyncio
@pytest.mark.parametrize('revision', (SUCCESSOR, NEW))
async def test_quality_successor_keeps_all_version_guards(revision, tmp_path):
    path = tmp_path / 'facts.json'
    profile = {**target(revision), 'alias': 'fixture'}
    path.write_text(json.dumps({'target': profile}))
    assert v2_config.load_profile(SimpleNamespace(PLC_FACTS_V2_PROFILE_FILE=path))['target'] == profile
    assert revision in ALLOWED_SCHEMA_REVISIONS
    assert sync_v2_maintenance.target_now(SyncProbe([revision]), profile) == NOW
    observed = observation.parse_profile(observation_document(revision))
    assert registry_available(observed)
    assert await probe_target(AsyncProbe([revision]), observed['target']) == NOW
    assert validate_target(target(revision), {**target(revision), "utcNow": NOW}).utcoffset().total_seconds() == 28800

    class MissingLayout(AsyncProbe):
        async def execute(self, statement):
            if 'information_schema.COLUMNS' in str(statement):
                raise EvidenceUnavailable()
            return await super().execute(statement)

    with pytest.raises(EvidenceUnavailable):
        await probe_target(MissingLayout([revision]), observed['target'])


@pytest.mark.asyncio
async def test_quality_successor_does_not_accept_a_mismatched_or_unknown_target():
    new, old = target(NEW), target(SUCCESSOR)
    for config, actual in ((new, SUCCESSOR), (old, NEW), (new, 'unknown')):
        with pytest.raises(V2Error, match='not_ready'):
            sync_v2_maintenance.target_now(SyncProbe([actual]), config)
        with pytest.raises(EvidenceUnavailable):
            await probe_target(AsyncProbe([actual]), config)
    with pytest.raises(ValueError, match='target'):
        validate_target(old, new)
    assert not registry_available({'target': target('unknown')})
