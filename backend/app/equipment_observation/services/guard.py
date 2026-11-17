"""业务目标及数据库时钟核验；不查询采集事实或 PLC 数据。"""
from sqlalchemy import text

from ..profile import REVISIONS


class EvidenceUnavailable(Exception):
    """目标未就绪或身份与配置不一致。"""


async def probe_target(db, target):
    if db.get_bind().dialect.name != "mysql":
        raise EvidenceUnavailable()
    revisions = list((await db.execute(text("SELECT version_num FROM alembic_version FOR SHARE"))).scalars())
    row = (await db.execute(text("SELECT @@server_uuid,DATABASE(),VERSION(),CURRENT_TIMESTAMP(6), "
                                 "TIMESTAMPDIFF(SECOND,UTC_TIMESTAMP(6),CURRENT_TIMESTAMP(6))"))).one()
    if (str(row[0]).lower() != target["serverUuid"] or row[1] != target["schema"]
            or not str(row[2]).split("-")[0].startswith("8.4.") or row[4] != 28800
            or target["schemaRevision"] not in REVISIONS or revisions != [target["schemaRevision"]]):
        raise EvidenceUnavailable()
    return row[3].replace(tzinfo=None)
