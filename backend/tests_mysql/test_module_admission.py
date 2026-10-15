"""B阶段显式MySQL接入入口；仅获具体动作批准后在独立E副本执行，无共享conftest。"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace


class DisposableTarget:
    """拒绝默认库、非公开fixture及未逐库确认的目标；不创建/删除数据库。"""

    def __init__(self, scenario):
        root = Path.cwd().resolve()
        assert (root / "profile.json").is_file(), "Run only from a generated public profile"
        assert not (root / ".env").exists(), "Real .env is prohibited"
        profile = json.loads((root / "profile.json").read_text())["profile"]
        assert profile == ("E" if scenario.startswith("e") else "F")
        assert os.environ.get("ARCH_BE005_ALLOW_MYSQL") == "I_CONFIRM_DISPOSABLE"
        database = os.environ["TEST_MYSQL_DATABASE"]
        names = {"e1": "be005_admission_e1_proof", "e2": "be005_admission_e2_proof", "f_empty": "be005_reintegration_proof", "f_upgrade": "be005_existing_head_proof", "f_rehearsal": "be005_rehearsal_proof"}
        assert database == names[scenario]
        assert os.environ.get("ARCH_BE005_ACK_DATABASE") == database
        assert database != os.environ["MYSQL_DATABASE"]
        assert os.environ.get("BACKEND_MOCK_ENABLED", "").lower() == "false"
        assert os.environ.get("PROJECTION_RUNNER_ENABLED", "").lower() == "false"
        assert os.environ.get("TESTING", "").lower() == "true"
        assert os.environ.get("MYSQL_HOST") == "127.0.0.1"
        assert os.environ.get("ARCH_BE005_ACK_ENDPOINT") == "127.0.0.1:" + os.environ["MYSQL_PORT"]
        for key in ("ADMIN_BOOTSTRAP_ENABLED", "SUPERVISOR_BOOTSTRAP_ENABLED", "OPERATOR_BOOTSTRAP_ENABLED"):
            assert os.environ.get(key, "").lower() == "false"
        import settings as configuration
        assert Path(configuration.__file__).resolve().parent == root
        settings = configuration.settings
        from sqlalchemy import create_engine, inspect
        assert settings.primary_database == "mysql" and settings.TEST_MYSQL_DATABASE == database
        self.root, self.database = root, database
        self.engine = create_engine(settings.SYNC_DATABASE_URL, pool_pre_ping=True)
        with self.engine.connect() as connection:
            actual, version = connection.exec_driver_sql("SELECT DATABASE(), VERSION()").one()
            assert actual == database and str(version).split("-")[0] == "8.4.6"
            assert not inspect(connection).get_table_names(), "The approved target must start empty"

    def migrate(self, revision, direction="upgrade"):
        # Credentials remain in the process environment; never written to a command or evidence file.
        subprocess.run([sys.executable, "-m", "alembic", direction, revision], cwd=self.root, check=True)

    def checksum(self, names):
        from sqlalchemy import MetaData, Table, select
        result = {}
        with self.engine.connect() as connection:
            for name in sorted(names):
                table = Table(name, MetaData(), autoload_with=connection)
                rows = sorted([tuple(map(str, row)) for row in connection.execute(select(table))])
                result[name] = hashlib.sha256(json.dumps(rows).encode()).hexdigest()
        return result

    def assert_schema(self):
        """逐表列/PK/FK/唯一约束/check/index对照；不调用metadata.create_all。"""
        from sqlalchemy import inspect, UniqueConstraint, CheckConstraint
        from sqlalchemy.dialects import mysql
        from database import Base
        from app.module_registry import import_model_packages
        import_model_packages()
        from app.user.models.token_blacklist import TokenBlacklist
        inspector = inspect(self.engine)
        assert set(inspector.get_table_names()) == set(Base.metadata.tables) | {"alembic_version"}
        for name, table in Base.metadata.tables.items():
            actual = inspector.get_columns(name)
            assert [column["name"] for column in actual] == list(table.columns.keys()), name
            for column, expected in zip(actual, table.columns):
                def normalized(value):
                    text = str(value).upper().replace("INTEGER", "INT")
                    return "TINYINT(1)" if text in {"BOOL", "BOOLEAN"} else text
                assert normalized(column["type"].compile(dialect=mysql.dialect())) == normalized(expected.type.compile(dialect=mysql.dialect())), (name, expected.name)
                assert column["nullable"] == expected.nullable, (name, expected.name)
            assert inspector.get_pk_constraint(name)["constrained_columns"] == [c.name for c in table.primary_key]
            expected_fk = {(tuple(fk.parent.name for fk in constraint.elements), tuple(fk.column.table.name for fk in constraint.elements), tuple(fk.column.name for fk in constraint.elements)) for constraint in table.foreign_key_constraints}
            actual_fk = {(tuple(fk["constrained_columns"]), tuple([fk["referred_table"]] * len(fk["referred_columns"])), tuple(fk["referred_columns"])) for fk in inspector.get_foreign_keys(name)}
            assert actual_fk == expected_fk, name
            expected_unique = {tuple(c.name for c in constraint.columns) for constraint in table.constraints if isinstance(constraint, UniqueConstraint)}
            assert {tuple(c["column_names"]) for c in inspector.get_unique_constraints(name)} == expected_unique, name
            actual_indexes = {index["name"]: (tuple(index["column_names"]), bool(index["unique"])) for index in inspector.get_indexes(name)}
            for index in table.indexes:
                assert actual_indexes[index.name] == (tuple(c.name for c in index.columns), index.unique), (name, index.name)
            expected_checks = {constraint.name for constraint in table.constraints if isinstance(constraint, CheckConstraint)}
            assert {constraint["name"] for constraint in inspector.get_check_constraints(name)} == expected_checks, name

    def api(self):
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from settings import settings
        from core.registrar import create_app
        from core.deps import get_current_user
        from database import get_db
        engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        app = create_app(testing=True)
        async def get_session():
            async with sessions() as session:
                yield session
        app.dependency_overrides[get_db] = get_session
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=1, role="admin", username="disposable")
        return app, engine, sessions


def test_explicit_mysql_e_admission():
    """E1/E2空库迁移、真实独立session API、唯一/FK、错误/权限、失败回滚及并发。"""
    scenario = os.environ["ARCH_BE005_MYSQL_SCENARIO"]
    assert scenario in {"e1", "e2"}
    target = DisposableTarget(scenario)
    try:
        target.migrate("head")
        target.assert_schema()
        core_tables = set(json.loads((target.root / "profile.json").read_text())["tables"])
        from sqlalchemy.orm import Session
        from app.user.models.user import User
        with Session(target.engine) as session:
            session.add(User(id=1, username="core-preservation", password="synthetic-not-a-login-hash", name="Core fixture", role="admin", is_active=True))
            session.commit()
        before = target.checksum(core_tables)
        async def run():
            from httpx import ASGITransport, AsyncClient
            from sqlalchemy.exc import IntegrityError
            from core.deps import get_current_user
            from core.role_permissions import build_role_api_permissions
            from app.module_registry import get_module_manifests
            from app.admission_probe.schemas import ItemCreate
            from app.admission_probe.services import async_item as service
            app, engine, sessions = target.api()
            try:
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://disposable") as client:
                    saved = await client.post("/api/v1/admission-probe/items", json={"itemLabel": "real"})
                    assert saved.status_code == 200
                    row = saved.json()["data"]
                    assert row["itemLabel"] == "real"
                    assert (await client.get("/api/v1/admission-probe/items")).json()["data"] == [row]
                    error = (await client.post("/api/v1/admission-probe/items", json={"itemLabel": " "})).json()
                    assert error["errorCode"] == "admission_probe.invalid_value"
                    if scenario == "e2":
                        summary = await client.post("/api/v1/admission-summary/items", json={"itemLabel": "summary", "probeId": row["id"]})
                        assert summary.status_code == 200 and summary.json()["data"]["probeState"] == "active"
                        assert (await client.get("/api/v1/admission-summary/items")).json()["data"] == [summary.json()["data"]]
                        from app.admission_summary.schemas import ItemCreate as SummaryCreate
                        from app.admission_summary.services import async_item as summary_service
                        async with sessions() as session:
                            try:
                                await summary_service.create_item(session, SummaryCreate(item_label="bad-fk", probe_id=999999))
                            except IntegrityError:
                                assert not session.in_transaction()
                            else:
                                raise AssertionError("FK must reject missing provider row")
                    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role="supervisor", username="disposable")
                    for grants in ([], ["unknown"]):
                        app.state.role_api_permissions = build_role_api_permissions(json.dumps(grants), "[]", get_module_manifests(), warn=lambda **kw: None)
                        assert (await client.get("/api/v1/admission-probe/items")).status_code == 403
                    app.state.role_api_permissions = build_role_api_permissions('["admission_probe-read"]', "[]", get_module_manifests(), warn=lambda **kw: None)
                    assert (await client.get("/api/v1/admission-probe/items")).status_code == 200
                    assert (await client.post("/api/v1/admission-probe/items", json={"itemLabel": "denied"})).status_code == 403
                async def insert_same():
                    async with sessions() as session:
                        try:
                            await service.create_item(session, ItemCreate(item_label="concurrent"))
                            return "saved"
                        except IntegrityError:
                            assert not session.in_transaction()
                            return "rolled_back"
                assert sorted(await asyncio.gather(insert_same(), insert_same())) == ["rolled_back", "saved"]
                async with sessions() as session:
                    assert sorted(item.item_label for item in await service.list_items(session)) == ["concurrent", "real"]
            finally:
                await engine.dispose()
        asyncio.run(run())
        assert target.checksum(core_tables) == before
    finally:
        target.engine.dispose()
