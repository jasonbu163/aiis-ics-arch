"""明确分域SQL及缺测SQL NULL，对照legacy默认；无真实连接。"""
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from sqlalchemy.dialects import mysql
from sqlalchemy import null
from sqlalchemy.orm.persistence import _collect_insert_commands
from sqlalchemy.orm import attributes
from app.equipment.models.equipment import EquipmentDrive,EquipmentProductionParameters
from app.performance.models.performance import Performance
from app.performance.crud import async_production_observation as production
from app.equipment.crud import async_drive_sample,async_equipment,sync_drive
from app.monitor.crud import async_process_curve_sample,async_temperature
from app.performance.crud.async_performance import PerformanceCRUD
from datetime import date
pytestmark=pytest.mark.no_db

class Capture:
    def __init__(self):self.queries=[];self.rows=[]
    async def execute(self,query):self.queries.append(query);return self
    def scalar_one_or_none(self):return None
    def scalar_one_or_none(self):return None
    def scalar_one(self):return 0
    def scalar(self):return 0
    def scalars(self):return self
    def all(self):return []
    def add(self,row):self.rows.append(row)
    async def flush(self):pass

def sql(query):return str(query.compile(dialect=mysql.dialect(),compile_kwargs={'literal_binds':True}))

@pytest.mark.asyncio
async def test_sql_scope_record_limit_and_day_boundaries():
    db=Capture()
    await async_drive_sample.list_records(db,'line-A',7,3)
    text=sql(db.queries[-1]);assert "equipment_drive.equipment_id = 'line-A'" in text and 'equipment_drive.id = 7' in text and 'LIMIT 3' in text
    await async_equipment.equipment_crud.get_latest_drive(db)
    assert 'equipment_drive.equipment_id IS NULL' in sql(db.queries[-1])
    await async_process_curve_sample.list_samples(db,'line-A',date(2026,10,16),None,5)
    text=sql(db.queries[-1]);assert '2026-10-15 16:00:00' in text and '2026-10-16 16:00:00' in text and 'LIMIT 5' in text
    assert 'sampled_at DESC' in text
    query=PerformanceCRUD(db).build_list_query(None,None,None,None,None)
    assert 'performance_main.equipment_id IS NULL' in sql(query)

@pytest.mark.asyncio
async def test_http_none_explicit_null_and_legacy_type_flags():
    db=Capture()
    row=await production.add_record(db,equipment_id='line-A',coil_no='A',parent_coil_no='A',production_date=date(2026,10,16))
    for field in ('output_quantity','qualified_quantity','efficiency_rate','quality_score'):
        assert getattr(row,field).compare(null())
        assert not Performance.__table__.c[field].type.should_evaluate_none
        assert Performance.__table__.c[field].default is not None
    # ORM insert collection is run without Session/engine/connection: explicit None must remain in SQL params.
    drive=EquipmentDrive(equipment_id='line-A',tv=0,km=None)
    state=attributes.instance_state(drive)
    commands=list(_collect_insert_commands(EquipmentDrive.__table__,[(state,state.dict,EquipmentDrive.__mapper__,SimpleNamespace(dialect=mysql.dialect()))],render_nulls=False))
    assert commands[0][2]['km'] is None and commands[0][2]['tv']==0
    assert EquipmentDrive.__table__.c.km.default.arg==0.0
    parameters=EquipmentProductionParameters(equipment_id='line-A',grade=None,width=None)
    state=attributes.instance_state(parameters)
    commands=list(_collect_insert_commands(EquipmentProductionParameters.__table__,[(state,state.dict,EquipmentProductionParameters.__mapper__,SimpleNamespace(dialect=mysql.dialect()))]))
    assert commands[0][2]['grade'] is None and commands[0][2]['width'] is None

    legacy=Performance(output_quantity=None,qualified_quantity=None,efficiency_rate=None,quality_score=None)
    state=attributes.instance_state(legacy)
    command=list(_collect_insert_commands(Performance.__table__,[(state,state.dict,Performance.__mapper__,SimpleNamespace(dialect=mysql.dialect()))]))[0]
    assert not {"output_quantity","qualified_quantity","efficiency_rate","quality_score"}.intersection(command[2])


def test_69_original_public_assignments_preserved_plus_three_empty_scopes():
    import hashlib
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    expected={'.env.example': (8327, '8c7ded4ac77432248965640e1fe6dc1ca7256ad6c929682b00990d0c4cb6376b'), '.env.docker.dev.example': (8232, '4c8c796d67886968837619241a92b22247569693507dd7fd364107ea04739e9d'), '.env.docker.prod.example': (8311, 'ca162c464d944a44989869f4179ab054a129fd6637aeef2c6ca81df97ead118a')}
    scopes={"EQUIPMENT_MAPPING_INGEST_ID","PERFORMANCE_MAPPING_INGEST_ID","MONITOR_MAPPING_INGEST_ID"}
    for name,(length,digest) in expected.items():
        data=(root/name).read_bytes()
        assert hashlib.sha256(data[:length]).hexdigest()==digest
        assignments={line.split('=',1)[0]:line.split('=',1)[1] for line in data.decode().splitlines() if line and not line.startswith('#') and '=' in line}
        assert len(assignments)==72
        assert all(assignments[key]=='' for key in scopes)


@pytest.mark.asyncio
@pytest.mark.parametrize('model',[EquipmentDrive,EquipmentProductionParameters])
async def test_real_async_orm_refresh_compiles_current_read_without_connection(model):
    """执行真正AsyncSession.refresh的SQL构造，在execute前截获；无bind/engine/DB。"""
    from sqlalchemy.orm import Session,make_transient_to_detached
    from sqlalchemy.ext.asyncio import AsyncSession
    from datetime import datetime
    captured=[]
    class CapturedSQL(Exception):pass
    class NoConnectionSession(Session):
        def _execute_internal(self,statement,*args,**kwargs):
            captured.append(str(statement.compile(dialect=mysql.dialect())))
            raise CapturedSQL()
    db=AsyncSession(sync_session_class=NoConnectionSession)
    metric='tv' if model==EquipmentDrive else 'width'
    row=model(id=7,equipment_id='line-A',timestamp=datetime(2026,10,17),**{metric:0})
    make_transient_to_detached(row);db.add(row)
    try:
        with pytest.raises(CapturedSQL):await db.refresh(row,with_for_update=True)
        assert len(captured)==1 and captured[0].endswith('FOR UPDATE')
        assert model.__tablename__+'.id =' in captured[0]
    finally:await db.close()
