"""BE010 r2隔离MySQL合成旧行T1证据入口源码；只对显式B目标运行，不是历史数据apply工具。"""
from __future__ import annotations
import asyncio
from datetime import date,datetime
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_business_integration import Target


async def run():
    target=Target()
    from sqlalchemy import select
    from common.integration.storage import to_storage_time,validate_adoption_probe,StorageProbe
    from importlib import import_module
    from app.equipment.models.temperature_sample import EquipmentTemperatureSample,EquipmentTemperatureSampleReceipt
    from app.equipment.models.equipment import EquipmentDrive,EquipmentProductionParameters
    from app.equipment.models.mapping_ingest import EquipmentMappingReceipt
    from app.performance.models.performance import Performance,ProcessTemperature,ProcessTension,ProcessSpeed
    from app.performance.models.mapping_ingest import PerformanceMappingReceipt,PerformanceObservationState
    from app.monitor.models.business_history import HistoryProcessCurve
    from app.monitor.models.mapping_ingest import MonitorMappingReceipt
    wall=datetime(2026,11,3,17,1,2,123000)
    equipment=target.prefix+'-time'
    fingerprint='1'*64
    old_result={'sampled_at':'2026-11-03T17:01:02.123Z','original':'preserve_exact_JSON_content'}
    try:
        async with target.sessions() as db:
            sample=EquipmentTemperatureSample(equipment_id=equipment,sampled_at=wall,quality='good',fingerprint=fingerprint,
                **{f'zone{n}_{mode}':0 for n in range(1,6) for mode in ('set','act')})
            drive=EquipmentDrive(equipment_id=equipment,timestamp=wall)
            parameters=EquipmentProductionParameters(equipment_id=equipment,timestamp=wall,entry_time=wall,coil_no=equipment,http_coil_key=equipment.encode(),process_steps=[])
            performance=Performance(equipment_id=equipment,coil_no=equipment,parent_coil_no=equipment,http_coil_key=equipment.encode(),
                production_date=date(2026,11,3),manual_override_weight=0,effective_weight=0,weight=0)
            curve=HistoryProcessCurve(equipment_id=equipment,sampled_at=wall,created_at=wall,fingerprint=fingerprint)
            db.add_all([sample,drive,parameters,performance,curve]);await db.flush()
            children=[kind(equipment_id=equipment,performance_id=performance.id,zone='fixture',http_zone_key=b'fixture',record_time=wall) for kind in (ProcessTemperature,ProcessTension,ProcessSpeed)]
            receipts=[EquipmentTemperatureSampleReceipt(actor_user_id=1,equipment_id=equipment,sample_id=target.prefix,fingerprint=fingerprint,sample_record_id=sample.id,sampled_at=wall,outcome='created'),
                EquipmentMappingReceipt(actor_user_id=1,equipment_id=equipment,stream='drive',sample_id=target.prefix,fingerprint=fingerprint,sampled_at=wall,outcome='created',result=old_result,drive_record_id=drive.id),
                PerformanceMappingReceipt(actor_user_id=1,equipment_id=equipment,stream='production_observation',sample_id=target.prefix,fingerprint=fingerprint,sampled_at=wall,outcome='created',result=old_result,performance_id=performance.id),
                PerformanceObservationState(equipment_id=equipment,last_sampled_at=wall,fingerprint=fingerprint,performance_id=performance.id,observation_status='in_production',result=old_result),
                MonitorMappingReceipt(actor_user_id=1,equipment_id=equipment,sample_id=target.prefix,fingerprint=fingerprint,sampled_at=wall,outcome='created',result=old_result,curve_record_id=curve.id)]
            rows=[sample,drive,parameters,performance,curve]+children+receipts
            profiles={owner:import_module('app.'+owner+'.integration_storage').BUSINESS_TIME_COLUMN_PROFILE for owner in ('equipment','performance','monitor')}
            columns={table:fields for profile in profiles.values() for table,fields in profile['columns'].items()}
            assert len(rows)==len(columns)==13 and sum(map(len,columns.values()))==41
            for row in rows:
                for field in columns[row.__tablename__]:setattr(row,field,wall)
            db.add_all(children+receipts);await db.commit()
        before={};ids={}
        async with target.sessions() as db:
            for original in rows:
                row=(await db.execute(select(type(original)).where(type(original).id==original.id))).scalar_one()
                before[row.__tablename__]={column.name:getattr(row,column.name) for column in row.__table__.columns}
                ids[row.__tablename__]=row.id
                for field in columns[row.__tablename__]:setattr(row,field,to_storage_time(getattr(row,field),'utc_wall'))
            await db.commit()
        async with target.sessions() as db:
            for original in rows:
                row=(await db.execute(select(type(original)).where(type(original).id==ids[original.__tablename__]))).scalar_one()
                for column in row.__table__.columns:
                    expected=before[row.__tablename__][column.name]
                    if column.name in columns[row.__tablename__]:expected=to_storage_time(expected,'utc_wall')
                    assert getattr(row,column.name)==expected,(row.__tablename__,column.name)
            assert (await db.execute(select(Performance).where(Performance.id==performance.id))).scalar_one().manual_override_weight==0
            for owner in profiles:
                probe=await import_module('app.'+owner+'.crud.async_integration').probe_storage(db)
                evidence=await target.adoption(owner,db)
                if owner=='performance':evidence['basisProfile']['manualNaive']='utc_wall'
                context=validate_adoption_probe(evidence,probe)
                assert context.manifest['state']=='adopted'
                evidence['serverUuid']='wrong-target'
                try:validate_adoption_probe(evidence,probe)
                except ValueError:pass
                else:raise AssertionError('wrong target adoption accepted')
        report=dict(event='be010_synthetic_time_complete',tables=13,calendarColumns=41,idsValuesFingerprintsJsonDatePreserved=True,
            state='isolated_synthetic_evidence_only',productionHistoricalAdoption=False)
        (target.root/'be010-time-proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
    finally:
        await target.engine.dispose();target.sync_engine.dispose()


if __name__=='__main__':asyncio.run(run())
