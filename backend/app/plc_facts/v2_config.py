"""v2 私有准入配置与机器身份，默认关闭并拒绝无效配置。"""
from functools import lru_cache
import hashlib
import hmac
import json
from pathlib import Path
import re
from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict

from settings import resolve_env_file
from .v2_domain import V2Error, identifier

REVISION = '5f7a9c1e3b25'


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


def parse_profile(document):
    if not isinstance(document, dict) or set(document) != {'target', 'instances', 'credentials', 'sources', 'readScopes'}:
        raise ValueError('invalid profile')
    target = document['target']
    if not isinstance(target, dict) or set(target) != {'alias', 'serverUuid', 'schema', 'schemaRevision'}:
        raise ValueError('invalid target')
    identifier(target['alias'])
    identifier(target['schema'])
    if (target['schemaRevision'] != REVISION or not isinstance(target['serverUuid'], str)
            or str(UUID(target['serverUuid'])) != target['serverUuid']):
        raise ValueError('invalid target revision or UUID')
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
    credentials = {}
    if not isinstance(document['credentials'], list):
        raise ValueError('invalid credentials')
    for item in document['credentials']:
        if not isinstance(item, dict) or set(item) != {'instanceId', 'tokenSha256'}:
            raise ValueError('invalid credential')
        name = identifier(item['instanceId'])
        digest = item['tokenSha256']
        if name not in instances or name in credentials or not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('invalid credential')
        if digest in credentials.values():
            raise ValueError('duplicate credential')
        credentials[name] = digest
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
    scopes = {}
    if not isinstance(document['readScopes'], dict):
        raise ValueError('invalid read scopes')
    for role, entries in document['readScopes'].items():
        identifier(role)
        if not isinstance(entries, list):
            raise ValueError('invalid read scope')
        scope = {}
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {'plcId', 'dbNumbers'}:
                raise ValueError('invalid read scope')
            plc = identifier(entry['plcId'])
            if plc in scope:
                raise ValueError('duplicate read scope')
            scope[plc] = _db_numbers(entry['dbNumbers'])
        scopes[role] = scope
    return {'target': target, 'instances': instances, 'credentials': credentials, 'sources': sources, 'readScopes': scopes}


def load_profile(settings):
    try:
        if not settings.PLC_FACTS_V2_PROFILE_FILE:
            raise ValueError('v2 profile missing')
        path = Path(settings.PLC_FACTS_V2_PROFILE_FILE).resolve(strict=True)
        repository = Path(__file__).resolve().parents[3]
        if path.is_relative_to(repository) or not path.is_file() or path.stat().st_size > 1024 * 1024:
            raise ValueError('invalid private profile location')
        document = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_unique_pairs)
        return parse_profile(document)
    except (ValueError, TypeError, OSError, UnicodeError, V2Error):
        raise V2Error('not_ready', 503) from None


@lru_cache(maxsize=1)
def get_profile():
    settings = V2Settings()
    if not settings.PLC_FACTS_V2_ENABLED:
        raise V2Error('not_ready', 503)
    return load_profile(settings)


def authenticate(profile, authorization):
    scheme, separator, token = (authorization or '').partition(' ')
    if not separator or scheme.lower() != 'bearer' or not token or ' ' in token:
        raise V2Error('invalid_credential', 401)
    try:
        encoded = token.encode('ascii')
    except UnicodeError:
        raise V2Error('invalid_credential', 401) from None
    digest = hashlib.sha256(encoded).hexdigest()
    matched = None
    for instance, expected in profile['credentials'].items():
        if hmac.compare_digest(digest, expected):
            matched = instance
    if matched is None:
        raise V2Error('invalid_credential', 401)
    return matched


def admit_source(profile, instance, sample):
    source = profile['sources'].get(sample.plc_id)
    if (instance != sample.instance_id or source is None or source[:2] != (instance, sample.source_generation)
            or sample.db_number not in source[2]):
        raise V2Error('scope_rejected', 403)
    if profile['instances'][instance] == 'daa' and (sample.group_id is None or sample.config_revision is None):
        raise V2Error('invalid_request', 422)


def read_scope(profile, role):
    return profile['readScopes'].get(role, {})
