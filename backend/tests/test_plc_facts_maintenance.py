"""维护裸帮助/参数/CAS/预算的无DB源码边界检查。"""
import ast
import runpy
from types import SimpleNamespace
import pytest
from app.plc_facts.services.sync_maintenance import adopt,MaintenanceOptions
from app.plc_facts.retention import instant
from app.plc_facts.error_codes import FactsError
from test_plc_facts_contract import ROOT
pytestmark=pytest.mark.no_db

def test_bare_cli_and_help_before_settings_import(capsys):
    namespace=runpy.run_path(str(ROOT/'backend/scripts/plc_facts_maintenance/main.py'),run_name='be009_cli_test')
    assert namespace['main']([])==0
    assert 'usage:' in capsys.readouterr().out
    with pytest.raises(SystemExit) as exc:namespace['main'](['--help'])
    assert exc.value.code==0

@pytest.mark.parametrize('action',['status','adopt','cleanup'])
def test_no_implicit_target_or_apply(action):
    namespace=runpy.run_path(str(ROOT/'backend/scripts/plc_facts_maintenance/main.py'),run_name='be009_cli_parser')
    with pytest.raises(SystemExit):namespace['parser']().parse_args([action])

def test_revalidate_never_accepts_source_arguments():
    options=MaintenanceOptions('adopt',False,'alias','schema','1b3d5f7a9c20','epoch','approved','operator',revalidate_schema_only=True,plc_id='forbidden')
    with pytest.raises(FactsError):adopt(None,options,{},None,instant('2026-11-04T10:00:00+08:00'))

def test_only_seven_owner_tables_and_no_commit_in_crud():
    for file in (ROOT/'backend/app/plc_facts/crud').glob('*.py'):
        tree=ast.parse(file.read_text())
        assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('commit','rollback','create_all') for n in ast.walk(tree))
    source=(ROOT/'backend/app/plc_facts/services/sync_maintenance.py').read_text()
    assert 'range(10' in source and '2000' in source and '20*1024*1024' in source and '2*1024*1024' in source
    assert 'time.monotonic()-started<0.1' in source


def test_source_epoch_switch_and_unchanged_definition_retention(monkeypatch):
    import json
    from app.plc_facts.models import LatestPoint
    from app.plc_facts.canonical import binary,canonical,sha
    from app.plc_facts.source import prepare,definition_digest
    from app.plc_facts.services.sync_maintenance import adopt
    from test_plc_facts_contract import sample
    from test_plc_facts_ordering import MemoryDb,NOW
    from app.plc_facts.crud.async_ingest import payload_size
    prepared=prepare(sample());db=MemoryDb(prepared);binding=db.bindings['plc-demo']
    db.state.adoption_id='adoption';db.state.storage_epoch='epoch'
    fact=prepared.parts[0].projection['points']['point_x']
    row=LatestPoint(plc_id=b'plc-demo',point_id=b'point_x',source_epoch=1,definition_digest=binary(definition_digest(prepared.parts[0].payload.points['point_x'].definition)),point_fact=canonical(fact))
    db.rows.append(row);db.state.value_bytes=payload_size(row)
    class Result:
        def scalars(self):return iter(db.rows)
    class SyncDb:
        def get(self,model,key):return binding
        def execute(self,statement):return Result()
        def delete(self,value):db.rows.remove(value)
    context=sample()['cycles'][0]['contextUtf8'];profile=dict(schemaProfile='BE009-B',revision='0a2c4e6f8b10',fingerprint='sha256:'+'00'*32)
    binding.config_revision=b'config-demo';binding.context_sha=binary(sha(context.encode()))
    base=dict(action='adopt',apply=True,target_alias='synthetic',schema='synthetic',expected_schema_revision='0a2c4e6f8b10',expected_storage_epoch='epoch',operation_approval='synthetic',confirmed_by='operator',expected_adoption_id='adoption',plc_id='plc-demo',instance_id='daa-demo',source_generation='generation-demo',config_revision='config-comment',context_utf8=context,context_sha256=sha(context.encode()),expected_binding_revision=1,seq_from=1)
    same=adopt(SyncDb(),MaintenanceOptions(**base),profile,db.state,NOW)
    assert same['sourceEpoch']=='1' and db.rows==[row] and db.state.value_bytes==payload_size(row)
    base.update(source_generation='generation-new',expected_binding_revision=2,old_seq_through=1005)
    switched=adopt(SyncDb(),MaintenanceOptions(**base),profile,db.state,NOW)
    assert switched['sourceEpoch']=='2' and db.rows==[] and db.state.value_bytes==0
    assert binding.source_epoch==2 and binding.seq_from==1


