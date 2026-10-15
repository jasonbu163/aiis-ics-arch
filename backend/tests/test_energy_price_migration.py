"""价格后继迁移真实操作、完整 metadata parity 与单 root/head。"""
import importlib.util
import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from app.module_registry import import_model_packages
from database import Base
from tests.test_core_migration_baseline import MigrationRecorder, _load_migration, _table_signature, EXPECTED_CORE_TABLES, VERSIONS_DIR, FORBIDDEN_PROJECT_RESIDUE

pytestmark=pytest.mark.no_db
PRICE_MIGRATION=VERSIONS_DIR/"20261013_1200_a6c8e0f2b4d6_add_public_energy_prices.py"


def load_price(path=PRICE_MIGRATION):
    spec=importlib.util.spec_from_file_location("energy_prices_migration",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_successor_operations_match_full_sixteen_table_metadata():
    import_model_packages()
    recorder=MigrationRecorder()
    root=_load_migration();root.op=recorder;root.upgrade()
    previous=list(recorder.operations)
    price=load_price();price.op=recorder;price.upgrade()
    assert recorder.operations[len(previous):]==[("create_table","energy_prices"),("create_index","ix_energy_prices_created_at_id","energy_prices",("created_at","id"),False)]
    hour=load_price(VERSIONS_DIR/"20261013_1600_b8d0f2a4c6e8_add_energy_price_hours.py");hour.op=recorder;hour.upgrade()
    assert recorder.operations[-2:]==[("create_table","energy_price_hours"),("create_index","ix_energy_price_hours_observed_at_id","energy_price_hours",("observed_at","id"),False)]
    assert set(recorder.metadata.tables)==EXPECTED_CORE_TABLES|{"energy_prices","energy_price_hours"}
    assert set(recorder.metadata.tables).issubset(Base.metadata.tables)
    for name in recorder.metadata.tables:
        assert _table_signature(recorder.metadata.tables[name])==_table_signature(Base.metadata.tables[name]),name
    table=Base.metadata.tables["energy_prices"]
    assert len([c for c in table.constraints if c.__class__.__name__=="CheckConstraint"])==7
    for name in ("electric_price","hydrogen_price","argon_price"):
        assert table.c[name].default is None and table.c[name].server_default is None
        assert not table.c[name].nullable
    hourly=Base.metadata.tables["energy_price_hours"]
    assert not hourly.c.observed_at.nullable and not hourly.c.hour_start.nullable
    assert str(hourly.c.created_at.server_default.arg)=="(UTC_TIMESTAMP(6))"
    assert str(hourly.c.updated_at.server_default.arg)=="(UTC_TIMESTAMP(6))"
    hour.downgrade()
    assert recorder.operations[-1]==("drop_table","energy_price_hours")
    assert "energy_prices" in recorder.metadata.tables
    price.downgrade()
    assert recorder.operations[-1]==("drop_table","energy_prices")
    assert set(recorder.metadata.tables)==EXPECTED_CORE_TABLES
    assert not any(value in PRICE_MIGRATION.read_text() for value in FORBIDDEN_PROJECT_RESIDUE)


def test_single_root_head_graph():
    config=Config("alembic.ini")
    graph=ScriptDirectory.from_config(config)
    assert graph.get_bases()==["d4e6f8a0b2c4"]
    assert len(graph.get_heads())==1
    assert "d2f4a6b8c0e2" in {revision.revision for revision in graph.walk_revisions()}
    assert graph.get_revision("a6c8e0f2b4d6").down_revision=="d4e6f8a0b2c4"

    assert graph.get_revision("b8d0f2a4c6e8").down_revision=="a6c8e0f2b4d6"


def test_documented_merge_sql_synthetic_winner_archive_and_conflict_guard():
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo
    from copy import deepcopy
    from pathlib import Path
    # Public fixture verifies the documented (created_at DESC,id DESC) whole-row rule.
    source=[dict(id=i,created_at=datetime.fromisoformat(time),electric_price=i,hydrogen_price=i+10,argon_price=i+20,remark=str(i),operator='fixture') for i,time in ((1,'2026-10-12T23:59:59'),(2,'2026-10-13T10:00:00'),(3,'2026-10-13T10:59:00'),(4,'2026-10-13T10:59:00'),(5,'2026-10-13T11:00:00'))]
    original=deepcopy(source)
    def merge(rows,target,source_zone):
        if target or source_zone is None: raise ValueError('stop_before_import')
        winners={}
        for row in sorted(rows,key=lambda r:(r['created_at'],r['id'])):
            observed=row['created_at'].replace(tzinfo=source_zone).astimezone(timezone.utc)
            hour=observed.astimezone(ZoneInfo('Asia/Shanghai')).replace(minute=0,second=0,microsecond=0,fold=0).astimezone(timezone.utc)
            winners[hour]=row.copy()|dict(observed_at=observed,hour_start=hour)
        return winners
    target=merge(source,{},ZoneInfo('Asia/Shanghai'))
    assert len(target)==3 and source==original
    assert target[datetime(2026,10,13,2,tzinfo=timezone.utc)]['id']==4
    assert target[datetime(2026,10,13,2,tzinfo=timezone.utc)]['remark']=='4'
    assert target[datetime(2026,10,12,15,tzinfo=timezone.utc)]['observed_at']==datetime(2026,10,12,15,59,59,tzinfo=timezone.utc)
    for existing,zone in ((target,ZoneInfo('Asia/Shanghai')),({},None)):
        with pytest.raises(ValueError): merge(source,existing,zone)
    for name in ('README.md','README.zh-CN.md'):
        doc=(Path(__file__).parents[1]/'app/energy'/name).read_text()
        for snippet in ('ROW_NUMBER()', 'created_at DESC, id DESC', 'energy_price_hours', '@legacy_offset', 'ROLLBACK', 'CHECKSUM TABLE energy_prices'):
            assert snippet in doc
