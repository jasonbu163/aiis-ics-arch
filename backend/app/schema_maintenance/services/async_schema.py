"""
文件路径: /backend/app/schema_maintenance/services/async_schema.py
功能描述: Schema maintenance create-missing-tables Service
主要功能:
    - 检查当前 registered model metadata 与目标数据库表状态
    - 仅创建缺失整表，跳过已存在同名表
    - 记录脱敏结构化维护事件
"""
from __future__ import annotations

from enum import StrEnum
from typing import Any

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.module_registry import import_model_packages
from app.schema_maintenance.schemas.schema_maintenance import (
    SchemaMaintenanceActionOut,
    SchemaMaintenanceDatabaseIdentity,
    SchemaMaintenanceStatusOut,
)
from common.exceptions import BusinessException
from common.log import log_event
from database import Base
from settings import settings


DRIFT_WARNING = "existing_table_drift_not_checked"


class SchemaMaintenanceErrorCode(StrEnum):
    """Schema maintenance 稳定业务错误码。"""

    SCHEMA_MAINTENANCE_STATUS_FAILED = "schema_maintenance_status_failed"
    SCHEMA_MAINTENANCE_ACTION_FAILED = "schema_maintenance_action_failed"


class SchemaMaintenanceRequestedAction(StrEnum):
    """Schema maintenance 写库动作语义。"""

    INITIALIZE = "initialize"
    UPGRADE = "upgrade"


def _database_identity() -> SchemaMaintenanceDatabaseIdentity:
    primary_database = settings.primary_database
    if primary_database == "mysql":
        database = settings.TEST_MYSQL_DATABASE if settings.TESTING else settings.MYSQL_DATABASE
        return SchemaMaintenanceDatabaseIdentity(
            primary_database=primary_database,
            dialect="mysql",
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            database=database,
        )
    if primary_database == "postgresql":
        return SchemaMaintenanceDatabaseIdentity(
            primary_database=primary_database,
            dialect="postgresql",
            host=settings.postgres_host,
            port=settings.postgres_port,
            database=settings.postgres_database,
        )
    if primary_database == "sqlite":
        return SchemaMaintenanceDatabaseIdentity(
            primary_database=primary_database,
            dialect="sqlite",
            database=settings.SQLITE_DATABASE_PATH,
        )
    if primary_database == "mssql":
        return SchemaMaintenanceDatabaseIdentity(
            primary_database=primary_database,
            dialect="mssql",
            host=settings.MSSQL_HOST,
            port=settings.MSSQL_PORT,
            database=settings.MSSQL_DATABASE,
        )
    return SchemaMaintenanceDatabaseIdentity(primary_database=primary_database, dialect=primary_database)


def _load_registered_model_tables() -> list[str]:
    import_model_packages()
    return sorted(Base.metadata.tables)


def _warnings_for(skipped_existing_tables: list[str]) -> list[str]:
    if skipped_existing_tables:
        return [DRIFT_WARNING]
    return []


def _audit_fields(
    *,
    actor: object,
    database_identity: SchemaMaintenanceDatabaseIdentity,
    created_tables: list[str],
    skipped_existing_tables: list[str],
    warnings: list[str],
    result: str,
    requested_action: str | None = None,
) -> dict[str, Any]:
    return {
        "actor_id": getattr(actor, "id", None),
        "actor_username": getattr(actor, "username", None),
        "actor_role": getattr(actor, "role", None),
        "requested_action": requested_action,
        "primary_database": database_identity.primary_database,
        "database_dialect": database_identity.dialect,
        "database_host": database_identity.host,
        "database_port": database_identity.port,
        "database_name": database_identity.database,
        "created_count": len(created_tables),
        "skipped_count": len(skipped_existing_tables),
        "warning_count": len(warnings),
        "warnings": warnings,
        "result": result,
    }


