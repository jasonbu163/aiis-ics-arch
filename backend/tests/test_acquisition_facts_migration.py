"""采集事实表迁移的离线目标、结构、权限与中断恢复测试。"""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.no_db


@pytest.fixture
def migration():
    path = Path(__file__).resolve().parents[1] / 'alembic/versions/20261111_1030_4e6a8b0d2f14_finalize_plc_facts_tables.py'
    spec = importlib.util.spec_from_file_location('acq003_migration_offline', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_names_ddl_and_forward_only(migration):
    assert migration.down_revision == '3d5f7a9c1e23'
    assert migration.revision == '4e6a8b0d2f14'
    assert migration.RENAME_SQL.count('RENAME TABLE') == 1
    assert migration.RENAME_SQL.count(' TO ') == 2
    assert migration.ALTER_SQL.count('ALTER TABLE') == 1
    assert 'CAST(`source_type` AS BINARY)' in migration.ALTER_SQL
    assert "'646161'" in migration.ALTER_SQL and "'65787465726E616C'" in migration.ALTER_SQL
    with pytest.raises(RuntimeError, match='forward-only'):
        migration.downgrade()


class Result(list):
    def one(self):
        assert len(self) == 1
        return self[0]

    def scalar_one(self):
        return self.one()[0]

    def first(self):
        return self[0] if self else None

    def scalars(self):
        return [row[0] for row in self]


def test_target_requires_exact_identity_timezone_and_operation(migration, monkeypatch):
    connection = SimpleNamespace(dialect=SimpleNamespace(name='mysql'))
    target = ['8.4.6', 'fixture-uuid', 'fixture_schema', 28800]
    monkeypatch.setattr(migration, '_execute', lambda *_: Result([target]))
    monkeypatch.setenv('ACQ_FACTS_EXPECTED_SERVER_UUID', 'fixture-uuid')
    monkeypatch.setenv('ACQ_FACTS_EXPECTED_SCHEMA', 'fixture_schema')
    monkeypatch.setenv('ACQ_FACTS_OPERATION_ID', 'fixture-op.1')
    assert migration._target(connection) == ('fixture_schema', 'fixture-uuid', 'fixture-op.1')
    for index, bad in ((0, '8.0.41'), (1, 'other'), (2, 'other'), (3, 0)):
        original = target[index]
        target[index] = bad
        with pytest.raises(RuntimeError, match='target'):
            migration._target(connection)
        target[index] = original
    monkeypatch.setenv('ACQ_FACTS_OPERATION_ID', '../invalid')
    with pytest.raises(RuntimeError, match='operation'):
        migration._target(connection)
    connection.dialect.name = 'sqlite'
    with pytest.raises(RuntimeError, match='MySQL'):
        migration._target(connection)


def test_state_rejects_mixed_names_and_engines(migration, monkeypatch):
    tables = [(migration.OLD_HISTORY, 'InnoDB', 'BASE TABLE'), (migration.OLD_LATEST, 'InnoDB', 'BASE TABLE')]
    columns = []
    def execute(_db, sql, _params=None):
        return Result(tables if 'information_schema.TABLES' in sql else [(c,) for c in columns])
    monkeypatch.setattr(migration, '_execute', execute)
    assert migration._state(None)[0] == 'old'
    tables[:] = [(migration.HISTORY, 'InnoDB', 'BASE TABLE'), (migration.LATEST, 'InnoDB', 'BASE TABLE')]
    assert migration._state(None)[0] == 'renamed'
    columns.append('source_type')
    assert migration._state(None)[0] == 'altered'
    tables[1] = (migration.OLD_LATEST, 'InnoDB', 'BASE TABLE')
    with pytest.raises(RuntimeError, match='mixed'):
        migration._state(None)
    tables[:] = [(migration.HISTORY, 'MyISAM', 'BASE TABLE'), (migration.LATEST, 'InnoDB', 'BASE TABLE')]
    with pytest.raises(RuntimeError, match='InnoDB'):
        migration._state(None)


def test_columns_and_indexes_are_exact(migration, monkeypatch):
    rows = [[name, kind, 'YES' if nullable else 'NO', extra, None,
             'utf8mb4' if kind.startswith('varchar(') else None,
             'utf8mb4_unicode_ci' if kind.startswith('varchar(') else None,
             6 if kind == 'datetime(6)' else None, '']
            for name, kind, nullable, extra in migration._expected_columns(True, True)]
    def execute(_db, sql, _params=None):
        if 'SCHEMATA' in sql:
            return Result([('utf8mb4', 'utf8mb4_unicode_ci', 'utf8mb4_unicode_ci')])
        return Result(rows)
    monkeypatch.setattr(migration, '_execute', execute)
    migration._check_columns(None, migration.HISTORY, True, True)
    rows[5][2] = 'NO'
    with pytest.raises(RuntimeError, match='column'):
        migration._check_columns(None, migration.HISTORY, True, True)
    rows[5][2] = 'YES'
    for index, replacement in ((4, 'unexpected-default'), (5, 'latin1'), (6, 'latin1_swedish_ci'),
                               (7, 0), (8, 'some generated expression')):
        previous = rows[-1][index]
        rows[-1][index] = replacement
        with pytest.raises(RuntimeError, match='column'):
            migration._check_columns(None, migration.HISTORY, True, True)
        rows[-1][index] = previous
    index_rows = [[name, unique, pos, column, None, 'BTREE', 'YES', None, 'A', '']
                  for name, (unique, cols) in migration.HISTORY_INDEXES.items()
                  for pos, column in enumerate(cols, 1)]
    monkeypatch.setattr(migration, '_execute', lambda *_: Result(index_rows))
    assert migration._check_indexes(None, migration.HISTORY, migration.HISTORY_INDEXES) == migration.HISTORY_INDEXES
    for index, replacement in ((4, 1), (8, 'D'), (9, 'YES')):
        previous = index_rows[0][index]
        index_rows[0][index] = replacement
        with pytest.raises(RuntimeError, match='index'):
            migration._check_indexes(None, migration.HISTORY, migration.HISTORY_INDEXES)
        index_rows[0][index] = previous
    index_rows.pop()
    with pytest.raises(RuntimeError, match='index'):
        migration._check_indexes(None, migration.HISTORY, migration.HISTORY_INDEXES)


def test_check_constraints_require_enforcement_and_byte_exact_types(migration, monkeypatch):
    rows = [
        ('ck_pfv2_sample_bounds', 'YES', '((`db_number` between 1 and 65535) and (`source_seq` > 0))'),
        ('ck_pfv2_source_type', 'YES', '((`source_type` is null) or (cast(`source_type` as char charset binary) in (0x646161,0x65787465726e616c)))'),
    ]
    monkeypatch.setattr(migration, '_execute', lambda *_: Result(rows))
    migration._check_checks(None, migration.HISTORY, True, True)
    rows[1] = (rows[1][0], 'NO', rows[1][2])
    with pytest.raises(RuntimeError, match='CHECK'):
        migration._check_checks(None, migration.HISTORY, True, True)
    rows[1] = (rows[1][0], 'YES', '`source_type` in (\'daa\',\'external\')')
    with pytest.raises(RuntimeError, match='CHECK'):
        migration._check_checks(None, migration.HISTORY, True, True)


def test_grants_require_new_table_or_schema_or_global_coverage(migration, monkeypatch):
    table_grants = [('app@host', migration.OLD_HISTORY, 'SELECT')]
    schema_grants = []
    global_grants = []
    def execute(_db, sql, _params=None):
        if 'TABLE_PRIVILEGES' in sql:
            return Result(table_grants)
        if 'SCHEMA_PRIVILEGES' in sql:
            return Result(schema_grants)
        if 'USER_PRIVILEGES' in sql:
            return Result(global_grants)
        raise AssertionError(sql)
    monkeypatch.setattr(migration, '_execute', execute)
    with pytest.raises(RuntimeError, match='grant'):
        migration._check_grants(None, 'fixture')
    table_grants.append(('app@host', migration.HISTORY, 'SELECT'))
    migration._check_grants(None, 'fixture')
    table_grants.pop()
    schema_grants.append(('app@host', 'SELECT'))
    migration._check_grants(None, 'fixture')
    schema_grants.clear()
    global_grants.append(('app@host', 'SELECT'))
    migration._check_grants(None, 'fixture')
    global_grants[:] = [('other@host', 'SELECT')]
    with pytest.raises(RuntimeError, match='grant'):
        migration._check_grants(None, 'fixture')


def test_recovery_evidence_binds_identity_and_original_data(migration, monkeypatch):
    monkeypatch.setattr(migration, '_target', lambda _: ('schema', 'uuid', 'operation'))
    monkeypatch.setattr(migration, '_state', lambda _: ('old', migration.OLD_HISTORY, migration.OLD_LATEST))
    for name in ('_check_columns', '_check_indexes', '_check_checks'):
        monkeypatch.setattr(migration, name, lambda *_: None)
    audit = {'history': {'count': 1, 'sha256': 'a' * 64}, 'historyAutoIncrement': 2}
    monkeypatch.setattr(migration, '_audit', lambda *_: audit)
    first = migration.recovery_evidence_sha256(None)
    assert len(first) == 64
    audit['history']['sha256'] = 'b' * 64
    assert migration.recovery_evidence_sha256(None) != first
    audit['history']['sha256'] = 'a' * 64
    monkeypatch.setattr(migration, '_target', lambda _: ('schema', 'uuid', 'another-operation'))
    assert migration.recovery_evidence_sha256(None) != first


@pytest.mark.parametrize('stage', ['old', 'renamed', 'altered'])
def test_upgrade_recovers_only_evidenced_stage(migration, monkeypatch, stage):
    current = [stage]
    statements = []
    proof = 'a' * 64
    def state(_):
        return (current[0], migration.OLD_HISTORY if current[0] == 'old' else migration.HISTORY,
                migration.OLD_LATEST if current[0] == 'old' else migration.LATEST)
    def execute(_db, sql, _params=None):
        if sql.startswith('SELECT version_num'):
            return Result([(migration.down_revision,)])
        if sql.startswith('SELECT @@SESSION'):
            return Result([(30,)])
        return Result([])
    def ddl(sql):
        statements.append(sql)
        current[0] = 'renamed' if sql == migration.RENAME_SQL else 'altered'
    monkeypatch.setattr(migration, 'context', SimpleNamespace(is_offline_mode=lambda: False))
    monkeypatch.setattr(migration, 'op', SimpleNamespace(get_bind=lambda: object(), execute=ddl))
    monkeypatch.setattr(migration, '_target', lambda _: ('fixture', 'uuid', 'op'))
    monkeypatch.setattr(migration, '_state', state)
    monkeypatch.setattr(migration, '_execute', execute)
    monkeypatch.setattr(migration, '_audit', lambda *_: {'count': 1})
    monkeypatch.setattr(migration, 'recovery_evidence_sha256', lambda *_: proof)
    monkeypatch.setattr(migration, '_check_dependencies', lambda *_: None)
    monkeypatch.setattr(migration, '_check_grants', lambda *_: None)
    if stage != 'old':
        monkeypatch.setenv('ACQ_FACTS_RECOVERY_STAGE', stage)
        monkeypatch.setenv('ACQ_FACTS_RECOVERY_EVIDENCE_SHA256', 'b' * 64)
        with pytest.raises(RuntimeError, match='evidence'):
            migration.upgrade()
        assert not statements
        monkeypatch.setenv('ACQ_FACTS_RECOVERY_EVIDENCE_SHA256', proof)
    migration.upgrade()
    assert statements == ({'old': [migration.RENAME_SQL, migration.ALTER_SQL],
                           'renamed': [migration.ALTER_SQL], 'altered': []}[stage])