class _SelectResult:
    """有限SELECT替身；实际WHERE/ORDER/LIMIT先解释，绝不连接数据库。"""
    def __init__(self, rows): self.rows=rows
    def scalars(self): return iter(self.rows)
    def scalar_one(self): return self.rows[0]
    def scalar_one_or_none(self): return self.rows[0] if self.rows else None
    def first(self): return self.rows[0] if self.rows else None


class _CleanupSelectDb:
    """执行真实cleanup CRUD生成的表达式，不按期望结果硬编码候选列表。"""
    def __init__(self, cycles=(), receipts=()):
        from app.plc_facts.models import RawSample,LatestPoint,Cycle,BatchReceipt,SampleReceipt
        self.models=(RawSample,LatestPoint,Cycle,BatchReceipt,SampleReceipt)
        self.rows={m.__table__.name:[] for m in self.models}
        self.rows[Cycle.__table__.name]=list(cycles)
        self.rows[SampleReceipt.__table__.name]=list(receipts)
        self.statements=[]

    def expression(self, expr, environment):
        from sqlalchemy.sql import operators
        from sqlalchemy.sql.elements import BindParameter,BooleanClauseList,BinaryExpression,Grouping,UnaryExpression,Null
        from sqlalchemy.sql.selectable import Exists
        from sqlalchemy.sql.functions import FunctionElement
        if isinstance(expr,BindParameter): return expr.value
        if isinstance(expr,Null): return None
        if isinstance(expr,Exists):
            statement=expr.element.element
            return any(all(self.expression(c,{**environment,table:row}) for c in statement._where_criteria)
                       for table in self.rows for row in self.rows[table]
                       if table=='plc_facts_sample_receipts')
        if isinstance(expr,Grouping): return self.expression(expr.element,environment)
        if isinstance(expr,BooleanClauseList):
            values=[self.expression(c,environment) for c in expr.clauses]
            return all(values) if expr.operator is operators.and_ else any(values)
        if isinstance(expr,UnaryExpression):
            assert expr.operator is operators.inv
            return not self.expression(expr.element,environment)
        if isinstance(expr,BinaryExpression):
            left=self.expression(expr.left,environment);right=self.expression(expr.right,environment)
            if expr.operator is operators.is_: return left is right
            if expr.operator is operators.is_not: return left is not right
            if left is None or right is None: return False
            assert expr.operator in (operators.eq,operators.ne,operators.lt,operators.le,operators.gt,operators.ge,operators.add)
            return expr.operator(left,right)
        if isinstance(expr,FunctionElement):
            values=[self.expression(c,environment) for c in expr.clauses]
            if expr.name=='octet_length': return len(values[0]) if values[0] is not None else None
            if expr.name=='coalesce': return next((v for v in values if v is not None),None)
            raise AssertionError(expr.name)
        if getattr(expr,'table',None) is not None:
            return getattr(environment[expr.table.name],expr.key)
        raise AssertionError(str(expr))

    def aggregate(self,expr,environments):
        from sqlalchemy.sql.functions import FunctionElement
        if not isinstance(expr,FunctionElement): return self.expression(expr,{})
        if expr.name=='coalesce': return next((v for v in (self.aggregate(c,environments) for c in expr.clauses) if v is not None),None)
        if expr.name=='count': return len(environments)
        values=[self.expression(next(iter(expr.clauses)),env) for env in environments]
        values=[v for v in values if v is not None]
        if not values:return None
        if expr.name=='min': return min(values)
        if expr.name=='sum': return sum(values)
        raise AssertionError(expr.name)

    def execute(self,statement):
        from sqlalchemy.sql.functions import FunctionElement
        self.statements.append(statement)
        model=statement.column_descriptions[0].get('entity')
        table=model.__table__.name if model else statement.get_final_froms()[0].name
        rows=[r for r in self.rows[table] if all(self.expression(c,{table:r}) for c in statement._where_criteria)]
        if statement._order_by_clauses:
            rows.sort(key=lambda r:tuple(self.expression(c,{table:r}) for c in statement._order_by_clauses))
        if statement._limit_clause is not None: rows=rows[:statement._limit_clause.value]
        column=statement.column_descriptions[0]['expr']
        if isinstance(column,FunctionElement):return _SelectResult([self.aggregate(column,[{table:r} for r in rows])])
        if column is model:return _SelectResult(rows)
        return _SelectResult([self.expression(column,{table:r}) for r in rows])

    def delete(self,row):self.rows[row.__table__.name].remove(row)
    def flush(self):pass


