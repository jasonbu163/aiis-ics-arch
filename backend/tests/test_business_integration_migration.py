"""仅静态 MySQL DDL：四声明表和引用保护，无 engine/连接/Alembic 执行。"""
import pytest
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.mysql import dialect
from sqlalchemy.schema import CreateTable
from app.equipment.models.integration import EquipmentIntegrationReceipt
from app.monitor.models.integration import MonitorIntegrationReceipt

pytestmark = pytest.mark.no_db
MODELS = (EquipmentIntegrationReceipt, MonitorIntegrationReceipt)
HISTORICAL_TABLES = {"equipment_integration_receipts", "performance_integration_receipts", "monitor_integration_receipts", "performance_integration_observation_events"}


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
    migrations=[load(path) for path in paths[:8]]
    by_revision={load(path).revision: load(path) for path in paths}
    assert migrations[-2].revision=='0a2c4e6f8b10' and migrations[-2].down_revision=='f6a8c0e2b4d6'
    assert migrations[-1].revision=='1b3d5f7a9c20' and migrations[-1].down_revision=='0a2c4e6f8b10'
    for migration in migrations[:6]:migration.op=recorder;migration.upgrade()
    assert len(recorder.metadata.tables)==64
    old={name:_table_signature(table) for name,table in recorder.metadata.tables.items()}
    facts=migrations[-2];facts.op=recorder;facts.upgrade()
    assert len(recorder.metadata.tables)==71
    assert not HISTORICAL_TABLES.intersection(recorder.metadata.tables)
    integration=migrations[-1];integration.op=recorder;integration.upgrade()
    assert len(recorder.metadata.tables)==75
    assert HISTORICAL_TABLES <= set(recorder.metadata.tables)
    for model in MODELS:
        assert _table_signature(recorder.metadata.tables[model.__tablename__])==_table_signature(model.__table__)
    for name,signature in old.items():assert _table_signature(recorder.metadata.tables[name])==signature
    successor=by_revision['2c4e6a8b0d12']
    assert successor.revision=='2c4e6a8b0d12' and successor.down_revision=='1b3d5f7a9c20'
    successor.op=recorder;successor.upgrade()
    assert len(recorder.metadata.tables)==77
    from app.plc_facts.models.v2 import SampleV2,LatestPointV2
    assert _table_signature(recorder.metadata.tables['plc_facts_latest_points_v2'])==_table_signature(LatestPointV2.__table__)
    old_history=_table_signature(recorder.metadata.tables['plc_facts_samples_v2'])
    new_history=_table_signature(SampleV2.__table__)
    old_columns={column[0]:column for column in old_history['columns']}
    new_columns={column[0]:column for column in new_history['columns']}
    assert set(new_columns)==set(old_columns)|{'source_type'}
    for name,old_column in old_columns.items():
        new_column=new_columns[name]
        if name in {'group_id','config_revision'}:
            assert old_column[:2]==new_column[:2] and old_column[2] is False and new_column[2] is True
            assert old_column[3:]==new_column[3:]
        else: assert old_column==new_column
    assert old_history['indexes']==new_history['indexes']
    retirement=by_revision['3d5f7a9c1e23']
    assert retirement.revision=='3d5f7a9c1e23' and retirement.down_revision==successor.revision
    final=by_revision['4e6a8b0d2f14']
    assert final.revision=='4e6a8b0d2f14' and final.down_revision==retirement.revision
    assert by_revision['5f7a9c1e3b25'].down_revision == final.revision


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
