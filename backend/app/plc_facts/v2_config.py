"""v2 私有目标配置；旧来源 JSON 解析仅供历史材料校验。"""
from functools import lru_cache
import json
from pathlib import Path
from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict

from settings import resolve_env_file
from .v2_domain import V2Error, identifier

LEGACY_REVISION = '5f7a9c1e3b25'
REVISION = '7b9d1f3a5c7e'


class V2Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=resolve_env_file(), extra='ignore')
    PLC_FACTS_V2_ENABLED: bool = False
    PLC_FACTS_V2_PROFILE_FILE: str = ''


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate configuration key')
        result[key] = value
    return result


def _db_numbers(values):
    if not isinstance(values, list) or any(type(value) is not int or not 1 <= value <= 65535 for value in values):
        raise ValueError('invalid DB numbers')
    if len(values) != len(set(values)):
        raise ValueError('duplicate DB numbers')
    return frozenset(values)


def validate_target(target, revision):
    if not isinstance(target, dict) or set(target) != {'alias', 'serverUuid', 'schema', 'schemaRevision'}:
        raise ValueError('invalid target')
    identifier(target['alias'])
    identifier(target['schema'])
    if (target['schemaRevision'] != revision or not isinstance(target['serverUuid'], str)
            or str(UUID(target['serverUuid'])) != target['serverUuid']):
        raise ValueError('invalid target revision or UUID')
    return target


def parse_profile(document):
    required_fields = {'target', 'instances', 'sources', 'readScopes'}
    # 兼容此前含凭据摘要的 profile，来源准入使用实例和活跃来源登记。
    if not isinstance(document, dict) or set(document) - {'credentials'} != required_fields:
        raise ValueError('invalid profile')
    target = validate_target(document['target'], LEGACY_REVISION)
    instances = {}
    if not isinstance(document['instances'], list):
        raise ValueError('invalid instances')
    for item in document['instances']:
        if not isinstance(item, dict) or set(item) != {'instanceId', 'sourceType'}:
            raise ValueError('invalid instance')
        name = identifier(item['instanceId'])
        kind = item['sourceType']
        if name in instances or kind not in ('daa', 'external'):
            raise ValueError('invalid instance')
        instances[name] = kind
    sources = {}
    if not isinstance(document['sources'], list):
        raise ValueError('invalid sources')
    for item in document['sources']:
        if not isinstance(item, dict) or set(item) != {'plcId', 'instanceId', 'sourceGeneration', 'dbNumbers'}:
            raise ValueError('invalid source')
        plc = identifier(item['plcId'])
        instance = identifier(item['instanceId'])
        generation = identifier(item['sourceGeneration'])
        if plc in sources or instance not in instances:
            raise ValueError('duplicate source')
        sources[plc] = (instance, generation, _db_numbers(item['dbNumbers']))
    read_scope = {}
    if not isinstance(document['readScopes'], dict):
        raise ValueError('invalid read scopes')
    # 仅解析旧配置各组读取范围的并集，供历史材料校验；当前 HTTP 不使用此范围。
    for role, entries in document['readScopes'].items():
        identifier(role)
        if not isinstance(entries, list):
            raise ValueError('invalid read scope')
        seen_plcs = set()
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {'plcId', 'dbNumbers'}:
                raise ValueError('invalid read scope')
            plc = identifier(entry['plcId'])
            if plc in seen_plcs:
                raise ValueError('duplicate read scope')
            seen_plcs.add(plc)
            read_scope[plc] = read_scope.get(plc, frozenset()) | _db_numbers(entry['dbNumbers'])
    return {'target': target, 'instances': instances, 'sources': sources, 'readScope': read_scope}


def load_profile(settings):
    try:
        if not settings.PLC_FACTS_V2_PROFILE_FILE:
            raise ValueError('v2 profile missing')
        path = Path(settings.PLC_FACTS_V2_PROFILE_FILE).resolve(strict=True)
        repository = Path(__file__).resolve().parents[3]
        if path.is_relative_to(repository) or not path.is_file() or path.stat().st_size > 1024 * 1024:
            raise ValueError('invalid private profile location')
        document = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_unique_pairs)
        if not isinstance(document, dict) or set(document) != {'target'}:
            raise ValueError('invalid target profile')
        return {'target': validate_target(document['target'], REVISION)}
    except (ValueError, TypeError, OSError, UnicodeError, V2Error):
        raise V2Error('not_ready', 503) from None


@lru_cache(maxsize=1)
def get_profile():
    settings = V2Settings()
    if not settings.PLC_FACTS_V2_ENABLED:
        raise V2Error('not_ready', 503)
    return load_profile(settings)


def admit_source(profile, sample):
    source = profile['sources'].get(sample.plc_id)
    if source is None or source[:2] != (sample.instance_id, sample.source_generation):
        raise V2Error('scope_rejected', 403)
