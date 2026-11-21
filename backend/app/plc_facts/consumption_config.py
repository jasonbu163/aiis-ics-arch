"""仅从仓外私有文件取得采集消费者服务身份和精确授权范围。"""
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from hmac import compare_digest
import json
from pathlib import Path
import re

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from settings import resolve_env_file
from .consumption_domain import ConsumerError, consumer_uuid, require_identifier
from .schemas.consumption import DbNumber, HashText, Identifier, Permission, UuidText
from .v2_config import _unique_pairs


class ConsumptionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=resolve_env_file(), extra='ignore')
    ACQ_CONSUMPTION_CREDENTIALS_FILE: str = ''


class GrantIn(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    sha256: HashText
    consumerId: UuidText
    plcId: Identifier
    dbNumber: DbNumber
    permissions: list[Permission] = Field(min_length=1, max_length=7)


@dataclass(frozen=True)
class Grant:
    digest: bytes
    consumer_id: str
    plc_id: str
    db_number: int
    permissions: frozenset[str]


def parse_grants(document):
    if not isinstance(document, dict) or set(document) != {'grants'} or not isinstance(document['grants'], list):
        raise ValueError('invalid grants')
    if len(document['grants']) > 1024:
        raise ValueError('too many grants')
    grants = []
    seen = set()
    for entry in document['grants']:
        item = GrantIn.model_validate(entry)
        grant = Grant(bytes.fromhex(item.sha256), consumer_uuid(item.consumerId),
                      require_identifier(item.plcId), item.dbNumber, frozenset(item.permissions))
        key = (grant.digest, grant.consumer_id)
        if key in seen or len(grant.permissions) != len(item.permissions):
            raise ValueError('duplicate grant')
        seen.add(key)
        grants.append(grant)
    return tuple(grants)


@lru_cache(maxsize=1)
def get_grants():
    try:
        file = ConsumptionSettings().ACQ_CONSUMPTION_CREDENTIALS_FILE
        if not file:
            return ()
        path = Path(file).resolve(strict=True)
        repository = Path(__file__).resolve().parents[3]
        if (path.is_relative_to(repository) or not path.is_file() or path.stat().st_size > 1024 * 1024
                or path.stat().st_mode & 0o077):
            raise ValueError('invalid private credentials file')
        return parse_grants(json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_unique_pairs))
    except (OSError, UnicodeError, ValueError, ValidationError, ConsumerError):
        raise ConsumerError('not_ready', 503) from None


def authorize(authorization, identity, permission):
    scheme, _, token = (authorization or '').partition(' ')
    if scheme.lower() != 'bearer' or not re.fullmatch(r'[A-Za-z0-9_~.+/=-]{32,256}', token):
        raise ConsumerError('authentication_required', 401)
    digest = sha256(token.encode('ascii')).digest()
    matches = [grant for grant in get_grants() if compare_digest(grant.digest, digest)]
    if not matches:
        raise ConsumerError('authentication_required', 401)
    for grant in matches:
        if grant.consumer_id == identity and permission in grant.permissions:
            return grant
    raise ConsumerError('scope_rejected', 403)
