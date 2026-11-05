"""旧迁移/monitor事实GET/Projection标量源冻结指纹，新增owner不改旧输入。"""
import hashlib
import pytest
from app.plc_facts.manifest import manifest
from test_plc_facts_contract import ROOT
pytestmark=pytest.mark.no_db
FROZEN={'alembic/versions/20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py': 'f038e80badccf322292a9b4dca5bf2bb563bb5c15388f4745bc36fd02ca478f2', 'alembic/versions/20261013_1200_a6c8e0f2b4d6_add_public_energy_prices.py': '0950882badedd3abea8c61c2f7ed09c6176f8a0ee3edd5e5cf3b601766188914', 'alembic/versions/20261013_1600_b8d0f2a4c6e8_add_energy_price_hours.py': '7efeba1aef3270a1f7c51b6b7bbbf2af670e49ac2ffdca342e978a03ce573d1a', 'alembic/versions/20261014_1600_d2f4a6b8c0e2_reintegrate_business_module_schema.py': '806b008ebc4d232326db9967132a5bdb5d507518dca96017592ed80e00d056eb', 'alembic/versions/20261016_1600_e4f6a8b0c2d4_add_equipment_temperature_samples.py': '6b691c4addb15303609c73e30fbbb9d462f6848632a9e78bd7340dd1cc62a6b8', 'alembic/versions/20261016_1900_f6a8c0e2b4d6_expand_mapping_business_api.py': 'd75bf6be613b972077cfddb63b9959c6a33fe991a00f4069e7e9bde17ce4019f', 'app/monitor/api/realtime.py': 'cf0d4e6b3f5ece1a0383b76e365fdfae245cf05550ba43cf368f108349464773', 'projection/input_resolver.py': '61c0b098390ea5c95ebf31cc7cc3cf0d04b771fe6c21592ca6763f4f85696981'}

@pytest.mark.parametrize('relative,expected',FROZEN.items())
def test_frozen_compatibility_source(relative,expected):
    assert hashlib.sha256((ROOT/'backend'/relative).read_bytes()).hexdigest()==expected

def test_isolated_owner_has_no_permissions_dependencies_or_projection():
    assert manifest.name=='plc_facts' and manifest.order==36 and manifest.enabled
    assert manifest.requires==manifest.model_requires==manifest.exports==manifest.permissions==()
    assert manifest.routers==('app.plc_facts.api.routes:router',)


def test_disabled_facts_module_only_removes_its_three_routes(monkeypatch):
    from dataclasses import replace
    import importlib
    from core.registrar import create_app
    module=importlib.import_module('app.plc_facts.manifest')
    monkeypatch.setattr(module,'manifest',replace(module.manifest,enabled=False))
    paths=create_app(testing=True).openapi()['paths']
    assert not any('/integration/plc-facts/' in path for path in paths)
    assert '/api/v1/monitor/realtime/latest' in paths
