"""ARCH-TASK-001 r3 的受保护目标探针回归，只使用内存替身和合成配置。"""
from datetime import datetime
from types import SimpleNamespace
import json

import pytest

from app.equipment_observation import profile as observation
from app.equipment_observation.services.guard import EvidenceUnavailable, probe_target
from app.plc_facts import v2_config
from app.plc_facts.crud import sync_v2_maintenance
from app.plc_facts.v2_domain import V2Error

pytestmark = pytest.mark.no_db
PREDECESSOR = '9d1f3a5c7e20'
TASK_SUCCESSOR = 'ae20b4d6f831'
RETIREMENT = 'c9e1a3b5d720'
ACQUISITION = 'da6c32f8a701'
RECEIPT_SEPARATION = 'd8f2a4c6b915'
SUCCESSOR = 'e9f3b5d7c021'
UUID = '00000000-0000-4000-8000-000000000001'
NOW = datetime(2026, 11, 18, 12, 0)


def target(revision):
    return {'serverUuid': UUID, 'schema': 'fixture_schema', 'schemaRevision': revision}


class Result:
    def __init__(self, value):
        self.value = value

    def scalars(self):
        return iter(self.value)

    def one(self):
        return self.value

    def all(self):
        return self.value


class SyncProbe:
    def __init__(self, revisions, *, driver='mysql', uuid=UUID, schema='fixture_schema', version='8.4.6', clock=28800):
        self.dialect = SimpleNamespace(name=driver)
        self.revisions = revisions
        self.row = (uuid, schema, version, NOW, clock)

    def get_bind(self):
        return self

    def connection(self):
        return self

    def execute(self, statement):
        sql = str(statement)
        if 'alembic_version' in sql:
            assert 'FOR SHARE' in sql
            return Result(self.revisions)
        if 'information_schema.COLUMNS' in sql:
            return Result([
                ("source_key", "varchar(64)", "NO", "utf8mb4_bin", None),
                ("storage_identity", "varchar(64)", "NO", "utf8mb4_bin", None),
                ("name", "varchar(128)", "YES", "utf8mb4_0900_ai_ci", None),
                ("enabled", "tinyint(1)", "NO", None, "1"),
                ("created_at", "datetime(6)", "NO", None, None),
                ("updated_at", "datetime(6)", "NO", None, None),
                ("deleted_at", "datetime(6)", "YES", None, None),
            ])
        if 'information_schema.STATISTICS' in sql:
            return Result([("InnoDB", "PRIMARY", 0, 1, "source_key", None),
                           ("InnoDB", "uq_obs_write_source_identity", 0, 1, "storage_identity", None)])
        assert '@@server_uuid' in sql and 'UTC_TIMESTAMP' in sql
        return Result(self.row)


class AsyncProbe(SyncProbe):
    async def execute(self, statement):
        return super().execute(statement)


@pytest.mark.parametrize('revision', ('7b9d1f3a5c7e', '8c0e2a4d6f18', PREDECESSOR, TASK_SUCCESSOR, RETIREMENT, ACQUISITION, RECEIPT_SEPARATION, SUCCESSOR))
def test_facts_legacy_profile_and_explicit_maintenance(revision, tmp_path):
    path = tmp_path / 'v2.json'
    config = SimpleNamespace(PLC_FACTS_V2_PROFILE_FILE=path)
    profile = {**target(revision), 'alias': 'fixture'}
    path.write_text(json.dumps({'target': profile}))
    assert v2_config.load_profile(config)['target'] == profile
    assert sync_v2_maintenance.target_now(SyncProbe([revision]), profile) == NOW


def observation_document(revision):
    return {
        'target': target(revision),
        'devices': [{'equipmentId': 'line', 'nameZh': '线', 'nameEn': 'Line',
                     'staleAfterSeconds': 45, 'futureToleranceSeconds': 2}],
        'readScopes': {'operator': ['line']}, 'producers': [], 'historyRules': [], 'groupSettings': [],
    }


