"""monitor匿名业务SQL边界；只使用调用方AsyncSession，不提交/回滚。"""
from sqlalchemy import select, text
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from common.integration.storage import StorageProbe
from app.monitor.models.integration import MonitorIntegrationReceipt as Receipt


async def probe_storage(db):
    target = dict((await db.execute(text("SELECT @@server_uuid AS serverUuid, DATABASE() AS `schema`, UTC_TIMESTAMP(3) AS utcNow"))).mappings().one())
    try:
        target["schemaRevision"] = (await db.execute(text("SELECT version_num FROM alembic_version FOR SHARE"))).scalar_one()
    except (NoResultFound,MultipleResultsFound):
        raise ValueError("adoption requires one exact schema revision") from None
    return StorageProbe(target["serverUuid"],target["schema"],target["schemaRevision"],target["utcNow"])


async def probe_adoption(db, adoption):
    from common.integration.storage import validate_adoption_probe
    return validate_adoption_probe(adoption, await probe_storage(db)).database_now



async def get_receipt(db, producer, event):
    return (await db.execute(select(Receipt).where(Receipt.producer_id == producer.encode("utf-8"),
        Receipt.event_id == event.encode("utf-8")).with_for_update())).scalar_one_or_none()


async def add_receipt(db, **values):
    row = Receipt(**values)
    db.add(row)
    await db.flush()
    return row

from app.monitor.models.business_history import HistoryProcessCurve as Curve


async def get_record(db, equipment, time):
    return (await db.execute(select(Curve).where(Curve.equipment_id == equipment,
        Curve.sampled_at == time).with_for_update())).scalar_one_or_none()


async def add_record(db, **values):
    row = Curve(**values)
    db.add(row)
    await db.flush()
    return row


async def storage_context(db):
    """旧入口默认直接旁路；adopted每次事务在业务SQL前验目标。"""
    from app.monitor.integration_config import IntegrationConfig
    from settings import resolve_env_file
    adoption=IntegrationConfig(_env_file=resolve_env_file()).adoption()
    if adoption is None:
        return None
    now=await probe_adoption(db,adoption)
    return adoption,now


_FLOAT_FIELDS=("line_speed_set","line_speed_act","unc_set_tension_p","unc_act_tension_p","rec_set_tension_p","rec_act_tension_p","unc_set_tension_kg","rec_set_tension_kg","furn_set_tension_kg","furn_act_tension_kg","cool_fan1_set_fre","cool_fan1_act_fre","cool_fan2_set_fre","cool_fan2_act_fre","n2_total","elect_consum","h2_flow","n2_flow","oxygen_content","dew_point","muffle_pressure")


async def stored_float_values(db, record_id):
    """固定曲线FLOAT列升格DOUBLE投影，避免MySQL文本协议显示舍入丢失物理精度。"""
    from sqlalchemy import cast, Double
    statement=select(*(cast(getattr(Curve,field),Double).label(field) for field in _FLOAT_FIELDS)).where(Curve.id==record_id).with_for_update()
    return (await db.execute(statement)).mappings().one()
