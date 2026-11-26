"""ARCH-ENERGY-001 r2：独立项目级金额、UTC 历史导入与可重跑的逐行对账。"""
import hashlib
import os
import re

import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.dialects.mysql import BINARY, DATETIME, VARCHAR

revision = "7cb6e40f3d19"
down_revision = "af6d8b2c4e90"
branch_labels = None
depends_on = None

SEEDS = (
    ("electric", "电能单价", "Electricity Price", "CNY/kWh", 10),
    ("hydrogen", "氢气单价", "Hydrogen Price", "CNY/Nm³", 20),
    ("argon", "氩气单价", "Argon Price", "CNY/Nm³", 30),
)
HOUR_FIELDS = ("hour_start", "observed_at", "created_at", "updated_at")
LEGACY_FIELDS = {"id", "operator", "remark", *HOUR_FIELDS,
                 *(f"{key}_{field}" for key, *_ in SEEDS for field in ("price", "remark"))}


def target_tables():
    metadata = sa.MetaData()
    key_type = VARCHAR(128, charset="utf8mb4", collation="utf8mb4_0900_bin")
    datetime_type = DATETIME(fsp=6)
    table_options = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"}
    items = sa.Table(
        "energy_price_items", metadata,
        sa.Column("item_key", key_type, primary_key=True),
        sa.Column("name_zh", sa.String(128)),
        sa.Column("name_en", sa.String(128)),
        sa.Column("unit", sa.String(128), nullable=False),
        sa.Column("sort_order", sa.BigInteger(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        **table_options,
    )
    hours = sa.Table(
        "energy_price_hour_meta", metadata,
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("hour_start", datetime_type, nullable=False, unique=True),
        sa.Column("remark", sa.Text()),
        sa.Column("observed_at", datetime_type),
        sa.Column("operator", sa.String(50)),
        sa.Column("created_at", datetime_type),
        sa.Column("updated_at", datetime_type),
        sa.Column("has_builtin", sa.Boolean(), nullable=False),
        sa.Index("ix_energy_price_hour_meta_observed_at_id", "observed_at", "id"),
        **table_options,
    )
    values = sa.Table(
        "energy_price_item_hours", metadata,
        sa.Column("item_key", key_type, sa.ForeignKey(items.c.item_key), primary_key=True),
        sa.Column("hour_start", datetime_type, sa.ForeignKey(hours.c.hour_start), primary_key=True),
        sa.Column("price", sa.Numeric(10, 4), nullable=False),
        sa.Column("remark", sa.Text()),
        sa.Column("observed_at", datetime_type, nullable=False),
        sa.Column("operator", sa.String(50), nullable=False),
        sa.Column("created_at", datetime_type, nullable=False),
        sa.Column("updated_at", datetime_type, nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_energy_price_item_hours_price_nonnegative"),
        sa.Index("ix_energy_price_item_hours_hour", "hour_start"),
        **table_options,
    )
    return items, hours, values


def verify_target(connection, expected_revision):
    if context.is_offline_mode() or connection.dialect.name != "mysql":
        raise RuntimeError("energy pricing requires an inspected online MySQL target")
    server, schema = connection.execute(sa.text("SELECT @@server_uuid, DATABASE()")).one()
    if (not schema or schema.lower() in {"mysql", "sys", "information_schema", "performance_schema"}
            or schema != os.environ.get("ENERGY_PRICING_EXPECTED_SCHEMA")
            or server != os.environ.get("ENERGY_PRICING_EXPECTED_SERVER_UUID")
            or os.environ.get("ENERGY_PRICING_WRITE_WINDOW") != f"{schema}:{server}:UTC"):
        raise RuntimeError("energy pricing migration target or write window mismatch")
    # Alembic owns a dedicated short-lived connection. Retain the lock through its
    # version update and release on close. Application writes must already be drained.
    lock_key = "energy_pricing_" + hashlib.sha256(schema.encode()).hexdigest()[:48]
    if connection.scalar(sa.select(sa.func.get_lock(lock_key, 0))) != 1:
        raise RuntimeError("another energy pricing migration is running")
    if list(connection.execute(sa.text("SELECT version_num FROM alembic_version")).scalars()) != [expected_revision]:
        raise RuntimeError("energy pricing migration requires the exact starting revision")
    inspector = sa.inspect(connection)
    source = sa.Table("energy_price_hours", sa.MetaData(), autoload_with=connection)
    if (inspector.get_table_options(source.name).get("mysql_engine") != "InnoDB"
            or not LEGACY_FIELDS.issubset(source.c.keys())
            or any(getattr(source.c[key].type, "fsp", None) != 6 for key in HOUR_FIELDS)):
        raise RuntimeError("required UTC hourly pricing predecessor layout missing")
    return source


def comparable_type(column, dialect):
    kind = column.type.compile(dialect=dialect).lower().replace("decimal(", "numeric(")
    return {"bool": "tinyint", "tinyint(1)": "tinyint"}.get(kind, kind)


def inspect_stage(connection, expected):
    inspector = sa.inspect(connection)
    if not inspector.has_table(expected.name):
        return False
    actual = sa.Table(expected.name, sa.MetaData(), autoload_with=connection)
    def columns(table):
        # Normal price writes omit the hour ID and rely on effective AUTO_INCREMENT.
        generated_id = table.autoincrement_column
        return {
            c.name: (comparable_type(c, connection.dialect), c.nullable, c.primary_key, c is generated_id)
            for c in table.columns
        }

    def indexes(table):
        return {(tuple(index.columns.keys()), index.unique) for index in table.indexes}
    expected_indexes = indexes(expected).union(
        (tuple(constraint.columns.keys()), True) for constraint in expected.constraints
        if isinstance(constraint, sa.UniqueConstraint)
    )
    # Both foreign keys have supporting indexes in the declared layout.
    actual_indexes = indexes(actual).union(
        (tuple(constraint.columns.keys()), True) for constraint in actual.constraints
        if isinstance(constraint, sa.UniqueConstraint)
    )
    def foreign_keys(table):
        return {(fk.parent.name, fk.target_fullname, fk.ondelete, fk.onupdate) for fk in table.foreign_keys}

    def checks(table):
        return {
            (constraint.name, re.sub(r"[\s`()]+", "", str(constraint.sqltext).lower()))
            for constraint in table.constraints if isinstance(constraint, sa.CheckConstraint)
        }

    if (columns(expected) != columns(actual) or expected_indexes != actual_indexes
            or foreign_keys(expected) != foreign_keys(actual) or checks(expected) != checks(actual)
            or inspector.get_table_options(expected.name).get("mysql_engine") != "InnoDB"):
        raise RuntimeError(f"energy pricing staged table differs from migration layout: {expected.name}")
    return True


def converted_source(source):
    # The old hour key is already the normalized UTC instant, including fold=0.
    times = {field: sa.func.timestampadd(sa.literal_column("HOUR"), 8, source.c[field]).label(field)
             for field in HOUR_FIELDS}
    seeds = sa.union_all(*[
        sa.select(
            sa.literal(key).label("item_key"), sa.literal(zh).label("name_zh"), sa.literal(en).label("name_en"),
            sa.literal(unit).label("unit"), sa.literal(order).label("sort_order"), sa.true().label("enabled"),
        ) for key, zh, en, unit, order in SEEDS
    ]).subquery()
    hours = sa.select(source.c.id, times["hour_start"], source.c.remark, times["observed_at"],
                      source.c.operator, times["created_at"], times["updated_at"], sa.true().label("has_builtin")).subquery()
    values = sa.union_all(*[
        sa.select(
            sa.literal(key).label("item_key"), times["hour_start"], source.c[key + "_price"].label("price"),
            source.c[key + "_remark"].label("remark"), times["observed_at"], source.c.operator,
            times["created_at"], times["updated_at"],
        ) for key, *_ in SEEDS
    ]).subquery()
    return seeds, hours, values


def row_count(connection, table):
    return connection.scalar(sa.select(sa.func.count()).select_from(table))


def verify_rows(connection, table, expected):
    keys = [col.name for col in table.primary_key]
    match = sa.and_(*(table.c[key] == expected.c[key] for key in keys))
    exact = []
    for column in table.columns:
        expected_value = expected.c[column.name]
        actual_value = column
        if isinstance(column.type, sa.String):
            actual_value, expected_value = sa.cast(column, BINARY), sa.cast(expected_value, BINARY)
        exact.append(actual_value.is_not_distinct_from(expected_value))
    mismatch = sa.select(1).select_from(expected.outerjoin(table, match)).where(
        table.c[keys[0]].is_(None) | ~sa.and_(*exact),
    ).limit(1)
    if row_count(connection, table) != row_count(connection, expected) or connection.scalar(mismatch):
        raise RuntimeError(f"energy pricing reconciliation failed: {table.name}")


def upgrade():
    if context.is_offline_mode():
        raise RuntimeError("energy pricing requires an inspected online MySQL target")
    connection = op.get_bind()
    source = verify_target(connection, down_revision)
    tables = target_tables()
    expected_rows = converted_source(source)
    existing = [inspect_stage(connection, table) for table in tables]
    # MySQL DDL may have committed before failure. Reuse only an exact layout and
    # only empty tables or rows that reconcile fully with the old source.
    for table, expected, found in zip(tables, expected_rows, existing):
        if found and row_count(connection, table):
            verify_rows(connection, table, expected)
    for table, found in zip(tables, existing):
        if not found:
            table.create(connection)
    # No DDL after data import so all three sets and the Alembic revision move together.
    for table, expected in zip(tables, expected_rows):
        if not row_count(connection, table):
            connection.execute(table.insert().from_select(table.columns.keys(), sa.select(expected)))
        verify_rows(connection, table, expected)


def downgrade():
    if context.is_offline_mode():
        raise RuntimeError("energy pricing requires an inspected online MySQL target")
    connection = op.get_bind()
    source = verify_target(connection, revision)
    tables = target_tables()
    existing = [inspect_stage(connection, table) for table in tables]
    # Only pristine, fully reproducible imported data is eligible for the Alembic
    # downgrade. Adopted pricing has to be exported before a separately approved rollback.
    for table, expected, found in zip(tables, converted_source(source), existing):
        if found:
            verify_rows(connection, table, expected)
    for table, found in reversed(list(zip(tables, existing))):
        if found:
            table.drop(connection)
