"""受控旧来源导入；预览只读，提交由单一事务完成。"""
import hashlib
import json
from uuid import uuid4

from sqlalchemy import func, select

from ..crud.sync_v2_maintenance import target_now
from ..models.source_registry import (SourceBinding, SourceGeneration, SourceInitialization, SourceInstance,
                                      SourceReadScope, SourceWriteScope)
from ..v2_config import LEGACY_REVISION, parse_profile, validate_target
from ..v2_domain import identifier, parse_time


class ImportCommitUnknown(Exception):
    """连接在提交边界失败；必须通过只读预览核对，不应直接重放。"""


def source_summary(profile):
    instances = sorted((name, kind) for name, kind in profile['instances'].items())
    sources = sorted((plc, source[0], source[1], sorted(source[2]))
                     for plc, source in profile['sources'].items())
    reads = sorted((plc, number) for plc, numbers in profile['readScope'].items() for number in numbers)
    canonical = json.dumps([instances, sources, reads], ensure_ascii=False, separators=(',', ':')).encode()
    return {
        'instanceCount': len(instances),
        'bindingCount': len(sources),
        'writeScopeCount': sum(len(source[3]) for source in sources),
        'readScopeCount': len(reads),
        'logicalSha256': hashlib.sha256(canonical).hexdigest(),
    }


def current_summary(db, target):
    instances = {row.instance_id.decode(): row.source_type
                 for row in db.execute(select(SourceInstance)).scalars()}
    sources = {row.plc_id.decode(): (row.instance_id.decode(), row.source_generation.decode(), set())
               for row in db.execute(select(SourceBinding)).scalars()}
    for plc, number in db.execute(select(SourceWriteScope.plc_id, SourceWriteScope.db_number)):
        sources[plc.decode()][2].add(number)
    reads = {}
    for plc, number in db.execute(select(SourceReadScope.plc_id, SourceReadScope.db_number)):
        reads.setdefault(plc.decode(), set()).add(number)
    return source_summary({'target': target, 'instances': instances, 'sources': sources, 'readScope': reads})


def export(db, target, restore_target):
    """导出一致读取快照；调用方必须先暂停登记、采集写入及维护。"""
    target_now(db, target)
    validate_target(restore_target, LEGACY_REVISION)
    marker = db.execute(select(SourceInitialization).where(SourceInitialization.id == 1)).scalar_one_or_none()
    if marker is None:
        raise ValueError('registry not initialized')
    instances = list(db.execute(select(SourceInstance).order_by(SourceInstance.instance_id)).scalars())
    bindings = list(db.execute(select(SourceBinding).order_by(SourceBinding.plc_id)).scalars())
    writes, reads = {}, {}
    for plc, number in db.execute(select(SourceWriteScope.plc_id, SourceWriteScope.db_number).order_by(SourceWriteScope.plc_id, SourceWriteScope.db_number)):
        writes.setdefault(plc.decode('utf-8'), []).append(number)
    for plc, number in db.execute(select(SourceReadScope.plc_id, SourceReadScope.db_number).order_by(SourceReadScope.plc_id, SourceReadScope.db_number)):
        reads.setdefault(plc.decode('utf-8'), []).append(number)
    legacy = {'target': restore_target,
              'instances': [{'instanceId': r.instance_id.decode('utf-8'), 'sourceType': r.source_type} for r in instances],
              'sources': [{'plcId': r.plc_id.decode('utf-8'), 'instanceId': r.instance_id.decode('utf-8'),
                           'sourceGeneration': r.source_generation.decode('utf-8'),
                           'dbNumbers': writes.get(r.plc_id.decode('utf-8'), [])} for r in bindings],
              'readScopes': {'restore': [{'plcId': plc, 'dbNumbers': numbers} for plc, numbers in reads.items()]}}
    parsed = parse_profile(legacy)
    generations = [{'plcId': r.plc_id.decode('utf-8'), 'instanceId': r.instance_id.decode('utf-8'),
                    'sourceGeneration': r.source_generation.decode('utf-8'), 'createdAt': r.created_at.isoformat(timespec='microseconds') + '+08:00'}
                   for r in db.execute(select(SourceGeneration).order_by(SourceGeneration.plc_id, SourceGeneration.source_generation)).scalars()]
    return {'formatVersion': 1, 'sourceTarget': target, 'legacyProfile': legacy,
            'generations': generations,
            'revisions': [{'plcId': r.plc_id.decode('utf-8'), 'registrationRevision': r.registration_revision,
                           'createdAt': r.created_at.isoformat(timespec='microseconds') + '+08:00',
                           'updatedAt': r.updated_at.isoformat(timespec='microseconds') + '+08:00'} for r in bindings],
            'summary': source_summary(parsed), 'initialInputSha256': marker.input_hash.hex()}


