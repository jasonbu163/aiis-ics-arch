"""BE006 B独立显式MySQL8.4.6验证入口；仅compile/collect不连接，执行须具体Owner批准。"""
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


def install_target_guard():
    """此显式B子进程只允许单一已批准schema/账号/loopback；嵌套Alembic继承。"""
    import socket,sqlite3
    from sqlalchemy.engine import Engine
    endpoint=('127.0.0.1',33076)
    schema=os.environ['TEST_MYSQL_DATABASE'];user=os.environ['MYSQL_USER']
    assert schema in {'arch_be006_r1_empty','arch_be006_r1_upgrade','arch_be006_r1_rollback'}
    assert user and user!='root' and os.environ['MYSQL_PORT']=='33076'
    assert os.environ['MYSQL_DATABASE']=='be006_unused_primary'
    def reject(*args,**kwargs):raise AssertionError('BE006 disposable target guard denied an operation')
    def check_url(engine):
        url=engine.url
        assert url.get_backend_name()=='mysql' and (url.host,url.port)==endpoint
        assert url.database==schema and url.username==user
    for name in ('connect','raw_connection'):
        original=getattr(Engine,name)
        def guarded(engine,*args,_original=original,**kwargs):
            check_url(engine);return _original(engine,*args,**kwargs)
        setattr(Engine,name,guarded)
    for module_name in ('pymysql','aiomysql'):
        module=__import__(module_name);original=module.connect
        def connect(*args,_original=original,**kwargs):
            assert not args
            assert (kwargs.get('host'),int(kwargs.get('port',3306)))==endpoint
            assert kwargs.get('db',kwargs.get('database'))==schema and kwargs.get('user')==user
            return _original(**kwargs)
        module.connect=connect
    for module_name in ('sqlite3','sqlite3.dbapi2','_sqlite3'):
        module=__import__(module_name,fromlist=['connect']);module.connect=reject
    original_connect=socket.socket.connect;original_connect_ex=socket.socket.connect_ex
    def socket_connect(sock,address):
        assert address==endpoint
        return original_connect(sock,address)
    def socket_connect_ex(sock,address):
        assert address==endpoint
        return original_connect_ex(sock,address)
    socket.socket.connect=socket_connect;socket.socket.connect_ex=socket_connect_ex
    socket.socket.bind=reject;socket.socket.listen=reject;socket.socket.sendto=reject
    socket.gethostbyname=reject;socket.gethostbyname_ex=reject;socket.gethostbyaddr=reject
    original_dns=socket.getaddrinfo
    def dns(host,port,*args,**kwargs):
        assert host==endpoint[0] and int(port)==endpoint[1]
        return original_dns(host,port,*args,**kwargs)
    socket.getaddrinfo=dns
    def audit(event,args):
        if event=='open' and args and isinstance(args[0],(str,bytes)):
            path=os.fsdecode(args[0]);name=os.path.basename(path)
            if path.startswith('/Users/jason/Desktop/DreamCode/') and name.startswith('.env') and not name.endswith('.example'):
                reject()
    sys.addaudithook(audit)


def schema_signatures(engine,names):
    from sqlalchemy import inspect
    inspector=inspect(engine);result={}
    for name in sorted(names):
        result[name]=dict(columns=inspector.get_columns(name),pk=inspector.get_pk_constraint(name),
            fk=inspector.get_foreign_keys(name),unique=inspector.get_unique_constraints(name),
            indexes=inspector.get_indexes(name),checks=inspector.get_check_constraints(name))
    return json.loads(json.dumps(result,sort_keys=True,default=str))


class BusinessTarget:
    """只接受本任务公开64表副本及逐库/endpoint/动作ACK；不创建或删除schema。"""
    def __init__(self):
        self.root=Path.cwd().resolve()
        assert self.root.is_relative_to(Path("/private/tmp")), "Only a dedicated temporary public profile is allowed"
        assert not (self.root/".env").exists()
        profile=json.loads((self.root/"profile.json").read_text())
        assert profile["profile"]=="BE006" and profile["expected_table_count"]==64
        assert profile["target_revision"]=="f6a8c0e2b4d6"
        self.scenario=os.environ["BE006_MYSQL_SCENARIO"]
        names={"empty":"arch_be006_r1_empty","upgrade":"arch_be006_r1_upgrade","rollback":"arch_be006_r1_rollback"}
        self.database=os.environ["TEST_MYSQL_DATABASE"]
        assert self.database==names[self.scenario]==os.environ["BE006_MYSQL_SCHEMA_ACK"]
        assert os.environ["BE006_MYSQL_DISPOSABLE_ACK"]=="ARCH-BE-006-r1"
        assert os.environ["MYSQL_HOST"]=="127.0.0.1" and os.environ["MYSQL_PORT"]=="33076"
        assert os.environ["MYSQL_DATABASE"]=="be006_unused_primary"
        assert os.environ["BE006_MYSQL_ENDPOINT_ACK"]=="127.0.0.1:"+os.environ["MYSQL_PORT"]
        assert self.database != os.environ["MYSQL_DATABASE"]
        assert os.environ["TESTING"].lower()=="true"
        for key in ("BACKEND_MOCK_ENABLED","PROJECTION_RUNNER_ENABLED","ADMIN_BOOTSTRAP_ENABLED","SUPERVISOR_BOOTSTRAP_ENABLED","OPERATOR_BOOTSTRAP_ENABLED"):
            assert os.environ[key].lower()=="false", key
        install_target_guard()
        # sitecustomize has no project imports/config secrets; nested migrations retain the exact same guard.
        import inspect as source_inspect
        guard_dir=self.root/'b-target-guard';guard_dir.mkdir(exist_ok=True)
        (guard_dir/'sitecustomize.py').write_text('import os,sys\n'+source_inspect.getsource(install_target_guard)+'\ninstall_target_guard()\n')
        os.environ['PYTHONPATH']=str(guard_dir)+os.pathsep+str(self.root)
        import settings as configuration
        assert Path(configuration.__file__).resolve().parent==self.root
        settings=configuration.settings
        assert settings.primary_database=="mysql" and settings.TEST_MYSQL_DATABASE==self.database
        from sqlalchemy import create_engine,inspect
        self.engine=create_engine(settings.SYNC_DATABASE_URL,pool_pre_ping=True)
        with self.engine.connect() as conn:
            database,version,account,isolation=conn.exec_driver_sql("SELECT DATABASE(),VERSION(),CURRENT_USER(),@@transaction_isolation").one()
            assert database==self.database and str(version).split("-")[0]=="8.4.6"
            assert str(account).split("@",1)[0]==os.environ["MYSQL_USER"] and not str(account).startswith("root@")
            assert not inspect(conn).get_table_names(), "Every scenario must start with a new empty schema"
            (self.root/"mysql-target.json").write_text(json.dumps(dict(database=database,version=version,account=account,isolation=isolation)))


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
        assert len(Base.metadata.tables) == 64
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
            # MySQL SHOW CREATE parenthesizes IS [NOT] NULL atoms; only these exact redundant groups fold.
            changed=True
            while changed:
                changed=False
                for start in range(len(tokens)):
                    atom=tokens[start:start+5]
                    width=5 if len(atom)==5 and atom[0]=='(' and atom[2:4]==['is','null'] and atom[-1]==')' else 0
                    longer=tokens[start:start+6]
                    if len(longer)==6 and longer[0]=='(' and longer[2:5]==['is','not','null'] and longer[-1]==')':width=6
                    if width:
                        tokens[start:start+width]=tokens[start+1:start+width-1];changed=True;break
            if tokens in (['current_timestamp'], ['current_timestamp', '(', ')']):
                tokens = ['now', '(', ')']
            return tuple(tokens)

        def action(value):
            return 'RESTRICT' if value in {None, 'NO ACTION', 'RESTRICT'} else value
        report = {'database': self.database, 'tables': sorted(Base.metadata.tables), 'comparisons': {}}
        for (name, table) in Base.metadata.tables.items():
            actual = inspector.get_columns(name)
            assert {column['name'] for column in actual} == set(table.columns.keys()), name
            actual = sorted(actual, key=lambda column: column["name"])
            for (column, expected) in zip(actual, sorted(table.columns, key=lambda column: column.name)):

                def normalized(value):
                    text = str(value).upper().replace('INTEGER', 'INT').replace('NUMERIC', 'DECIMAL')
                    # MySQL反射显式展开bin collation自带的utf8mb4；仅折叠这一确切等价对。
                    text = text.replace(' CHARACTER SET UTF8MB4 COLLATE UTF8MB4_BIN', ' COLLATE UTF8MB4_BIN')
                    if text == 'DECIMAL':
                        text = 'DECIMAL(10, 0)'
                    return 'TINYINT(1)' if text in {'BOOL', 'BOOLEAN'} else text
                assert normalized(column['type'].compile(dialect=mysql.dialect())) == normalized(expected.type.compile(dialect=mysql.dialect())), (name, expected.name)
                assert column['nullable'] == expected.nullable, (name, expected.name)
                default = expected.server_default.arg if expected.server_default is not None else None
                if hasattr(default,'compile'):default=str(default.compile(dialect=mysql.dialect(),compile_kwargs={'literal_binds':True}))
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
            assert actual_check_sql == expected_check_sql, (name,actual_check_sql,expected_check_sql)
            report['comparisons'][name] = dict(columns=[dict(name=c['name'], type=str(c['type']), nullable=c['nullable'], default=c['default']) for c in actual], foreign_keys=inspector.get_foreign_keys(name), unique=inspector.get_unique_constraints(name), indexes=inspector.get_indexes(name), checks=inspector.get_check_constraints(name))
        (self.root / 'schema-reflection.json').write_text(json.dumps(report, indent=2, default=str))

    def seed_legacy(self):
        from app.module_registry import import_model_packages
        import_model_packages() # e4 fixture still uses unchanged User/Plan/old temperature Models only.
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
            from app.plan.models.plan import Plan
            db.add(Plan(coil_no="manual-fixture-plan",grade="legacy",spec="legacy",weight=0,thickness=0,width=0))
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
        from app.equipment.mapping_config import MappingConfig as EC,get_mapping_config as ec
        from app.performance.mapping_config import MappingConfig as PC,get_mapping_config as pc
        from app.monitor.mapping_config import MappingConfig as MC,get_mapping_config as mc
        app.dependency_overrides[ec]=lambda:EC(EQUIPMENT_MAPPING_INGEST_ID="line-A",_env_file=None)
        app.state.performance_mapping_config=PC(PERFORMANCE_MAPPING_INGEST_ID="line-A",_env_file=None)
        app.dependency_overrides[pc]=lambda:app.state.performance_mapping_config
        app.dependency_overrides[mc]=lambda:MC(MONITOR_MAPPING_INGEST_ID="line-A",_env_file=None)
        return app,engine,sessions



