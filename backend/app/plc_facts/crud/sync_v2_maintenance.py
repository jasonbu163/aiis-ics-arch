"""v2 到期候选及条件清理 SQL；调用者持有事务。"""
import time

from sqlalchemy import delete, func, select, text, update

from ..models.v2 import LatestPointV2, SampleV2
from ..v2_config import REVISION
from ..v2_domain import V2Error


def target_now(db, target):
    if db.connection().dialect.name != 'mysql':
        raise V2Error('not_ready', 503)
    revisions = list(db.execute(text('SELECT version_num FROM alembic_version FOR SHARE')).scalars())
    row = db.execute(text(
        'SELECT @@server_uuid, DATABASE(), VERSION(), CURRENT_TIMESTAMP(6), '
        'TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))'
    )).one()
    if (str(row[0]).lower() != target['serverUuid'] or row[1] != target['schema']
            or not str(row[2]).split('-')[0].startswith('8.4.') or row[4] != 28800
            or target['schemaRevision'] != REVISION or revisions != [REVISION]):
        raise V2Error('not_ready', 503)
    return row[3].replace(tzinfo=None)


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
    return db.execute(statement).rowcount


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
