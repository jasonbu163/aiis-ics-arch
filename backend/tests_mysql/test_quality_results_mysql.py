"""质量迁移和并发写的显式隔离 MySQL 8.4 验证。"""
import asyncio
import os
from pathlib import Path

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

BEFORE = "e9f3b5d7c021"
AFTER = "f0a2b4c6d8e1"
BACKEND = Path(__file__).resolve().parents[1]


@pytest.fixture
def disposable_target(monkeypatch):
    required = ['QUALITY_FIXTURE_UUID', 'QUALITY_FIXTURE_PORT', 'QUALITY_FIXTURE_SCHEMA',
                'QUALITY_FIXTURE_USER', 'QUALITY_FIXTURE_PASSWORD', 'QUALITY_FIXTURE_ACK']
    if any(not os.environ.get(key) for key in required):
        pytest.skip('requires an explicitly provisioned disposable ARCH-QUALITY-001 MySQL target')
    uid, port, schema, user, password, ack = (os.environ[key] for key in required)
    if (port not in {'13411', '13412'} or schema != f'arch_quality_fixture_{port}'
            or user != 'quality_fixture' or ack != f'ARCH-QUALITY-001:{uid}:{port}:{schema}'):
        raise RuntimeError('fixture target identity rejected')
    url = URL.create('mysql+pymysql', username=user, password=password, host='127.0.0.1',
                     port=int(port), database=schema)
    engine = create_engine(url, connect_args={'connect_timeout': 3})
    config = Config(str(BACKEND / 'alembic.ini'))
    config.set_main_option('script_location', str(BACKEND / 'alembic'))
    scripts = ScriptDirectory.from_config(config)
    try:
        with engine.begin() as db:
            version, actual_uid, actual_schema, current_user, offset = db.execute(text(
                'SELECT VERSION(), @@server_uuid, DATABASE(), CURRENT_USER(), '
                'TIMESTAMPDIFF(SECOND,UTC_TIMESTAMP(6),CURRENT_TIMESTAMP(6))')).one()
            if (not str(version).startswith('8.4.') or actual_uid != uid or actual_schema != schema
                    or current_user.split('@')[0] != user or offset != 28800
                    or inspect(db).get_table_names()):
                raise RuntimeError('fixture must be an empty, disposable, matching MySQL 8.4 schema')

            db.execute(text("CREATE TABLE synthetic_predecessor_data (id INT PRIMARY KEY, label VARCHAR(32))"))
            db.execute(text("INSERT INTO synthetic_predecessor_data VALUES (1, 'preserved')"))
            MigrationContext.configure(db).stamp(scripts, BEFORE)

        monkeypatch.setenv('QUALITY_EXPECTED_SCHEMA', schema)
        monkeypatch.setenv('QUALITY_EXPECTED_SERVER_UUID', uid)
        for _ in range(2):
            with engine.begin() as db:
                with EnvironmentContext(config, scripts, fn=lambda rev, _: scripts._upgrade_revs(AFTER, rev)) as env:
                    env.configure(connection=db)
                    env.run_migrations()

        with engine.connect() as db:
            assert db.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == AFTER
            assert db.execute(text("SELECT label FROM synthetic_predecessor_data")).scalar_one() == 'preserved'
            assert db.execute(text("SELECT revision FROM quality_field_config WHERE id=1")).scalar_one() == 1
            assert inspect(db).get_foreign_keys("quality_main") == []
            assert inspect(db).get_foreign_keys("quality_field_config") == []
            assert {row[0]: row[1] for row in db.execute(text(
                "SELECT COLUMN_NAME, COLUMN_TYPE FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='quality_main'"
            ))}['created_at'] == 'datetime(6)'
        yield url.set(drivername='mysql+aiomysql')
    finally:
        engine.dispose()


@pytest.mark.asyncio
async def test_migrated_quality_unique_keys_and_concurrent_updates(disposable_target):
    from app.quality.schemas.results import ConfigSnapshot
    from app.quality.services.results import save_config
    from core.registrar import create_app
    from database import get_db

    candidate = create_async_engine(disposable_target)
    session = async_sessionmaker(candidate, expire_on_commit=False, autoflush=False)

    async def private_db():
        async with session() as db:
            yield db

    app = create_app(testing=True)
    app.dependency_overrides[get_db] = private_db
    try:
        async with session() as db:
            await save_config(db, ConfigSnapshot.model_validate({"revision": 1, "definitions": [
                {"name": name, "labels": {"zh-CN": name, "en-US": name}, "type": kind}
                for name, kind in [('defects', 'number'), ('reviewed', 'boolean')]
            ]}))
            await db.commit()
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://fixture') as client:
            path = '/api/v1/integration/quality'
            responses = await asyncio.gather(*[
                client.post(path + '/upsert', json={"taskNo": task, "items": values})
                for task, values in [(' local-1 ', {'defects': 0}), ('LOCAL-1', {'reviewed': False})]
            ])
            for response in responses:
                assert response.status_code == 200, response.text
            assert {r.json()['data']['outcome'] for r in responses} == {'created', 'updated'}
            response = await client.get(path + '/by-task/local-1')
            assert response.json()['data']['items'] == {'defects': 0, 'reviewed': False}
            assert response.json()['data']['createdAt'].endswith('+08:00')
            assert (await client.get(path)).json()['data']['total'] == 1
    finally:
        await candidate.dispose()