def seed_affected_legacy(target):
    """只在专用目标：反射e4/f6真实旧列，七表合成0/秒时间/重复键，不用当前ORM写e4。"""
    from datetime import date
    from sqlalchemy import MetaData,Table,DateTime,Date,Numeric,Float,Integer,Boolean,String,JSON
    moment=datetime(2020,1,2,3,4,5)
    names=("equipment_drive","equipment_production_parameters","performance_main","performance_process_temperature",
           "performance_process_tension","performance_process_speed","monitor_history_process_curves")
    with target.engine.begin() as connection:
        parent_id=None
        for name in names:
            table=Table(name,MetaData(),autoload_with=connection)
            values={}
            for column in table.columns:
                if column.primary_key or column.nullable or column.server_default is not None:
                    continue
                if isinstance(column.type,DateTime):values[column.name]=moment
                elif isinstance(column.type,Date):values[column.name]=date(2020,1,2)
                elif isinstance(column.type,JSON):values[column.name]=[]
                elif isinstance(column.type,(Numeric,Float,Integer)):values[column.name]=0
                elif isinstance(column.type,Boolean):values[column.name]=False
                elif isinstance(column.type,String):values[column.name]="legacy"
                else:raise AssertionError((name,column.name,str(column.type)))
            if "timestamp" in table.c:values["timestamp"]=moment
            if name in {"equipment_drive","equipment_production_parameters"}:
                for column in table.c:
                    if isinstance(column.type,Float):values[column.name]=0
            if name=="equipment_production_parameters":values.update(coil_no="legacy-coil",grade="legacy",process_steps=[])
            if name=="performance_main":values.update(coil_no="legacy-coil",parent_coil_no="legacy-coil",production_date=date(2020,1,2),output_quantity=0,qualified_quantity=0,is_split=False)
            if name.startswith("performance_process_"):
                values.update(performance_id=parent_id,zone="legacy-zone",record_time=moment)
            if name=="monitor_history_process_curves":
                values.update(device_id=999,coil_number="legacy-coil",created_at=moment)
                for column in table.c:
                    if column.name not in {"id","device_id"} and isinstance(column.type,(Integer,Float)):
                        values[column.name]=0
            first=connection.execute(table.insert().values(**values))
            if name=="performance_main":parent_id=first.inserted_primary_key[0]
            # NULL-domain duplicate timestamp/coil/zone values must survive the new HTTP uniques unchanged.
            connection.execute(table.insert().values(**values))


def capture_legacy_rows(target,names):
    from sqlalchemy import MetaData,Table,select
    snapshot={}
    with target.engine.connect() as connection:
        for name in sorted(names):
            table=Table(name,MetaData(),autoload_with=connection)
            columns=tuple(column.name for column in table.c)
            keys=tuple(column.name for column in table.primary_key)
            assert keys,name
            rows={tuple(str(row._mapping[key]) for key in keys):tuple(str(row._mapping[column]) for column in columns)
                  for row in connection.execute(select(table))}
            snapshot[name]=dict(columns=columns,primary_key=keys,rows=rows)
    return snapshot


def assert_legacy_rows(target,snapshot):
    """升级前列+原PK集合逐行比较；新HTTP行与新增列不进入旧行校验。"""
    from sqlalchemy import MetaData,Table,select
    report={}
    with target.engine.connect() as connection:
        for name,before in snapshot.items():
            table=Table(name,MetaData(),autoload_with=connection)
            columns=before["columns"];keys=before["primary_key"]
            current={}
            for row in connection.execute(select(*(table.c[column] for column in columns))):
                key=tuple(str(row._mapping[column]) for column in keys)
                if key in before["rows"]:
                    current[key]=tuple(str(row._mapping[column]) for column in columns)
            assert current==before["rows"],name
            report[name]=dict(columns=columns,primary_key=keys,row_count=len(current),sha256=hashlib.sha256(json.dumps(sorted(current.items())).encode()).hexdigest())
    with (target.root/"legacy-row-protection.jsonl").open('a') as stream:
        stream.write(json.dumps(report,sort_keys=True)+'\n')


def test_explicit_mysql_mapping_business_api(monkeypatch):
    """仅获具体BE006 B批准后显式--noconftest选择，不由普通no_db套件执行。"""
    target=BusinessTarget()
    try:
        from sqlalchemy import inspect
        added={"equipment_mapping_receipts","performance_mapping_receipts","monitor_mapping_receipts","performance_mapping_observation_state"}
        if target.scenario=="empty":
            target.migrate("f6a8c0e2b4d6")  # Real base -> f6 with all six revisions.
            target.assert_schema()
            target.seed_legacy()
            seed_affected_legacy(target)
            old_tables=set(inspect(target.engine).get_table_names())-{"alembic_version"}-added
            snapshot=capture_legacy_rows(target,old_tables)
        else:
            target.migrate("e4f6a8b0c2d4")
            target.seed_legacy()
            seed_affected_legacy(target)
            old_tables=set(inspect(target.engine).get_table_names())-{"alembic_version"}
            snapshot=capture_legacy_rows(target,old_tables)
            unaffected=old_tables-{"equipment_drive","equipment_production_parameters","performance_main","performance_process_temperature","performance_process_tension","performance_process_speed","monitor_history_process_curves"}
            before53=schema_signatures(target.engine,unaffected)
            target.migrate("f6a8c0e2b4d6")
            target.assert_schema()
            assert schema_signatures(target.engine,unaffected)==before53
            (target.root/'unchanged-53.json').write_text(json.dumps(before53,indent=2,default=str))
            assert_legacy_rows(target,snapshot)
        assert len(old_tables)==60
        if target.scenario=="rollback":
            assert_irreversible_legacy_refused(target)
            target.migrate("e4f6a8b0c2d4","downgrade")
            assert set(inspect(target.engine).get_table_names())==old_tables|{"alembic_version"}
            assert_legacy_rows(target,snapshot)
            target.migrate("f6a8c0e2b4d6")
            target.assert_schema()
            assert_legacy_rows(target,snapshot)
        asyncio.run(prove_first_state_competition(target,monkeypatch))
        asyncio.run(real_business_behavior(target,monkeypatch))
        asyncio.run(extended_business_behavior(target,monkeypatch))
        prove_legacy_sync_transaction(target)
        assert_legacy_rows(target,snapshot)
        # Once HTTP data exists, downgrade must refuse before any destructive DDL.
        result=subprocess.run([sys.executable,"-m","alembic","downgrade","e4f6a8b0c2d4"],cwd=target.root,capture_output=True,text=True)
        assert result.returncode!=0
        target.assert_schema()
        assert_legacy_rows(target,snapshot)
    finally:
        target.engine.dispose()


