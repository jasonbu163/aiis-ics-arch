"""ARCH-ACQ-007：离线验证运行兼容探针、迁移前后条件和维护目标。"""
from datetime import datetime
from types import SimpleNamespace

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.mysql import dialect
from sqlalchemy.exc import OperationalError

from app.plc_facts.crud import async_v2, sync_v2_maintenance
from app.plc_facts.v2_config import TABLE_NAMES_REVISION
from app.plc_facts.v2_domain import V2Error

pytestmark = pytest.mark.no_db
NOW = datetime(2026, 11, 24, 10)
TARGET = {'alias': 'fixture', 'serverUuid': '00000000-0000-4000-8000-000000000001',
          'schema': 'fixture_schema', 'schemaRevision': 'e9f3b5d7c021'}


class Rows(list):
    def all(self):
        return self

    def one(self):
        (row,) = self
        return row

    def scalar_one_or_none(self):
        return self.one()[0] if self else None

    def scalar_one(self):
        return self.one()[0]

    def scalars(self):
        return [row[0] for row in self]


class LayoutProbe:
    def __init__(self, *, revision='eeeeeeeeeeee', fault=None):
        self.revision = revision
        self.fault = fault
        self.calls = []
        self.dialect = SimpleNamespace(name='sqlite' if fault == 'dialect' else 'mysql')
        self.target_row = (TARGET['serverUuid'] if fault != 'uuid' else 'different',
                           TARGET['schema'] if fault != 'schema' else 'different',
                           '8.4.6' if fault != 'version' else '8.0.9', NOW, 28800 if fault != 'clock' else 0)

    def get_bind(self):
        return self

    async def run_sync(self, operation, *args):
        return operation(self, *args)

    def execute(self, statement, params=None):
        sql = str(statement)
        self.calls.append(sql)
        if '@@server_uuid' in sql:
            return Rows([self.target_row])
        if 'alembic_version' in sql:
            assert 'FOR SHARE' in sql
            return Rows([(self.revision,)])
        if 'information_schema.TABLES' in sql:
            return Rows((name, 'MyISAM' if self.fault == 'engine' else 'InnoDB') for name in params['tables']
                        if self.fault != 'table' or name != 'acq_plc_facts_latest')
        if 'information_schema.COLUMNS' in sql:
            if self.fault == 'permission':
                raise OperationalError('synthetic', {}, RuntimeError('denied'))
            data = Rows()
            for name, table in sync_v2_maintenance._LAYOUT.items():
                for column in table.columns:
                    collation = getattr(column.type, 'collation', None)
                    kind = column.type.compile(dialect=dialect()).lower().split(' character set ', 1)[0]
                    nullable = 'YES' if column.nullable else 'NO'
                    extra = 'auto_increment' if (name, column.name) == ('acq_plc_facts_history', 'id') else ''
                    if (name, column.name) == ('acq_plc_facts_latest', 'source_seq'):
                        if self.fault == 'column':
                            continue
                        if self.fault == 'type':
                            kind = 'bigint unsigned'
                        if self.fault == 'nullable':
                            nullable = 'YES'
                    data.append((name, column.name, kind, nullable, collation, extra))
            return data
        if 'information_schema.STATISTICS' in sql:
            data = Rows()
            for name, table in sync_v2_maintenance._LAYOUT.items():
                data.extend((name, 'PRIMARY', column.name, None) for column in table.primary_key.columns
                            if self.fault != 'pk' or name != 'acq_plc_facts_latest')
                for constraint in table.constraints:
                    if isinstance(constraint, UniqueConstraint):
                        prefix = 4 if self.fault == 'prefix' else None
                        data.extend((name, constraint.name, column.name, prefix) for column in constraint.columns
                                    if self.fault != 'unique' or name != 'acq_consumption_events')
            return data
        assert 'acq_consumption_activation' in sql and 'TRIGGER' not in sql
        return Rows([] if self.fault == 'no_ready_row' else [(0 if self.fault == 'inactive' else 1,)])


