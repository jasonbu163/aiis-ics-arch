"""仅静态 MySQL DDL：四声明表和引用保护，无 engine/连接/Alembic 执行。"""
import pytest
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.mysql import dialect
from sqlalchemy.schema import CreateTable
from app.equipment.models.integration import EquipmentIntegrationReceipt
from app.performance.models.integration import PerformanceIntegrationReceipt, PerformanceIntegrationObservationEvent
from app.monitor.models.integration import MonitorIntegrationReceipt

pytestmark = pytest.mark.no_db
MODELS = (EquipmentIntegrationReceipt, PerformanceIntegrationReceipt, MonitorIntegrationReceipt, PerformanceIntegrationObservationEvent)


@pytest.mark.parametrize("model", MODELS)
def test_static_mysql_declarations_only(model):
    table = model.__table__
    sql = str(CreateTable(table).compile(dialect=dialect()))
    assert "DATETIME(3)" in sql and "UTC_TIMESTAMP" not in sql
    assert "CASCADE" not in sql and "actor_user_id" not in table.c
    assert not any(c.server_default is not None for c in table.columns)
    for key in table.foreign_key_constraints:
        assert key.referred_table.name not in {"plc_db_block_raw_snapshots", "plc_db_block_latest_snapshots"}
        assert key.ondelete is None
        assert "equipment_id" in key.column_keys
    if table.name.endswith("receipts"):
        assert "VARBINARY(512)" in sql
        assert any(isinstance(c,UniqueConstraint) and tuple(c.columns.keys()) == ("producer_id","event_id") for c in table.constraints)
        assert "request_digest" in table.c and "business_digest" in table.c
        assert "CHECK" in sql
    else:
        assert any(isinstance(c,UniqueConstraint) and tuple(c.columns.keys()) == ("equipment_id","sampled_at") for c in table.constraints)


def test_exact_chained_64_71_75_stages_and_four_table_parity():
    """Recorder只构建离线metadata；不调用Alembic CLI/env或任何连接。"""
    from pathlib import Path
    from tests.test_business_module_migration import load
    from tests.test_core_migration_baseline import MigrationRecorder,_table_signature,VERSIONS_DIR
    from database import Base
    from tests.test_mapping_migration import Recorder
    recorder=Recorder()
    paths=sorted(VERSIONS_DIR.glob('*.py'))
    assert len(paths)==8
    migrations=[load(path) for path in paths]
    assert migrations[-2].revision=='0a2c4e6f8b10' and migrations[-2].down_revision=='f6a8c0e2b4d6'
    assert migrations[-1].revision=='1b3d5f7a9c20' and migrations[-1].down_revision=='0a2c4e6f8b10'
    for migration in migrations[:6]:migration.op=recorder;migration.upgrade()
    assert len(recorder.metadata.tables)==64
    old={name:_table_signature(table) for name,table in recorder.metadata.tables.items()}
    facts=migrations[-2];facts.op=recorder;facts.upgrade()
    assert len(recorder.metadata.tables)==71
    assert not {model.__tablename__ for model in MODELS}.intersection(recorder.metadata.tables)
    integration=migrations[-1];integration.op=recorder;integration.upgrade()
    assert len(recorder.metadata.tables)==75
    for model in MODELS:
        assert _table_signature(recorder.metadata.tables[model.__tablename__])==_table_signature(model.__table__)
    for name,signature in old.items():assert _table_signature(recorder.metadata.tables[name])==signature


def test_downgrade_refuses_any_nonempty_new_table_without_deletion():
    from tests.test_business_module_migration import load
    from tests.test_core_migration_baseline import VERSIONS_DIR
    migration=load(next(VERSIONS_DIR.glob('*1b3d5f7a9c20*.py')))
    class Result:
        def first(self):return (1,)
    class Connection:
        def execute(self,statement):return Result()
    class Operation:
        dropped=[]
        def get_bind(self):return Connection()
        def drop_table(self,name):self.dropped.append(name)
    operation=Operation();migration.op=operation
    with pytest.raises(RuntimeError,match='nonempty'):migration.downgrade()
    assert operation.dropped==[]
