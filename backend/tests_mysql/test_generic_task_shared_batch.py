"""隔离 MySQL 8.4.6 验证共享及本地字段 HTTP、锁竞争和回滚。"""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from secrets import token_hex
from types import SimpleNamespace
from uuid import UUID
import os

import pytest

KEYS = ('ROLE', 'PORT', 'SERVER_UUID', 'PASSWORD_FILE', 'EXECUTION_ACK')


def isolated_settings(task):
    values = [os.environ.get(f'TASK{task}_TEST_{key}') for key in KEYS]
    if not all(values):
        return None
    role, port, server, password_file, ack = values
    if (role not in ('dev', 'qa') or not port.isdecimal() or not 20000 <= int(port) <= 65535
            or str(UUID(server)) != server or ack != f'ARCH-TASK-{task}-r1:{role}:127.0.0.1:{port}:{server}'):
        raise RuntimeError(f'unconfirmed ARCH-TASK-{task} MySQL server identity')
    return role, int(port), server, password_file


SETTINGS = {task: isolated_settings(task) for task in ('002', '003')}
if not any(SETTINGS.values()):
    pytest.skip('requires a dedicated ARCH-TASK-002/003 MySQL fixture', allow_module_level=True)

import httpx
import pymysql
import pytest_asyncio
from fastapi import FastAPI, Request
from sqlalchemy import select, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.performance.api.routes import router as performance_router
from app.performance.models import Performance
from app.plan.api.routes import router as plan_router
from app.plan.models.plan import DispatchAttempt, Plan
from app.task.api.routes import router as task_router
from app.task.models import FieldConfigState, FieldConfigUse, FieldConfigVersion, FieldDefinition
from core.deps import get_current_user
from database import get_db

CONFIG = '/api/v1/task-field-configs'
BATCH = CONFIG + '/batch-delete'


def identity(slot, name):
    return {'scope': 'shared_sync', 'slotNo': slot, 'name': name}


def definition(slot, name):
    return {**identity(slot, name), 'type': 'string', 'enabled': True, 'planEditable': True,
            'performanceOwner': 'automated', 'labels': {'zh-CN': name, 'en-US': name}}


@asynccontextmanager
async def isolated_fixture(task):
    if SETTINGS[task] is None:
        pytest.skip(f'requires the dedicated ARCH-TASK-{task} MySQL fixture')
    role, port, target_server, password_file = SETTINGS[task]
    password = Path(password_file).read_text().rstrip('\r\n')
    root = pymysql.connect(host='127.0.0.1', port=port, user='root', password=password,
                           autocommit=True, connect_timeout=5)
    schema = f'task{task}_{role}_{token_hex(8)}'
    created = False
    engine = None
    try:
        with root.cursor() as cursor:
            cursor.execute('SELECT @@server_uuid, VERSION(), TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(), CURRENT_TIMESTAMP())')
            server, version, offset = cursor.fetchone()
            if server != target_server or version != '8.4.6' or offset != 28800:
                raise RuntimeError(f'ARCH-TASK-{task} MySQL server UUID, version or clock mismatch')
            cursor.execute(f'CREATE DATABASE `{schema}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
            created = True
        engine = create_async_engine(URL.create('mysql+aiomysql', username='root', password=password,
                                                host='127.0.0.1', port=port, database=schema))
        maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
        async with engine.begin() as connection:
            for model in (FieldConfigState, FieldConfigVersion, FieldDefinition, FieldConfigUse, Plan, Performance, DispatchAttempt):
                await connection.run_sync(model.__table__.create)
        async with maker.begin() as session:
            session.add_all([FieldConfigState(id=1), FieldConfigVersion(config_version=1, definition_count=0)])
        prepared = asyncio.Event()
        release = asyncio.Event()

        async def test_session(request: Request):
            async with maker() as session:
                try:
                    native_commit = session.commit
                    async def controlled_commit():
                        if request.headers.get('x-fixture') == 'precommit-failure':
                            await session.rollback()
                            raise RuntimeError('injected before physical commit')
                        if request.headers.get('x-fixture') == 'hold' and not prepared.is_set():
                            prepared.set()
                            await asyncio.wait_for(release.wait(), 15)
                        await native_commit()
                    session.commit = controlled_commit
                    yield session
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise

        app = FastAPI()
        for router in (task_router, plan_router, performance_router):
            app.include_router(router, prefix='/api/v1')
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=1, role='admin')
        app.dependency_overrides[get_db] = test_session
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://fixture') as http:
            yield SimpleNamespace(http=http, maker=maker, prepared=prepared, release=release, schema=schema)
    finally:
        if engine:
            await engine.dispose()
        if created:
            with root.cursor() as cursor:
                cursor.execute(f'DROP DATABASE `{schema}`')
        root.close()


