"""
File Path: /tools/plc/projection-mapping/src-python/core/database.py
Description: Database table discovery and schema export for projection mapping.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from core.common import ToolError, read_json, write_json
from core.targets import normalize_targets


@dataclass(frozen=True)
class DbUrl:
    host: str
    port: int
    user: str
    password: str
    database: str


def parse_database_url(raw_url: str) -> DbUrl:
    parsed = urlparse(raw_url)
    scheme = parsed.scheme.lower()
    if scheme not in {"mysql", "mysql+pymysql", "mariadb", "mariadb+pymysql"}:
        raise ToolError("only mysql/mysql+pymysql/mariadb URLs are supported by export-schema")
    if not parsed.hostname or not parsed.username or not parsed.path.strip("/"):
        raise ToolError("database URL must include host, user and database name")
    return DbUrl(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=unquote(parsed.username),
        password=unquote(parsed.password or ""),
        database=unquote(parsed.path.strip("/")),
    )


def export_schema(database_url: str, targets_path: Path, output_path: Path) -> dict[str, Any]:
    try:
        import pymysql
    except ImportError as exc:
        raise ToolError("PyMySQL is required for export-schema") from exc

    db_url = parse_database_url(database_url)
    targets = normalize_targets(read_json(targets_path))
    placeholders = ", ".join(["%s"] * len(targets))
    started_at = time.time()

    connection = pymysql.connect(
        host=db_url.host,
        port=db_url.port,
        user=db_url.user,
        password=db_url.password,
        database=db_url.database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    c.TABLE_NAME AS table_name,
                    c.COLUMN_NAME AS column_name,
                    c.ORDINAL_POSITION AS ordinal_position,
                    c.COLUMN_TYPE AS column_type,
                    c.DATA_TYPE AS data_type,
                    c.IS_NULLABLE AS is_nullable,
                    c.COLUMN_DEFAULT AS column_default,
                    c.COLUMN_KEY AS column_key,
                    c.EXTRA AS extra,
                    c.COLUMN_COMMENT AS column_comment
                FROM information_schema.COLUMNS c
                WHERE c.TABLE_SCHEMA = %s
                  AND c.TABLE_NAME IN ({placeholders})
                ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION
                """,
                [db_url.database, *targets],
            )
            column_rows = cursor.fetchall()

            cursor.execute(
                f"""
                SELECT
                    k.TABLE_NAME AS table_name,
                    k.CONSTRAINT_NAME AS constraint_name,
                    k.COLUMN_NAME AS column_name,
                    k.ORDINAL_POSITION AS ordinal_position,
                    tc.CONSTRAINT_TYPE AS constraint_type
                FROM information_schema.KEY_COLUMN_USAGE k
                JOIN information_schema.TABLE_CONSTRAINTS tc
                  ON tc.CONSTRAINT_SCHEMA = k.CONSTRAINT_SCHEMA
                 AND tc.TABLE_NAME = k.TABLE_NAME
                 AND tc.CONSTRAINT_NAME = k.CONSTRAINT_NAME
                WHERE k.CONSTRAINT_SCHEMA = %s
                  AND k.TABLE_NAME IN ({placeholders})
                  AND tc.CONSTRAINT_TYPE IN ('PRIMARY KEY', 'UNIQUE')
                ORDER BY k.TABLE_NAME, k.CONSTRAINT_NAME, k.ORDINAL_POSITION
                """,
                [db_url.database, *targets],
            )
            key_rows = cursor.fetchall()
    finally:
        connection.close()

    tables: list[dict[str, Any]] = []
    missing_tables = []
    for table_name in targets:
        table_columns = [row for row in column_rows if row["table_name"] == table_name]
        if not table_columns:
            missing_tables.append(table_name)
            continue
        table_keys = [row for row in key_rows if row["table_name"] == table_name]
        tables.append({
            "table_name": table_name,
            "columns": [
                {
                    "name": row["column_name"],
                    "field_name": row["column_name"],
                    "field_type": row["column_type"],
                    "data_type": row["data_type"],
                    "nullable": row["is_nullable"] == "YES",
                    "default": row["column_default"],
                    "key": row["column_key"],
                    "extra": row["extra"],
                    "comment": row["column_comment"],
                }
                for row in table_columns
            ],
            "constraints": [
                {
                    "name": row["constraint_name"],
                    "type": row["constraint_type"],
                    "column_name": row["column_name"],
                    "ordinal_position": row["ordinal_position"],
                }
                for row in table_keys
            ],
        })

    if missing_tables:
        raise ToolError(f"database does not contain target tables: {missing_tables}")

    result = {
        "version": 1,
        "source": {
            "database": db_url.database,
            "exported_at_unix": round(started_at, 3),
            "target_count": len(targets),
        },
        "tables": tables,
    }
    write_json(output_path, result)
    return result


def list_tables(database_url: str, output_path: Path) -> dict[str, Any]:
    try:
        import pymysql
    except ImportError as exc:
        raise ToolError("PyMySQL is required for list-tables") from exc

    db_url = parse_database_url(database_url)
    started_at = time.time()
    connection = pymysql.connect(
        host=db_url.host,
        port=db_url.port,
        user=db_url.user,
        password=db_url.password,
        database=db_url.database,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    TABLE_NAME AS table_name,
                    TABLE_ROWS AS estimated_rows,
                    TABLE_COMMENT AS table_comment
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s
                  AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
                """,
                [db_url.database],
            )
            table_rows = cursor.fetchall()
    finally:
        connection.close()

    result = {
        "version": 1,
        "source": {
            "database": db_url.database,
            "exported_at_unix": round(started_at, 3),
            "table_count": len(table_rows),
        },
        "tables": [
            {
                "table": row["table_name"],
                "estimated_rows": row["estimated_rows"],
                "comment": row["table_comment"],
            }
            for row in table_rows
        ],
    }
    write_json(output_path, result)
    return result
