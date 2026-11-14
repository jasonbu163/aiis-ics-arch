"""旧采集清退的离线护栏、装配与精确后继自检；不连接数据库。"""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory

pytestmark = pytest.mark.no_db


def migration():
    path = Path(__file__).resolve().parents[1] / 'alembic/versions/20261110_2215_3d5f7a9c1e23_retire_legacy_acquisition.py'
    spec = importlib.util.spec_from_file_location('acq002_migration', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Result:
    def __init__(self, rows): self.rows = rows
    def __iter__(self): return iter(self.rows)
    def one(self): return self.rows[0]
    def first(self): return self.rows[0] if self.rows else None


class Connection:
    dialect = SimpleNamespace(name='mysql')
    def __init__(self, module):
        self.module = module
        self.identity = ('8.4.6', 'fixture-uuid', 'fixture_schema')
        self.revisions = [(module.down_revision,)]
        self.tables = set(module.EXPECTED_TABLES)
        self.nonempty = set()
        self.foreign_keys = []
        self.views = []
        self.triggers = []
        self.routines = []
        self.events = []
        self.engines = {}
        self.statements = []
        self.lock_error = False
    def execute(self, statement, parameters=None):
        sql = str(statement)
        self.statements.append(sql)
        if 'SELECT VERSION()' in sql: return Result([self.identity])
        if 'SELECT @@SESSION.lock_wait_timeout' in sql: return Result([(60,)])
        if sql.startswith('SET SESSION lock_wait_timeout') or sql == 'UNLOCK TABLES': return Result([])
        if sql.startswith('LOCK TABLES'):
            if self.lock_error: raise RuntimeError('lock timeout')
            return Result([])
        if 'FROM alembic_version' in sql: return Result(self.revisions)
        if 'information_schema.TABLES' in sql: return Result([(x, self.engines.get(x, 'InnoDB')) for x in self.tables])
        if 'information_schema.KEY_COLUMN_USAGE' in sql: return Result(self.foreign_keys)
        if 'information_schema.VIEWS' in sql: return Result(self.views)
        if 'information_schema.TRIGGERS' in sql: return Result(self.triggers)
        if 'information_schema.ROUTINES' in sql: return Result(self.routines)
        if 'information_schema.EVENTS' in sql: return Result(self.events)
        if sql.startswith('SELECT 1 FROM `'):
            table = sql.split('`')[1]
            return Result([(1,)] if table in self.nonempty else [])
        raise AssertionError(sql)


def prepared(monkeypatch):
    module = migration()
    conn = Connection(module)
    ddl = []
    monkeypatch.setenv('ACQ_RETIREMENT_EXPECTED_SERVER_UUID', 'fixture-uuid')
    monkeypatch.setenv('ACQ_RETIREMENT_EXPECTED_SCHEMA', 'fixture_schema')
    monkeypatch.delenv('ACQ_RETIREMENT_RECOVERY_CONFIRMED', raising=False)
    monkeypatch.delenv('ACQ_RETIREMENT_RECOVERY_EVIDENCE_SHA256', raising=False)
    module.context = SimpleNamespace(is_offline_mode=lambda: False)
    module.op = SimpleNamespace(get_bind=lambda: conn, execute=ddl.append)
    return module, conn, ddl


def test_single_head_and_metadata_retire_only_nine_tables():
    from app.module_registry import import_model_packages
    from app.control_agent.models.gate_token import ControlAgentGateToken  # noqa: F401
    from database import Base
    module = migration()
    import_model_packages()
    graph = ScriptDirectory.from_config(Config('alembic.ini'))
    assert graph.get_heads() == ['7b9d1f3a5c7e']
    assert graph.get_revision('7b9d1f3a5c7e').down_revision == '6a8c0e2b4d16'
    assert graph.get_revision('6a8c0e2b4d16').down_revision == '5f7a9c1e3b25'
    assert graph.get_revision('4e6a8b0d2f14').down_revision == module.revision
    assert graph.get_revision(module.revision).down_revision == module.down_revision
    assert len(module.EXPECTED_TABLES) == 77 and len(module.RETIRED_TABLES) == 9
    original = module.EXPECTED_TABLES - set(module.RETIRED_TABLES)
    expected = (original - {'plc_facts_samples_v2', 'plc_facts_latest_points_v2'}) | {
        'plc_facts_history', 'plc_facts_latest'}
    task_revision = graph.get_revision('5f7a9c1e3b25').module
    expected = (expected - set(task_revision.OLD_TABLES)) | set(task_revision.NEW_ONLY) | {'performance_main', 'plc_source_registry'}
    assert set(Base.metadata.tables) == expected


def test_offline_and_downgrade_refuse():
    module = migration()
    module.context = SimpleNamespace(is_offline_mode=lambda: True)
    with pytest.raises(RuntimeError, match='online'): module.upgrade()
    with pytest.raises(RuntimeError, match='forward-only'): module.downgrade()


def test_online_uses_one_exact_ddl_after_checks(monkeypatch):
    module, conn, ddl = prepared(monkeypatch)
    module.upgrade()
    assert len(ddl) == 1
    assert ddl[0] == 'DROP TABLE ' + ', '.join(f'`{name}`' for name in module.RETIRED_TABLES)
    assert sum(s.startswith('SELECT 1 FROM `') for s in conn.statements) == 9
    assert sum(s.startswith('LOCK TABLES') for s in conn.statements) == 1
    assert conn.statements[-2:] == ['UNLOCK TABLES', 'SET SESSION lock_wait_timeout = :timeout']


@pytest.mark.parametrize('case', ['identity', 'version', 'revision', 'extra', 'partial', 'nonempty', 'engine',
                                  'foreign_key', 'view', 'trigger', 'routine', 'event', 'unreadable'])
def test_invalid_target_state_or_dependency_rejected_before_ddl(monkeypatch, case):
    module, conn, ddl = prepared(monkeypatch)
    table = module.RETIRED_TABLES[0]
    if case == 'identity': conn.identity = ('8.4.6', 'wrong', 'fixture_schema')
    elif case == 'version': conn.identity = ('8.0.40', 'fixture-uuid', 'fixture_schema')
    elif case == 'revision': conn.revisions = [(module.down_revision,), ('unexpected',)]
    elif case == 'extra': conn.tables.add('unexpected')
    elif case == 'partial': conn.tables.remove(table)
    elif case == 'nonempty': conn.nonempty.add(table)
    elif case == 'engine': conn.engines[table] = 'MyISAM'
    elif case == 'foreign_key': conn.foreign_keys = [('other', 'child', 'fixture_schema', table)]
    elif case == 'view': conn.views = [('other', 'select * from ' + table)]
    elif case == 'trigger': conn.triggers = [('other', 'insert into ' + table)]
    elif case == 'routine': conn.routines = [('other', 'select * from ' + table)]
    elif case == 'event': conn.events = [('other', 'delete from ' + table)]
    else: conn.views = [('other', None)]
    with pytest.raises(RuntimeError): module.upgrade()
    assert ddl == []


def test_lock_failure_releases_and_restores_timeout_before_any_ddl(monkeypatch):
    module, conn, ddl = prepared(monkeypatch)
    conn.lock_error = True
    with pytest.raises(RuntimeError, match='lock timeout'): module.upgrade()
    assert ddl == []
    assert conn.statements[-2:] == ['UNLOCK TABLES', 'SET SESSION lock_wait_timeout = :timeout']


def test_absent_tables_require_explicit_evidence_and_confirmation(monkeypatch):
    module, conn, ddl = prepared(monkeypatch)
    conn.tables -= set(module.RETIRED_TABLES)
    with pytest.raises(RuntimeError, match='evidence'): module.upgrade()
    monkeypatch.setenv('ACQ_RETIREMENT_RECOVERY_EVIDENCE_SHA256', 'a' * 64)
    with pytest.raises(RuntimeError, match='evidence'): module.upgrade()
    monkeypatch.setenv('ACQ_RETIREMENT_RECOVERY_CONFIRMED', 'fixture_schema:fixture-uuid')
    module.upgrade()
    assert ddl == []  # Alembic owns the subsequent version registration.


def test_legacy_routes_absent_and_v2_business_routes_present():
    from core.registrar import create_app
    app = create_app(testing=True)
    paths = app.openapi()['paths']
    for path in ('/api/v1/integration/plc-facts/batches', '/api/v1/integration/plc-facts/latest',
                 '/api/v1/integration/plc-facts/history', '/api/v1/monitor/realtime/latest'):
        assert path not in paths
    assert not any(path.startswith('/api/v1/projection-mappings') for path in paths)
    for path in ('/api/v1/integration/plc-facts/samples', '/api/v1/acquisition-data/options',
                 '/api/v1/acquisition-data/latest', '/api/v1/acquisition-data/history',
                 '/api/v1/acquisition-data/history/{id}', '/api/v1/monitor/collector/status',
                 '/api/v1/sys-dict', '/api/v1/auth/login'):
        assert path in paths
