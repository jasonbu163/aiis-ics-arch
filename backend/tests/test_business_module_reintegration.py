"""完整F来源/表owner、错误闭包与8个本地Projection descriptor静态回归。"""
import ast
from pathlib import Path
import pytest
from app.module_registry import get_module_manifests
from core.registrar import create_app
from database import Base
from common.error_codes import ErrorCode

pytestmark=pytest.mark.no_db


def test_f_has_exact_58_tables_and_price_has_one_owner():
    from tests.test_business_module_migration import load, VERSIONS_DIR
    from tests.test_core_migration_baseline import MigrationRecorder
    recorder=MigrationRecorder()
    for path in sorted(VERSIONS_DIR.glob("*.py")):
        if not any(revision in path.name for revision in ("d4e6f8a0b2c4", "a6c8e0f2b4d6", "b8d0f2a4c6e8", "d2f4a6b8c0e2")):
            continue
        module=load(path);module.op=recorder;module.upgrade()
    assert len(recorder.metadata.tables)==58
    assert set(recorder.metadata.tables).issubset(Base.metadata.tables)
    from app.energy.models import EnergyPrice,EnergyPriceHour
    assert EnergyPrice.__module__=='app.energy.models.energy_price'
    assert EnergyPriceHour.__module__=='app.energy.models.energy_price_hour'
    manifests={m.name:m for m in get_module_manifests()}
    assert manifests['hr'].enabled is False
    assert manifests['auxiliary'].permissions==('auxiliary',)
    assert manifests['energy'].permissions==('energy-price-read','energy-price-manage')
    assert manifests['dashboard'].model_requires==('plan',)
    assert manifests['reports'].requires==()


def test_all_active_global_errorcode_references_are_closed():
    for source in Path('app').rglob('*.py'):
        if source.name=='module_preflight.py':continue
        tree=ast.parse(source.read_text())
        core_import=any(isinstance(n,ast.ImportFrom) and n.module=='common.error_codes' for n in tree.body)
        if not core_import:continue
        for node in ast.walk(tree):
            if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='ErrorCode':
                assert node.attr in ErrorCode.__members__,(source,node.lineno,node.attr)


def test_eight_sync_descriptors_stay_local_and_uniquely_owned():
    handlers=create_app(testing=True).state.projection_registry.handlers
    expected={
        'equipment.sync_drive','equipment.sync_temperature','equipment.sync_production_parameters',
        'performance.sync_production_record','performance.sync_process_temperature','performance.sync_process_tension','performance.sync_process_speed','monitor.sync_process_curve'}
    assert expected.issubset(h.handler_key for h in handlers)
    for handler in handlers:
        if handler.handler_key not in expected: continue
        assert handler.invoke.__module__.startswith('app.'+handler.owner_module+'.services.sync_')