def _cleanup_fixture(count=201):
    from datetime import timedelta
    from app.plc_facts.models import Cycle
    now=instant('2027-02-06T12:00:00+08:00')
    cycles=[Cycle(instance_id=b'instance',cycle_id=str(n).encode(),expires_at=now.wall-timedelta(hours=26)+timedelta(seconds=n),expires_ns=0,
                  proof_expires_at=now.wall+timedelta(days=20),manifest_utf8=b'm',context_utf8=b'c',transport_manifest=b't') for n in range(count)]
    state=SimpleNamespace(value_bytes=count*3,proof_rows=count,max_value_bytes=1073741824,max_proof_rows=1000000,
                          proof_floor_serial=0,proof_floor_ordinal=0,cleanup_failures=0,cleanup_last_success=None,
                          storage_epoch='synthetic',adoption_id='synthetic',high_serial=0)
    return cycles,state,now


def _assert_cleanup_counts(db,state):
    from app.plc_facts.crud import sync_maintenance as crud
    assert state.value_bytes==crud.blob_bytes(db)
    assert state.proof_rows==crud.proof_rows(db)


@pytest.mark.parametrize('empty',[None,b''])
def test_cleanup_empty_cycle_prefix_does_not_hide_later_original_or_status(monkeypatch,empty):
    from app.plc_facts.crud import sync_maintenance as crud
    from app.plc_facts.services import sync_maintenance as service
    from app.plc_facts.models import Cycle
    rows,state,now=_cleanup_fixture()
    for row in rows[:200]:row.manifest_utf8=row.context_utf8=row.transport_manifest=empty
    state.value_bytes=3;db=_CleanupSelectDb(rows)
    # The deterministic clock isolates candidate selection, not real DB latency/SLA.
    monkeypatch.setattr(service.time,'monotonic',lambda:0)
    assert service.summary(db,state,now)['physicalCleanupSlaViolated']
    result=service.cleanup_batch(db,state,now,True)
    assert (result['rows'],result['valueBytes'],state.value_bytes)==(1,3,0)
    assert len(db.rows[Cycle.__table__.name])==201 and state.proof_rows==201
    assert crud.oldest_expired(db,Cycle,now) is None
    assert not service.summary(db,state,now)['physicalCleanupSlaViolated']
    _assert_cleanup_counts(db,state)


def test_cleanup_multiple_ticks_clear_the_201st_cycle_without_repeated_empty_prefix(monkeypatch):
    from app.plc_facts.services import sync_maintenance as service
    rows,state,now=_cleanup_fixture();db=_CleanupSelectDb(rows)
    monkeypatch.setattr(service.time,'monotonic',lambda:0)
    results=[service.cleanup_batch(db,state,now,True) for _ in range(3)]
    assert [r['rows'] for r in results]==[200,1,0]
    assert [r['valueBytes'] for r in results]==[600,3,0]
    assert state.value_bytes==0 and state.proof_rows==201
    _assert_cleanup_counts(db,state)


def test_cleanup_referenced_cycle_proof_prefix_does_not_hide_later_unreferenced_proof(monkeypatch):
    from datetime import timedelta
    from app.plc_facts.models import Cycle,SampleReceipt
    from app.plc_facts.services import sync_maintenance as service
    rows,state,now=_cleanup_fixture();receipts=[]
    for n,row in enumerate(rows):
        row.manifest_utf8=row.context_utf8=row.transport_manifest=None
        row.proof_expires_at=now.wall-timedelta(hours=2)+timedelta(seconds=n)
        if n<200:receipts.append(SampleReceipt(id=n+1,instance_id=row.instance_id,cycle_id=row.cycle_id,commit_serial=n+1,ordinal=1,proof_expires_at=now.wall+timedelta(days=1)))
    state.value_bytes=0;state.proof_rows=401;db=_CleanupSelectDb(rows,receipts)
    monkeypatch.setattr(service.time,'monotonic',lambda:0)
    result=service.cleanup_batch(db,state,now,True)
    remaining=db.rows[Cycle.__table__.name]
    assert result['proofRows']==1 and state.proof_rows==400
    assert len(remaining)==200 and all(row.cycle_id!=b'200' for row in remaining)
    assert len(db.rows[SampleReceipt.__table__.name])==200
    assert (state.proof_floor_serial,state.proof_floor_ordinal)==(0,0)
    _assert_cleanup_counts(db,state)


