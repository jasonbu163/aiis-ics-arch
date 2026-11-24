"""v2 到期候选及条件清理 SQL；调用者持有事务。"""
import time

from sqlalchemy import UniqueConstraint, bindparam, delete, func, select, text, update
from sqlalchemy.dialects.mysql import dialect
from sqlalchemy.exc import SQLAlchemyError

from common.log import log_event

from ..models.consumption import (
    AcquisitionConsumer, AcquisitionDelivery, AcquisitionOperation, ConsumptionActivation,
    ConsumptionEvent, ConsumptionStream,
)
from ..models.source_registry import PlcSourceRegistry

from ..models.v2 import LatestPointV2, SampleV2
from ..v2_domain import V2Error


_LAYOUT = {model.__tablename__: model.__table__ for model in (
    PlcSourceRegistry, SampleV2, LatestPointV2, ConsumptionStream, ConsumptionEvent,
    AcquisitionConsumer, AcquisitionDelivery, AcquisitionOperation, ConsumptionActivation,
)}
_MYSQL = dialect()
_TARGET_SQL = text(
    'SELECT @@server_uuid, DATABASE(), VERSION(), CURRENT_TIMESTAMP(6), '
    'TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))'
)
CLOCK_SQL = text(
    'SELECT CURRENT_TIMESTAMP(6), TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))'
)
_TABLES_SQL = text('''
    SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN :tables AND TABLE_TYPE = 'BASE TABLE'
''').bindparams(bindparam('tables', expanding=True))
_COLUMNS_SQL = text('''
    SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLLATION_NAME, EXTRA
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN :tables
''').bindparams(bindparam('tables', expanding=True))
_KEYS_SQL = text('''
    SELECT TABLE_NAME, INDEX_NAME, COLUMN_NAME, SUB_PART
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN :tables AND NON_UNIQUE = 0
    ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX
''').bindparams(bindparam('tables', expanding=True))
_READY_SQL = select(ConsumptionActivation.ready).where(ConsumptionActivation.id == 1).with_for_update(read=True)


def reject_target(reason, **evidence):
    log_event('WARNING', 'plc_facts_target_not_ready', reason=reason, **evidence)
    raise V2Error('not_ready', 503)


def check_target(db, target):
    if db.get_bind().dialect.name != 'mysql':
        reject_target('database_dialect')
    row = db.execute(_TARGET_SQL).one()
    if str(row[0]).lower() != target['serverUuid'] or row[1] != target['schema']:
        reject_target('target_identity')
    if not str(row[2]).split('-')[0].startswith('8.4.'):
        reject_target('mysql_version')
    return checked_clock(row[3], row[4])


def checked_clock(now, offset):
    if offset != 28800:
        reject_target('database_clock')
    return now.replace(tzinfo=None)


def check_layout(db):
    """同一事务内核对采集的九张业务表；在线账号只需 DML 权限。"""
    params = {'tables': tuple(_LAYOUT)}
    engines = dict(db.execute(_TABLES_SQL, params).all())
    columns = {(table, column): (kind, nullable, collation, extra)
               for table, column, kind, nullable, collation, extra in db.execute(_COLUMNS_SQL, params)}
    keys = {table: {} for table in _LAYOUT}
    for table, name, column, prefix in db.execute(_KEYS_SQL, params):
        if table in keys:
            keys[table].setdefault(name, []).append(column if prefix is None else None)
    for name, table in _LAYOUT.items():
        if engines.get(name) != 'InnoDB':
            reject_target('missing_table_or_engine', table=name)
        for column in table.columns:
            kind, nullable, collation, extra = columns.get((name, column.name), ('', '', None, ''))
            expected_kind = column.type.compile(dialect=_MYSQL).lower().split(' character set ', 1)[0]
            expected_collation = getattr(column.type, 'collation', None)
            if (kind.lower() != expected_kind or nullable != ('YES' if column.nullable else 'NO')
                    or (expected_collation is not None and collation != expected_collation)
                    or (column is SampleV2.__table__.c.id and 'auto_increment' not in extra.split())):
                reject_target('missing_or_incompatible_column', table=name, column=column.name)
        primary = tuple(table.primary_key.columns.keys())
        unique = {tuple(constraint.columns.keys()) for constraint in table.constraints
                  if isinstance(constraint, UniqueConstraint)}
        actual_unique = {tuple(parts) for index, parts in keys[name].items() if index != 'PRIMARY'}
        if tuple(keys[name].get('PRIMARY', ())) != primary or actual_unique != unique:
            reject_target('incompatible_keys', table=name)
    if db.execute(_READY_SQL).scalar_one_or_none() != 1:
        reject_target('consumption_inactive')


