"""BE003 B独立显式MySQL8.4.6验证入口；仅compile/collect不连接，执行须具体Owner批准。"""
from __future__ import annotations
import asyncio
from datetime import datetime,timedelta
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


class TemperatureTarget:
    """只接受本任务公开60表副本及逐库/endpoint/动作ACK；不创建或删除schema。"""
    def __init__(self):
        self.root=Path.cwd().resolve()
        assert self.root.is_relative_to(Path("/private/tmp")), "Only a dedicated temporary public profile is allowed"
        assert not (self.root/".env").exists()
        profile=json.loads((self.root/"profile.json").read_text())
        assert profile["profile"]=="BE003" and profile["expected_table_count"]==60
        assert profile["target_revision"]=="e4f6a8b0c2d4"
        self.scenario=os.environ["BE003_MYSQL_SCENARIO"]
        names={"empty":"arch_be003_r3_empty","upgrade":"arch_be003_r3_upgrade","rollback":"arch_be003_r3_rollback"}
        self.database=os.environ["TEST_MYSQL_DATABASE"]
        assert self.database==names[self.scenario]==os.environ["BE003_MYSQL_SCHEMA_ACK"]
        assert os.environ["BE003_MYSQL_DISPOSABLE_ACK"]=="ARCH-BE-003-r3"
        assert os.environ["MYSQL_HOST"]=="127.0.0.1"
        assert os.environ["BE003_MYSQL_ENDPOINT_ACK"]=="127.0.0.1:"+os.environ["MYSQL_PORT"]
        assert self.database != os.environ["MYSQL_DATABASE"]
        assert os.environ["TESTING"].lower()=="true"
        for key in ("BACKEND_MOCK_ENABLED","PROJECTION_RUNNER_ENABLED","ADMIN_BOOTSTRAP_ENABLED","SUPERVISOR_BOOTSTRAP_ENABLED","OPERATOR_BOOTSTRAP_ENABLED"):
            assert os.environ[key].lower()=="false", key
        import settings as configuration
        assert Path(configuration.__file__).resolve().parent==self.root
        settings=configuration.settings
        assert settings.primary_database=="mysql" and settings.TEST_MYSQL_DATABASE==self.database
        from sqlalchemy import create_engine,inspect
        self.engine=create_engine(settings.SYNC_DATABASE_URL,pool_pre_ping=True)
        with self.engine.connect() as conn:
            database,version,account=conn.exec_driver_sql("SELECT DATABASE(),VERSION(),CURRENT_USER()").one()
            assert database==self.database and str(version).split("-")[0]=="8.4.6"
            assert not str(account).startswith("root@")
            assert not inspect(conn).get_table_names(), "Every scenario must start with a new empty schema"
            (self.root/"mysql-target.json").write_text(json.dumps(dict(database=database,version=version,account=account)))


    def migrate(self, revision, direction='upgrade'):
        command = [sys.executable, '-m', 'alembic', direction, revision]
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        output = result.stdout + result.stderr
        for key in ('MYSQL_PASSWORD', 'MYSQL_ROOT_PASSWORD'):
            secret = os.environ.get(key)
            if secret:
                output = output.replace(secret, '[REDACTED]')
        with (self.root / 'migration-commands.jsonl').open('a') as stream:
            stream.write(json.dumps(dict(command=command, exit_code=result.returncode, output=output)) + '\n')
        result.check_returncode()

    def checksum(self, names):
        from sqlalchemy import MetaData, Table, select
        result = {}
        with self.engine.connect() as connection:
            for name in sorted(names):
                table = Table(name, MetaData(), autoload_with=connection)
                rows = sorted([tuple(map(str, row)) for row in connection.execute(select(table))])
                result[name] = hashlib.sha256(json.dumps(rows).encode()).hexdigest()
        with (self.root / 'checksum-snapshots.jsonl').open('a') as stream:
            stream.write(json.dumps(result, sort_keys=True) + '\n')
        return result

    def assert_schema(self):
        """逐表列/PK/FK/唯一约束/check/index对照；不调用metadata.create_all。"""
        from sqlalchemy import inspect, UniqueConstraint, CheckConstraint
        from sqlalchemy.dialects import mysql
        from database import Base
        from app.module_registry import import_model_packages
        import_model_packages()
        from app.control_agent.models.gate_token import ControlAgentGateToken
        from app.user.models.token_blacklist import TokenBlacklist
        inspector = inspect(self.engine)
        assert len(Base.metadata.tables) == 60
        assert set(inspector.get_table_names()) == set(Base.metadata.tables) | {'alembic_version'}

        def expression(value):
            if value is None:
                return None
            tokens = re.findall('\'(?:\'\'|\\\\.|[^\'])*\'|\\"(?:\\"\\"|\\\\.|[^\\"])*\\"|`[^`]*`|[a-zA-Z_][a-zA-Z_0-9]*|\\d+(?:\\.\\d+)?|>=|<=|<>|!=|[^\\s]', str(value))
            tokens = [token if token.startswith(("'", '"')) else token.strip('`').lower() for token in tokens]
            tokens = [token for (position, token) in enumerate(tokens) if not (token == '_utf8mb4' and position + 1 < len(tokens) and tokens[position + 1].startswith(("'", '"')))]
            while tokens and tokens[0] == '(' and (tokens[-1] == ')'):
                depth = 0
                for (position, token) in enumerate(tokens):
                    depth += (token == '(') - (token == ')')
                    if depth == 0:
                        break
                if position != len(tokens) - 1:
                    break
                tokens = tokens[1:-1]
            position = 0
            while position + 4 < len(tokens):
                group = tokens[position:position + 5]
                if group[0] == '(' and group[4] == ')' and (group[2] in {'>=', '<=', '=', '<', '>', '!=', '<>'}) and all((token not in {'(', ')', 'and', 'or', 'xor', 'not'} for token in (group[1], group[3]))):
                    tokens[position:position + 5] = group[1:4]
                position += 1
            if tokens in (['current_timestamp'], ['current_timestamp', '(', ')']):
                tokens = ['now', '(', ')']
            return tuple(tokens)

        def action(value):
            return 'RESTRICT' if value in {None, 'NO ACTION', 'RESTRICT'} else value
        report = {'database': self.database, 'tables': sorted(Base.metadata.tables), 'comparisons': {}}
        for (name, table) in Base.metadata.tables.items():
            actual = inspector.get_columns(name)
            assert [column['name'] for column in actual] == list(table.columns.keys()), name
            for (column, expected) in zip(actual, table.columns):

                def normalized(value):
                    text = str(value).upper().replace('INTEGER', 'INT').replace('NUMERIC', 'DECIMAL')
                    # MySQL反射显式展开bin collation自带的utf8mb4；仅折叠这一确切等价对。
                    text = text.replace(' CHARACTER SET UTF8MB4 COLLATE UTF8MB4_BIN', ' COLLATE UTF8MB4_BIN')
                    if text == 'DECIMAL':
                        text = 'DECIMAL(10, 0)'
                    return 'TINYINT(1)' if text in {'BOOL', 'BOOLEAN'} else text
                assert normalized(column['type'].compile(dialect=mysql.dialect())) == normalized(expected.type.compile(dialect=mysql.dialect())), (name, expected.name)
                assert column['nullable'] == expected.nullable, (name, expected.name)
                default = str(expected.server_default.arg) if expected.server_default is not None else None
                assert expression(column['default']) == expression(default), (name, expected.name, column['default'], default)
            assert inspector.get_pk_constraint(name)['constrained_columns'] == [c.name for c in table.primary_key]
            expected_fk = {(tuple((fk.parent.name for fk in constraint.elements)), tuple((fk.column.table.name for fk in constraint.elements)), tuple((fk.column.name for fk in constraint.elements))) for constraint in table.foreign_key_constraints}
            actual_fk = {(tuple(fk['constrained_columns']), tuple([fk['referred_table']] * len(fk['referred_columns'])), tuple(fk['referred_columns'])) for fk in inspector.get_foreign_keys(name)}
            assert actual_fk == expected_fk, name
            expected_options = {tuple((fk.parent.name for fk in constraint.elements)): (action(constraint.ondelete), action(constraint.onupdate)) for constraint in table.foreign_key_constraints}
            actual_options = {tuple(fk['constrained_columns']): (action(fk.get('options', {}).get('ondelete')), action(fk.get('options', {}).get('onupdate'))) for fk in inspector.get_foreign_keys(name)}
            assert actual_options == expected_options, name
            expected_unique = {tuple((c.name for c in constraint.columns)) for constraint in table.constraints if isinstance(constraint, UniqueConstraint)}
            expected_unique |= {tuple((c.name for c in index.columns)) for index in table.indexes if index.unique}
            assert {tuple(c['column_names']) for c in inspector.get_unique_constraints(name)} == expected_unique, name
            actual_indexes = {index['name']: (tuple(index['column_names']), bool(index['unique'])) for index in inspector.get_indexes(name)}
            for index in table.indexes:
                assert actual_indexes[index.name] == (tuple((c.name for c in index.columns)), index.unique), (name, index.name)
            expected_checks = {constraint.name for constraint in table.constraints if isinstance(constraint, CheckConstraint)}
            assert {constraint['name'] for constraint in inspector.get_check_constraints(name)} == expected_checks, name
            actual_check_sql = {constraint['name']: expression(constraint['sqltext']) for constraint in inspector.get_check_constraints(name)}
            expected_check_sql = {constraint.name: expression(constraint.sqltext) for constraint in table.constraints if isinstance(constraint, CheckConstraint)}
            assert actual_check_sql == expected_check_sql, name
            report['comparisons'][name] = dict(columns=[dict(name=c['name'], type=str(c['type']), nullable=c['nullable'], default=c['default']) for c in actual], foreign_keys=inspector.get_foreign_keys(name), unique=inspector.get_unique_constraints(name), indexes=inspector.get_indexes(name), checks=inspector.get_check_constraints(name))
        (self.root / 'schema-reflection.json').write_text(json.dumps(report, indent=2, default=str))

    def seed_legacy(self):
        from sqlalchemy.orm import Session
        from app.user.models.user import User
        from app.equipment.models.equipment import EquipmentTemperature
        with Session(self.engine) as db:
            db.add_all([User(username="temperature-admin-one",password="synthetic-unused",name="Fixture one",role="admin",is_active=True),
                        User(username="temperature-admin-two",password="synthetic-unused",name="Fixture two",role="admin",is_active=True),
                        User(username="temperature-supervisor",password="synthetic-unused",name="Fixture supervisor",role="supervisor",is_active=True),
                        User(username="temperature-operator",password="synthetic-unused",name="Fixture operator",role="operator",is_active=True),
                        User(username="temperature-unknown",password="synthetic-unused",name="Fixture unknown",role="unknown",is_active=True),
                        User(username="temperature-inactive",password="synthetic-unused",name="Fixture inactive",role="admin",is_active=False)])
            db.add(EquipmentTemperature(timestamp=datetime(2020,1,2,3,4,5),**{f"zone{z}_{k}":z+0.25 for z in range(1,6) for k in ("set","act")}))
            from core.jwt import create_access_token,decode_token
            from app.user.models.token_blacklist import TokenBlacklist
            self.revoked_token=create_access_token({"sub":"temperature-admin-one"})
            db.add(TokenBlacklist(token=decode_token(self.revoked_token)["jti"],expires_at=datetime.now()+timedelta(hours=1)))
            db.commit()

    def api(self):
        from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
        from settings import settings
        from core.registrar import create_app
        from app.equipment.config import TemperatureConfig,get_temperature_config
        from database import get_db
        engine=create_async_engine(settings.DATABASE_URL,pool_pre_ping=True)
        sessions=async_sessionmaker(engine,expire_on_commit=False,autoflush=False)
        app=create_app(testing=True)
        async def get_session():
            async with sessions() as db:
                try:
                    yield db
                    await db.commit()
                except Exception:
                    await db.rollback()
                    raise
        app.dependency_overrides[get_db]=get_session
        app.dependency_overrides[get_temperature_config]=lambda:TemperatureConfig(EQUIPMENT_TEMPERATURE_PILOT_ID="temperature-pilot-01",_env_file=None)
        return app,engine,sessions


