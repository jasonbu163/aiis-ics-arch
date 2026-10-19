"""生产参数HTTP部分观测事务及同记录dashboard；不生成加工步骤。"""
from app.equipment.crud import async_production_parameter_sample as crud
from app.equipment.services.async_drive_sample import receive_partial
from app.equipment.mapping_domain import utc_time
FIELDS = ("grade", "entry_time", "thickness", "width", "total_time", "weight", "speed")
async def receive_sample(db, sample, actor):
    return await receive_partial(db, sample, actor, "production_parameters", crud, FIELDS,
        dict(coil_no=sample.coil_no, http_coil_key=sample.coil_no.encode("utf-8"), process_steps=[]))
async def read_samples(db, equipment_id, record_id=None, limit=100):
    records = await crud.list_records(db, equipment_id, record_id, limit)
    items = [dict(record_id=r.id, equipment_id=r.equipment_id, coil_no=r.coil_no, sampled_at=utc_time(r.timestamp),
        **{f:utc_time(getattr(r,f)) if f == "entry_time" and getattr(r,f) is not None else getattr(r,f) for f in FIELDS}) for r in records]
    parameters = dict(items[0], last_update=items[0]["sampled_at"], status=None) if items else {}
    return dict(equipment_id=equipment_id, items=items, dashboard=dict(production_parameters=parameters, process_steps=[]))