def test_cleanup_nonempty_cycle_proof_prefix_keeps_values_and_allows_later_empty_proof(monkeypatch):
    from datetime import timedelta
    from app.plc_facts.models import Cycle
    from app.plc_facts.services import sync_maintenance as service
    rows,state,now=_cleanup_fixture()
    for row in rows:
        row.expires_at=now.wall+timedelta(days=1)
        row.proof_expires_at=now.wall-timedelta(days=1)
    rows[-1].manifest_utf8=rows[-1].context_utf8=rows[-1].transport_manifest=b''
    state.value_bytes=600;db=_CleanupSelectDb(rows)
    monkeypatch.setattr(service.time,'monotonic',lambda:0)
    result=service.cleanup_batch(db,state,now,True)
    assert (result['proofRows'],result['valueBytes'],state.proof_rows,state.value_bytes)==(1,0,200,600)
    assert all(row.cycle_id!=b'200' for row in db.rows[Cycle.__table__.name])
    _assert_cleanup_counts(db,state)


def test_cleanup_partial_cycle_values_obey_byte_budget_and_exact_nanosecond_cutoff(monkeypatch):
    from app.plc_facts.services import sync_maintenance as service
    rows,state,now=_cleanup_fixture(1);row=rows[0]
    row.manifest_utf8=None;row.context_utf8=b'ab';row.transport_manifest=b'c';state.value_bytes=3
    row.expires_at=now.wall;row.expires_ns=1
    db=_CleanupSelectDb(rows);monkeypatch.setattr(service.time,'monotonic',lambda:0)
    assert service.cleanup_batch(db,state,now,True)['rows']==0
    row.expires_ns=0
    first=service.cleanup_batch(db,state,now,True,remaining_bytes=2)
    assert (first['rows'],first['valueBytes'],state.value_bytes)==(1,2,1)
    second=service.cleanup_batch(db,state,now,True)
    assert (second['rows'],second['valueBytes'],state.value_bytes)==(1,1,0)
    _assert_cleanup_counts(db,state)


def test_cleanup_sample_proof_deletes_only_complete_expired_serial_prefix(monkeypatch):
    from datetime import timedelta
    from app.plc_facts.models import SampleReceipt
    from app.plc_facts.services import sync_maintenance as service
    _,state,now=_cleanup_fixture(0)
    receipts=[SampleReceipt(id=n+1,instance_id=b'i',cycle_id=b'c',commit_serial=serial,ordinal=ordinal,
                            proof_expires_at=now.wall+timedelta(days=1) if n==0 else now.wall-timedelta(days=1))
              for n,(serial,ordinal) in enumerate(((1,1),(1,2),(2,1)))]
    state.proof_rows=3;db=_CleanupSelectDb(receipts=receipts)
    monkeypatch.setattr(service.time,'monotonic',lambda:0)
    assert service.cleanup_batch(db,state,now,True)['rows']==0
    receipts[0].proof_expires_at=now.wall-timedelta(days=1)
    assert service.cleanup_batch(db,state,now,True,remaining_rows=1)['rows']==0
    first=service.cleanup_batch(db,state,now,True)
    assert first['proofRows']==2 and (state.proof_floor_serial,state.proof_floor_ordinal)==(1,2)
    second=service.cleanup_batch(db,state,now,True)
    assert second['proofRows']==1 and (state.proof_floor_serial,state.proof_floor_ordinal)==(2,1)
    _assert_cleanup_counts(db,state)


def test_cleanup_budget_includes_each_real_write_flush(monkeypatch):
    """写入耗时必须参与下一候选预算，不能200项末尾才发现整批超时。"""
    from app.plc_facts.services import sync_maintenance as service
    rows,state,now=_cleanup_fixture()
    db=_CleanupSelectDb(rows)
    elapsed=[0.0]
    monkeypatch.setattr(service.time,'monotonic',lambda:elapsed[0])
    def flush(): elapsed[0]+=0.03
    db.flush=flush
    result=service.cleanup_batch(db,state,now,True)
    assert result['rows']==3 and result['valueBytes']==9
    assert sum(bool(row.manifest_utf8) for row in rows)==198
    _assert_cleanup_counts(db,state)
