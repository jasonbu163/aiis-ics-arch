"""
文件路径: /backend/settings.py
功能描述: 应用配置管理
主要功能:
    - 从源码根目录或冻结制品同目录的 .env 读取配置
    - 提供配置类型定义
    - 提供计算属性（如 DATABASE_URL）
"""
import sys
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


def resolve_env_file() -> Path:
    """Return the single runtime .env path for source or packaged execution."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / ".env"
    return Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=resolve_env_file(),
        case_sensitive=True,
        extra="ignore"
    )
    
    APP_NAME: str
    APP_VERSION: str
    APP_DESCRIPTION: str = "AIIS ICS Architecture Core Backend"
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    BACKEND_WORKERS: int = 1
    TZ: str = "Asia/Shanghai"
    DEBUG: bool
    TESTING: bool = False
    PROJECTION_RUNNER_ENABLED: bool = False
    PROJECTION_RUNNER_INTERVAL_SECONDS: float = 1.0
    PROJECTION_RUNNER_BATCH_SIZE: int = 100
    
    # Backend business mock mode: True allows module Service mock providers / sample seeds.
    BACKEND_MOCK_ENABLED: bool = False
    
    # Primary database keeps the existing get_db / get_sync_db_context contract.
    # DATABASE_TYPE is kept as a legacy alias for existing local env files.
    PRIMARY_DATABASE: str | None = None
    DATABASE_TYPE: str = "mysql"
    MYSQL_ENABLED: bool = True
    POSTGRES_ENABLED: bool = False
    SQLITE_ENABLED: bool = False
    MSSQL_ENABLED: bool = False
    
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str
    TEST_MYSQL_DATABASE: str = "aiis_ics_architecture_test"
    
    MYSQL_ROOT_USER: str
    MYSQL_ROOT_PASSWORD: str
    
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DATABASE: str | None = None

    SQLITE_DATABASE_PATH: str = "./data/aiis_ics_architecture.sqlite3"

    MSSQL_HOST: str = "host.docker.internal"
    MSSQL_PORT: int = 1433
    MSSQL_USER: str = "sa"
    MSSQL_PASSWORD: str = ""
    MSSQL_DATABASE: str = "aiis_ics_architecture"
    MSSQL_DRIVER: str = "ODBC Driver 18 for SQL Server"
    MSSQL_TRUST_SERVER_CERTIFICATE: bool = True

    @property
    def primary_database(self) -> str:
        database = (self.PRIMARY_DATABASE or self.DATABASE_TYPE or "mysql").strip().lower()
        if database in {"postgres", "pg"}:
            return "postgresql"
        if database in {"mssql", "sqlserver", "sql_server"}:
            return "mssql"
        return database

    def _assert_database_enabled(self, database: str) -> None:
        enabled_map = {
            "mysql": self.MYSQL_ENABLED,
            "postgresql": self.POSTGRES_ENABLED,
            "sqlite": self.SQLITE_ENABLED,
            "mssql": self.MSSQL_ENABLED,
        }
        if not enabled_map.get(database, False):
            raise ValueError(f"Primary database '{database}' is not enabled in environment config")

    @property
    def postgres_host(self) -> str:
        if not self.POSTGRES_HOST:
            raise ValueError("POSTGRES_HOST is required when PostgreSQL is enabled")
        return self.POSTGRES_HOST

    @property
    def postgres_port(self) -> int:
        if not self.POSTGRES_PORT:
            raise ValueError("POSTGRES_PORT is required when PostgreSQL is enabled")
        return self.POSTGRES_PORT

    @property
    def postgres_user(self) -> str:
        if not self.POSTGRES_USER:
            raise ValueError("POSTGRES_USER is required when PostgreSQL is enabled")
        return self.POSTGRES_USER

    @property
    def postgres_password(self) -> str:
        return self.POSTGRES_PASSWORD or ""

    @property
    def postgres_database(self) -> str:
        if not self.POSTGRES_DATABASE:
            raise ValueError("POSTGRES_DATABASE is required when PostgreSQL is enabled")
        return self.POSTGRES_DATABASE
    
    @property
    def DATABASE_URL(self) -> str:
        database_type = self.primary_database
        self._assert_database_enabled(database_type)

        if database_type == "mysql":
            password = quote_plus(self.MYSQL_PASSWORD)
            database = self.TEST_MYSQL_DATABASE if self.TESTING else self.MYSQL_DATABASE
            return f"mysql+aiomysql://{self.MYSQL_USER}:{password}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{database}"
        elif database_type == "postgresql":
            password = quote_plus(self.postgres_password)
            return f"postgresql+asyncpg://{self.postgres_user}:{password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
        elif database_type == "sqlite":
            return f"sqlite+aiosqlite:///{self.SQLITE_DATABASE_PATH}"
        elif database_type == "mssql":
            password = quote_plus(self.MSSQL_PASSWORD)
            driver = quote_plus(self.MSSQL_DRIVER)
            trust_cert = "yes" if self.MSSQL_TRUST_SERVER_CERTIFICATE else "no"
            return (
                f"mssql+aioodbc://{self.MSSQL_USER}:{password}"
                f"@{self.MSSQL_HOST}:{self.MSSQL_PORT}/{self.MSSQL_DATABASE}"
                f"?driver={driver}&TrustServerCertificate={trust_cert}"
            )
        raise ValueError(f"Unsupported primary database '{database_type}'")
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        database_type = self.primary_database
        self._assert_database_enabled(database_type)

        if database_type == "mysql":
            password = quote_plus(self.MYSQL_PASSWORD)
            database = self.TEST_MYSQL_DATABASE if self.TESTING else self.MYSQL_DATABASE
            return f"mysql+pymysql://{self.MYSQL_USER}:{password}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{database}"
        elif database_type == "postgresql":
            password = quote_plus(self.postgres_password)
            return f"postgresql://{self.postgres_user}:{password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
        elif database_type == "sqlite":
            return f"sqlite:///{self.SQLITE_DATABASE_PATH}"
        elif database_type == "mssql":
            password = quote_plus(self.MSSQL_PASSWORD)
            driver = quote_plus(self.MSSQL_DRIVER)
            trust_cert = "yes" if self.MSSQL_TRUST_SERVER_CERTIFICATE else "no"
            return (
                f"mssql+pyodbc://{self.MSSQL_USER}:{password}"
                f"@{self.MSSQL_HOST}:{self.MSSQL_PORT}/{self.MSSQL_DATABASE}"
                f"?driver={driver}&TrustServerCertificate={trust_cert}"
            )
        raise ValueError(f"Unsupported primary database '{database_type}'")
    
    @property
    def ROOT_DATABASE_URL(self) -> str:
        password = quote_plus(self.MYSQL_ROOT_PASSWORD)
        return f"mysql+pymysql://{self.MYSQL_ROOT_USER}:{password}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/mysql"
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    # Only non-admin role grants are deployment configuration. Administrator
    # privilege is fixed in core.deps and never sourced from this setting.
    ROLE_API_PERMISSIONS_JSON: str = '{}'
    
    API_V1_PREFIX: str
    
    ADMIN_BOOTSTRAP_ENABLED: bool = False
    ADMIN_BOOTSTRAP_USERNAME: str = "admin"
    ADMIN_BOOTSTRAP_PASSWORD: str = ""
    ADMIN_BOOTSTRAP_NAME: str = "Administrator"
    ADMIN_BOOTSTRAP_ROLE: str = "admin"
    ADMIN_BOOTSTRAP_RESET_PASSWORD: bool = False

    SUPERVISOR_BOOTSTRAP_ENABLED: bool = False
    SUPERVISOR_BOOTSTRAP_USERNAME: str = "supervisor"
    SUPERVISOR_BOOTSTRAP_PASSWORD: str = ""
    SUPERVISOR_BOOTSTRAP_NAME: str = "Supervisor"
    SUPERVISOR_BOOTSTRAP_ROLE: str = "supervisor"
    SUPERVISOR_BOOTSTRAP_RESET_PASSWORD: bool = False

    OPERATOR_BOOTSTRAP_ENABLED: bool = False
    OPERATOR_BOOTSTRAP_USERNAME: str = "operator"
    OPERATOR_BOOTSTRAP_PASSWORD: str = ""
    OPERATOR_BOOTSTRAP_NAME: str = "Operator"
    OPERATOR_BOOTSTRAP_ROLE: str = "operator"
    OPERATOR_BOOTSTRAP_RESET_PASSWORD: bool = False
    
    LOG_DIR: str = "logs"
    LOG_LEVEL: str = "INFO"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024
    LOG_BACKUP_COUNT: int = 5

    @field_validator(
        'DEBUG',
        'TESTING',
        'PROJECTION_RUNNER_ENABLED',
        'BACKEND_MOCK_ENABLED',
        'MYSQL_ENABLED',
        'POSTGRES_ENABLED',
        'SQLITE_ENABLED',
        'MSSQL_ENABLED',
        'MSSQL_TRUST_SERVER_CERTIFICATE',
        'ADMIN_BOOTSTRAP_ENABLED',
        'ADMIN_BOOTSTRAP_RESET_PASSWORD',
        'SUPERVISOR_BOOTSTRAP_ENABLED',
        'SUPERVISOR_BOOTSTRAP_RESET_PASSWORD',
        'OPERATOR_BOOTSTRAP_ENABLED',
        'OPERATOR_BOOTSTRAP_RESET_PASSWORD',
        mode='before',
    )
    @classmethod
    def normalize_bool_flags(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {'1', 'true', 'yes', 'on', 'debug', 'dev', 'development'}:
                return True
            if normalized in {'0', 'false', 'no', 'off', 'release', 'prod', 'production'}:
                return False
        return value

    @field_validator(
        'BACKEND_PORT',
        'BACKEND_WORKERS',
        'PROJECTION_RUNNER_INTERVAL_SECONDS',
        'PROJECTION_RUNNER_BATCH_SIZE',
    )
    @classmethod
    def validate_projection_runtime_limits(cls, value):
        if value <= 0:
            raise ValueError("Projection runtime limits must be positive")
        return value


settings = Settings() # type: ignore
