"""Shared pytest fixtures for the public Core backend tests."""

from __future__ import annotations

import os

os.environ.setdefault("TESTING", "True")
os.environ.setdefault("DATABASE_TYPE", "mysql")
os.environ.setdefault("TEST_MYSQL_DATABASE", "aiis_ics_architecture_test")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.module_registry import import_model_packages
from app.user.models.user import User
from common.log import setup_logger
from core.registrar import create_app
from core.security import hash_password
from database import Base, SyncSessionLocal, get_db
from settings import settings


import_model_packages()

test_async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
)
test_session_maker = async_sessionmaker(
    bind=test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


def ensure_test_database() -> None:
    """Allow destructive setup only for an explicitly separate MySQL test DB."""
    database_name = settings.TEST_MYSQL_DATABASE.strip()
    primary_database_name = settings.MYSQL_DATABASE.strip()
    if not settings.TESTING or settings.primary_database != "mysql":
        raise RuntimeError("Destructive test database setup is only permitted for MySQL test runs")
    if not database_name:
        raise RuntimeError("TEST_MYSQL_DATABASE must be configured for destructive test database setup")
    if database_name.casefold() == primary_database_name.casefold():
        raise RuntimeError("TEST_MYSQL_DATABASE must differ from MYSQL_DATABASE before destructive cleanup")

    root_engine = create_engine(settings.ROOT_DATABASE_URL, pool_pre_ping=True)
    mysql_user = settings.MYSQL_USER
    mysql_password = settings.MYSQL_PASSWORD.replace("'", "\'")
    with root_engine.connect() as conn:
        conn.execute(
            text(
                "CREATE DATABASE IF NOT EXISTS " + database_name
                + " CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        conn.execute(
            text(
                "CREATE USER IF NOT EXISTS '" + mysql_user
                + "'@'%' IDENTIFIED BY '" + mysql_password + "'"
            )
        )
        conn.execute(
            text(
                "GRANT ALL PRIVILEGES ON " + database_name
                + ".* TO '" + mysql_user + "'@'%'"
            )
        )
        conn.execute(text("FLUSH PRIVILEGES"))
        conn.commit()
    root_engine.dispose()


def _drop_existing_tables(connection) -> None:
    preparer = connection.dialect.identifier_preparer
    for table_name in inspect(connection).get_table_names():
        connection.exec_driver_sql(
            "DROP TABLE IF EXISTS " + preparer.quote(table_name)
        )


@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_test_database(request):
    if request.node.get_closest_marker("no_db"):
        yield
        return

    ensure_test_database()
    async with test_async_engine.begin() as conn:
        await conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        try:
            await conn.run_sync(_drop_existing_tables)
        finally:
            await conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_session_maker() as session:
        await session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        session.add(
            User(
                username="admin",
                password=hash_password("admin123"),
                name="Administrator",
                role="admin",
                is_active=True,
            )
        )
        await session.commit()
        yield session


@pytest.fixture(scope="function")
def sync_db_session():
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest_asyncio.fixture(scope="function")
async def test_client(db_session: AsyncSession):
    app = create_app(testing=True)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost:8000",
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_token(test_client: AsyncClient):
    response = await test_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["data"]["accessToken"]


@pytest_asyncio.fixture(scope="function")
async def auth_headers(auth_token: str):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(autouse=True)
def reset_test_logger():
    yield
    setup_logger("api")
