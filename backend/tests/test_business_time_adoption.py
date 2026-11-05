"""只读采用CLI的无副作用入口与candidate gate；不读取目标env或连接DB。"""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest

pytestmark=pytest.mark.no_db


def tool():
    path=Path(__file__).resolve().parents[1]/"scripts/business_time_adoption/main.py"
    spec=importlib.util.spec_from_file_location("business_time_tool",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_bare_cli_only_help(capsys,monkeypatch):
    module=tool()
    monkeypatch.setattr(module,"config",lambda *args:pytest.fail("bare help read target"))
    assert module.main([])==0
    output=capsys.readouterr().out
    assert "inspect" in output and "verify" in output and "--env-file" in output
    with pytest.raises(SystemExit):module.main(["apply"])


def test_plan_is_finite_candidate_and_unknown_never_adopts():
    module=tool()
    inspection=dict(state="candidate",module="equipment",target=dict(schema="synthetic"),fixedColumnDigest="sha256:"+"0"*64,
        columns={"equipment_drive.timestamp":dict(rows=2,digest="sha256:"+"1"*64)})
    classification=dict(version="business-time-classification/v1",columns={"equipment_drive.timestamp":dict(basis="unknown",coveredRows=2,evidenceRef="private:source-proof")})
    result=module.plan(inspection,classification)
    assert result["state"]=="candidate" and not result["adoptionEligible"]
    assert result["unknownColumns"]==["equipment_drive.timestamp"]
    classification["columns"]["equipment_drive.timestamp"]["basis"]="utc_wall"
    assert not module.plan(inspection,classification)["adoptionEligible"]
    classification["columns"]["other_table.column"]={}
    with pytest.raises(ValueError):module.plan(inspection,classification)


def test_tool_only_declared_profiles_and_same_session_probe():
    module=tool()
    for owner in ("equipment","performance","monitor"):
        profile,probe=module.load_owner(owner)
        assert profile["profileId"]=="be010.fixed-columns/v1" and callable(probe)
