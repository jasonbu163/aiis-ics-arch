"""BE010 A0 public configuration snapshot；旧公开前缀保留，不修改冻结历史断言。"""
from pathlib import Path
import hashlib
import json
import pytest
pytestmark = pytest.mark.no_db


def test_public_examples_preserve_entry_prefix_and_add_only_closed_integration_keys():
    root = Path(__file__).resolve().parents[1]
    expected = {'.env.example': (8506, '93375dc6d1424e4b5d615061a0e81c5e2a0d3062c5723b877ba2eb2724bc206c'), '.env.docker.dev.example': (8411, '76a9931773dde6bd92276e356e499bc63dae86c62fa803721d1b7f5004518724'), '.env.docker.prod.example': (8490, 'e3dd138b78221c467a19f010a8b2ae77150e569a70dc239455d110c65c355ce6')}
    for name, (length, digest) in expected.items():
        data = (root/name).read_bytes()
        assert hashlib.sha256(data[:length]).hexdigest() == digest
        tail = data[length:].decode()
        assignments = dict(line.split("=",1) for line in tail.splitlines() if line and not line.startswith("#"))
        a0={key:value for key,value in assignments.items() if not key.startswith("PLC_FACTS_") and not key.endswith("_INTEGRATION_ADOPTION_FILE")}
        assert len(a0) == 12
        assert len([key for key in assignments if key.startswith("PLC_FACTS_")]) == 4
        assert len([key for key in assignments if key.endswith("_INTEGRATION_ADOPTION_FILE")]) == 3
        assert len(assignments) == 19
        for module in ("EQUIPMENT", "PERFORMANCE", "MONITOR"):
            assert assignments[module+"_INTEGRATION_ENABLED"] == "False"
            assert assignments[module+"_INTEGRATION_EQUIPMENT_IDS_JSON"] == "'[]'"
            assert assignments[module+"_INTEGRATION_PRODUCER_IDS_JSON"] == "'[]'"
            assert assignments[module+"_INTEGRATION_STORAGE_PROFILE"] == '"unadopted"'


def test_distinct_a0_profile_is_models_only_with_84_public_assignments(tmp_path):
    from tests.module_admission_fixtures import generate_business_integration_profile
    profile = generate_business_integration_profile(tmp_path / "BE010-A0")
    metadata = json.loads((profile / "profile.json").read_text())
    assert metadata["profile"] == "BE010-A0" and metadata["expected_table_count"] == 68
    assert metadata["target_revision"] is None
    assert metadata["schema_state"] == "models_only_unadopted_no_migration"
    assert metadata["public_env_assignment_count"] == 84
    assert not (profile / ".env").exists()
    for name in (".env.example", ".env.docker.dev.example", ".env.docker.prod.example"):
        assignments = [line for line in (profile / name).read_text().splitlines()
                       if line and not line.startswith("#") and "=" in line]
        assert len(assignments) == 84