async def real_business_behavior(target,monkeypatch):
    from httpx import ASGITransport,AsyncClient
    from sqlalchemy import select,func
    from app.equipment.models.equipment import EquipmentDrive,EquipmentProductionParameters
    from app.performance.models.performance import Performance,ProcessTemperature,ProcessTension,ProcessSpeed
    from app.monitor.models.business_history import HistoryProcessCurve
    from app.user.models.user import User
    from core.jwt import create_access_token
    app,engine,sessions=target.api()
    token=create_access_token({"sub":"temperature-admin-one"})
    headers={"Authorization":"Bearer "+token}
    def payload(sample,**values):
        result=dict(equipmentId="line-A",sampleId=sample,sampledAt="2026-10-16T10:00:00.123Z",quality="good")
        result.update(values);return result
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://fixture") as client:
        async def post(path,data,expected=200):
            response=await client.post("/api/v1"+path,json=data,headers=headers)
            assert response.status_code==expected,response.text
            return response.json()["data"]
        async def get(path,**params):
            response=await client.get("/api/v1"+path,params=dict(equipmentId="line-A",**params),headers=headers)
            assert response.status_code==200,response.text
            return response.json()["data"]
        # All twenty drive fields, all production parameter measurements and complete curve fields.
        drive_fields=("tv","km","dewPointSet","dewPointActual","oxygen","mufflePressure","nh3FlowSet","nh3FlowActual","ngFlowSet","ngFlowActual","uncoilerSet","uncoilerActual","entryLooperSet","entryLooperActual","furnaceSet","furnaceActual","exitLooperSet","exitLooperActual","recoilerSet","recoilerActual")
        drive=payload("drive-all",**{key:index+0.25 for index,key in enumerate(drive_fields)})
        d=await post("/equipment/drive-samples",drive)
        item=(await get("/equipment/drive-samples",recordId=d["recordId"]))["items"][0]
        for field in drive_fields:assert abs(item[field]-drive[field])<=max(1e-6,abs(drive[field])*1e-6)
        assert (await post("/equipment/drive-samples",drive))["recordId"]==d["recordId"]
        conflict=dict(drive,tv=99);await post("/equipment/drive-samples",conflict,409)
        partial=payload("drive-partial",tv=0);partial["sampledAt"]="2026-10-16T10:01:00.123Z"
        p=await post("/equipment/drive-samples",partial)
        async with sessions() as db:
            row=await db.get(EquipmentDrive,p["recordId"])
            assert row.tv==0 and all(getattr(row,key) is None for key in ("km","oxygen","dew_point_actual"))
        fill=dict(partial,sampleId="drive-fill",km=1.25)
        assert (await post("/equipment/drive-samples",fill))["outcome"]=="updated"
        params=payload("parameters",coilNo="Case-卷",grade="A",entryTime="2026-10-16T08:00:00.001Z",thickness=0,width=1,totalTime=2,weight=3,speed=4)
        p=await post("/equipment/production-parameter-samples",params)
        item=(await get("/equipment/production-parameter-samples",recordId=p["recordId"]))["items"][0]
        assert item["coilNo"]=="Case-卷" and item["thickness"]==0 and item["entryTime"].endswith(".001Z")
        observation=payload("production-A",coilNo="0",observationStatus="in_production",weight=1.2345,totalLength=2.25,diameter=3.25,density=4.125,
            outputQuantity=5.0001,qualifiedQuantity=6.0001,efficiencyRate=150.25,qualityScore=101.25,grade="A",spec="S",remark="reported",
            startTime="2026-10-16T08:00:00.123Z",endTime="2026-10-16T09:00:00.123Z")
        parent=await post("/performances/production-observations",observation);parent_id=parent["recordId"]
        item=await get(f"/performances/mapping-records/{parent_id}")
        assert item["weight"]==1.2345 and item["totalDurationSeconds"]==3600 and item["totalDurationSource"]=="reported_time"
        old=await client.get(f"/api/v1/performances/{parent_id}",headers=headers)
        assert old.status_code==404 or old.json()["code"]==404
        response=await client.put(f"/api/v1/performances/{parent_id}",params={"dataSource":"http","equipmentId":"line-A"},json={"weight":0,"remark":"manual"},headers=headers)
        assert response.status_code==200,response.text
        newer=dict(observation,sampleId="production-A-new",sampledAt="2026-10-16T11:00:00.123Z",weight=9)
        await post("/performances/production-observations",newer)
        item=await get(f"/performances/mapping-records/{parent_id}")
        assert item["weight"]==0 and item["collectedWeight"]==9 and item["effectiveWeightSource"]=="manual_override_weight"
        for kind,values in [("temperature",dict(setTemp=0,minTemp=-1,maxTemp=2,avgTemp=1,duration=5)),
                            ("tension",dict(setTension=0,minTension=0,avgTension=1,maxTension=2)),
                            ("speed",dict(setSpeed=0,avgSpeed=1,maxSpeed=2))]:
            data=dict(equipmentId="line-A",sampleId="process-"+kind,quality="good",recordTime="2026-10-16T10:00:00.125Z",coilNo="0",zone="Z",**values)
            child=await post(f"/performances/{parent_id}/process-{kind}-samples",data)
            item=(await get(f"/performances/mapping-records/{parent_id}/process-data"))[kind][0]
            assert item["recordId"]==child["recordId"]
            for key,value in values.items():assert item[key]==value
        temperature=dict(equipmentId="temperature-pilot-01",sampleId="temperature-all",sampledAt="2026-10-16T10:00:00.123Z",quality="good",
            **{f"zone{zone}{kind}":zone+0.125 for zone in range(1,6) for kind in ("Set","Act")})
        original=await post("/equipment/temperature-samples",temperature)
        response=await client.get("/api/v1/equipment/temperature-sample-dashboard",params={"equipmentId":"temperature-pilot-01","recordId":original["recordId"]},headers=headers)
        assert response.status_code==200 and response.json()["data"]["recordId"]==original["recordId"]
        from app.monitor.schemas.process_curve_in import ProcessCurveIn
        from common.schema_base import to_camel
        curve_values={to_camel(key):0 if key.startswith("z") else 1.25 for key in ProcessCurveIn.model_fields if key not in {"equipment_id","sample_id","sampled_at","quality","coil_number"}}
        curve=payload("curve-all",coilNumber="0",**curve_values)
        c=await post("/monitor/process-curve-samples",curve)
        item=(await get("/monitor/process-curve-samples",date="2026-10-16",recordId=c["recordId"]))["items"][0]
        for key,value in curve_values.items():assert item[key]==value
        # Independent AsyncSessions behind each ASGI request; unique constraints decide first-insert races.
        concurrent=payload("race",tv=7);concurrent["sampledAt"]="2026-10-16T12:00:00.123Z"
        async def concurrent_post(index):
            data=dict(concurrent,sampleId=f"race-{index}")
            response=await client.post('/api/v1/equipment/drive-samples',json=data,headers=headers)
            if response.status_code==503:return await post('/equipment/drive-samples',data)
            assert response.status_code==200,response.text
            return response.json()['data']
        outcomes=await asyncio.gather(*(concurrent_post(i) for i in range(4)))
        assert len({x["recordId"] for x in outcomes})==1
        async with sessions() as db:
            count=await db.scalar(select(func.count()).select_from(EquipmentDrive).where(EquipmentDrive.equipment_id=="line-A",EquipmentDrive.timestamp==datetime(2026,10,16,12,0,0,123000)))
            assert count==1
    await engine.dispose()


def assert_irreversible_legacy_refused(target):
    """独立legacy NULL/非零毫秒均在任何DDL之前拒绝；删除本函数自己的探针行。"""
    from sqlalchemy import MetaData,Table,select
    table=Table('equipment_drive',MetaData(),autoload_with=target.engine)
    with target.engine.connect() as connection:
        source=dict(connection.execute(select(table).limit(1)).mappings().one())
    source.pop('id');source['equipment_id']=None
    before=schema_signatures(target.engine,set(__import__('sqlalchemy').inspect(target.engine).get_table_names()))
    for kind in ('null','millisecond'):
        values=dict(source)
        values['timestamp']=datetime(2020,2,3,4,5,6,123000 if kind=='millisecond' else 0)
        if kind=='null':values['tv']=None
        with target.engine.begin() as connection:record_id=connection.execute(table.insert().values(**values)).inserted_primary_key[0]
        result=subprocess.run([sys.executable,'-m','alembic','downgrade','e4f6a8b0c2d4'],cwd=target.root,capture_output=True,text=True)
        assert result.returncode!=0,kind
        assert schema_signatures(target.engine,set(before))==before
        with target.engine.begin() as connection:
            assert connection.execute(select(table.c.id).where(table.c.id==record_id)).scalar_one()==record_id
            connection.execute(table.delete().where(table.c.id==record_id))
        with (target.root/'downgrade-refusals.jsonl').open('a') as stream:stream.write(json.dumps(dict(reason=kind,exit_code=result.returncode,schema_unchanged=True))+'\n')


class BusinessProof:
    """单专用目标上的真实JWT/Session验证；记录仅合成字段/状态，不记token/配置。"""
    def __init__(self,target,client,sessions,app):
        from core.jwt import create_access_token
        self.target=target;self.client=client;self.sessions=sessions;self.app=app;self.sequence=0;self.report=[];self.engine=sessions.kw["bind"]
        self.tokens={name:create_access_token({'sub':'temperature-'+name}) for name in ('admin-one','admin-two','supervisor','operator','unknown','inactive')}
    def sample(self,stream,**changes):
        self.sequence+=1
        # All subsequent production events are later than the initial 11:00 lifecycle fixture.
        moment=datetime(2026,10,17)+timedelta(seconds=self.sequence)
        base=dict(equipmentId='line-A',sampleId=f'proof-{stream}-{self.sequence}',quality='good')
        if stream.startswith('process_') and stream!='process_curve':
            base.update(recordTime=moment.isoformat(timespec='milliseconds')+'Z',coilNo='0',zone='Z',**{'process_temperature':{'setTemp':0},'process_tension':{'setTension':0},'process_speed':{'setSpeed':0}}[stream])
        else:
            base.update(sampledAt=moment.isoformat(timespec='milliseconds')+'Z',**{'drive':{'tv':0},'production_parameters':{'coilNo':'Proof','width':0},'production_observation':{'observationStatus':'in_production','coilNo':'Proof','weight':0},'process_curve':{'lineSpeedAct':0},'temperature':dict(equipmentId='temperature-pilot-01',**{f'zone{z}{k}':0 for z in range(1,6) for k in ('Set','Act')})}[stream])
        base.update(changes);return base
    def path(self,stream,parent=None):
        return {'drive':'/equipment/drive-samples','production_parameters':'/equipment/production-parameter-samples','production_observation':'/performances/production-observations','process_curve':'/monitor/process-curve-samples','temperature':'/equipment/temperature-samples'}.get(stream,f'/performances/{parent}/'+stream.replace('_','-')+'-samples')
    async def request(self,method,path,data=None,params=None,actor='admin-one',status=200,error=None,headers=None):
        response=await self.client.request(method,'/api/v1'+path,json=data,params=params,headers=headers if headers is not None else {'Authorization':'Bearer '+self.tokens[actor]})
        assert response.status_code==status,(method,path,response.status_code,response.text)
        body=response.json()
        if status!=200:
            assert 'private' not in response.text and 'Traceback' not in response.text,response.text
            assert body['code']==status and body['data'] is None,(path,body)
            if error:assert body['errorCode'].endswith(error),body
        return body['data']
    async def post(self,stream,data,parent=None,**kwargs):return await self.request('POST',self.path(stream,parent),data,**kwargs)
    async def snapshot(self):
        from sqlalchemy import select
        from database import Base
        names=('equipment_drive','equipment_production_parameters','performance_main','performance_process_temperature','performance_process_tension','performance_process_speed','monitor_history_process_curves','equipment_mapping_receipts','performance_mapping_receipts','monitor_mapping_receipts','performance_mapping_observation_state','equipment_temperature_samples','equipment_temperature_sample_receipts')
        async with self.sessions() as db:
            return {name:sorted([tuple(map(str,row)) for row in (await db.execute(select(Base.metadata.tables[name]))).all()]) for name in names}
    def note(self,case,**values):
        self.report.append(dict(case=case,**values))
        (self.target.root/"business-proof.json").write_text(json.dumps(self.report,indent=2,default=str))


async def extended_business_behavior(target,monkeypatch):
    from httpx import ASGITransport,AsyncClient
    app,engine,sessions=target.api()
    try:
        async with AsyncClient(transport=ASGITransport(app=app),base_url='http://fixture') as client:
            proof=BusinessProof(target,client,sessions,app)
            await prove_complete_storage(proof)
            await prove_delivery_and_partial(proof)
            await prove_auth_scope_and_modules(proof,monkeypatch)
            await prove_first_insert_races(proof,monkeypatch)
            await prove_locked_refresh_current_read(proof,monkeypatch)
            await prove_rr_and_delivery_waits(proof,monkeypatch)
            await prove_lifecycle_and_manual_order(proof,monkeypatch)
            await prove_faults(proof,monkeypatch)
            await prove_database_constraints(proof)
            await prove_identity_check_constraints(proof)
            await prove_energy_unchanged(proof)
            await prepare_browser_rows(proof)
            (target.root/'business-proof.json').write_text(json.dumps(proof.report,indent=2,default=str))
    finally:await engine.dispose()


