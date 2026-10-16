"""模块scope配置优先级、隔离、公开env安全值；不读取真实env。"""
import inspect
from pathlib import Path
import sys
import pytest
from app.equipment.config import TemperatureConfig
from common.exceptions import BusinessException
from settings import resolve_env_file

pytestmark=pytest.mark.no_db


def test_explicit_process_dotenv_priority_and_no_shared_cache(tmp_path,monkeypatch):
    env=tmp_path/"synthetic.env";env.write_text("EQUIPMENT_TEMPERATURE_PILOT_ID='file-key'\n")
    monkeypatch.delenv("EQUIPMENT_TEMPERATURE_PILOT_ID",raising=False)
    assert TemperatureConfig(_env_file=env).allowed_equipment()=="file-key"
    monkeypatch.setenv("EQUIPMENT_TEMPERATURE_PILOT_ID","process-key")
    assert TemperatureConfig(_env_file=env).allowed_equipment()=="process-key"
    assert TemperatureConfig(EQUIPMENT_TEMPERATURE_PILOT_ID="explicit-key",_env_file=env).allowed_equipment()=="explicit-key"
    monkeypatch.delenv("EQUIPMENT_TEMPERATURE_PILOT_ID")
    for key in ("", " ", " key", "key\n", "x"*129):
        with pytest.raises(BusinessException) as caught:
            TemperatureConfig(EQUIPMENT_TEMPERATURE_PILOT_ID=key,_env_file=None).allowed_equipment()
        assert caught.value.code==403
    first=TemperatureConfig(EQUIPMENT_TEMPERATURE_PILOT_ID="First",_env_file=None)
    second=TemperatureConfig(EQUIPMENT_TEMPERATURE_PILOT_ID="Second",_env_file=None)
    assert first.allowed_equipment()=="First" and second.allowed_equipment()=="Second"
    with pytest.raises(BusinessException):first.allowed_equipment("first")


def test_public_helper_signature_source_and_frozen_path(monkeypatch,tmp_path):
    assert tuple(inspect.signature(resolve_env_file).parameters)==()
    import settings
    monkeypatch.delattr(sys,"frozen",raising=False)
    assert resolve_env_file()==Path(settings.__file__).resolve().parent/".env"
    monkeypatch.setattr(sys,"frozen",True,raising=False)
    monkeypatch.setattr(sys,"executable",str(tmp_path/"application"))
    assert resolve_env_file()==tmp_path/".env"


def test_three_examples_add_only_empty_scope_with_english_comment():
    root=Path(__file__).resolve().parents[1]
    for name in (".env.example",".env.docker.dev.example",".env.docker.prod.example"):
        source=(root/name).read_text()
        assert source.count("EQUIPMENT_TEMPERATURE_PILOT_ID=")==1
        assert "EQUIPMENT_TEMPERATURE_PILOT_ID=''" in source
        assert "Single allowed business equipment key" in source
        assignments=[line.split("=",1)[0] for line in source.splitlines() if line and not line.startswith("#") and "=" in line]
        assert len(assignments)==len(set(assignments))==69


def test_app_local_lazy_snapshot_requires_restart_and_no_cross_app_cache(tmp_path,monkeypatch):
    from fastapi import FastAPI,Request
    import app.equipment.config as config
    file=tmp_path/"synthetic.env";file.write_text("EQUIPMENT_TEMPERATURE_PILOT_ID='first'\n")
    monkeypatch.delenv("EQUIPMENT_TEMPERATURE_PILOT_ID",raising=False)
    monkeypatch.setattr(config,"resolve_env_file",lambda:file)
    one,two=FastAPI(),FastAPI()
    def request(app):return Request({"type":"http","app":app})
    assert not hasattr(one.state,"equipment_temperature_config")
    first=config.get_temperature_config(request(one))
    file.write_text("EQUIPMENT_TEMPERATURE_PILOT_ID='second'\n")
    assert config.get_temperature_config(request(one)) is first
    assert config.get_temperature_config(request(one)).allowed_equipment()=="first"
    assert config.get_temperature_config(request(two)).allowed_equipment()=="second"
    assert one.state.equipment_temperature_config is not two.state.equipment_temperature_config