@pytest_asyncio.fixture
async def mysql_http():
    async with isolated_fixture('002') as fixture:
        yield fixture


@pytest_asyncio.fixture
async def mysql_local_http():
    async with isolated_fixture('003') as fixture:
        yield fixture


def result(response):
    assert response.status_code == 200, response.text
    return response.json()['data']


async def request(factory, method, path, body=None, *, hold=False):
    return await factory.http.request(method, path, json=body, headers={'x-fixture': 'hold'} if hold else {})


async def wait_for_config_lock(factory):
    query = text("""
        SELECT 1
        FROM performance_schema.data_lock_waits waits
        JOIN performance_schema.data_locks requested ON requested.ENGINE_LOCK_ID = waits.REQUESTING_ENGINE_LOCK_ID
        WHERE requested.OBJECT_SCHEMA = :schema AND requested.OBJECT_NAME = 'task_field_config_state'
        LIMIT 1
    """)
    async with factory.maker() as session:
        for _ in range(100):
            if (await session.execute(query, {'schema': factory.schema})).first():
                return
            await asyncio.sleep(.04)
    pytest.fail('contender did not reach a real configuration row lock wait')


@pytest.mark.parametrize('other', ['plan', 'performance', 'plan_update', 'performance_update', 'save', 'single'])
@pytest.mark.parametrize('batch_first', [True, False])
async def test_batch_delete_serializes_against_field_writers(mysql_http, other, batch_first):
    fx = mysql_http
    subject = other.removesuffix('_update')
    task_writer = subject in ('plan', 'performance')
    if task_writer:
        path = 'plans' if subject == 'plan' else 'performances'
        upsert = f'/api/v1/integration/{path}/upsert'
        if other.endswith('_update'):
            result(await request(fx, 'POST', upsert, {'taskNo':'TASK'}))
    configured = result(await request(fx, 'PUT', CONFIG, {
        'module':'shared', 'configRevision':'1',
        'changes':[definition(1, 'first'), definition(2, 'second'), definition(3, 'third')],
    }))
    revision = configured['configRevision']
    batch = ('POST', BATCH, {'configRevision':revision, 'fields':[identity(1,'first'), identity(2,'second')]})
    if task_writer:
        competitor = ('POST', upsert, {'taskNo':'TASK', 'items':{'first':'value'}})
    elif other == 'save':
        competitor = ('PUT', CONFIG, {'module':'shared','configRevision':revision,'changes':[definition(4,'fourth')]})
    else:
        competitor = ('POST', CONFIG+'/delete', {**identity(3,'third'), 'configRevision':revision})
    initial, later = (batch, competitor) if batch_first else (competitor, batch)
    leader = asyncio.create_task(request(fx, *initial, hold=True))
    follower = None
    try:
        await asyncio.wait_for(fx.prepared.wait(), 7)
        follower = asyncio.create_task(request(fx, *later))
        await wait_for_config_lock(fx)
    finally:
        fx.release.set()
        leading_response = await asyncio.wait_for(leader, 12)
        if follower:
            following_response = await asyncio.wait_for(follower, 12)
    result(leading_response)
    final = result(await fx.http.get(CONFIG, params={'module':'plan'}))
    names = [field['name'] for field in final['fields']]
    if batch_first:
        assert names == ['third']
        assert final['configVersion'] == configured['configVersion'] + 1
        assert following_response.status_code == (422 if task_writer else 409)
    else:
        assert names == {
            'plan':['first','second','third'], 'performance':['first','second','third'],
            'save':['first','second','third','fourth'], 'single':['first','second'],
        }[subject]
        assert following_response.status_code == 409
        assert following_response.json()['errorCode'] == ('task.field_in_use' if task_writer
                                                          else 'task.config_revision_conflict')
        if task_writer:
            async with fx.maker() as session:
                use = await session.scalar(select(FieldConfigUse).where(FieldConfigUse.subject_kind == subject,
                    FieldConfigUse.config_version == configured['configVersion']))
                assert use.subject_key == 'TASK'
    assert final['configRevision'] == str(int(revision) + (other in ('save','single') or batch_first))