async def prove_complete_storage(proof):
    from sqlalchemy import select
    from app.equipment.models.equipment import EquipmentDrive,EquipmentProductionParameters
    from app.equipment.models.temperature_sample import EquipmentTemperatureSample
    from app.performance.models.performance import Performance,ProcessTemperature,ProcessTension,ProcessSpeed
    from app.monitor.models.business_history import HistoryProcessCurve
    from common.schema_base import to_camel
    models=[(EquipmentDrive,'drive-all'),(EquipmentProductionParameters,'parameters'),(Performance,'production-A'),(ProcessTemperature,'process-temperature'),(ProcessTension,'process-tension'),(ProcessSpeed,'process-speed'),(HistoryProcessCurve,'curve-all'),(EquipmentTemperatureSample,'temperature-all')]
    # Initial HTTP fixture values are checked against DB, not a returned receipt/request echo.
    from app.equipment.models.mapping_ingest import EquipmentMappingReceipt as ER
    from app.performance.models.mapping_ingest import PerformanceMappingReceipt as PR
    from app.monitor.models.mapping_ingest import MonitorMappingReceipt as MR
    from app.equipment.models.temperature_sample import EquipmentTemperatureSampleReceipt as TR
    async with proof.sessions() as db:
        for model,sample_id in models:
            if model==EquipmentTemperatureSample:
                receipt=(await db.execute(select(TR).where(TR.sample_id==sample_id))).scalar_one();record_id=receipt.sample_record_id
            else:
                owner=ER if model in (EquipmentDrive,EquipmentProductionParameters) else MR if model==HistoryProcessCurve else PR
                receipt=(await db.execute(select(owner).where(owner.sample_id==sample_id))).scalar_one();record_id=receipt.result['record_id']
            row=await db.get(model,record_id)
            assert row is not None
            if model in (ProcessTemperature,ProcessTension,ProcessSpeed):
                kind={ProcessTemperature:'temperature',ProcessTension:'tension',ProcessSpeed:'speed'}[model]
                expected={'temperature':dict(set_temp=0,min_temp=-1,max_temp=2,avg_temp=1,duration=5),'tension':dict(set_tension=0,min_tension=0,avg_tension=1,max_tension=2),'speed':dict(set_speed=0,avg_speed=1,max_speed=2)}[kind]
                assert all(getattr(row,key)==Decimal(str(value)) for key,value in expected.items())
            public_path=('/equipment/temperature-samples' if model==EquipmentTemperatureSample else '/equipment/drive-samples' if model==EquipmentDrive else '/equipment/production-parameter-samples' if model==EquipmentProductionParameters else '/monitor/process-curve-samples' if model==HistoryProcessCurve else f'/performances/mapping-records/{record_id}' if model==Performance else f'/performances/mapping-records/{row.performance_id}/process-data')
            public=await proof.request('GET',public_path,params=dict(equipmentId='temperature-pilot-01' if model==EquipmentTemperatureSample else 'line-A',**({'recordId':record_id,'date':'2026-10-16'} if model==HistoryProcessCurve else {'recordId':record_id} if model in (EquipmentDrive,EquipmentProductionParameters,EquipmentTemperatureSample) else {})))
            public=public['items'][0] if 'items' in public else public[kind][0] if model in (ProcessTemperature,ProcessTension,ProcessSpeed) else public
            checked=[]
            for column in model.__table__.columns:
                key=to_camel(column.name)
                if key in public and isinstance(getattr(row,column.name),(int,float,Decimal)) and not isinstance(getattr(row,column.name),bool) and column.name!='id':
                    actual=getattr(row,column.name)
                    assert Decimal(str(public[key]))==Decimal(str(actual)),(model.__tablename__,key,public[key],actual)
                    checked.append(key)
            proof.note('specified-get-versus-database',table=model.__tablename__,record_id=record_id,checked_fields=checked)
            proof.note('eight-stream-db-readback',table=model.__tablename__,record_id=record_id,fields={c.name:getattr(row,c.name) for c in model.__table__.columns if c.name not in {'created_at','updated_at'}})
        drive=(await db.execute(select(EquipmentDrive).where(EquipmentDrive.equipment_id=='line-A',EquipmentDrive.timestamp==datetime(2026,10,16,10,0,0,123000)))).scalar_one()
        fields=['tv','km','dew_point_set','dew_point_actual','oxygen','muffle_pressure','nh3_flow_set','nh3_flow_actual','ng_flow_set','ng_flow_actual','uncoiler_set','uncoiler_actual','entry_looper_set','entry_looper_actual','furnace_set','furnace_actual','exit_looper_set','exit_looper_actual','recoiler_set','recoiler_actual']
        assert all(abs(getattr(drive,key)-(i+.25))<=max(1e-6,abs(i+.25)*1e-6) for i,key in enumerate(fields))
        params=(await db.execute(select(EquipmentProductionParameters).where(EquipmentProductionParameters.equipment_id=='line-A'))).scalar_one()
        assert params.coil_no=='Case-卷' and params.entry_time.microsecond==1000 and params.thickness==0 and params.width==1 and params.total_time==2 and params.weight==3 and params.speed==4 and params.process_steps==[]
        parent=(await db.execute(select(Performance).where(Performance.equipment_id=='line-A',Performance.http_coil_key==b'0'))).scalar_one()
        assert parent.collected_weight==Decimal('9.0000') and parent.weight==0 and parent.manual_override_weight==0
        for key,value in dict(total_length='2.25',diameter='3.25',density='4.125',output_quantity='5.0001',qualified_quantity='6.0001',efficiency_rate='150.25',quality_score='101.25').items():assert getattr(parent,key)==Decimal(value)
        assert all(getattr(parent,key) is None for key in ('device_id','plc_key','db_number','group_name','first_raw_snapshot_id','last_raw_snapshot_id','plan_id'))
        proof.parent=parent.id
        temperature=(await db.execute(select(EquipmentTemperatureSample).where(EquipmentTemperatureSample.equipment_id=='temperature-pilot-01'))).scalar_one()
        for z in range(1,6):
            for k in ('set','act'):assert getattr(temperature,f'zone{z}_{k}')==Decimal(str(z+.125))
        curve=(await db.execute(select(HistoryProcessCurve).where(HistoryProcessCurve.equipment_id=='line-A'))).scalar_one()
        for key in __import__('app.monitor.services.async_process_curve_sample',fromlist=['FIELDS']).FIELDS:assert getattr(curve,key)==(0 if key.startswith('z') else 1.25)
    for stream,model,fields in [('production_parameters',EquipmentProductionParameters,('grade','entry_time','thickness','total_time','weight','speed')),('production_observation',Performance,('output_quantity','qualified_quantity','efficiency_rate','quality_score')),('process_temperature',ProcessTemperature,('max_temp','min_temp','avg_temp','duration')),('process_tension',ProcessTension,('avg_tension','max_tension','min_tension')),('process_speed',ProcessSpeed,('avg_speed','max_speed')),('process_curve',HistoryProcessCurve,('z1_temp_act','dew_point','coil_number'))]:
        result=await proof.post(stream,proof.sample(stream),proof.parent)
        async with proof.sessions() as db:
            row=await db.get(model,result['recordId']);assert all(getattr(row,key) is None for key in fields),(stream,fields)
        proof.note('missing-is-real-null',stream=stream,record_id=result['recordId'],null_fields=fields)
    # Real manual legacy create keeps its old explicitly None -> zero ORM defaults.
    from app.performance.services.async_performance import async_performance_service
    from app.performance.schemas.performance_in import PerformanceCreate
    async with proof.sessions() as db:
        from app.plan.models.plan import Plan
        plan_id=await db.scalar(select(Plan.id).where(Plan.coil_no=='manual-fixture-plan'))
        row=await async_performance_service.create(db,PerformanceCreate(plan_id=plan_id,grade='legacy',weight=0,coil_no='manual-none-proof',production_date=datetime(2026,10,17).date(),output_quantity=None,qualified_quantity=None,efficiency_rate=None,quality_score=None))
        await db.commit();await db.refresh(row)
        assert row.equipment_id is None and all(getattr(row,k)==0 for k in ('output_quantity','qualified_quantity','efficiency_rate','quality_score'))
        proof.note('manual-none-preserves-legacy-zero',record_id=row.id)


