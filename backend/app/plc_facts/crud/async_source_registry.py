"""PLC 来源登记的异步 SQL 操作；提交由 Service 控制。"""
from sqlalchemy import delete, func, select, text, update
from sqlalchemy.dialects.mysql import insert

from ..models.source_registry import PlcSourceRegistry
from ..models.v2 import LatestPointV2, SampleV2
from ..v2_domain import V2Error, wire_time


def key(value):
    return value.encode('utf-8')


async def admit(db, sample):
    query = (select(PlcSourceRegistry.source_type)
             .where(PlcSourceRegistry.plc_id == key(sample.plc_id),
                    PlcSourceRegistry.instance_id == key(sample.instance_id),
                    PlcSourceRegistry.source_generation == key(sample.source_generation))
             .with_for_update(read=True))
    source_type = (await db.execute(query)).scalar_one_or_none()
    if source_type is None:
        raise V2Error('scope_rejected', 403)
    return source_type


async def read_profile(db, target):
    """只读取得当前 PLC 绑定及每台 PLC 的展示标签。"""
    sources, source_types = {}, {}
    for row in (await db.execute(select(PlcSourceRegistry))).scalars():
        plc = row.plc_id.decode('utf-8')
        sources[plc] = (row.instance_id.decode('utf-8'), row.source_generation.decode('utf-8'))
        source_types[plc] = row.source_type
    return {'target': target, 'sources': sources, 'sourceTypes': source_types}


async def binding_for_update(db, plc):
    query = select(PlcSourceRegistry).where(PlcSourceRegistry.plc_id == key(plc)).with_for_update()
    return (await db.execute(query)).scalar_one_or_none()


async def insert_binding(db, body, revision):
    statement = insert(PlcSourceRegistry).values(
        plc_id=key(body.plc_id), instance_id=key(body.instance_id),
        source_generation=key(body.source_generation), source_type=body.source_type,
        retired_generations=[], registration_revision=revision,
    )
    await db.execute(statement.on_duplicate_key_update(plc_id=statement.inserted.plc_id))
    return await binding_for_update(db, body.plc_id)


async def generation_exists(db, plc, generation, binding=None):
    if binding is not None:
        retired = binding.retired_generations
        if not isinstance(retired, list) or any(not isinstance(value, str) for value in retired):
            raise ValueError('invalid retired generations')
        if generation == binding.source_generation.decode('utf-8') or generation in retired:
            return True
    plc_key, generation_key = key(plc), key(generation)
    for model in (SampleV2, LatestPointV2):
        query = (select(model.plc_id)
                 .where(model.plc_id == plc_key, model.source_generation == generation_key)
                 .limit(1).with_for_update(read=True))
        if (await db.execute(query)).first() is not None:
            return True
    return False


async def update_binding(db, binding, revision, source_type, replacement=None):
    values = {
        'source_type': source_type,
        'registration_revision': revision,
        'updated_at': text('CURRENT_TIMESTAMP(6)'),
    }
    if replacement is not None:
        values.update(
            instance_id=key(replacement.instance_id),
            source_generation=key(replacement.source_generation),
            retired_generations=[*binding.retired_generations, binding.source_generation.decode('utf-8')],
        )
    await db.execute(update(PlcSourceRegistry).where(PlcSourceRegistry.plc_id == binding.plc_id).values(**values))


async def delete_binding(db, binding):
    await db.execute(delete(PlcSourceRegistry).where(PlcSourceRegistry.plc_id == binding.plc_id))


async def source(db, plc):
    query = (select(PlcSourceRegistry).where(PlcSourceRegistry.plc_id == key(plc))
             .execution_options(populate_existing=True))
    row = (await db.execute(query)).scalar_one_or_none()
    if row is None:
        return None
    return {
        'sourceType': row.source_type,
        'instanceId': row.instance_id.decode('utf-8'),
        'plcId': row.plc_id.decode('utf-8'),
        'sourceGeneration': row.source_generation.decode('utf-8'),
        'registrationRevision': row.registration_revision,
        'createdAt': wire_time(row.created_at),
        'updatedAt': wire_time(row.updated_at),
    }


async def page(db, page, page_size):
    total = (await db.execute(select(func.count()).select_from(PlcSourceRegistry))).scalar_one()
    offset = (page - 1) * page_size
    items = []
    if offset < total:
        query = (select(PlcSourceRegistry.plc_id).order_by(PlcSourceRegistry.plc_id)
                 .limit(page_size).offset(offset))
        keys = (await db.execute(query)).scalars()
        items = [await source(db, plc.decode('utf-8')) for plc in keys]
    return {'items': items, 'total': total, 'page': page, 'pageSize': page_size,
            'totalPages': (total + page_size - 1) // page_size}