@pytest.mark.asyncio
async def test_observation_exact_target_and_device_timing():
    for revision in ('8c0e2a4d6f18', PREDECESSOR, TASK_SUCCESSOR, RETIREMENT, ACQUISITION, RECEIPT_SEPARATION):
        with pytest.raises(ValueError, match='invalid target'):
            observation.parse_profile(observation_document(revision))
    document = observation_document(SUCCESSOR)
    parsed = observation.parse_profile(document)
    assert await probe_target(AsyncProbe([SUCCESSOR]), parsed['target']) == NOW
    for missing in ({'staleAfterSeconds'}, {'futureToleranceSeconds'}, {'staleAfterSeconds', 'futureToleranceSeconds'}):
        incomplete = observation_document(SUCCESSOR)
        for field in missing:
            del incomplete['devices'][0][field]
        with pytest.raises(ValueError):
            observation.parse_profile(incomplete)


@pytest.mark.asyncio
@pytest.mark.parametrize('revision, revisions, metadata', (
    (SUCCESSOR, [PREDECESSOR], {}),
    (SUCCESSOR, [SUCCESSOR, PREDECESSOR], {}),
    (SUCCESSOR, [SUCCESSOR], {'driver': 'sqlite'}),
    (SUCCESSOR, [SUCCESSOR], {'uuid': 'other-server'}),
    (SUCCESSOR, [SUCCESSOR], {'schema': 'other_schema'}),
    (SUCCESSOR, [SUCCESSOR], {'version': '8.0.4'}),
    (SUCCESSOR, [SUCCESSOR], {'clock': 0}),
))
async def test_all_target_guards_reject_mismatches(revision, revisions, metadata):
    with pytest.raises(V2Error, match='not_ready'):
        sync_v2_maintenance.target_now(SyncProbe(revisions, **metadata), target(revision))
    with pytest.raises(EvidenceUnavailable):
        await probe_target(AsyncProbe(revisions, **metadata), target(revision))


def test_unknown_profile_revision_and_disabled_facts_stay_rejected(monkeypatch, tmp_path):
    path = tmp_path / 'v2.json'
    path.write_text(json.dumps({'target': {**target('unrecognized'), 'alias': 'fixture'}}))
    config = SimpleNamespace(PLC_FACTS_V2_PROFILE_FILE=path, PLC_FACTS_V2_ENABLED=False)
    with pytest.raises(V2Error, match='not_ready'):
        v2_config.load_profile(config)
    v2_config.get_profile.cache_clear()
    monkeypatch.setattr(v2_config, 'V2Settings', lambda: config)
    with pytest.raises(V2Error, match='not_ready'):
        v2_config.get_profile()
    with pytest.raises(ValueError):
        observation.parse_profile(observation_document('unrecognized'))


def test_new_observation_revision_keeps_machine_and_user_scopes():
    from hashlib import sha256
    from app.equipment_observation.domain import ObservationError

    document = observation_document(SUCCESSOR)
    document['producers'] = [{'producerId':'fixture', 'tokenSha256':sha256(b'fixture-secret').hexdigest(),
        'kind':'external', 'enabled':True,
        'grants':[{'equipmentId':'line','groupKey':'drive','target':'latest','metricKeys':['speed']}]}]
    profile = observation.parse_profile(document)
    assert observation.allowed_device(profile,SimpleNamespace(role='operator'),'line')['equipmentId'] == 'line'
    producer = observation.authenticate(profile,'Bearer fixture-secret')
    assert observation.permitted(producer,'line','drive','latest') == {'speed'}
    for header in (None, 'Bearer wrong-token'):
        with pytest.raises(ObservationError):
            observation.authenticate(profile,header)
    for args in (('other','drive','latest'), ('line','other','latest'), ('line','drive','history')):
        with pytest.raises(ObservationError):
            observation.permitted(producer,*args)
    with pytest.raises(ObservationError):
        observation.allowed_device(profile,SimpleNamespace(role='ungranted'),'line')