async def test_batch_delete_rollback_before_physical_commit(mysql_http):
    fx = mysql_http
    initial = result(await request(fx, 'PUT', CONFIG, {
        'module':'shared','configRevision':'1','changes':[definition(1,'first'),definition(2,'second')],
    }))
    payload = {'configRevision':initial['configRevision'],'fields':[identity(1,'first'),identity(2,'second')]}
    failed = await fx.http.post(BATCH, json=payload, headers={'x-fixture':'precommit-failure'})
    assert failed.status_code == 503 and failed.json()['errorCode'] == 'task.commit_unknown'
    assert result(await fx.http.get(CONFIG, params={'module':'plan'})) == initial
    async with fx.maker() as session:
        assert await session.get(FieldConfigVersion, initial['configVersion'] + 1) is None
        assert list((await session.scalars(select(FieldDefinition.name).where(
            FieldDefinition.config_version == initial['configVersion']).order_by(FieldDefinition.slot_no))).all()) == ['first','second']


LOCAL_BATCH = CONFIG + '/local/batch-delete'


def local_item(module, slot, name):
    return {**identity(slot, name), 'scope': f'{module}_local'}


def local_definition(module, slot, name):
    document = definition(slot, name)
    if module == 'plan':
        del document['performanceOwner']
    else:
        del document['planEditable']
    return {**document, **local_item(module, slot, name)}


