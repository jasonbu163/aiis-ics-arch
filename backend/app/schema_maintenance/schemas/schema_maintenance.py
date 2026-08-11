"""
文件路径: /backend/app/schema_maintenance/schemas/schema_maintenance.py
功能描述: Schema maintenance API 输出合同
主要功能:
    - 定义 create-missing-tables 状态 / 执行结果响应结构
    - 通过 ApiSchema 输出 camelCase 字段
"""
from common.schema_base import ApiSchema


class SchemaMaintenanceDatabaseIdentity(ApiSchema):
    primary_database: str
    dialect: str
    host: str | None = None
    port: int | None = None
    database: str | None = None


class SchemaMaintenanceStatusOut(ApiSchema):
    model_tables: list[str]
    existing_tables: list[str]
    missing_tables: list[str]
    skipped_existing_tables: list[str]
    warnings: list[str]
    table_count: int
    database_identity: SchemaMaintenanceDatabaseIdentity


class SchemaMaintenanceActionOut(ApiSchema):
    requested_action: str
    created_tables: list[str]
    skipped_existing_tables: list[str]
    missing_tables_before: list[str]
    missing_tables_after: list[str]
    warnings: list[str]
    table_count: int
    database_identity: SchemaMaintenanceDatabaseIdentity