class SchemaMaintenanceService:
    """Create-missing-only schema maintenance service."""

    @staticmethod
    async def _existing_table_names(db: AsyncSession) -> list[str]:
        connection = await db.connection()

        def inspect_tables(sync_connection) -> list[str]:
            return sorted(inspect(sync_connection).get_table_names())

        return await connection.run_sync(inspect_tables)

    @staticmethod
    async def _create_missing_tables(db: AsyncSession, missing_tables: list[str]) -> list[str]:
        if not missing_tables:
            return []
        missing_table_set = set(missing_tables)
        connection = await db.connection()

        def create_tables(sync_connection) -> list[str]:
            created: list[str] = []
            for table in Base.metadata.sorted_tables:
                if table.name not in missing_table_set:
                    continue
                table.create(bind=sync_connection, checkfirst=True)
                created.append(table.name)
            return created

        return await connection.run_sync(create_tables)

    async def get_status(self, db: AsyncSession, actor: object) -> SchemaMaintenanceStatusOut:
        try:
            model_tables = _load_registered_model_tables()
            existing_tables = await self._existing_table_names(db)
            existing_table_set = set(existing_tables)
            missing_tables = [table_name for table_name in model_tables if table_name not in existing_table_set]
            skipped_existing_tables = [
                table_name for table_name in model_tables if table_name in existing_table_set
            ]
            warnings = _warnings_for(skipped_existing_tables)
            database_identity = _database_identity()
            log_event(
                "INFO",
                "schema_maintenance_status_checked",
                **_audit_fields(
                    actor=actor,
                    database_identity=database_identity,
                    created_tables=[],
                    skipped_existing_tables=skipped_existing_tables,
                    warnings=warnings,
                    result="success",
                ),
            )
            return SchemaMaintenanceStatusOut(
                model_tables=model_tables,
                existing_tables=existing_tables,
                missing_tables=missing_tables,
                skipped_existing_tables=skipped_existing_tables,
                warnings=warnings,
                table_count=len(model_tables),
                database_identity=database_identity,
            )
        except SQLAlchemyError as exc:
            log_event(
                "ERROR",
                "schema_maintenance_status_failed",
                actor_id=getattr(actor, "id", None),
                actor_username=getattr(actor, "username", None),
                actor_role=getattr(actor, "role", None),
                result="failed",
            )
            raise BusinessException(
                SchemaMaintenanceErrorCode.SCHEMA_MAINTENANCE_STATUS_FAILED,
                message=SchemaMaintenanceErrorCode.SCHEMA_MAINTENANCE_STATUS_FAILED.value,
            ) from exc

    async def run_create_missing_action(
        self,
        db: AsyncSession,
        actor: object,
        requested_action: SchemaMaintenanceRequestedAction,
    ) -> SchemaMaintenanceActionOut:
        database_identity = _database_identity()
        try:
            model_tables = _load_registered_model_tables()
            existing_before = set(await self._existing_table_names(db))
            missing_tables_before = [
                table_name for table_name in model_tables if table_name not in existing_before
            ]
            skipped_existing_tables = [
                table_name for table_name in model_tables if table_name in existing_before
            ]

            created_tables = await self._create_missing_tables(db, missing_tables_before)

            existing_after = set(await self._existing_table_names(db))
            missing_tables_after = [
                table_name for table_name in model_tables if table_name not in existing_after
            ]
            warnings = _warnings_for(skipped_existing_tables)

            log_event(
                "INFO",
                f"schema_maintenance_{requested_action.value}_completed",
                **_audit_fields(
                    actor=actor,
                    database_identity=database_identity,
                    created_tables=created_tables,
                    skipped_existing_tables=skipped_existing_tables,
                    warnings=warnings,
                    result="success",
                    requested_action=requested_action.value,
                ),
            )
            return SchemaMaintenanceActionOut(
                requested_action=requested_action.value,
                created_tables=created_tables,
                skipped_existing_tables=skipped_existing_tables,
                missing_tables_before=missing_tables_before,
                missing_tables_after=missing_tables_after,
                warnings=warnings,
                table_count=len(model_tables),
                database_identity=database_identity,
            )
        except SQLAlchemyError as exc:
            log_event(
                "ERROR",
                f"schema_maintenance_{requested_action.value}_failed",
                **_audit_fields(
                    actor=actor,
                    database_identity=database_identity,
                    created_tables=[],
                    skipped_existing_tables=[],
                    warnings=[],
                    result="failed",
                    requested_action=requested_action.value,
                ),
            )
            raise BusinessException(
                SchemaMaintenanceErrorCode.SCHEMA_MAINTENANCE_ACTION_FAILED,
                message=SchemaMaintenanceErrorCode.SCHEMA_MAINTENANCE_ACTION_FAILED.value,
            ) from exc


schema_maintenance_service = SchemaMaintenanceService()