@pytest.mark.parametrize('module', ('plan', 'performance'))
@pytest.mark.parametrize('other', ('create', 'update', 'save', 'single', 'shared', 'other_local'))
@pytest.mark.parametrize('batch_first', (True, False))
async def test_local_batch_delete_serializes_against_field_writers(mysql_local_http, module, other, batch_first):
    fx = mysql_local_http
    other_module = 'performance' if module == 'plan' else 'plan'
    upsert = f"/api/v1/integration/{'plans' if module == 'plan' else 'performances'}/upsert"
    task_writer = other in ('create', 'update')
    if other == 'update':
        result(await request(fx, 'POST', upsert, {'taskNo': 'TASK'}))

    async def configure(name, revision, changes):
        return result(await request(fx, 'PUT', CONFIG, {
            'module': name, 'configRevision': revision, 'changes': changes,
        }))

    shared = await configure('shared', '1', [definition(1, 'sharedField')])
    other_local = await configure(other_module, shared['configRevision'], [local_definition(other_module, 1, 'first')])
    configured = await configure(module, other_local['configRevision'], [
        local_definition(module, 1, 'first'), local_definition(module, 2, 'second'), local_definition(module, 3, 'third'),
    ])
    revision = configured['configRevision']
    batch = ('POST', LOCAL_BATCH, {'module': module, 'configRevision': revision,
                                  'fields': [local_item(module, 1, 'first'), local_item(module, 2, 'second')]})
    if task_writer:
        competitor = ('POST', upsert, {'taskNo': 'TASK', 'items': {'first': 'value'}})
    elif other == 'save':
        competitor = ('PUT', CONFIG, {'module': module, 'configRevision': revision,
                                      'changes': [local_definition(module, 4, 'fourth')]})
    elif other == 'single':
        competitor = ('POST', CONFIG + '/delete', {**local_item(module, 3, 'third'), 'configRevision': revision})
    elif other == 'shared':
        competitor = ('POST', BATCH, {'configRevision': revision, 'fields': [identity(1, 'sharedField')]})
    else:
        competitor = ('POST', LOCAL_BATCH, {'module': other_module, 'configRevision': revision,
                                           'fields': [local_item(other_module, 1, 'first')]})
    initial, later = (batch, competitor) if batch_first else (competitor, batch)
    leader = asyncio.create_task(request(fx, *initial, hold=True))
    follower = None
    try:
        await asyncio.wait_for(fx.prepared.wait(), 7)
        follower = asyncio.create_task(request(fx, *later))
        await wait_for_config_lock(fx)
    finally:
        fx.release.set()
        leading_response = await asyncio.wait_for(leader, 12)
        if follower:
            following_response = await asyncio.wait_for(follower, 12)
    result(leading_response)
    final = result(await fx.http.get(CONFIG, params={'module': module}))
    final_other = result(await fx.http.get(CONFIG, params={'module': other_module}))
    names = [row['name'] for row in final['fields'] if row['scope'] == f'{module}_local']
    other_names = [row['name'] for row in final_other['fields'] if row['scope'] == f'{other_module}_local']
    shared_names = [row['name'] for row in final['fields'] if row['scope'] == 'shared_sync']
    if batch_first:
        assert names == ['third']
        assert following_response.status_code == (422 if task_writer else 409)
    else:
        assert names == {
            'create': ['first', 'second', 'third'], 'update': ['first', 'second', 'third'],
            'save': ['first', 'second', 'third', 'fourth'], 'single': ['first', 'second'],
            'shared': ['first', 'second', 'third'], 'other_local': ['first', 'second', 'third'],
        }[other]
        assert following_response.status_code == 409
        assert following_response.json()['errorCode'] == ('task.field_in_use' if task_writer
                                                          else 'task.config_revision_conflict')
        if task_writer:
            async with fx.maker() as session:
                use = await session.scalar(select(FieldConfigUse).where(FieldConfigUse.subject_kind == module,
                    FieldConfigUse.config_version == configured['configVersion']))
                assert use.subject_key == 'TASK'
    assert other_names == ([] if not batch_first and other == 'other_local' else ['first'])
    assert shared_names == ([] if not batch_first and other == 'shared' else ['sharedField'])
    generations = int(batch_first or not task_writer)
    assert final['configVersion'] == configured['configVersion'] + generations
    assert final['configRevision'] == str(int(revision) + generations)


@pytest.mark.parametrize('module', ('plan', 'performance'))
async def test_local_batch_rollback_before_physical_commit(mysql_local_http, module):
    fx = mysql_local_http
    initial = result(await request(fx, 'PUT', CONFIG, {
        'module': module, 'configRevision': '1',
        'changes': [local_definition(module, 1, 'first'), local_definition(module, 2, 'second')],
    }))
    payload = {'module': module, 'configRevision': initial['configRevision'],
               'fields': [local_item(module, 1, 'first'), local_item(module, 2, 'second')]}
    failed = await fx.http.post(LOCAL_BATCH, json=payload, headers={'x-fixture': 'precommit-failure'})
    assert failed.status_code == 503 and failed.json()['errorCode'] == 'task.commit_unknown'
    assert result(await fx.http.get(CONFIG, params={'module': module})) == initial
    async with fx.maker() as session:
        assert await session.get(FieldConfigVersion, initial['configVersion'] + 1) is None