async def prove_delivery_and_partial(proof):
    from sqlalchemy import select
    from app.equipment.models.equipment import EquipmentDrive,EquipmentProductionParameters
    from app.performance.models.performance import ProcessTemperature,ProcessTension,ProcessSpeed
    rows=[('drive','tv','km'),('production_parameters','width','speed'),('process_temperature','setTemp','avgTemp'),('process_tension','setTension','avgTension'),('process_speed','setSpeed','avgSpeed'),('process_curve','lineSpeedAct',None),('production_observation','weight',None),('temperature','zone1Set',None)]
    for stream,field,fill in rows:
        data=proof.sample(stream)
        if stream=='production_observation':data['coilNo']='delivery-'+data['sampleId']
        first=await proof.post(stream,data,proof.parent)
        assert (await proof.post(stream,data,proof.parent))['recordId']==first['recordId']
        refreshed=proof.tokens['admin-one']
        from core.jwt import create_access_token
        proof.tokens['admin-one']=create_access_token({'sub':'temperature-admin-one'})
        assert (await proof.post(stream,data,proof.parent))['recordId']==first['recordId']
        proof.tokens['admin-one']=refreshed
        changed=dict(data,**{field:1})
        await proof.post(stream,changed,proof.parent,status=409,error='sample_id_conflict')
        other=dict(data,sampleId=data['sampleId']+'-other')
        assert (await proof.post(stream,other,proof.parent,actor='admin-two'))['recordId']==first['recordId']
        different=dict(other,sampleId=data['sampleId']+'-different',**{field:2})
        before=await proof.snapshot()
        await proof.post(stream,different,proof.parent,status=409,error='sample_time_conflict' if stream in ('temperature','process_curve') else 'observation_time_conflict' if stream=='production_observation' else 'value_conflict')
        assert await proof.snapshot()==before
        if fill:
            full=dict(data,sampleId=data['sampleId']+'-fill',**{fill:2})
            assert (await proof.post(stream,full,proof.parent))['outcome']=='updated'
            bad=dict(full,sampleId=data['sampleId']+'-atomic',**{field:2})
            before=await proof.snapshot();await proof.post(stream,bad,proof.parent,status=409,error='value_conflict');assert await proof.snapshot()==before
        # Case-sensitive sample identities are distinct delivery rows, even same actor and values.
        for suffix in ('Case','case'):await proof.post(stream,dict(data,sampleId=data['sampleId']+suffix),proof.parent)
        proof.note('delivery-replay-presence-conflict-case',stream=stream,record_id=first['recordId'])
    # Raw JSON contract is exercised against real JWT/DB dependency, with no writes on failure.
    path=proof.path('drive');base=proof.sample('drive');before=await proof.snapshot()
    raw=json.dumps(base)
    invalids=[raw[:-1]+',"tv":1}',json.dumps(dict(base,tv=True)),json.dumps(dict(base,tv='1')),json.dumps(dict(base,tv=None)),json.dumps(dict(base,equipment_id='line-A')),raw.replace('"tv": 0','"tv": NaN'),json.dumps(dict(base,sampledAt='2026-10-17T00:00:00.0001Z')),json.dumps(dict(base,tv=1e-40))]
    for body in invalids:
        response=await proof.client.post('/api/v1'+path,content=body,headers={'Authorization':'Bearer '+proof.tokens['admin-one'],'Content-Type':'application/json'})
        assert response.status_code==422,response.text
    assert await proof.snapshot()==before
    for stream,changes in [('production_observation',dict(weight=1.00001)),('process_temperature',dict(duration=1.5)),('process_tension',dict(minTension=2,avgTension=1)),('process_speed',dict(avgSpeed=2,maxSpeed=1)),('process_curve',dict(z1TempAct=1.5))]:
        await proof.post(stream,proof.sample(stream,**changes),proof.parent,status=422)
    proof.note('strict-json-real-auth-and-storage',invalid_cases=len(invalids)+5)


async def prove_auth_scope_and_modules(proof,monkeypatch):
    from core.jwt import create_access_token,create_refresh_token
    from dataclasses import replace
    import importlib
    from httpx import ASGITransport,AsyncClient
    from core.registrar import create_app
    owners=[('equipment','drive','equipment-mapping-ingest','equipment-mapping-read','/equipment/drive-samples',{'equipmentId':'line-A'}),('performance','production_observation','performance-mapping-ingest','performance-mapping-read','/performances/mapping-records',{'equipmentId':'line-A'}),('monitor','process_curve','monitor-curve-ingest','monitor-curve-read','/monitor/process-curve-samples',{'equipmentId':'line-A','date':'2026-10-17'})]
    invalid=[None,'bad',create_access_token({'sub':'temperature-admin-one'},timedelta(seconds=-1)),create_refresh_token({'sub':'temperature-admin-one'}),proof.target.revoked_token,proof.tokens['inactive']]
    before=await proof.snapshot()
    for owner,stream,ingest,read,path,params in owners:
        data=proof.sample(stream)
        for token in invalid:
            headers={} if token is None else {'Authorization':'Bearer '+token}
            await proof.request('POST',proof.path(stream),data,status=401,headers=headers)
            await proof.request('GET',path,params=params,status=401,headers=headers)
        await proof.request('POST',proof.path(stream),data,status=401,headers={'Authorization':'Basic '+proof.tokens['admin-one']})
        for role in ('supervisor','operator'):
            for grants,expected in [((read,),200),((ingest,),403),((owner,'projection-mapping-manage','control-agent-read'),403)]:
                proof.app.state.role_api_permissions={role:grants}
                await proof.request('GET',path,params=params,actor=role,status=expected)
                await proof.post(stream,data,actor=role,status=403)
        proof.app.state.role_api_permissions={'unknown':(read,ingest)}
        await proof.request('GET',path,params=params,actor='unknown',status=403)
        await proof.post(stream,dict(data,equipmentId='Line-A'),status=403)
        await proof.request('GET',path,params=dict(params,equipmentId='other'),status=403)
        config=importlib.import_module('app.'+owner+'.mapping_config');key={'equipment':'EQUIPMENT_MAPPING_INGEST_ID','performance':'PERFORMANCE_MAPPING_INGEST_ID','monitor':'MONITOR_MAPPING_INGEST_ID'}[owner]
        original=proof.app.dependency_overrides[config.get_mapping_config]
        def empty_config():return config.MappingConfig(**{key:''},_env_file=None)
        proof.app.dependency_overrides[config.get_mapping_config]=empty_config
        try:
            await proof.post(stream,data,status=403)
            await proof.request('GET',path,params=params,status=403)
        finally:proof.app.dependency_overrides[config.get_mapping_config]=original
        proof.note('real-jwt-roles-read-ingest-scope',owner=owner)
    assert await proof.snapshot()==before
    import app.router as routes
    for owner,stream,_,_,path,_ in owners:
        declaration=importlib.import_module('app.'+owner+'.manifest')
        with monkeypatch.context() as patch:
            patch.setattr(declaration,'manifest',replace(declaration.manifest,enabled=False))
            try:
                importlib.reload(routes);disabled=create_app(testing=True)
                async with AsyncClient(transport=ASGITransport(app=disabled),base_url='http://fixture') as client:
                    for method,url in [('GET',path),('POST',proof.path(stream))]:assert (await client.request(method,'/api/v1'+url)).status_code==404
            finally:patch.undo();importlib.reload(routes)
        proof.note('disabled-module-recomposition',owner=owner)


async def prove_first_insert_races(proof,monkeypatch):
    """两Session初查receipt的真实一致性读完成后barrier，不用sleep猜调度。"""
    import importlib
    for stream in ('drive','production_parameters','production_observation','process_temperature','process_tension','process_speed','process_curve'):
        owner='equipment' if stream in ('drive','production_parameters') else 'monitor' if stream=='process_curve' else 'performance'
        receipts=importlib.import_module('app.'+owner+'.crud.async_mapping_ingest')
        for same_id,changed in ((True,False),(True,True),(False,False),(False,True)):
            data=proof.sample(stream)
            if stream=='production_observation':data['coilNo']='race-'+data['sampleId']
            second=dict(data,sampleId=data['sampleId'] if same_id else data['sampleId']+'-other')
            key={'drive':'tv','production_parameters':'width','production_observation':'weight','process_temperature':'setTemp','process_tension':'setTension','process_speed':'setSpeed','process_curve':'lineSpeedAct'}[stream]
            if changed:second[key]=1
            barrier=asyncio.Barrier(2);seen=set();original=receipts.get_receipt
            async def synchronized(db,*args):
                result=await original(db,*args)
                task=asyncio.current_task()
                if task not in seen:
                    seen.add(task);await asyncio.wait_for(barrier.wait(),15)
                return result
            async def send(payload):return await proof.client.post('/api/v1'+proof.path(stream,proof.parent),json=payload,headers={'Authorization':'Bearer '+proof.tokens['admin-one']})
            with monkeypatch.context() as patch:
                patch.setattr(receipts,'get_receipt',synchronized)
                responses=await asyncio.wait_for(asyncio.gather(send(data),send(second)),30)
            initial=[response.status_code for response in responses]
            # A genuine InnoDB deadlock/unavailable is a 503, never a duplicate; same-key retry is then required.
            for index,response in enumerate(responses):
                if response.status_code==503:responses[index]=await send(data if index==0 else second)
            assert sorted(response.status_code for response in responses)==([200,409] if changed else [200,200]),[(response.status_code,response.text) for response in responses]
            if changed:
                rejected=next(response for response in responses if response.status_code==409)
                expected='sample_id_conflict' if same_id else 'observation_time_conflict' if stream=='production_observation' else 'sample_time_conflict' if stream=='process_curve' else 'value_conflict'
                assert rejected.json()['errorCode'].endswith(expected)
            else:assert responses[0].json()['data']['recordId']==responses[1].json()['data']['recordId']
            proof.note('first-insert-two-real-sessions',stream=stream,same_identity=same_id,changed=changed,barrier='after both initial receipt SELECTs',initial_statuses=initial,final_statuses=[response.status_code for response in responses])