def restore_generations(profile, exported):
    if not isinstance(exported, dict) or exported.get('formatVersion') != 1 or not isinstance(exported.get('generations'), list):
        raise ValueError('invalid generation export')
    previous = parse_profile(exported.get('legacyProfile'))
    if previous['target'] != profile['target']:
        raise ValueError('generation export target mismatch')
    result = {}
    for row in exported['generations']:
        if not isinstance(row, dict) or set(row) != {'plcId', 'instanceId', 'sourceGeneration', 'createdAt'}:
            raise ValueError('invalid generation record')
        plc, instance, generation = map(identifier, (row['plcId'], row['instanceId'], row['sourceGeneration']))
        if (plc not in profile['sources'] or instance not in profile['instances']
                or previous['instances'].get(instance) != profile['instances'][instance]):
            raise ValueError('generation references missing source')
        key = (plc, generation)
        if key in result:
            raise ValueError('duplicate generation record')
        result[key] = (instance, parse_time(row['createdAt']))
    for plc, (instance, generation, _numbers) in profile['sources'].items():
        if (plc, generation) in result and result[(plc, generation)][0] != instance:
            raise ValueError('generation identity conflict')
    return result


def run(db, target, profile, input_hash, apply, exported=None, export_hash=None):
    target_now(db, target)
    source = profile['target']
    if any(source[name] != target[name] for name in ('alias', 'schema', 'serverUuid')):
        raise ValueError('source target mismatch')
    result = source_summary(profile)
    result['sourceSha256'] = input_hash.hex()
    generations = restore_generations(profile, exported) if exported is not None else {}
    if exported is not None:
        if export_hash is None or len(export_hash) != 32:
            raise ValueError('generation export digest required')
        result['generationFileSha256'] = export_hash.hex()
        result['preservedGenerationCount'] = len(generations)
        input_hash = hashlib.sha256(b'acq004-import-v1\0' + input_hash + export_hash).digest()
    target_hash = hashlib.sha256(json.dumps(target, sort_keys=True, separators=(',', ':')).encode()).digest()
    marker = select(SourceInitialization).where(SourceInitialization.id == 1)
    if apply:
        marker = marker.with_for_update()
    existing = db.execute(marker).scalar_one_or_none()
    if existing is not None:
        if existing.input_hash != input_hash or existing.target_hash != target_hash:
            raise ValueError('different initialization')
        initial_digest = existing.logical_hash.hex()
        current = current_summary(db, target)
        db.rollback()
        return {**result, 'outcome': 'unchanged', 'initialLogicalSha256': initial_digest,
                'currentSummary': current, 'currentMatchesInitial': current['logicalSha256'] == initial_digest}
    models = (SourceInstance, SourceBinding, SourceGeneration, SourceWriteScope, SourceReadScope)
    if any(db.execute(select(func.count()).select_from(model)).scalar_one() for model in models):
        raise ValueError('registry is not empty')
    if not apply:
        db.rollback()
        return {**result, 'outcome': 'preview'}
    for name, kind in profile['instances'].items():
        db.add(SourceInstance(instance_id=name.encode(), source_type=kind))
    db.flush()
    for plc, (instance, generation, numbers) in profile['sources'].items():
        db.add(SourceBinding(plc_id=plc.encode(), instance_id=instance.encode(),
                             source_generation=generation.encode(), registration_revision=str(uuid4())))
    db.flush()
    for plc, (instance, generation, _numbers) in profile['sources'].items():
        generations.setdefault((plc, generation), (instance, None))
    for (plc, generation), (instance, created_at) in generations.items():
        values = dict(plc_id=plc.encode(), instance_id=instance.encode(), source_generation=generation.encode())
        if created_at is not None:
            values['created_at'] = created_at
        db.add(SourceGeneration(**values))
    for plc, (_instance, _generation, numbers) in profile['sources'].items():
        db.add_all(SourceWriteScope(plc_id=plc.encode(), db_number=n) for n in sorted(numbers))
    for plc, numbers in profile['readScope'].items():
        db.add_all(SourceReadScope(plc_id=plc.encode(), db_number=n) for n in sorted(numbers))
    db.add(SourceInitialization(id=1, input_hash=input_hash,
                                logical_hash=bytes.fromhex(result['logicalSha256']), target_hash=target_hash))
    db.flush()
    counts = (len(profile['instances']), len(profile['sources']), len(generations),
              result['writeScopeCount'], result['readScopeCount'])
    if any(db.execute(select(func.count()).select_from(model)).scalar_one() != count
           for model, count in zip(models, counts)):
        raise ValueError('import count mismatch')
    actual = current_summary(db, target)
    if actual != {key: result[key] for key in actual}:
        raise ValueError('import digest mismatch')
    try:
        db.commit()
    except Exception as exc:
        raise ImportCommitUnknown() from exc
    return {**result, 'outcome': 'created'}