def runtime_target_now(db, target):
    try:
        now = check_target(db, target)
        check_layout(db)
        return now
    except SQLAlchemyError:
        reject_target('structure_probe_failed')


def target_now(db, target, *, require_layout=False):
    """显式维护只接受操作方提供并锁定的实际全库 revision。"""
    now = check_target(db, target)
    revisions = list(db.execute(text('SELECT version_num FROM alembic_version FOR SHARE')).scalars())
    if revisions != [target['schemaRevision']]:
        reject_target('maintenance_revision')
    if require_layout:
        check_layout(db)
    return now


def candidates(db, now, limit, lock, deadline=None):
    sample_size = 74 + sum(func.coalesce(func.octet_length(column), 0) for column in (
        SampleV2.instance_id, SampleV2.sample_id, SampleV2.plc_id, SampleV2.group_id,
        SampleV2.config_revision, SampleV2.source_generation, SampleV2.points_json, SampleV2.source_type,
    ))
    sample_statement = (select(SampleV2.id, SampleV2.expires_at, sample_size.label('size'))
                        .where(SampleV2.expires_at <= now)
                        .order_by(SampleV2.expires_at, SampleV2.id).limit(limit))
    latest_size = 16 + sum(func.coalesce(func.octet_length(column), 0) for column in (
        LatestPointV2.point_name, LatestPointV2.data_type, LatestPointV2.value_json,
        LatestPointV2.quality, LatestPointV2.reason, LatestPointV2.sample_id,
    ))
    latest_statement = (select(LatestPointV2.plc_id, LatestPointV2.db_number, LatestPointV2.point_id,
                               LatestPointV2.expires_at, LatestPointV2.instance_id,
                               LatestPointV2.source_generation, LatestPointV2.source_seq, latest_size.label('size'))
                        .where(LatestPointV2.expires_at <= now)
                        .order_by(LatestPointV2.expires_at, LatestPointV2.plc_id,
                                  LatestPointV2.db_number, LatestPointV2.point_id).limit(limit))
    if lock:
        sample_statement = sample_statement.with_for_update(skip_locked=True)
        latest_statement = latest_statement.with_for_update(skip_locked=True)
    if deadline is not None and time.monotonic() >= deadline:
        return []
    rows = [(row.expires_at, 0, (row.id,), int(row.size)) for row in db.execute(sample_statement)]
    if deadline is not None and time.monotonic() >= deadline:
        return []
    rows.extend((row.expires_at, 1, (row.plc_id, row.db_number, row.point_id,
                row.instance_id, row.source_generation, row.source_seq), int(row.size))
                for row in db.execute(latest_statement))
    return sorted(rows, key=lambda item: (item[0], item[1], item[2][:3]))[:limit]


def clear(db, candidate, now):
    expiry, kind, identity, _ = candidate
    if kind == 0:
        statement = delete(SampleV2).where(SampleV2.id == identity[0], SampleV2.expires_at == expiry,
                                           SampleV2.expires_at <= now)
    else:
        plc, number, point, instance, generation, sequence = identity
        statement = update(LatestPointV2).where(
            LatestPointV2.plc_id == plc, LatestPointV2.db_number == number, LatestPointV2.point_id == point,
            LatestPointV2.expires_at == expiry, LatestPointV2.expires_at <= now,
            LatestPointV2.instance_id == instance, LatestPointV2.source_generation == generation,
            LatestPointV2.source_seq == sequence,
        ).values(point_name=None, data_type=None, value_json=None, quality=None, reason=None,
                 observed_at=None, expires_at=None, sample_id=None)
    if kind != 0:
        return db.execute(statement).rowcount
    db.execute(text('SET @acq006_prune_id = :identity'), {'identity': identity[0]})
    try:
        return db.execute(statement).rowcount
    finally:
        try:
            db.execute(text('SET @acq006_prune_id = NULL'))
        except Exception:
            db.invalidate()
            raise


def oldest(db, now, deadline=None):
    values = []
    for model in (SampleV2, LatestPointV2):
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError('cleanup budget exhausted')
        values.append(db.execute(select(func.min(model.expires_at)).where(model.expires_at <= now)).scalar_one())
    return min((value for value in values if value is not None), default=None)


def database_time(db):
    """无表锁的数据库完成时刻。"""
    return db.execute(text('SELECT CURRENT_TIMESTAMP(6)')).scalar_one().replace(tzinfo=None)