def sample_payload(**changes):
    result=dict(equipmentId="temperature-pilot-01",sampleId="delivery-A",sampledAt="2026-10-16T10:00:00.123Z",quality="good")
    result.update({f"zone{z}{k}":0 if z==1 else z+0.125 for z in range(1,6) for k in ("Set","Act")})
    result["zone2Set"]=0.0000000001
    result["zone5Act"]=99999999999999999999
    result.update(changes)
    return result


def test_explicit_mysql_temperature_samples(monkeypatch):
    target=TemperatureTarget()
    try:
        if target.scenario=="empty":
            target.migrate("e4f6a8b0c2d4")
            target.seed_legacy()
        else:
            target.migrate("d2f4a6b8c0e2")
            target.seed_legacy()
        from sqlalchemy import inspect,text
        old_tables=set(inspect(target.engine).get_table_names())-{"alembic_version","equipment_temperature_samples","equipment_temperature_sample_receipts"}
        assert len(old_tables)==58
        before=target.checksum(old_tables)
        if target.scenario!="empty":target.migrate("e4f6a8b0c2d4")
        target.assert_schema()
        assert target.checksum(old_tables)==before
        asyncio.run(real_behavior(target,monkeypatch))
        assert target.checksum(old_tables)==before
        if target.scenario=="rollback":
            target.migrate("d2f4a6b8c0e2","downgrade")
            assert set(inspect(target.engine).get_table_names())==old_tables|{"alembic_version"}
            assert target.checksum(old_tables)==before
            target.migrate("e4f6a8b0c2d4")
            target.assert_schema()
            assert target.checksum(old_tables)==before
    finally:
        target.engine.dispose()


