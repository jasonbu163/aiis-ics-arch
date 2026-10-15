"""四revision显式操作/58表完整签名及增量撤回；只用recorder，不连接数据库。"""
import importlib.util
from pathlib import Path
import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateTable, CreateIndex
from database import Base
from tests.test_core_migration_baseline import MigrationRecorder, _table_signature, VERSIONS_DIR, EXPECTED_CORE_TABLES

pytestmark = pytest.mark.no_db


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def test_all_operations_match_58_tables_and_only_new_42_are_removed():
    recorder = MigrationRecorder()
    migrations = [load(path) for path in sorted(VERSIONS_DIR.glob('*.py')) if any(revision in path.name for revision in ('d4e6f8a0b2c4','a6c8e0f2b4d6','b8d0f2a4c6e8','d2f4a6b8c0e2'))]
    for module in migrations:
        module.op = recorder; module.upgrade()
    assert len(recorder.metadata.tables) == 58
    assert set(recorder.metadata.tables).issubset(Base.metadata.tables)
    for name, table in recorder.metadata.tables.items():
        assert _table_signature(table) == _table_signature(Base.metadata.tables[name]), name
        str(CreateTable(table).compile(dialect=mysql.dialect()))
        for index in table.indexes:
            str(CreateIndex(index).compile(dialect=mysql.dialect()))
    before = {name: _table_signature(recorder.metadata.tables[name]) for name in EXPECTED_CORE_TABLES | {'energy_prices','energy_price_hours'}}
    migrations[-1].downgrade()
    assert set(recorder.metadata.tables) == set(before)
    assert {name: _table_signature(recorder.metadata.tables[name]) for name in before} == before


def test_graph_is_single_root_and_unique_explicit_successor():
    graph = ScriptDirectory.from_config(Config('alembic.ini'))
    assert graph.get_bases() == ['d4e6f8a0b2c4']
    assert len(graph.get_heads()) == 1
    assert 'd2f4a6b8c0e2' in {revision.revision for revision in graph.walk_revisions()}
    assert graph.get_revision('d2f4a6b8c0e2').down_revision == 'b8d0f2a4c6e8'
    source = (VERSIONS_DIR/'20261014_1600_d2f4a6b8c0e2_reintegrate_business_module_schema.py').read_text()
    for forbidden in ('create_all','stamp(','bulk_insert','INSERT INTO','execute('):
        assert forbidden not in source
