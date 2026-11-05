"""owner本地同步只读采用探针；仅使用传入会话，无begin/commit/rollback。"""
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from common.integration.storage import StorageProbe

TARGET_SQL = "SELECT @@server_uuid AS serverUuid, DATABASE() AS `schema`, UTC_TIMESTAMP(3) AS utcNow"


def probe_storage(db):
    target = dict((db.execute(text("SELECT @@server_uuid AS serverUuid, DATABASE() AS `schema`, UTC_TIMESTAMP(3) AS utcNow"))).mappings().one())
    try:
        target["schemaRevision"] = (db.execute(text("SELECT version_num FROM alembic_version FOR SHARE"))).scalar_one()
    except (NoResultFound,MultipleResultsFound):
        raise ValueError("adoption requires one exact schema revision") from None
    return StorageProbe(target["serverUuid"],target["schema"],target["schemaRevision"],target["utcNow"])


def probe_adoption(db, adoption):
    from common.integration.storage import validate_adoption_probe
    return validate_adoption_probe(adoption, probe_storage(db)).database_now



def storage_context(db):
    from app.equipment.integration_config import IntegrationConfig
    from settings import resolve_env_file
    adoption=IntegrationConfig(_env_file=resolve_env_file()).adoption()
    if adoption is None:
        return None
    now=probe_adoption(db,adoption)
    return adoption,now