@pytest.mark.asyncio
async def test_stale_profile_and_unrelated_head_run_without_version_or_trigger_lookup():
    db = LayoutProbe()
    assert await async_v2.target_now(db, TARGET) == NOW
    assert len(db.calls) == 5
    assert not any('alembic_version' in call or 'TRIGGER' in call for call in db.calls)

    with pytest.raises(V2Error, match='not_ready'):
        sync_v2_maintenance.target_now(db, TARGET, require_layout=True)
    assert sync_v2_maintenance.target_now(db, dict(TARGET, schemaRevision=db.revision), require_layout=True) == NOW


@pytest.mark.asyncio
@pytest.mark.parametrize('fault', ('uuid', 'schema', 'version', 'clock', 'dialect', 'engine', 'table', 'column',
                                  'type', 'nullable', 'pk', 'unique', 'prefix', 'permission', 'no_ready_row', 'inactive'))
async def test_runtime_fails_closed_before_business_sql(fault):
    with pytest.raises(V2Error, match='not_ready'):
        await async_v2.target_now(LayoutProbe(fault=fault), TARGET)


def test_rename_revision_is_forward_only_and_has_the_inspected_quality_parent():
    graph = ScriptDirectory.from_config(Config('alembic.ini'))
    assert graph.get_heads() == [TABLE_NAMES_REVISION]
    migration = graph.get_revision(TABLE_NAMES_REVISION).module
    assert migration.down_revision == 'f0a2b4c6d8e1'
    assert len(migration.RENAMES) == 3
    assert set(migration.RENAMES.values()) | migration.CONSUMPTION_TABLES == set(sync_v2_maintenance._LAYOUT)
    with pytest.raises(RuntimeError, match='forward-only'):
        migration.downgrade()


def test_frozen_source_registry_ddl_matches_runtime_layout_except_name():
    from sqlalchemy import MetaData
    from sqlalchemy.schema import CreateTable

    from app.plc_facts.models.source_registry import PlcSourceRegistry
    from database import Base

    graph = ScriptDirectory.from_config(Config('alembic.ini'))
    historical = graph.get_revision('7b9d1f3a5c7e').module
    assert historical.down_revision == '6a8c0e2b4d16'
    old = historical.SOURCE_REGISTRY
    assert old.name == 'plc_source_registry'
    assert old.metadata is not Base.metadata
    assert 'plc_source_registry' not in Base.metadata.tables
    expected = PlcSourceRegistry.__table__.to_metadata(MetaData(), name=old.name)
    assert str(CreateTable(old).compile(dialect=dialect())) == str(CreateTable(expected).compile(dialect=dialect()))
    assert set(old.indexes) == set(expected.indexes) == set()
    assert old.c.retired_generations.default.arg.__wrapped__ is list


@pytest.mark.parametrize('change', ('none', 'missing', 'unreadable', 'extra', 'table', 'timing', 'event', 'body'))
def test_maintenance_trigger_verification(change):
    migration = ScriptDirectory.from_config(Config('alembic.ini')).get_revision(TABLE_NAMES_REVISION).module
    history = 'acq_plc_facts_history'
    rows = Rows((name, timing, event, history, body) for name, (timing, event, body) in migration.TRIGGERS.items())
    if change == 'missing':
        rows.pop()
    if change == 'extra':
        rows.append(('unexpected', 'BEFORE', 'UPDATE', history, 'SET @unexpected=1'))
    if change in ('table', 'timing', 'event', 'body'):
        name, timing, event, table, body = rows[0]
        rows[0] = (name, 'BEFORE' if change == 'timing' else timing,
                   'UPDATE' if change == 'event' else event,
                   'other_history' if change == 'table' else table, 'SET @unexpected=1' if change == 'body' else body)

    def execute(statement, params):
        assert 'TRIGGER_SCHEMA = DATABASE()' in str(statement)
        assert set(params['trigger_names']) == set(migration.TRIGGERS)
        if change == 'unreadable':
            raise OperationalError('synthetic', {}, RuntimeError('denied'))
        return rows

    conn = SimpleNamespace(execute=execute)
    if change == 'none':
        migration._require_triggers(conn, history)
    else:
        with pytest.raises((RuntimeError, OperationalError)):
            migration._require_triggers(conn, history)


