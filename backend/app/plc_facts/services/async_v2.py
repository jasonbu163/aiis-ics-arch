"""v2 样本事务、PLC/DB 范围查询和提交回执。"""
from datetime import timedelta
import hmac

from sqlalchemy.exc import IntegrityError

from ..crud import async_v2 as crud
from ..crud import async_source_registry as registry
from ..v2_domain import V2Error, public_points, real_number, validate_times, wire_time


def receipt(sample, outcome):
    return {'code': 200, 'message': 'success', 'data': {
        'contractVersion': 'plc-facts/v2', 'instanceId': sample.instance_id,
        'sampleId': sample.sample_id, 'status': 'committed', 'outcome': outcome,
    }}


def existing_outcome(rows, sample, digest):
    if not rows:
        return None
    if (len(rows) == 1 and rows[0].instance_id == crud.key(sample.instance_id)
            and rows[0].sample_id == crud.key(sample.sample_id)
            and hmac.compare_digest(bytes(rows[0].content_hash), digest)):
        return 'duplicate'
    raise V2Error('sample_content_conflict', 409)


async def write_sample(db, profile, sample, document, digest, boundary):
    try:
        now = await crud.target_now(db, profile['target'])
        source_type = await registry.admit(db, sample)
        observed, expires = validate_times(sample, now)
        await crud.insert_sample(db, sample, document, digest, observed, expires, now,
                                 source_type)
        await crud.advance_latest(db, sample, observed, expires)
        validate_times(sample, await crud.target_now(db, profile['target']))
        boundary['commit_attempted'] = True
        await db.commit()
        boundary['committed'] = True
        return receipt(sample, 'created')
    except IntegrityError:
        if boundary.get('commit_attempted'):
            try:
                await db.rollback()
            finally:
                raise V2Error('commit_outcome_unknown', 503) from None
        try:
            await db.rollback()
            await crud.target_now(db, profile['target'])
            await registry.admit(db, sample)
            rows = await crud.identities(db, sample)
            validate_times(sample, await crud.target_now(db, profile['target']))
            outcome = existing_outcome(rows, sample, digest)
            await db.rollback()
            if outcome:
                return receipt(sample, outcome)
        except V2Error:
            await db.rollback()
            raise
        except Exception:
            raise V2Error('not_ready', 503) from None
        raise V2Error('not_ready', 503) from None
    except V2Error:
        await db.rollback()
        raise
    except Exception:
        unknown = boundary.get('commit_attempted', False)
        try:
            await db.rollback()
        except Exception:
            unknown = True
        raise V2Error('commit_outcome_unknown' if unknown else 'not_ready', 503) from None


def allowed_scope(profile, plc, number):
    if plc not in profile['sources']:
        raise V2Error('scope_rejected', 403)


def matching_scope(profile, plc, number):
    if plc is not None and plc not in profile['sources']:
        raise V2Error('scope_rejected', 403)
    return {key: None if number is None else {number} for key in profile['sources']
            if plc is None or key == plc}


def summary(row, count):
    return {
        'id': str(row.id), 'instanceId': row.instance_id.decode('utf-8'),
        'sampleId': row.sample_id.decode('utf-8'), 'plcId': row.plc_id.decode('utf-8'),
        'dbNumber': row.db_number, 'groupId': row.group_id.decode('utf-8') if row.group_id is not None else None,
        'configRevision': row.config_revision.decode('utf-8') if row.config_revision is not None else None,
        'sourceType': row.source_type,
        'sourceGeneration': row.source_generation.decode('utf-8'), 'sourceSeq': str(row.source_seq),
        'sampledAt': wire_time(row.sampled_at), 'storedAt': wire_time(row.stored_at), 'pointCount': count,
    }


async def options(db, profile, view=None):
    now = await crud.target_now(db, profile['target'])
    rows = await crud.options(db, now, view)
    grouped = {}
    for plc, number in rows:
        grouped.setdefault(plc.decode('utf-8'), []).append(number)
    return {'items': [{'plcId': plc, 'dbNumbers': numbers} for plc, numbers in grouped.items()]}


def latest_item(row, source_type):
    return {
        'pointId': row.point_id.decode('utf-8'),
        'name': row.point_name or row.point_id.decode('utf-8'), 'dataType': row.data_type,
        'value': real_number(row.value_json) if row.data_type == 'REAL' and row.quality == 'good' else row.value_json,
        'quality': row.quality, 'reason': row.reason,
        'observedAt': wire_time(row.observed_at), 'instanceId': row.instance_id.decode('utf-8'),
        'sourceGeneration': row.source_generation.decode('utf-8'), 'sourceSeq': str(row.source_seq),
        'sampleId': row.sample_id.decode('utf-8'), 'sourceType': source_type,
    }


async def latest(db, profile, plc, number, point_id=None):
    now = await crud.target_now(db, profile['target'])
    profile = await registry.read_profile(db, profile['target'])
    allowed_scope(profile, plc, number)
    source = profile['sources'].get(plc)
    if source is None:
        return {'items': []}
    rows = await crud.latest(db, plc, number, source, now, point_id)
    return {'items': [latest_item(row, profile['sourceTypes'][plc]) for row in rows]}


def page_result(items, total, page, page_size):
    return {'items': items, 'total': total, 'page': page, 'pageSize': page_size,
            'totalPages': (total + page_size - 1) // page_size}


async def browse_latest(db, profile, plc, number, search, page, page_size):
    now = await crud.target_now(db, profile['target'])
    profile = await registry.read_profile(db, profile['target'])
    scope = matching_scope(profile, plc, number)
    total, rows = await crud.browse_latest(db, scope, profile['sources'], search, page, page_size, now)
    items = []
    for row in rows:
        plc_id = row.plc_id.decode('utf-8')
        source_type = profile['sourceTypes'][plc_id]
        items.append({**latest_item(row, source_type), 'plcId': plc_id, 'dbNumber': row.db_number})
    return page_result(items, total, page, page_size)


async def history(db, profile, plc, number, start, end, page, page_size):
    if end <= start or end - start > timedelta(days=7):
        raise V2Error('invalid_request', 422)
    now = await crud.target_now(db, profile['target'])
    total, rows = await crud.history(db, plc, number, start, end, page, page_size, now)
    return page_result([summary(row, count) for row, count in rows], total, page, page_size)


async def detail(db, profile, identity):
    now = await crud.target_now(db, profile['target'])
    row = await crud.detail(db, identity, now)
    if row is None:
        raise V2Error('not_found', 404)
    result = summary(row, len(row.points_json))
    result['points'] = public_points(row.points_json)
    return result