async def prove_rr_and_delivery_waits(proof,monkeypatch):
    from app.performance.crud import async_mapping_ingest as pr,async_production_observation as pc
    from app.equipment.crud import async_mapping_ingest as er,async_drive_sample as ec
    from app.performance.models.mapping_ingest import PerformanceObservationState
    from app.equipment.models.equipment import EquipmentDrive
    from sqlalchemy import select
    # F-001: C has completed its real initial consistent read, waits while t1 and t2 commit.
    for changed in (False,True):
        t1=proof.sample('production_observation',coilNo='rr-'+str(changed),weight=1)
        t2=proof.sample('production_observation',observationStatus='not_in_production');t2.pop('coilNo');t2.pop('weight')
        replay=dict(t1,sampleId=t1['sampleId']+'-replay',weight=2 if changed else 1)
        read_done=asyncio.Event();continue_replay=asyncio.Event();original=pr.get_receipt
        async def initial_read(db,actor,equipment,stream,sample_id):
            result=await original(db,actor,equipment,stream,sample_id)
            if sample_id==replay['sampleId'] and not read_done.is_set():
                read_done.set();await asyncio.wait_for(continue_replay.wait(),15)
            return result
        with monkeypatch.context() as patch:
            patch.setattr(pr,'get_receipt',initial_read)
            task=asyncio.create_task(proof.post('production_observation',replay,status=409 if changed else 200,error='observation_time_conflict' if changed else None))
            await asyncio.wait_for(read_done.wait(),15)
            first=await proof.post('production_observation',t1)
            await proof.post('production_observation',t2)
            continue_replay.set();result=await asyncio.wait_for(task,15)
        if not changed:assert result['outcome']=='duplicate' and result['recordId']==first['recordId']
        async with proof.sessions() as db:
            state=(await db.execute(select(PerformanceObservationState).where(PerformanceObservationState.equipment_id=='line-A'))).scalar_one()
            assert state.last_sampled_at==datetime.fromisoformat(t2['sampledAt'][:-1])
        proof.note('F-001-real-RR-t1-t2',changed=changed,original_record_id=first['recordId'],outcome='409 observation_time_conflict' if changed else result['outcome'],barrier='replay initial receipt SELECT complete before t1/t2 commits')
    # F-002: B initial consistent read precedes A's uncommitted business insert; B waits on its actual row lock.
    for stream in ('drive','production_parameters'):
        from app.equipment.crud import async_production_parameter_sample as ep
        access=ec if stream=='drive' else ep
        a=proof.sample(stream);field='tv' if stream=='drive' else 'width';a[field]=1;b=dict(a,**{field:2})
        read_done=asyncio.Event();a_written=asyncio.Event();b_lock_entered=asyncio.Event();a_release=asyncio.Event()
        original_read=er.get_receipt;original_add=access.add_record;original_get=access.get_business_record
        a_task=None;b_task=None
        async def receipt(db,*args):
            result=await original_read(db,*args)
            if asyncio.current_task() is b_task and not read_done.is_set():
                read_done.set();await asyncio.wait_for(a_written.wait(),15)
            return result
        async def add(db,**values):
            row=await original_add(db,**values)
            if asyncio.current_task() is a_task:
                a_written.set();await asyncio.wait_for(a_release.wait(),15)
            return row
        async def get(db,sample):return await original_get(db,sample)
        from sqlalchemy import event
        def dispatched(connection,cursor,statement,parameters,context,executemany):
            if asyncio.current_task() is b_task and 'FOR UPDATE' in statement and ('equipment_drive' if stream=='drive' else 'equipment_production_parameters') in statement:b_lock_entered.set()
        with monkeypatch.context() as patch:
            patch.setattr(er,'get_receipt',receipt);patch.setattr(access,'add_record',add);patch.setattr(access,'get_business_record',get)
            event.listen(proof.engine.sync_engine,'before_cursor_execute',dispatched)
            b_task=asyncio.create_task(proof.post(stream,b,status=409,error='sample_id_conflict'))
            await asyncio.wait_for(read_done.wait(),15)
            a_task=asyncio.create_task(proof.post(stream,a))
            await asyncio.wait_for(a_written.wait(),15);await asyncio.wait_for(b_lock_entered.wait(),15)
            try:
                a_release.set();first,second=await asyncio.wait_for(asyncio.gather(a_task,b_task),30)
            finally:event.remove(proof.engine.sync_engine,'before_cursor_execute',dispatched)
        proof.note('F-002-real-lock-wait',stream=stream,record_id=first['recordId'],conflict='sample_id_conflict',barriers=['B receipt read','A business flushed','B get-business lock entered','A commit released'])


async def prove_lifecycle_and_manual_order(proof,monkeypatch):
    from sqlalchemy import select
    from app.performance.models.performance import Performance
    from app.performance.models.mapping_ingest import PerformanceObservationState
    from app.performance.crud import async_production_observation as crud
    # Status transitions and stale/new successful old event distinctions.
    a=proof.sample('production_observation',coilNo='lifecycle-A',weight=1)
    first=await proof.post('production_observation',a);parent=first['recordId']
    for status in ('unknown','not_in_production'):
        data=proof.sample('production_observation',observationStatus=status);data.pop('coilNo');data.pop('weight')
        await proof.post('production_observation',data)
    active=proof.sample('production_observation',coilNo='lifecycle-A',weight=2)
    assert (await proof.post('production_observation',active))['recordId']==parent
    b=proof.sample('production_observation',coilNo='lifecycle-B');await proof.post('production_observation',b)
    old=proof.sample('production_observation',coilNo='late-new-coil',sampledAt='2026-10-16T00:00:00.000Z')
    assert (await proof.post('production_observation',old))['outcome']=='stale'
    async with proof.sessions() as db:
        row=await db.get(Performance,parent);assert row.observation_status=='not_in_production'
        assert await db.scalar(select(Performance.id).where(Performance.http_coil_key==b'late-new-coil')) is None
    child=proof.sample('process_temperature',coilNo='lifecycle-A',zone='ended-parent',duration=7)
    await proof.post('process_temperature',child,parent)
    await proof.post('process_temperature',dict(child,sampleId='missing-parent'),999999,status=404,error='parent_not_found')
    await proof.post('process_temperature',dict(child,sampleId='mismatch-parent',coilNo='wrong'),parent,status=409,error='parent_mismatch')
    # Parent not ready: same child sampleId can be retried after its exact future parent is committed.
    async with proof.sessions() as db:
        from sqlalchemy import text
        future=await db.scalar(text("SELECT AUTO_INCREMENT FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name='performance_main'"))
    late_child=proof.sample('process_speed',coilNo='future-parent')
    await proof.post('process_speed',late_child,future,status=404)
    new_parent=await proof.post('production_observation',proof.sample('production_observation',coilNo='future-parent'))
    assert new_parent['recordId']==future
    await proof.post('process_speed',late_child,future)
    # HTTP PUT stays on original edit grant, with explicit source/scope and strict fields.
    path=f'/performances/{parent}';query={'dataSource':'http','equipmentId':'line-A'}
    await proof.request('PUT',path,{'weight':0},params=query)
    await proof.request('PUT',path,{'weight':1,'grade':'unsupported'},params=query,status=422)
    await proof.request('PUT',path,{'weight':1},params=dict(query,equipmentId='other'),status=403)
    await proof.request('DELETE',path,params=query,status=409,error='delete_forbidden')
    proof.app.state.role_api_permissions={'supervisor':('performance-mapping-read','performance-mapping-ingest')}
    await proof.request('PUT',path,{'weight':0},params=query,actor='supervisor',status=403)
    proof.app.state.role_api_permissions={'supervisor':('performance',)}
    await proof.request('PUT',path,{'weight':0},params=query,actor='supervisor')
    legacy=await proof.client.get('/api/v1'+path,headers={'Authorization':'Bearer '+proof.tokens['admin-one']})
    assert legacy.status_code==404 or legacy.json()['code']==404
    # Both actual commit orders: hold the first writer after obtaining the same real parent row lock.
    for manual_first in (True,False):
        coil='manual-order-'+str(manual_first);base=proof.sample('production_observation',coilNo=coil,weight=1)
        row=await proof.post('production_observation',base);record_id=row['recordId']
        observation=proof.sample('production_observation',coilNo=coil,weight=9)
        first_locked=asyncio.Event();second_entered=asyncio.Event();release=asyncio.Event();original=crud.by_id;original_coil=crud.by_coil
        first_task=None;second_task=None
        async def after_lock(operation,db,*args,**kwargs):
            current=asyncio.current_task()
            result=await operation(db,*args,**kwargs)
            if current is first_task:
                first_locked.set();await asyncio.wait_for(release.wait(),15)
            return result
        async def by_id(db,*args,**kwargs):return await after_lock(original,db,*args,**kwargs)
        async def by_coil(db,*args,**kwargs):return await after_lock(original_coil,db,*args,**kwargs)
        from sqlalchemy import event
        def dispatched(connection,cursor,statement,parameters,context,executemany):
            if asyncio.current_task() is second_task and 'FOR UPDATE' in statement and 'performance_main' in statement:second_entered.set()
        async def manual():return await proof.request('PUT',f'/performances/{record_id}',{'weight':0,'remark':'order proof'},params=query)
        async def observed():return await proof.post('production_observation',observation)
        with monkeypatch.context() as patch:
            patch.setattr(crud,'by_id',by_id);patch.setattr(crud,'by_coil',by_coil)
            event.listen(proof.engine.sync_engine,'before_cursor_execute',dispatched)
            first_task=asyncio.create_task(manual() if manual_first else observed())
            await asyncio.wait_for(first_locked.wait(),15)
            second_task=asyncio.create_task(observed() if manual_first else manual())
            await asyncio.wait_for(second_entered.wait(),15);release.set()
            try:await asyncio.wait_for(asyncio.gather(first_task,second_task),30)
            finally:event.remove(proof.engine.sync_engine,'before_cursor_execute',dispatched)
        async with proof.sessions() as db:
            stored=await db.get(Performance,record_id)
            assert stored.weight==0 and stored.effective_weight==0 and stored.collected_weight==9 and stored.manual_override_weight==0 and stored.effective_weight_source=='manual_override_weight'
        proof.note('manual-observation-lock-commit-order',manual_first=manual_first,record_id=record_id,manual_weight=0,collected_weight=9)
    proof.note('lifecycle-parent-late-source-delete-and-original-edit-permission',parent=parent)


