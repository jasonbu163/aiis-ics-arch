"""equipment匿名业务SQL边界；只使用调用方AsyncSession，不提交/回滚。"""
from sqlalchemy import select, text
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from common.integration.storage import StorageProbe
from app.equipment.models.integration import EquipmentIntegrationReceipt as Receipt


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

from app.equipment.models.temperature_sample import EquipmentTemperatureSample
from app.equipment.models.equipment import EquipmentDrive, EquipmentProductionParameters
MODELS = {"temperature": EquipmentTemperatureSample, "drive": EquipmentDrive, "production_parameters": EquipmentProductionParameters}


async def get_record(db, resource, data, time):
    model = MODELS[resource]
    column = model.sampled_at if resource == "temperature" else model.timestamp
    query = select(model).where(model.equipment_id == data.equipment_id, column == time)
    if resource == "production_parameters":
        query = query.where(model.http_coil_key == data.coil_no.encode("utf-8"))
    return (await db.execute(query.with_for_update())).scalar_one_or_none()


async def add_record(db, resource, **values):
    row = MODELS[resource](**values)
    db.add(row)
    await db.flush()
    return row


async def storage_context(db):
    """旧入口默认直接旁路；adopted每次事务在业务SQL前验目标。"""
    from app.equipment.integration_config import IntegrationConfig
    from settings import resolve_env_file
    adoption=IntegrationConfig(_env_file=resolve_env_file()).adoption()
    if adoption is None:
        return None
    now=await probe_adoption(db,adoption)
    return adoption,now


# MySQL FLOAT文本协议可能仅返回约6位有效数字；DOUBLE投影保留物理binary32的全部值。
_FLOAT_FIELDS={"drive":("tv","km","dew_point_set","dew_point_actual","oxygen","muffle_pressure","nh3_flow_set","nh3_flow_actual","ng_flow_set","ng_flow_actual","uncoiler_set","uncoiler_actual","entry_looper_set","entry_looper_actual","furnace_set","furnace_actual","exit_looper_set","exit_looper_actual","recoiler_set","recoiler_actual"),
    "production_parameters":("thickness","width","total_time","weight","speed")}


async def stored_float_values(db, resource, record_id):
    """只读本owner固定FLOAT列；调用方已持有业务行锁，不提交或改ORM绑定值。"""
    from sqlalchemy import cast, Double
    fields=_FLOAT_FIELDS.get(resource,())
    if not fields:
        return {}
    model=MODELS[resource]
    statement=select(*(cast(getattr(model,field),Double).label(field) for field in fields)).where(model.id==record_id).with_for_update()
    return (await db.execute(statement)).mappings().one()