async def real_behavior(target,monkeypatch):
    from httpx import ASGITransport,AsyncClient
    from sqlalchemy import select,func
    from sqlalchemy.exc import IntegrityError,OperationalError
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.user.models.user import User
    from app.equipment.models.temperature_sample import EquipmentTemperatureSample as Sample,EquipmentTemperatureSampleReceipt as Receipt
    from app.equipment.crud import async_temperature_sample as crud
    from app.equipment.services import async_temperature_sample as service
    from core.jwt import create_access_token,create_refresh_token
    app,engine,sessions=target.api()
    async with sessions() as db:
        users=list((await db.execute(select(User).order_by(User.id))).scalars())
    tokens=[create_access_token({"sub":user.username}) for user in users]
    async def counts():
        async with sessions() as db:
            return (await db.scalar(select(func.count()).select_from(Sample)),await db.scalar(select(func.count()).select_from(Receipt)))
    async def post(client,data,actor=0):
        return await client.post("/api/v1/equipment/temperature-samples",json=data,headers={"Authorization":"Bearer "+tokens[actor]})
    try:
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://fixture") as client:
            headers={"Authorization":"Bearer "+tokens[0]}
            old=(await client.get("/api/v1/equipment/temperature-control?limit=1",headers=headers)).json()
            assert old["data"]["temperatureHistory"][0]["time"]=="03:04:05"
            invalid_tokens=[None,"malformed",create_access_token({"sub":users[0].username},timedelta(seconds=-1)),
                            create_refresh_token({"sub":users[0].username}),target.revoked_token,tokens[5]]
            for token in invalid_tokens:
                for method in ("GET","POST"):
                    auth={} if token is None else {"Authorization":"Bearer "+token}
                    response=await client.request(method,"/api/v1/equipment/temperature-samples",json=sample_payload() if method=="POST" else None,headers=auth)
                    assert response.status_code==401 and response.json()["errorCode"]=="equipment.temperature_unauthenticated"
            for actor,grants,read_status in [(2,("equipment-temperature-read",),200),(3,("equipment-temperature-read",),200),
                    (2,("equipment-temperature-ingest",),403),(3,("equipment","projection-mapping-manage","control-agent-read"),403),
                    (4,("equipment-temperature-read",),403)]:
                app.state.role_api_permissions={users[actor].role:grants}
                response=await client.get("/api/v1/equipment/temperature-samples",headers={"Authorization":"Bearer "+tokens[actor]})
                assert response.status_code==read_status
                assert (await post(client,sample_payload(),actor)).status_code==403
            from app.equipment.config import TemperatureConfig,get_temperature_config
            configured=app.dependency_overrides[get_temperature_config]
            app.dependency_overrides[get_temperature_config]=lambda:TemperatureConfig(EQUIPMENT_TEMPERATURE_PILOT_ID="",_env_file=None)
            try:
                assert (await client.get("/api/v1/equipment/temperature-samples",headers=headers)).status_code==403
                assert (await post(client,sample_payload())).status_code==403
            finally:app.dependency_overrides[get_temperature_config]=configured
            assert await counts()==(0,0)
            response=await post(client,sample_payload());assert response.status_code==200
            first=response.json()["data"];assert first["outcome"]=="created"
            response=await client.get("/api/v1/equipment/temperature-samples",params={"recordId":first["recordId"]},headers=headers)
            item=response.json()["data"]["items"][0]
            for z in range(1,6):
                for k in ("Set","Act"):assert item[f"zone{z}{k}"]==sample_payload()[f"zone{z}{k}"]
            assert item["sampledAt"]=="2026-10-16T10:00:00.123Z" and item["createdAt"].endswith("Z")
            assert "sampleId" not in item
            for data,actor in [(sample_payload(),0),(sample_payload(sampledAt="2026-10-16T18:00:00.123+08:00"),0),(sample_payload(sampleId="delivery-B"),0),(sample_payload(),1)]:
                response=await post(client,data,actor);assert response.status_code==200 and response.json()["data"]["recordId"]==first["recordId"] and response.json()["data"]["outcome"]=="duplicate"
            # 刷新access token后稳定User.id仍使用同一receipt。
            tokens[0]=create_access_token({"sub":users[0].username})
            assert (await post(client,sample_payload())).json()["data"]["recordId"]==first["recordId"]
            assert await counts()==(1,3)
            for data,key in [(sample_payload(zone1Set=1),"sample_id_conflict"),(sample_payload(sampleId="new",zone1Set=1),"sample_time_conflict")]:
                response=await post(client,data);assert response.status_code==409 and response.json()["errorCode"].endswith(key)
            assert await counts()==(1,3)
            for n,time in enumerate(["2026-10-16T10:00:00.124Z","2026-10-16T09:00:00.123Z"]):
                assert (await post(client,sample_payload(sampleId=f"time-{n}",sampledAt=time))).status_code==200
            response=await client.get("/api/v1/equipment/temperature-samples?limit=1",headers=headers)
            assert response.json()["data"]["items"][0]["sampledAt"].endswith(".124Z")
            assert await counts()==(3,5)
            response=await client.get("/api/v1/equipment/temperature-samples?recordId=999999",headers=headers)
            assert response.json()["data"]["items"]==[]
            response=await client.get("/api/v1/equipment/temperature-samples?equipmentId=Temperature-pilot-01",headers=headers)
            assert response.status_code==403
            assert (await post(client,sample_payload(equipmentId="Temperature-pilot-01"))).status_code==403
            # 首次竞争：同投递同/异payload，以及不同投递同业务键同/异payload。
            for n,(same_id,changed) in enumerate([(True,False),(True,True),(False,False),(False,True)]):
                time=f"2026-10-16T11:00:0{n}.123Z"
                a=sample_payload(sampleId=f"race-{n}-A",sampledAt=time)
                b=sample_payload(sampleId=f"race-{n}-A" if same_id else f"race-{n}-B",sampledAt=time,zone1Set=1 if changed else 0)
                starting=await counts()
                responses=await asyncio.gather(post(client,a),post(client,b))
                assert sorted(x.status_code for x in responses)==([200,409] if changed else [200,200])
                assert (await counts())[0]==starting[0]+1
                assert (await counts())[1]==starting[1]+(1 if same_id or changed else 2)
                if not changed:assert responses[0].json()["data"]["recordId"]==responses[1].json()["data"]["recordId"]
            # 同actor的Case/case投递key不被默认CI collation合并。
            for key in ("Case","case"):assert (await post(client,sample_payload(sampleId=key))).status_code==200
            async with sessions() as db:
                rows=list((await db.execute(select(Receipt).where(Receipt.sample_id.in_(["Case","case"])))).scalars())
                assert len(rows)==2
            # 业务/回执/flush/commit失败均回滚；已提交但响应丢失及未知提交可同键恢复。
            for n,name in enumerate(("business","receipt","flush","commit")):
                data=sample_payload(sampleId=f"failure-{name}",sampledAt=f"2026-10-16T12:00:0{n}.123Z")
                starting=await counts()
                with monkeypatch.context() as patch:
                    if name in {"business","receipt"}:
                        method=crud.add_sample if name=="business" else crud.add_receipt
                        async def failure(*args,**kwargs):
                            await method(*args,**kwargs)
                            raise RuntimeError("synthetic persistence failure")
                        patch.setattr(crud,"add_sample" if name=="business" else "add_receipt",failure)
                    elif name=="flush":
                        async def failure(*args,**kwargs):raise RuntimeError("synthetic flush failure")
                        patch.setattr(AsyncSession,"flush",failure)
                    else:
                        async def failure(*args,**kwargs):raise OperationalError("synthetic",{},Exception("synthetic commit failure"))
                        patch.setattr(AsyncSession,"commit",failure)
                    response=await post(client,data)
                    assert response.status_code==(503 if name=="commit" else 500)
                assert await counts()==starting
            data=sample_payload(sampleId="unknown-commit",sampledAt="2026-10-16T13:00:00.123Z")
            original=AsyncSession.commit
            with monkeypatch.context() as patch:
                async def unknown(db):
                    await original(db)
                    raise OperationalError("synthetic",{},Exception("unknown commit result"))
                patch.setattr(AsyncSession,"commit",unknown)
                response=await post(client,data);assert response.status_code==503
            replay=await post(client,data);assert replay.status_code==200 and replay.json()["data"]["outcome"]=="duplicate"
            lost=sample_payload(sampleId="lost-response",sampledAt="2026-10-16T13:00:01.123Z")
            with monkeypatch.context() as patch:
                def failed_log(*args,**kwargs):raise RuntimeError("synthetic post-commit failure")
                patch.setattr(service,"log_event",failed_log)
                assert (await post(client,lost)).status_code==500
            async with sessions() as db:
                committed_id=await db.scalar(select(Receipt.sample_record_id).where(Receipt.sample_id=="lost-response"))
            recovered=(await post(client,lost)).json()["data"]
            assert recovered["outcome"]=="duplicate" and recovered["recordId"]==committed_id
            assert (await client.get("/api/v1/equipment/temperature-control?limit=1",headers=headers)).json()["data"]==old["data"]
        # 模拟重启重组后disabled整组404；不修改源码或删除数据。
        from dataclasses import replace
        import importlib
        import app.equipment.manifest as declaration
        import app.router as routes
        from core.registrar import create_app
        with monkeypatch.context() as patch:
            patch.setattr(declaration,"manifest",replace(declaration.manifest,enabled=False))
            try:
                importlib.reload(routes)
                disabled=create_app(testing=True)
                async with AsyncClient(transport=ASGITransport(app=disabled),base_url="http://fixture") as client:
                    for path in ("temperature-samples","temperature-control","drive","production-parameters"):
                        assert (await client.get("/api/v1/equipment/"+path)).status_code==404
                    assert (await client.post("/api/v1/equipment/temperature-samples")).status_code==404
            finally:
                patch.undo();importlib.reload(routes)
        # 直接数据库约束证据：sample unique、receipt unique及跨设备引用FK均实际拒绝。
        async with sessions() as db:
            sample=(await db.execute(select(Sample).where(Sample.id==first["recordId"]))).scalar_one()
            receipt=(await db.execute(select(Receipt).limit(1))).scalar_one()
            sample_values={c.name:getattr(sample,c.name) for c in Sample.__table__.columns if c.name not in {"id","created_at","updated_at"}}
            receipt_values={c.name:getattr(receipt,c.name) for c in Receipt.__table__.columns if c.name not in {"id","created_at","updated_at"}}
        for model,values in [(Sample,sample_values),(Receipt,receipt_values),(Receipt,{**receipt_values,"sample_id":"wrong-device","equipment_id":"other-device"})]:
            async with sessions() as db:
                db.add(model(**values))
                try:await db.commit()
                except IntegrityError:await db.rollback()
                else:raise AssertionError("Database constraint did not reject invalid row")
        # 业务key自身区分大小写，API scope仍只开放原一个key。
        async with sessions() as db:
            db.add(Sample(**{**sample_values,"equipment_id":"Temperature-pilot-01"}))
            await db.commit()
            rows=list((await db.execute(select(Sample).where(Sample.sampled_at==sample.sampled_at))).scalars())
            assert {x.equipment_id for x in rows}=={"temperature-pilot-01","Temperature-pilot-01"}
        (target.root/"temperature-behavior.json").write_text(json.dumps(dict(scenario=target.scenario,record_id=first["recordId"],counts=await counts(),old_get_preserved=True)))
    finally:
        await engine.dispose()
