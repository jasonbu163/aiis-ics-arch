"""v2 异步数据库访问；事务由 Service 持有。"""
from sqlalchemy import and_, case, cast, false, func, or_, select, text
from sqlalchemy.dialects.mysql import CHAR, insert
from sqlalchemy.orm import load_only

from ..models.v2 import LatestPointV2, SampleV2
from ..v2_config import REVISION
from ..v2_domain import V2Error, stored_points, stored_value


def key(value):
    return value.encode('utf-8')


async def target_now(db, target):
    if db.get_bind().dialect.name != 'mysql':
        raise V2Error('not_ready', 503)
    revisions = list((await db.execute(text('SELECT version_num FROM alembic_version FOR SHARE'))).scalars())
    row = (await db.execute(text(
        'SELECT @@server_uuid, DATABASE(), VERSION(), CURRENT_TIMESTAMP(6), '
        'TIMESTAMPDIFF(SECOND, UTC_TIMESTAMP(6), CURRENT_TIMESTAMP(6))'
    ))).one()
    if (str(row[0]).lower() != target['serverUuid'] or row[1] != target['schema']
            or not str(row[2]).split('-')[0].startswith('8.4.') or row[4] != 28800
            or target['schemaRevision'] != REVISION or revisions != [REVISION]):
        raise V2Error('not_ready', 503)
    return row[3].replace(tzinfo=None)


async def identities(db, sample):
    by_id = and_(SampleV2.instance_id == key(sample.instance_id), SampleV2.sample_id == key(sample.sample_id))
    by_sequence = and_(
        SampleV2.instance_id == key(sample.instance_id), SampleV2.plc_id == key(sample.plc_id),
        SampleV2.db_number == sample.db_number, SampleV2.source_generation == key(sample.source_generation),
        SampleV2.source_seq == int(sample.source_seq),
    )
    statement = select(SampleV2).where(or_(by_id, by_sequence)).with_for_update()
    return list((await db.execute(statement)).scalars())


async def insert_sample(db, sample, document, digest, observed, expires, now, source_type):
    row = SampleV2(
        instance_id=key(sample.instance_id), sample_id=key(sample.sample_id),
        plc_id=key(sample.plc_id), db_number=sample.db_number,
        group_id=key(sample.group_id) if sample.group_id is not None else None,
        config_revision=key(sample.config_revision) if sample.config_revision is not None else None,
        source_generation=key(sample.source_generation), source_type=source_type,
        source_seq=int(sample.source_seq), points_json=stored_points(document['points']), content_hash=digest,
        sampled_at=max(observed), stored_at=now, expires_at=min(expires),
    )
    db.add(row)
    await db.flush()


async def advance_latest(db, sample, observed, expires):
    rows = []
    for point, point_time, point_expiry in sorted(
        zip(sample.points, observed, expires), key=lambda item: item[0].point_id.encode('utf-8')
    ):
        rows.append(dict(
            plc_id=key(sample.plc_id), db_number=sample.db_number, point_id=key(point.point_id),
            point_name=point.name or None, data_type=point.data_type, value_json=stored_value(point),
            quality=point.quality, reason=point.reason, observed_at=point_time, expires_at=point_expiry,
            instance_id=key(sample.instance_id), source_generation=key(sample.source_generation),
            source_seq=int(sample.source_seq), sample_id=key(sample.sample_id),
        ))
    statement = insert(LatestPointV2).values(rows)
    incoming = statement.inserted
    eligible = or_(
        LatestPointV2.instance_id != incoming.instance_id,
        LatestPointV2.source_generation != incoming.source_generation,
        LatestPointV2.source_seq < incoming.source_seq,
    )
    # MySQL evaluates assignments left to right. Change ordering fields last so every
    # value/metadata decision sees the previous generation and sequence.
    names = ('point_name', 'data_type', 'value_json', 'quality', 'reason', 'observed_at',
             'expires_at', 'sample_id', 'source_seq', 'source_generation', 'instance_id')
    updates = [(name, case((eligible, getattr(incoming, name)), else_=getattr(LatestPointV2, name))) for name in names]
    await db.execute(statement.on_duplicate_key_update(updates))


async def latest(db, plc, number, source, now, point_id=None):
    statement = select(LatestPointV2).where(
        LatestPointV2.plc_id == key(plc), LatestPointV2.db_number == number,
        LatestPointV2.instance_id == key(source[0]), LatestPointV2.source_generation == key(source[1]),
        LatestPointV2.expires_at > now,
    )
    if point_id is not None:
        statement = statement.where(LatestPointV2.point_id == key(point_id))
    statement = statement.order_by(LatestPointV2.point_id)
    return list((await db.execute(statement)).scalars())


def scope_condition(model, scope):
    return or_(false(), *(and_(model.plc_id == key(plc), model.db_number.in_(sorted(numbers)))
                          for plc, numbers in scope.items() if numbers))


async def browse_latest(db, scope, sources, search, page, page_size, now):
    active = []
    for plc, numbers in scope.items():
        source = sources.get(plc)
        allowed_numbers = numbers if source is not None else frozenset()
        if allowed_numbers:
            active.append(and_(
                LatestPointV2.plc_id == key(plc), LatestPointV2.db_number.in_(sorted(allowed_numbers)),
                LatestPointV2.instance_id == key(source[0]),
                LatestPointV2.source_generation == key(source[1]),
            ))
    predicates = [or_(false(), *active), LatestPointV2.expires_at > now]
    if search:
        escaped = search.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        pattern = '%' + escaped + '%'
        point_id = cast(LatestPointV2.point_id, CHAR(charset='utf8mb4')).collate('utf8mb4_0900_as_ci')
        name = LatestPointV2.point_name.collate('utf8mb4_0900_as_ci')
        predicates.append(or_(point_id.like(pattern, escape='\\'), name.like(pattern, escape='\\')))
    total = (await db.execute(select(func.count()).select_from(LatestPointV2).where(*predicates))).scalar_one()
    offset = (page - 1) * page_size
    if offset >= total:
        return total, []
    statement = (select(LatestPointV2).where(*predicates)
                 .order_by(LatestPointV2.plc_id, LatestPointV2.db_number, LatestPointV2.point_id)
                 .limit(page_size).offset(offset))
    return total, list((await db.execute(statement)).scalars())


async def history(db, scope, start, end, page, page_size, now):
    predicates = (scope_condition(SampleV2, scope), SampleV2.sampled_at >= start,
                  SampleV2.sampled_at < end, SampleV2.expires_at > now)
    total = (await db.execute(select(func.count()).select_from(SampleV2).where(*predicates))).scalar_one()
    offset = (page - 1) * page_size
    if offset >= total:
        return total, []
    summary_fields = (SampleV2.id, SampleV2.instance_id, SampleV2.sample_id, SampleV2.plc_id,
                      SampleV2.db_number, SampleV2.group_id, SampleV2.config_revision, SampleV2.source_type,
                      SampleV2.source_generation, SampleV2.source_seq, SampleV2.sampled_at, SampleV2.stored_at)
    statement = (select(SampleV2, func.json_length(SampleV2.points_json)).options(load_only(*summary_fields)).where(*predicates)
                 .order_by(SampleV2.sampled_at.desc(), SampleV2.id.desc())
                 .limit(page_size).offset(offset))
    return total, list((await db.execute(statement)).all())


async def detail(db, identity, now):
    statement = select(SampleV2).where(SampleV2.id == identity, SampleV2.expires_at > now)
    return (await db.execute(statement)).scalar_one_or_none()
