"""业务目标及数据库时钟核验；不查询采集事实或 PLC 数据。"""
from common.integration.storage import to_storage_time
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from ..profile import REVISIONS


class EvidenceUnavailable(Exception):
    """目标未就绪或身份与配置不一致。"""


async def probe_target(db, target):
    if db.get_bind().dialect.name != "mysql":
        raise EvidenceUnavailable()
    try:
        return await _verified_clock(db, target)
    except DBAPIError as exc:
        raise EvidenceUnavailable() from exc


async def _verified_clock(db, target):
    revisions = list((await db.execute(text("SELECT version_num FROM alembic_version FOR SHARE"))).scalars())
    row = (await db.execute(text("SELECT @@server_uuid,DATABASE(),VERSION(),CURRENT_TIMESTAMP(6), "
                                 "TIMESTAMPDIFF(SECOND,UTC_TIMESTAMP(6),CURRENT_TIMESTAMP(6))"))).one()
    if (str(row[0]).lower() != target["serverUuid"] or row[1] != target["schema"]
            or not str(row[2]).split("-")[0].startswith("8.4.") or row[4] != 28800
            or target["schemaRevision"] not in REVISIONS or revisions != [target["schemaRevision"]]):
        raise EvidenceUnavailable()
    await _check_registry_layout(db)
    return row[3].replace(tzinfo=None)


async def verify_energy_target(db, target):
    if db.get_bind().dialect.name != "mysql":
        raise EvidenceUnavailable()
    uuid, schema = (await db.execute(text("SELECT @@server_uuid, DATABASE()"))).one()
    if str(uuid).lower() != target["serverUuid"] or schema != target["schema"]:
        raise EvidenceUnavailable()


async def current_clock(db):
    utc_now = (await db.execute(text("SELECT UTC_TIMESTAMP(6)"))).scalar_one()
    return to_storage_time(utc_now)


async def _check_registry_layout(db):
    columns = set((await db.execute(text(
        "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLLATION_NAME, COLUMN_DEFAULT "
        "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() "
        "AND TABLE_NAME = 'observation_write_sources'"
    ))).all())
    if (("name", "varchar(128)", "YES") not in {row[:3] for row in columns}
            or {row for row in columns if row[0] != "name"} != {
        ("source_key", "varchar(64)", "NO", "utf8mb4_bin", None),
        ("storage_identity", "varchar(64)", "NO", "utf8mb4_bin", None),
        ("enabled", "tinyint(1)", "NO", None, "1"),
        ("created_at", "datetime(6)", "NO", None, None),
        ("updated_at", "datetime(6)", "NO", None, None),
        ("deleted_at", "datetime(6)", "YES", None, None),
    }):
        raise EvidenceUnavailable()
    layout = set((await db.execute(text(
        "SELECT t.ENGINE, s.INDEX_NAME, s.NON_UNIQUE, s.SEQ_IN_INDEX, s.COLUMN_NAME, s.SUB_PART "
        "FROM information_schema.TABLES t JOIN information_schema.STATISTICS s "
        "ON t.TABLE_SCHEMA = s.TABLE_SCHEMA AND t.TABLE_NAME = s.TABLE_NAME "
        "WHERE t.TABLE_SCHEMA = DATABASE() AND t.TABLE_NAME = 'observation_write_sources'"
    ))).all())
    if layout != {("InnoDB", "PRIMARY", 0, 1, "source_key", None),
                  ("InnoDB", "uq_obs_write_source_identity", 0, 1, "storage_identity", None)}:
        raise EvidenceUnavailable()
