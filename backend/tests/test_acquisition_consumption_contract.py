"""ARCH-ACQ-006 合同发行物、配置范围和时序原语的无库校验。"""
import json
from hashlib import sha256
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import FastAPI

from app.plc_facts.api.consumption import router
from app.plc_facts.consumption_config import authorize, parse_grants
from app.plc_facts.consumption_domain import ConsumerError, delivery_id, sequence
from app.plc_facts.schemas.consumption import AckIn, CreateConsumerIn
from app.plc_facts.v2_config import CONSUMPTION_REVISION

pytestmark = pytest.mark.no_db
BACKEND = Path(__file__).resolve().parents[1]
PUBLIC = BACKEND.parent / 'contracts' / 'published' / 'http-api' / 'acquisition-consumers-v1'


def test_single_forward_successor():
    config = Config(str(BACKEND / 'alembic.ini'))
    config.set_main_option('script_location', str(BACKEND / 'alembic'))
    graph = ScriptDirectory.from_config(config)
    assert graph.get_heads() == ['e9f3b5d7c021']
    assert graph.get_revision('d8f2a4c6b915').down_revision == CONSUMPTION_REVISION
    assert graph.get_revision(CONSUMPTION_REVISION).down_revision == 'c9e1a3b5d720'


def test_published_openapi_schema_and_vectors_match_router():
    published = json.loads((PUBLIC / 'openapi.json').read_text())
    standalone = json.loads((PUBLIC / 'schema.json').read_text())
    vectors = json.loads((PUBLIC / 'vectors.json').read_text())
    app = FastAPI()
    app.include_router(router, prefix='/api/v1')
    runtime = app.openapi()
    assert published['paths'] == runtime['paths']
    assert len(published['paths']) == 6 and sum(map(len, published['paths'].values())) == 7
    assert published['components'] == runtime['components']
    assert standalone['$defs'] == json.loads(json.dumps(runtime['components']['schemas']).replace(
        '#/components/schemas/', '#/$defs/'))
    assert all(operation['security'] == [{'AcquisitionConsumerBearer': []}]
               for methods in published['paths'].values() for operation in methods.values())
    case = {case['name']: case for case in vectors['cases']}
    identity = vectors['syntheticConsumerId']
    expected = delivery_id(identity, sequence(case['ready-identity']['eventSeq']))
    assert case['ready-identity']['deliveryId'] == expected
    assert case['ready-identity']['deliveryTarget']['sampleId'] == expected
    assert CreateConsumerIn.model_validate(case['create-retained']['request']).start_mode == 'retained'
    assert AckIn.model_validate(case['ack-first-commit']['request']).sample_id == expected


def test_service_grant_scope_permissions_and_token(monkeypatch):
    raw = 'synthetic-test-case-v1-' + 'a' * 40
    identity = '10000000-0000-4000-8000-000000000001'
    entry = {'sha256': sha256(raw.encode()).hexdigest(), 'consumerId': identity, 'plcId': 'synthetic',
             'dbNumber': 21, 'permissions': ['read']}
    grants = parse_grants({'grants': [entry]})
    monkeypatch.setattr('app.plc_facts.consumption_config.get_grants', lambda: grants)
    assert authorize('Bearer ' + raw, identity, 'read').db_number == 21
    cases = [(None, identity, 'read', 401), ('Bearer ' + 'b' * 40, identity, 'read', 401),
             ('Bearer ' + raw, identity, 'create', 403),
             ('Bearer ' + raw, '20000000-0000-4000-8000-000000000002', 'read', 403)]
    for bearer, consumer, permission, status in cases:
        with pytest.raises(ConsumerError) as error:
            authorize(bearer, consumer, permission)
        assert error.value.status == status
    with pytest.raises(ValueError, match='duplicate grant'):
        parse_grants({'grants': [entry, entry]})