async def prove_faults(proof,monkeypatch):
    """真实业务SQL已经进入事务后注入有界故障；逐项对照所有业务/receipt/state。"""
    import importlib
    from database import get_db
    from sqlalchemy import event
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker
    business={'temperature':'equipment_temperature_samples','drive':'equipment_drive','production_parameters':'equipment_production_parameters','production_observation':'performance_main','process_temperature':'performance_process_temperature','process_tension':'performance_process_tension','process_speed':'performance_process_speed','process_curve':'monitor_history_process_curves'}
    fields={'temperature':('zone1Set',None),'drive':('tv','km'),'production_parameters':('width','speed'),'production_observation':('weight','grade'),'process_temperature':('setTemp','avgTemp'),'process_tension':('setTension','avgTension'),'process_speed':('setSpeed','avgSpeed'),'process_curve':('lineSpeedAct',None)}
    from settings import settings
    monkeypatch.setattr(settings,'DEBUG',True);monkeypatch.setattr(proof.app,'debug',True);proof.app.middleware_stack=None
    bind=proof.sessions.kw['bind']
    original_dependency=proof.app.dependency_overrides[get_db]
    for stream,table in business.items():
        owner='equipment' if stream in ('temperature','drive','production_parameters') else 'monitor' if stream=='process_curve' else 'performance'
        for phase in ('insert','update','receipt','state','flush','commit-before','commit-after','dependency-commit','dependency-rollback','dependency-close','log-after-commit'):
            if phase=='state' and stream!='production_observation':continue
            if phase=='update' and stream in ('temperature','process_curve'):continue # Immutable curve has no update path.
            data=proof.sample(stream)
            if stream=='production_observation':data['coilNo']='fault-'+data['sampleId']
            if phase=='update':
                await proof.post(stream,data,proof.parent)
                data=dict(data,sampleId=data['sampleId']+'-fill',**{fields[stream][1]:'updated' if stream=='production_observation' else 2})
                if stream=='production_observation':data['sampledAt']=proof.sample(stream)['sampledAt']
            before=await proof.snapshot();fired=False
            def fail():raise OperationalError('synthetic',{},Exception('private controlled database failure'))
            def sql_fault(connection,cursor,statement,parameters,context,executemany):
                nonlocal fired
                if fired:return
                target={'insert':('INSERT INTO',table),'update':('UPDATE',table),'receipt':('INSERT INTO','equipment_temperature_sample_receipts' if stream=='temperature' else owner+'_mapping_receipts'),'state':('UPDATE','performance_mapping_observation_state')}.get(phase)
                if target and statement.upper().startswith(target[0]) and target[1] in statement:
                    fired=True;fail()
            class FaultSession(AsyncSession):
                commits=0
                async def flush(self,*args,**kwargs):
                    nonlocal fired
                    result=await super().flush(*args,**kwargs)
                    if phase=='flush' and not fired:fired=True;raise RuntimeError('private controlled flush failure')
                    return result
                async def commit(self):
                    nonlocal fired
                    self.commits+=1
                    if phase=='commit-before' and not fired:fired=True;fail()
                    result=await super().commit()
                    if phase=='commit-after' and not fired:fired=True;fail()
                    if phase=='dependency-commit' and self.commits==2 and not fired:fired=True;fail()
                    return result
            fault_sessions=async_sessionmaker(bind,class_=FaultSession,expire_on_commit=False,autoflush=False)
            async def dependency():
                nonlocal fired
                db=fault_sessions()
                try:
                    yield db
                    await db.commit()
                    if phase=='dependency-close' and not fired:
                        fired=True;await db.close();raise RuntimeError('private controlled close failure')
                except Exception:
                    await db.rollback()
                    if phase=='dependency-rollback' and not fired:fired=True;fail()
                    raise
                finally:
                    await AsyncSession.rollback(db);await AsyncSession.close(db)
            # Dependency rollback needs a business rejection after a real SQL read.
            if phase=='dependency-rollback':
                first=await proof.post(stream,data,proof.parent)
                data=dict(data,**{fields[stream][0]:1});before=await proof.snapshot()
            with monkeypatch.context() as patch:
                proof.app.dependency_overrides[get_db]=dependency
                event.listen(bind.sync_engine,'before_cursor_execute',sql_fault)
                if phase=='log-after-commit':
                    service=importlib.import_module('app.'+owner+'.services.'+('async_temperature_sample' if stream=='temperature' else {'equipment':'async_drive_sample','performance':'async_production_observation','monitor':'async_process_curve_sample'}[owner]))
                    def log(*args,**kwargs):
                        nonlocal fired
                        if any((str(value).endswith('_mapping_received') or str(value)=='temperature_sample_received') for value in args):fired=True;raise RuntimeError('private post commit log failure')
                    patch.setattr(service,'log_event',log)
                try:
                    expected=500 if phase in ('flush','dependency-close','log-after-commit') else 503
                    await proof.post(stream,data,proof.parent,status=expected)
                finally:
                    event.remove(bind.sync_engine,'before_cursor_execute',sql_fault)
                    proof.app.dependency_overrides[get_db]=original_dependency
            assert fired,(stream,phase)
            durable=phase in ('commit-after','dependency-commit','dependency-close','log-after-commit')
            after=await proof.snapshot()
            if not durable:assert after==before,(stream,phase)
            else:
                assert after!=before,(stream,phase)
                result=await proof.post(stream,data,proof.parent)
                assert result['outcome']=='duplicate',(stream,phase,result)
                assert await proof.snapshot()==after
            proof.note('real-transaction-fault',stream=stream,phase=phase,status=expected,persisted=durable,same_key_retry='duplicate original row' if durable else 'no business/receipt/state effect')


async def prove_database_constraints(proof):
    """独立Session真实约束拒绝，不将Python校验当数据库保护。"""
    from sqlalchemy import select,insert
    from sqlalchemy.exc import IntegrityError
    from database import Base
    tables=['equipment_drive','equipment_production_parameters','performance_main','performance_process_temperature','performance_process_tension','performance_process_speed','monitor_history_process_curves','equipment_mapping_receipts','performance_mapping_receipts','monitor_mapping_receipts','performance_mapping_observation_state']
    for name in tables:
        table=Base.metadata.tables[name]
        async with proof.sessions() as db:
            query=select(table).where(table.c.equipment_id=='line-A')
            if name=='performance_mapping_receipts':query=query.where(table.c.performance_id.is_not(None))
            row=(await db.execute(query.limit(1))).mappings().first()
            assert row is not None,name
            values={key:value for key,value in row.items() if key not in {'id','created_at','updated_at'}}
        async with proof.sessions() as db:
            try:await db.execute(insert(table).values(**values));await db.commit()
            except IntegrityError:await db.rollback()
            else:raise AssertionError(('unique did not reject',name))
        if name.endswith('_receipts'):
            bad=dict(values,equipment_id='other',sample_id='cross-device-'+name)
            async with proof.sessions() as db:
                try:await db.execute(insert(table).values(**bad));await db.commit()
                except IntegrityError:await db.rollback()
                else:raise AssertionError(('composite target FK did not reject',name))
        proof.note('real-unique-and-composite-fk',table=name)
    # Exact HTTP business coil and zone keys permit case variants while preserving legacy CI columns.
    for stream in ('production_parameters','production_observation'):
        first=proof.sample(stream,coilNo='ExactCase');second=dict(first,sampleId=first['sampleId']+'-case',coilNo='exactcase')
        if stream=='production_observation':second['sampledAt']=proof.sample(stream)['sampledAt']
        a=await proof.post(stream,first);b=await proof.post(stream,second);assert a['recordId']!=b['recordId']
    for kind in ('temperature','tension','speed'):
        data=proof.sample('process_'+kind,zone='ExactZone')
        a=await proof.post('process_'+kind,data,proof.parent);b=await proof.post('process_'+kind,dict(data,zone='exactzone',sampleId=data['sampleId']+'-case'),proof.parent)
        assert a['recordId']!=b['recordId']
    proof.note('case-sensitive-http-business-coil-zone')


async def prepare_browser_rows(proof):
    """给当轮真实页面保留可审计最新合成观测，UI操作者按同recordId/字段核对。"""
    from app.equipment.services.async_drive_sample import DRIVE_FIELDS
    from app.monitor.services.async_process_curve_sample import FIELDS
    from common.schema_base import to_camel
    moment='2026-10-17T07:00:00.123Z';rows={}
    drive={to_camel(key):0 if index==0 else index+.25 for index,key in enumerate(DRIVE_FIELDS)}
    parameter=dict(coilNo='UI-卷-0',grade='UI',entryTime='2026-10-17T06:00:00.001Z',thickness=0,width=1.25,totalTime=2.5,weight=3.75,speed=4.25)
    production=dict(coilNo='UI-卷-0',observationStatus='in_production',grade='UI',weight=1.2345,totalLength=2.25,diameter=3.25,density=4.125,spec='UI-S',startTime='2026-10-17T06:00:00.123Z',endTime='2026-10-17T07:00:00.123Z',outputQuantity=5.0001,qualifiedQuantity=6.0001,efficiencyRate=150.25,qualityScore=101.25,remark='UI reported')
    curve={to_camel(key):0 if key.startswith('z') else 1.25 for key in FIELDS}
    for stream,values in [('drive',drive),('production_parameters',parameter),('production_observation',production),('process_curve',dict(coilNumber='UI-卷-0',**curve)),('temperature',{f'zone{zone}{kind}':0 if zone==1 else zone+.125 for zone in range(1,6) for kind in ('Set','Act')})]:
        data=proof.sample(stream,sampledAt=moment,**values);result=await proof.post(stream,data)
        rows[stream]=dict(result=result,payload=data)
    parent=rows['production_observation']['result']['recordId']
    for kind,values in [('temperature',dict(setTemp=0,minTemp=-1,maxTemp=2,avgTemp=1,duration=5)),('tension',dict(setTension=0,minTension=0,avgTension=1,maxTension=2)),('speed',dict(setSpeed=0,avgSpeed=1,maxSpeed=2))]:
        data=proof.sample('process_'+kind,coilNo='UI-卷-0',recordTime=moment,**values);result=await proof.post('process_'+kind,data,parent)
        rows['process_'+kind]=dict(result=result,payload=data)
    await proof.request('PUT',f'/performances/{parent}',dict(weight=0,remark='UI manual zero'),params=dict(dataSource='http',equipmentId='line-A'))
    (proof.target.root/'browser-rows.json').write_text(json.dumps(rows,indent=2))
    proof.note('browser-latest-row-fixture',record_ids={key:row['result']['recordId'] for key,row in rows.items()},source_time=moment,date_shanghai='2026-10-17',parent_id=parent)