@pytest.mark.parametrize('fault', (None, 'revision', 'layout', 'ready', 'references', 'post_trigger'))
def test_rename_statement_is_guarded_and_interruption_does_not_repair(monkeypatch, fault):
    from contextlib import nullcontext

    migration = ScriptDirectory.from_config(Config('alembic.ini')).get_revision(TABLE_NAMES_REVISION).module
    calls = []
    renamed = False

    def execute(statement, params=None):
        nonlocal renamed
        sql = ' '.join(str(statement).split())
        calls.append(sql)
        if '@@server_uuid' in sql:
            return Rows([(TARGET['serverUuid'], TARGET['schema'], '8.4.6', 28800)])
        if any(token in sql for token in ('SHA2(', 'GET_LOCK', 'RELEASE_LOCK', 'SELECT @@SESSION.')):
            return Rows([(1,)])
        if 'alembic_version' in sql:
            return Rows([('eeeeeeeeeeee' if fault == 'revision' else migration.down_revision,)])
        if 'information_schema.TABLES' in sql:
            names = migration.RENAMES.values() if renamed else migration.RENAMES
            names = set(names) | migration.CONSUMPTION_TABLES
            if fault == 'layout':
                names.add('acq_plc_facts_history')
            return Rows((name, 'BASE TABLE', 'InnoDB') for name in names)
        if 'SELECT ready' in sql:
            return Rows([(0 if fault == 'ready' else 1,)])
        if 'information_schema.TRIGGERS' in sql:
            known = 'acq_plc_facts_history' if renamed and fault != 'post_trigger' else 'plc_facts_history'
            return Rows((name, timing, event, known, body) for name, (timing, event, body) in migration.TRIGGERS.items())
        if 'information_schema.KEY_COLUMN_USAGE' in sql:
            return SimpleNamespace(first=lambda: (1,) if fault == 'references' else None)
        if 'information_schema.VIEW_TABLE_USAGE' in sql:
            return SimpleNamespace(first=lambda: None)
        if sql.startswith('RENAME TABLE'):
            renamed = True
        return Rows()

    conn = SimpleNamespace(dialect=SimpleNamespace(name='mysql'), execute=execute)
    monkeypatch.setattr(migration, 'context', SimpleNamespace(is_offline_mode=lambda: False))
    monkeypatch.setattr(migration, 'op', SimpleNamespace(
        get_context=lambda: SimpleNamespace(autocommit_block=nullcontext), get_bind=lambda: conn))
    monkeypatch.setenv('ACQ_TABLE_NAMES_EXPECTED_SCHEMA', TARGET['schema'])
    monkeypatch.setenv('ACQ_TABLE_NAMES_EXPECTED_SERVER_UUID', TARGET['serverUuid'])
    monkeypatch.setenv('ACQ_TABLE_NAMES_WINDOW_CONFIRMED',
                       f"{TARGET['schema']}:{TARGET['serverUuid']}:{migration.down_revision}")

    if fault is None:
        migration.upgrade()
    else:
        with pytest.raises(RuntimeError):
            migration.upgrade()
    expected_rename = fault in (None, 'post_trigger')
    assert renamed is expected_rename
    assert calls[-1] == 'SELECT RELEASE_LOCK(:name)'
    if expected_rename:
        (ddl,) = [call for call in calls if call.startswith('RENAME TABLE')]
        assert ddl.count(' TO ') == 3
        assert calls.index('SELECT version_num FROM alembic_version FOR UPDATE') < calls.index(ddl)
        assert calls.index('SELECT ready FROM acq_consumption_activation WHERE id = 1 FOR UPDATE') < calls.index(ddl)
