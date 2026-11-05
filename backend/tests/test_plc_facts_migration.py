"""显式迁移源码DDL编译/七表Model一致性；不执行任何Alembic或DB命令。"""
import ast
import importlib.util
from pathlib import Path
import pytest
from sqlalchemy import MetaData,Table,Index
from sqlalchemy.schema import CreateTable,CreateIndex
from sqlalchemy.dialects import mysql
from app.plc_facts.models import TABLES
from app.plc_facts.crud.sync_maintenance import fingerprint,BASELINE_TABLES,PENDING
from test_plc_facts_contract import ROOT
pytestmark=pytest.mark.no_db
MIGRATION=ROOT/'backend/alembic/versions/20261104_1200_0a2c4e6f8b10_add_plc_facts_integration.py'

def module():
    spec=importlib.util.spec_from_file_location('be009_frozen_migration',MIGRATION);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_explicit_chain_no_other_table_and_static_sql_model_parity(monkeypatch):
    m=module();assert m.revision=='0a2c4e6f8b10' and m.down_revision=='f6a8c0e2b4d6'
    metadata=MetaData()
    class Recorder:
        def create_table(self,name,*items):return Table(name,metadata,*items)
        def create_index(self,name,table,columns):return Index(name,*[metadata.tables[table].c[col] for col in columns])
    monkeypatch.setattr(m,'op',Recorder());m.upgrade()
    assert set(metadata.tables)=={t.name for t in TABLES} and len(TABLES)==7
    for table in TABLES:
        actual=str(CreateTable(metadata.tables[table.name]).compile(dialect=mysql.dialect()))
        expected=str(CreateTable(table).compile(dialect=mysql.dialect()))
        assert actual==expected
        assert all(c.name in ('created_at','updated_at') for c in table.columns if c.name.endswith('_at') and c.name in ('created_at','updated_at'))
        assert all(c.type.fsp==6 for c in table.columns if c.name in ('created_at','updated_at'))
        assert sorted(str(CreateIndex(i).compile(dialect=mysql.dialect())) for i in metadata.tables[table.name].indexes)==sorted(str(CreateIndex(i).compile(dialect=mysql.dialect())) for i in table.indexes)
    assert len(BASELINE_TABLES)==64 and len(set(BASELINE_TABLES)|{t.name for t in TABLES}|PENDING)==75
    assert fingerprint().startswith('sha256:')

@pytest.mark.parametrize('occupied',range(7))
def test_nonempty_downgrade_refuses_before_drop(monkeypatch,occupied):
    m=module();calls=[]
    class Bind:
        def execute(self,statement):
            calls.append(str(statement));return self
        def first(self):return (1,) if len(calls)-1==occupied else None
    class Op:
        def get_bind(self):return Bind()
        def drop_table(self,name):pytest.fail('nonempty downgrade must never drop')
    monkeypatch.setattr(m,'op',Op())
    with pytest.raises(RuntimeError):m.downgrade()


def test_mysql_inherited_collation_preserves_semantic_type():
    """真实MySQL反射的继承collation不应使同一VARCHAR语义F7误拒绝。"""
    from sqlalchemy.dialects.mysql import VARCHAR
    from app.plc_facts.crud.sync_maintenance import normalized_type
    assert normalized_type(VARCHAR(36, collation='utf8mb4_bin')) == normalized_type(VARCHAR(36)) == 'VARCHAR(36)'


def test_stream_singleton_id_is_not_mysql_auto_increment():
    """MySQL不允许CHECK引用自增列；单例id必须由采用命令明确写1。"""
    from sqlalchemy.dialects import mysql
    from sqlalchemy.schema import CreateTable
    from app.plc_facts.models import StreamState
    assert 'AUTO_INCREMENT' not in str(CreateTable(StreamState.__table__).compile(dialect=mysql.dialect()))