def prove_legacy_sync_transaction(target):
    """只直调八个旧sync业务Service；不启动/调用Projection runner、PLC或collector。"""
    from sqlalchemy import select,func
    from sqlalchemy.orm import Session
    from projection.provenance_contract import get_expected_device_id
    from app.equipment.services import sync_drive as drive,sync_temperature as temperature,sync_production_parameters as parameters
    from app.performance.services import sync_production_record as production,sync_process_temperature as pt,sync_process_tension as pn,sync_process_speed as ps
    from app.monitor.services import sync_process_curve as curve
    from app.system.models.projection_mapping import ProjectionMappingSet,ProjectionRuntimeCursor,ProjectionRuntimeAuditEvent
    from app.equipment.models.equipment import EquipmentDrive,EquipmentProductionParameters
    from app.performance.models.performance import Performance
    moment=datetime(2026,10,16,10,0,0,123000)
    common=dict(plc_key='PLC_1',device_id=get_expected_device_id('PLC_1'),db_number=28,group_name='CD_HMI_Read_Data',raw_snapshot_id=999001,collected_at=moment,quality='good')
    def apply(db):
        mapping=ProjectionMappingSet(plc_key='PLC_1',db_number=28,group_name='CD_HMI_Read_Data',handler_key='synthetic-business-transaction-test')
        db.add(mapping);db.flush()
        results=[]
        results.append(drive.sync_drive(db,drive.EquipmentDriveFact(**common,values=dict(tv=99))))
        results.append(temperature.sync_temperature(db,temperature.EquipmentTemperatureFact(**common,values=dict(zone1_set=99))))
        results.append(parameters.sync_production_parameters(db,parameters.EquipmentProductionParametersFact(**common,values=dict(coil_no='Case-卷',width=99))))
        results.append(production.sync_production_record(db,production.ProductionRecordFact(**common,coil_no_value='0',weight_value=99)))
        process_common=dict(common,coil_no_value='0',zone_value='Z',record_time_value=datetime(2026,10,16,10,0,0,125000))
        results.append(pt.sync_process_temperature(db,pt.ProcessTemperatureFact(**process_common,set_temp_value=99)))
        results.append(pn.sync_process_tension(db,pn.ProcessTensionFact(**process_common,set_tension_value=99)))
        results.append(ps.sync_process_speed(db,ps.ProcessSpeedFact(**process_common,set_speed_value=99)))
        results.append(curve.sync_process_curve(db,curve.ProcessCurveFact(**common,values=dict(line_speed_act=99))))
        db.add(ProjectionRuntimeCursor(mapping_set_id=mapping.id,last_raw_snapshot_id=999001))
        db.add(ProjectionRuntimeAuditEvent(mapping_set_id=mapping.id,event_type='processed',first_raw_snapshot_id=999001,last_raw_snapshot_id=999001,processed_snapshot_count=1))
        db.flush();assert all(result.action=='created' for result in results),results
        return mapping.id
    with Session(target.engine) as db:
        baseline=db.scalar(select(func.count()).select_from(ProjectionMappingSet));db.rollback()
        apply(db);db.rollback()
        assert db.scalar(select(func.count()).select_from(ProjectionMappingSet))==baseline;db.rollback()
        mapping_id=apply(db)
        # Separate connection cannot see business/cursor/audit before the caller's commit.
        with Session(target.engine) as observer:
            assert observer.get(ProjectionMappingSet,mapping_id) is None
            assert observer.scalar(select(func.count()).select_from(ProjectionRuntimeCursor).where(ProjectionRuntimeCursor.mapping_set_id==mapping_id))==0
        db.commit()
    with Session(target.engine) as db:
        assert db.get(ProjectionMappingSet,mapping_id) is not None
        assert db.scalar(select(func.count()).select_from(ProjectionRuntimeCursor).where(ProjectionRuntimeCursor.mapping_set_id==mapping_id))==1
        assert db.scalar(select(func.count()).select_from(ProjectionRuntimeAuditEvent).where(ProjectionRuntimeAuditEvent.mapping_set_id==mapping_id))==1
        assert db.scalar(select(EquipmentDrive.tv).where(EquipmentDrive.equipment_id=='line-A',EquipmentDrive.timestamp==moment))==.25
        assert db.scalar(select(EquipmentProductionParameters.width).where(EquipmentProductionParameters.equipment_id=='line-A',EquipmentProductionParameters.timestamp==moment))==1
        assert db.scalar(select(Performance.weight).where(Performance.equipment_id=='line-A',Performance.http_coil_key==b'0'))==0
    (target.root/'legacy-sync-transaction.json').write_text(json.dumps(dict(services=8,caller_rollback_no_business_cursor_audit=True,caller_commit_business_cursor_audit=True,http_rows_unchanged=True,projection_runner_executed=False,mapping_set_id=mapping_id),indent=2))


async def prove_energy_unchanged(proof):
    from sqlalchemy import select
    from database import Base
    async def rows():
        async with proof.sessions() as db:
            return {name:[tuple(map(str,row)) for row in (await db.execute(select(Base.metadata.tables[name]))).all()] for name in ('energy_prices','energy_price_hours')}
    before=await rows()
    for path in ('/energy/current','/energy?date=2026-10-17'):
        response=await proof.client.get('/api/v1'+path,headers={'Authorization':'Bearer '+proof.tokens['admin-one']})
        assert response.status_code==200 and response.json()['code']==200,response.text
    proof.app.state.role_api_permissions={'supervisor':('equipment-mapping-read','performance-mapping-ingest','monitor-curve-read')}
    response=await proof.client.post('/api/v1/energy',json=dict(electricPrice=0,hydrogenPrice=0,argonPrice=0),headers={'Authorization':'Bearer '+proof.tokens['supervisor']})
    assert response.status_code==403 or response.json()['code']==403
    assert await rows()==before
    proof.note('energy-two-tables-three-api-isolation',unchanged=True)


async def prove_first_state_competition(target,monkeypatch):
    from httpx import ASGITransport,AsyncClient
    from sqlalchemy import select,func
    from app.performance.models.mapping_ingest import PerformanceObservationState
    from app.performance.crud import async_mapping_ingest as receipts
    app,engine,sessions=target.api()
    try:
        async with sessions() as db:assert await db.scalar(select(func.count()).select_from(PerformanceObservationState))==0
        async with AsyncClient(transport=ASGITransport(app=app),base_url='http://fixture') as client:
            proof=BusinessProof(target,client,sessions,app)
            data=dict(equipmentId='line-A',sampleId='first-state-A',sampledAt='2026-10-16T00:00:00.123Z',quality='good',observationStatus='unknown')
            second=dict(data,sampleId='first-state-B');barrier=asyncio.Barrier(2);seen=set();original=receipts.get_receipt
            async def synchronized(db,*args):
                result=await original(db,*args);task=asyncio.current_task()
                if task not in seen:seen.add(task);await asyncio.wait_for(barrier.wait(),15)
                return result
            async def send(payload):return await client.post('/api/v1/performances/production-observations',json=payload,headers={'Authorization':'Bearer '+proof.tokens['admin-one']})
            with monkeypatch.context() as patch:
                patch.setattr(receipts,'get_receipt',synchronized)
                responses=await asyncio.wait_for(asyncio.gather(send(data),send(second)),30)
            initial=[response.status_code for response in responses]
            for index,response in enumerate(responses):
                if response.status_code==503:responses[index]=await send(data if index==0 else second)
            assert all(response.status_code==200 for response in responses),[(r.status_code,r.text) for r in responses]
            assert {r.json()['data']['outcome'] for r in responses}=={'updated','duplicate'}
            async with sessions() as db:
                assert await db.scalar(select(func.count()).select_from(PerformanceObservationState))==1
                state=(await db.execute(select(PerformanceObservationState))).scalar_one()
                assert state.performance_id is None and state.last_sampled_at==datetime(2026,10,16,0,0,0,123000)
            (target.root/'first-state-competition.json').write_text(json.dumps(dict(initial_statuses=initial,final_statuses=[r.status_code for r in responses],outcomes=[r.json()['data']['outcome'] for r in responses],barrier='both real receipt consistent reads before first state lock',state_rows=1),indent=2))
    finally:await engine.dispose()


async def prove_locked_refresh_current_read(proof,monkeypatch):
    from app.equipment.crud import async_mapping_ingest as receipts
    for stream in ('drive','production_parameters'):
        data=proof.sample(stream);second=dict(data,sampleId=data['sampleId']+'-late-reader')
        ready=asyncio.Event();release=asyncio.Event();original=receipts.get_receipt
        async def receipt(db,actor,equipment,kind,sample_id):
            result=await original(db,actor,equipment,kind,sample_id)
            if sample_id==second['sampleId'] and not ready.is_set():ready.set();await asyncio.wait_for(release.wait(),15)
            return result
        with monkeypatch.context() as patch:
            patch.setattr(receipts,'get_receipt',receipt)
            task=asyncio.create_task(proof.post(stream,second))
            await asyncio.wait_for(ready.wait(),15)
            first=await proof.post(stream,data)
            release.set();replay=await asyncio.wait_for(task,15)
        assert replay['outcome']=='duplicate' and replay['recordId']==first['recordId']
        from app.equipment.models.equipment import EquipmentDrive,EquipmentProductionParameters
        async with proof.sessions() as db:
            row=await db.get(EquipmentDrive if stream=='drive' else EquipmentProductionParameters,first['recordId'])
            assert getattr(row,'tv' if stream=='drive' else 'width')==0
            assert all(getattr(row,key) is None for key in (('km','oxygen') if stream=='drive' else ('grade','weight')))
        proof.note('locked-row-refresh-current-RR-read',stream=stream,record_id=first['recordId'],barrier='late reader receipt snapshot before first business commit')


async def prove_identity_check_constraints(proof):
    from sqlalchemy import select,insert
    from sqlalchemy.exc import DBAPIError
    from database import Base
    for stream in ('drive','production_parameters','production_observation','process_temperature','process_tension','process_speed','process_curve','temperature'):
        name='equipment_mapping_receipts' if stream in ('drive','production_parameters') else 'monitor_mapping_receipts' if stream=='process_curve' else 'equipment_temperature_sample_receipts' if stream=='temperature' else 'performance_mapping_receipts'
        table=Base.metadata.tables[name]
        async with proof.sessions() as db:
            # Match the exact pair emitted by delivery tests, excluding other stream sample IDs.
            condition=table.c.sample_id.like('proof-'+stream+'-%Case') | table.c.sample_id.like('proof-'+stream+'-%case')
            if 'stream' in table.c:condition=condition & (table.c.stream==stream)
            keys=[key for key in (await db.execute(select(table.c.sample_id).where(condition))).scalars() if re.fullmatch('proof-'+re.escape(stream)+r'-\d+(?:Case|case)',key)]
            assert len(keys)==2 and any(key.endswith('Case') for key in keys) and any(key.endswith('case') for key in keys),(stream,keys)
        proof.note('case-sensitive-delivery-rows',stream=stream,distinct_case_rows=2)
    for name in ('equipment_mapping_receipts','performance_mapping_receipts','monitor_mapping_receipts'):
        table=Base.metadata.tables[name]
        async with proof.sessions() as db:
            source=(await db.execute(select(table).limit(1))).mappings().one()
            values={key:value for key,value in source.items() if key not in {'id','created_at','updated_at'}}
        values.update(sample_id='check-uppercase-'+name,stream=values['stream'].upper())
        async with proof.sessions() as db:
            try:await db.execute(insert(table).values(**values));await db.commit()
            except DBAPIError as exc:
                await db.rollback();assert getattr(exc.orig,'args',())[0]==3819,(name,type(exc.orig).__name__)
            else:raise AssertionError(('stream target CHECK not enforced',name))
        proof.note('real-stream-target-check-enforced',table=name)
