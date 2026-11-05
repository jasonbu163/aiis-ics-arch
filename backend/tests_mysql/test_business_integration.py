"""BE010 r2 B独立MySQL8.4.6入口源码；执行须另批目标/账号/迁移/故障/清理，不由pytest共享fixture启动。"""
from __future__ import annotations
import argparse
import asyncio
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
import json
import os
from pathlib import Path
import sys


class Target:
    """仅接受显式临时公开BE010-r2-B、单一schema/endpoint ACK；不创建/删除数据库。"""
    def __init__(self):
        self.root=Path.cwd().resolve()
        if not self.root.is_relative_to(Path('/private/tmp')) or (self.root/'.env').exists():
            raise RuntimeError('dedicated public temporary source required')
        profile=json.loads((self.root/'profile.json').read_text())
        assert profile['profile']=='BE010-r2-B' and profile['expected_table_count']==75
        assert profile['target_revision']=='1b3d5f7a9c20'
        assert os.environ['BE010_MYSQL_EXECUTION_ACK']=='ARCH-BE-010-r2-B'
        assert os.environ['BE010_MYSQL_SCHEMA_ACK']==os.environ['TEST_MYSQL_DATABASE']
        assert os.environ['BE010_MYSQL_ENDPOINT_ACK']==os.environ['MYSQL_HOST']+':'+os.environ['MYSQL_PORT']
        assert os.environ['MYSQL_HOST']=='127.0.0.1'
        assert os.environ['TEST_MYSQL_DATABASE'].startswith('arch_be010_r2_')
        assert os.environ['TEST_MYSQL_DATABASE']!=os.environ['MYSQL_DATABASE']
        assert os.environ['MYSQL_USER']!='root' and os.environ['TESTING'].lower()=='true'
        assert all(os.environ.get(key,'False').lower()=='false' for key in ('BACKEND_MOCK_ENABLED','PROJECTION_RUNNER_ENABLED','ADMIN_BOOTSTRAP_ENABLED','SUPERVISOR_BOOTSTRAP_ENABLED','OPERATOR_BOOTSTRAP_ENABLED'))
        self._guard()
        from settings import settings
        assert settings.primary_database=='mysql' and settings.TEST_MYSQL_DATABASE==os.environ['TEST_MYSQL_DATABASE']
        from sqlalchemy import create_engine, inspect, text
        self.sync_engine=create_engine(settings.SYNC_DATABASE_URL,pool_pre_ping=True)
        with self.sync_engine.connect() as connection:
            assert str(connection.execute(text('SELECT VERSION()')).scalar_one()).split('-')[0]=='8.4.6'
            assert connection.execute(text('SELECT version_num FROM alembic_version')).scalar_one()=='1b3d5f7a9c20'
            from app.module_registry import import_model_packages
            import_model_packages()
            from app.user.models.user import User
            from app.user.models.token_blacklist import TokenBlacklist
            from app.control_agent.models.gate_token import ControlAgentGateToken
            from database import Base
            assert len(Base.metadata.tables)==75
            assert set(inspect(connection).get_table_names())==set(Base.metadata.tables)|{'alembic_version'}
        from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
        self.engine=create_async_engine(settings.DATABASE_URL,pool_pre_ping=True)
        self.sessions=async_sessionmaker(self.engine,expire_on_commit=False,autoflush=False)
        self.prefix='be010-'+os.environ['BE010_MYSQL_RUN_ID']
        if not self.prefix.replace('-','').isalnum():raise RuntimeError('simple unique run id required')

    def _guard(self):
        import socket,sqlite3
        from sqlalchemy.engine import Engine
        endpoint=(os.environ['MYSQL_HOST'],int(os.environ['MYSQL_PORT']))
        schema=os.environ['TEST_MYSQL_DATABASE'];user=os.environ['MYSQL_USER']
        original=socket.socket.connect
        def connect(sock,address):
            assert address==endpoint
            return original(sock,address)
        def denied(*args,**kwargs):raise AssertionError('BE010 explicit target guard denied operation')
        socket.socket.connect=connect;socket.socket.bind=denied;socket.socket.listen=denied
        sqlite3.connect=denied
        for name in ('connect','raw_connection'):
            old=getattr(Engine,name)
            def guarded(engine,*args,_old=old,**kwargs):
                url=engine.url
                assert url.get_backend_name()=='mysql' and (url.host,url.port)==endpoint and url.database==schema and url.username==user
                return _old(engine,*args,**kwargs)
            setattr(Engine,name,guarded)
        for name in ('pymysql','aiomysql'):
            module=__import__(name);old=module.connect
            def db_connect(*args,_old=old,**kwargs):
                assert not args and (kwargs['host'],int(kwargs.get('port',3306)))==endpoint
                assert kwargs.get('db',kwargs.get('database'))==schema and kwargs['user']==user
                return _old(**kwargs)
            module.connect=db_connect

    async def adoption(self,owner,db):
        from importlib import import_module
        from tests.test_business_integration_storage import manifest
        probe=await import_module('app.'+owner+'.crud.async_integration').probe_storage(db)
        evidence=manifest(owner)
        evidence.update(serverUuid=probe.server_uuid,schema=probe.schema,schemaRevision=probe.schema_revision,
            sourceRevision=os.environ['BE010_SOURCE_REVISION_ACK'],ownerApprovalRef='synthetic-B:'+os.environ['BE010_MYSQL_EXECUTION_ACK'])
        return evidence

    def payload(self,index,event=None):
        from tests.test_business_integration_contract import example
        payload=example(index)
        payload.update(producerId=self.prefix,eventId=event or 'resource-'+str(index))
        payload['data']['equipmentId']=self.prefix
        if 'coilNo' in payload['data']:payload['data']['coilNo']=self.prefix
        return payload

    async def receive(self,index,payload,parent_id=None,session=None):
        from tests.test_business_integration_contract import REQUESTS,RESOURCES
        owners=('equipment',)*3+('performance',)*4+('monitor',)
        from importlib import import_module
        async def invoke(db):
            evidence=await self.adoption(owners[index],db)
            request=REQUESTS[index].model_validate(payload)
            if index<3:return await import_module('app.equipment.services.async_integration').receive_sample(db,request,evidence,RESOURCES[index])
            if index==3:return await import_module('app.performance.services.async_integration_observation').receive_observation(db,request,evidence)
            if index<7:return await import_module('app.performance.services.async_integration_process').receive_sample(db,request,evidence,parent_id,RESOURCES[index].removeprefix('process_'))
            return await import_module('app.monitor.services.async_integration').receive_sample(db,request,evidence)
        if session is not None:return await invoke(session)
        async with self.sessions() as db:return await invoke(db)

    async def business(self):
        from sqlalchemy import select
        from tests.test_business_integration_contract import RESOURCES
        from app.equipment.crud.async_integration import MODELS as EQUIPMENT
        from app.performance.crud.async_integration import MODELS as PROCESS
        from app.performance.models.performance import Performance
        from app.monitor.models.business_history import HistoryProcessCurve
        models=[EQUIPMENT['temperature'],EQUIPMENT['drive'],EQUIPMENT['production_parameters'],Performance,PROCESS['temperature'],PROCESS['tension'],PROCESS['speed'],HistoryProcessCurve]
        parent=None;results=[]
        for index in (3,0,1,2,4,5,6,7):
            payload=self.payload(index)
            result=await self.receive(index,payload,parent)
            if index==3:parent=result.record_id
            replay=await self.receive(index,payload,parent)
            assert replay.receipt_id==result.receipt_id and replay.record_id==result.record_id and replay.committed_at==result.committed_at
            assert replay.outcome=='duplicate' and replay.original_outcome==result.original_outcome
            async with self.sessions() as db:
                row=(await db.execute(select(models[index]).where(models[index].id==result.record_id))).scalar_one()
                assert row.equipment_id==self.prefix
                field={0:'zone1_act',1:'tv',2:'weight',3:'collected_weight',4:'set_temp',5:'set_tension',6:'set_speed',7:'z6_temp_act'}[index]
                expected=Decimal('199.5') if index==0 else Decimal('0.1') if index==1 else Decimal(0)
                assert abs(Decimal(str(getattr(row,field)))-expected)<=Decimal('0.000001')
            changed=deepcopy(payload);changed['mappingRevision']='conflict'
            from common.exceptions import BusinessException
            try:await self.receive(index,changed,parent)
            except BusinessException as exc:assert exc.code==409 and str(exc.error_code).endswith('event_conflict')
            else:raise AssertionError('same delivery changed content accepted')
            results.append(dict(resource=RESOURCES[index],receiptId=result.receipt_id,recordId=result.record_id,requestDigest=result.request_digest))
        (self.root/'be010-business-proof.json').write_text(json.dumps(results,indent=2))
        return parent

    async def faults_and_concurrency(self,parent):
        from common.exceptions import BusinessException
        from sqlalchemy.ext.asyncio import AsyncSession
        payload=self.payload(1,'concurrent')
        results=await asyncio.gather(*(self.receive(1,payload) for _ in range(4)),return_exceptions=True)
        successes=[result for result in results if not isinstance(result,Exception)]
        assert successes and len({r.receipt_id for r in successes})==1
        for result in results:
            if isinstance(result,Exception):assert isinstance(result,BusinessException) and result.code==503
        class LostCommit(AsyncSession):
            async def commit(self):
                await super().commit()
                raise RuntimeError('synthetic response loss after committed transaction')
        payload=self.payload(1,'lost-commit')
        async with LostCommit(bind=self.engine,expire_on_commit=False,autoflush=False) as db:
            try:await self.receive(1,payload,session=db)
            except BusinessException as exc:assert str(exc.error_code).endswith('commit_unknown')
            else:raise AssertionError('unknown commit claimed success')
        recovered=await self.receive(1,payload)
        assert recovered.outcome=='duplicate'
        missing=self.payload(4,'missing-parent')
        try:await self.receive(4,missing,2147483647)
        except BusinessException as exc:assert exc.code==404
        else:raise AssertionError('missing parent accepted')
        mismatch=self.payload(4,'wrong-coil');mismatch['data']['coilNo']='different'
        try:await self.receive(4,mismatch,parent)
        except BusinessException as exc:assert exc.code==409
        else:raise AssertionError('mismatched parent accepted')

    async def retained(self):
        from sqlalchemy import select
        from importlib import import_module
        proof=json.loads((self.root/'be010-business-proof.json').read_text())
        for item in proof:
            owner='equipment' if item['resource'] in ('temperature','drive','production_parameters') else 'monitor' if item['resource']=='process_curve' else 'performance'
            cls=import_module('app.'+owner+'.models.integration').__dict__[owner.title()+'IntegrationReceipt']
            async with self.sessions() as db:
                receipt=(await db.execute(select(cls).where(cls.id==item['receiptId']))).scalar_one()
                assert receipt.request_digest==item['requestDigest'] and receipt.source_refs
                replay=await self.receive(('temperature','drive','production_parameters','production_observation','process_temperature','process_tension','process_speed','process_curve').index(item['resource']),self.payload(('temperature','drive','production_parameters','production_observation','process_temperature','process_tension','process_speed','process_curve').index(item['resource'])),next(x['recordId'] for x in proof if x['resource']=='production_observation'))
                assert replay.receipt_id==item['receiptId']


async def run(suite):
    target=Target()
    try:
        if suite=='retained':await target.retained()
        else:
            parent=await target.business()
            await target.faults_and_concurrency(parent)
        print(json.dumps(dict(event='be010_mysql_complete',suite=suite,state='B_evidence_only')))
    finally:
        await target.engine.dispose();target.sync_engine.dispose()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--suite',choices=('business','retained'),required=True)
    asyncio.run(run(parser.parse_args().suite))
