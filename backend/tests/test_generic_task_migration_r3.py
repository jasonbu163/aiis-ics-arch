"""后继迁移历史审计与显式停止条件的无库验证。"""
from types import SimpleNamespace

from alembic.config import Config
from alembic.script import ScriptDirectory
import pytest

pytestmark = pytest.mark.no_db


@pytest.fixture
def migration():
    graph = ScriptDirectory.from_config(Config('alembic.ini'))
    assert graph.get_heads() == ['e9f3b5d7c021']
    assert graph.get_revision('ae20b4d6f831').down_revision == '9d1f3a5c7e20'
    return graph.get_revision('ae20b4d6f831').module


class Rows(list):
    def scalars(self):
        return self

    def all(self):
        return self

    def first(self):
        return self[0] if self else None


def audit_fixture(migration, monkeypatch, case=None):
    def execute(_connection, sql, **_params):
        if 'SELECT active_version' in sql:
            return Rows([2])
        if 'FROM task_field_definitions' in sql:
            return Rows([] if case == 'missing-version' else [
                (2,'shared_sync',1,'length','number','m'), (2,'performance_local',2,'ready','boolean',None)])
        if 'SELECT task_no' in sql:
            if 'FROM plan_main' in sql:
                return Rows([('A','Demo',None,2,'{"01":"0"}','{}')])
            return Rows([('A','Demo','completed',2,'{}',
                          '{"02":"unknown"}' if case == 'wrong-slot-type' else '{"02":"false"}')])
        if 'WHERE plan.target_key <>' in sql:
            return Rows([1] if case == 'conflicting-targets' else [])
        if 'SELECT dispatch_id' in sql:
            return Rows([('00000000-0000-4000-8000-000000000001',5 if case == 'missing-dispatch-version' else 2)])
        if 'FROM plan_action_events' in sql:
            return Rows([1] if case == 'dangling-action' else [])
        raise AssertionError(sql)
    monkeypatch.setattr(migration, '_execute', execute)


def test_history_counts_keep_empty_version_and_used_fields(migration, monkeypatch):
    audit_fixture(migration, monkeypatch)
    assert migration._history(object()) == {1:0,2:2}
    assert 'WHERE plan.production_status IS NULL' in migration.FILL_STATUS
    assert 'SET plan.production_status = COALESCE(perf.production_status, \'new\')' in migration.FILL_STATUS
    assert 'updated_at' not in migration.FILL_STATUS


@pytest.mark.parametrize('case,reason', [
    ('missing-version','definition version'),
    ('wrong-slot-type','slot or type'),
    ('conflicting-targets','targets conflict'),
    ('missing-dispatch-version','dispatch'),
    ('dangling-action','unknown dispatch'),
])
def test_uncertain_history_refuses_before_any_ddl(migration, monkeypatch, case, reason):
    audit_fixture(migration, monkeypatch, case)
    with pytest.raises(RuntimeError, match=reason):
        migration._history(object())


def test_offline_and_downgrade_refuse(migration, monkeypatch):
    monkeypatch.setattr(migration, 'context', SimpleNamespace(is_offline_mode=lambda: True))
    with pytest.raises(RuntimeError, match='online'):
        migration.upgrade()
    with pytest.raises(RuntimeError, match='forward-only'):
        migration.downgrade()
