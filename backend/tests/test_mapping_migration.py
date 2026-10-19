"""BE006/64/f6独立增量profile；不改冻结58/60断言、不连接数据库。"""
from pathlib import Path
import hashlib
import pytest
import sqlalchemy as sa
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateTable,CreateIndex
from database import Base
from core.registrar import create_app
from tests.test_core_migration_baseline import MigrationRecorder,_table_signature,VERSIONS_DIR
from tests.test_business_module_migration import load
pytestmark=pytest.mark.no_db
CHANGED={'equipment_drive','equipment_production_parameters','performance_main','performance_process_temperature','performance_process_tension','performance_process_speed','monitor_history_process_curves'}
NEW={'equipment_mapping_receipts','performance_mapping_receipts','monitor_mapping_receipts','performance_mapping_observation_state'}

class Recorder(MigrationRecorder):
    def add_column(self,table,column,**kwargs):
        self.metadata.tables[table].append_column(column)
        self.operations.append(('add_column',table,column.name))
    def alter_column(self,table,name,**kwargs):
        column=self.metadata.tables[table].c[name]
        if 'type_' in kwargs:column.type=kwargs['type_']
        if 'nullable' in kwargs:column.nullable=kwargs['nullable']
        if 'server_default' in kwargs:column.server_default=sa.DefaultClause(kwargs['server_default']) if kwargs['server_default'] is not None else None
        self.operations.append(('alter_column',table,name))
    def create_unique_constraint(self,name,table,columns,**kwargs):
        self.metadata.tables[table].append_constraint(sa.UniqueConstraint(*columns,name=name))
        self.operations.append(('unique',table,name))

def signature(table):
    s=_table_signature(table);s['columns']=frozenset(s['columns']);return s

def test_six_revision_60_to_64_model_parity_and_53_protection():
    create_app(testing=True)
    migrations=[load(p) for p in sorted(VERSIONS_DIR.glob('*.py'))]
    assert [m.revision for m in migrations]==['d4e6f8a0b2c4','a6c8e0f2b4d6','b8d0f2a4c6e8','d2f4a6b8c0e2','e4f6a8b0c2d4','f6a8c0e2b4d6']
    recorder=Recorder()
    for m in migrations[:-1]:m.op=recorder;m.upgrade()
    assert len(recorder.metadata.tables)==60
    before={name:signature(table) for name,table in recorder.metadata.tables.items()}
    final=migrations[-1];final.op=recorder;final.upgrade()
    assert len(recorder.metadata.tables)==64
    assert set(recorder.metadata.tables)-set(before)==NEW
    assert len(set(before)-CHANGED)==53
    for name,table in recorder.metadata.tables.items():
        assert signature(table)==signature(Base.metadata.tables[name]),name
        str(CreateTable(table).compile(dialect=mysql.dialect()))
        for index in table.indexes:str(CreateIndex(index).compile(dialect=mysql.dialect()))
        if name in set(before)-CHANGED:assert signature(table)==before[name]
    for name in CHANGED|NEW:
        assert recorder.metadata.tables[name].c.equipment_id.type.dialect_impl(mysql.dialect()).collation=='utf8mb4_bin'
    assert recorder.metadata.tables['equipment_drive'].c.timestamp.type.dialect_impl(mysql.dialect()).fsp==3
    assert recorder.metadata.tables['performance_process_temperature'].c.record_time.type.dialect_impl(mysql.dialect()).fsp==3
    for table, key in [('equipment_production_parameters','http_coil_key'),('performance_main','http_coil_key'),('performance_process_temperature','http_zone_key')]:
        assert isinstance(recorder.metadata.tables[table].c[key].type.dialect_impl(mysql.dialect()),mysql.VARBINARY)
        assert 'VARBINARY(200)' in str(CreateTable(recorder.metadata.tables[table]).compile(dialect=mysql.dialect()))
    assert ScriptDirectory.from_config(Config('alembic.ini')).get_heads()==['f6a8c0e2b4d6']

def test_downgrade_offline_refuses_without_any_mutation(monkeypatch):
    final=load(VERSIONS_DIR/'20261016_1900_f6a8c0e2b4d6_expand_mapping_business_api.py')
    final.op=Recorder();monkeypatch.setattr(final.context,'is_offline_mode',lambda:True)
    with pytest.raises(RuntimeError,match='disposable database inspection'):final.downgrade()
    assert final.op.operations==[]

@pytest.mark.parametrize('hit',[1,5,8,11,18,35])
def test_downgrade_data_or_precision_guard_precedes_ddl(monkeypatch,hit):
    final=load(VERSIONS_DIR/'20261016_1900_f6a8c0e2b4d6_expand_mapping_business_api.py')
    class Connection:
        calls=0
        def execute(self,query):
            self.calls+=1
            return type('Result',(),{'first':lambda _:True if self.calls==hit else None})()
    connection=Connection();recorder=Recorder();recorder.get_bind=lambda:connection;final.op=recorder
    monkeypatch.setattr(final.context,'is_offline_mode',lambda:False)
    with pytest.raises(RuntimeError,match='refuses'):final.downgrade()
    assert not recorder.operations


def test_original_five_migrations_are_byte_identical():
    expected={'20260810_1200_d4e6f8a0b2c4_create_core_schema_baseline.py': 'f038e80badccf322292a9b4dca5bf2bb563bb5c15388f4745bc36fd02ca478f2', '20261013_1200_a6c8e0f2b4d6_add_public_energy_prices.py': '0950882badedd3abea8c61c2f7ed09c6176f8a0ee3edd5e5cf3b601766188914', '20261013_1600_b8d0f2a4c6e8_add_energy_price_hours.py': '7efeba1aef3270a1f7c51b6b7bbbf2af670e49ac2ffdca342e978a03ce573d1a', '20261014_1600_d2f4a6b8c0e2_reintegrate_business_module_schema.py': '806b008ebc4d232326db9967132a5bdb5d507518dca96017592ed80e00d056eb', '20261016_1600_e4f6a8b0c2d4_add_equipment_temperature_samples.py': '6b691c4addb15303609c73e30fbbb9d462f6848632a9e78bd7340dd1cc62a6b8'}
    assert len(expected)==5
    for name,digest in expected.items():
        assert hashlib.sha256((VERSIONS_DIR/name).read_bytes()).hexdigest()==digest


def test_prepared_b_old_columns_and_primary_keys_survive_new_columns_and_rows(monkeypatch,tmp_path):
    """实际B校验函数以合成SQL结果运行；不实例化目标或连接数据库。"""
    import importlib.util
    from types import SimpleNamespace
    from sqlalchemy import MetaData,Table,Column,Integer,Float,String
    path=VERSIONS_DIR.parents[1]/'tests_mysql/test_mapping_business_api.py'
    spec=importlib.util.spec_from_file_location('be006_prepared_b',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    old=Table('equipment_drive',MetaData(),Column('id',Integer,primary_key=True),Column('tv',Float))
    new=Table('equipment_drive',MetaData(),Column('id',Integer,primary_key=True),Column('tv',Float),Column('equipment_id',String(128)))
    active={'table':old,'rows':[{'id':1,'tv':0}]}
    queries=[]
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def execute(self,query):
            names=tuple(column.name for column in query.selected_columns);queries.append(names)
            return [SimpleNamespace(_mapping={key:row[key] for key in names}) for row in active['rows']]
    target=SimpleNamespace(root=tmp_path,engine=SimpleNamespace(connect=lambda:Connection()))
    monkeypatch.setattr(sa,'Table',lambda *args,**kwargs:active['table'])
    before=module.capture_legacy_rows(target,{'equipment_drive'})
    assert before['equipment_drive']['columns']==('id','tv') and before['equipment_drive']['primary_key']==('id',)
    active.update(table=new,rows=[{'id':1,'tv':0,'equipment_id':None},{'id':2,'tv':9,'equipment_id':'line-A'}])
    module.assert_legacy_rows(target,before)
    assert queries[-1]==('id','tv')
    active['rows'][0]['tv']=1
    with pytest.raises(AssertionError):module.assert_legacy_rows(target,before)


def test_equipment_millisecond_default_has_matching_mysql_precision():
    from sqlalchemy.schema import CreateTable
    from sqlalchemy.dialects import mysql
    from app.equipment.models.equipment import EquipmentDrive,EquipmentProductionParameters
    for model in (EquipmentDrive,EquipmentProductionParameters):
        column=model.__table__.c.timestamp
        assert column.type.dialect_impl(mysql.dialect()).fsp==3
        assert str(column.server_default.arg.compile(dialect=mysql.dialect(),compile_kwargs={'literal_binds':True})).upper()=='CURRENT_TIMESTAMP(3)'
        assert 'CURRENT_TIMESTAMP(3)' in str(CreateTable(model.__table__).compile(dialect=mysql.dialect())).upper()
