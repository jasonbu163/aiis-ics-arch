"""三过程真实async接线；仅可靠生产事件父，补NULL前校验完整范围，无人工/legacy造父。"""
from decimal import Decimal
from common.integration.storage import to_storage_time as storage_time
from app.performance.crud import async_integration as crud
from app.performance.services.async_integration_observation import transaction, fail
from app.performance.integration_error_codes import IntegrationError as Error
from app.performance.schemas import integration as dto

FIELDS={"temperature":("set_temp","max_temp","min_temp","avg_temp","duration"),
        "tension":("set_tension","avg_tension","max_tension","min_tension"),"speed":("set_speed","avg_speed","max_speed")}
TYPES={"temperature":dto.ProcessTemperatureReceipt,"tension":dto.ProcessTensionReceipt,"speed":dto.ProcessSpeedReceipt}


def validate_range(values,kind):
    suffix={"temperature":"temp","tension":"tension","speed":"speed"}[kind]
    low,avg,high=(values.get(prefix+"_"+suffix) for prefix in ("min","avg","max"))
    for a,b in ((low,avg),(avg,high),(low,high)):
        if a is not None and b is not None and a>b:
            fail(Error.INVALID_REQUEST,422)


async def receive_sample(db,envelope,adoption,parent_id,kind):
    async def apply(db,envelope,digest,now):
        data=envelope.data
        parent=await crud.parent(db,parent_id)
        if parent is None:
            fail(Error.PARENT_NOT_FOUND,404)
        if parent.equipment_id!=data.equipment_id or parent.coil_no!=data.coil_no or parent.http_coil_key!=data.coil_no.encode("utf-8"):
            fail(Error.PARENT_MISMATCH)
        if await crud.parent_event(db,data.equipment_id,parent_id) is None:
            fail(Error.PARENT_MISMATCH)
        fields=FIELDS[kind]
        supplied={field:getattr(data,field) for field in fields if field in data.model_fields_set}
        row=await crud.get_process(db,kind,parent_id,data,storage_time(data.record_time))
        updates=dict(supplied)
        outcome="created"
        if row is not None:
            for field,value in supplied.items():
                if getattr(row,field) is not None and getattr(row,field)!=value:
                    fail(Error.VALUE_CONFLICT)
            updates={field:value for field,value in supplied.items() if getattr(row,field) is None}
            merged={field:updates.get(field,getattr(row,field)) for field in fields}
            validate_range(merged,kind)
            for field,value in updates.items():
                setattr(row,field,value)
            outcome="updated" if updates else "duplicate"
            if updates:
                row.updated_at=storage_time(now)
            await db.flush()
        else:
            validate_range(supplied,kind)
            row=await crud.add_process(db,kind,equipment_id=data.equipment_id,performance_id=parent_id,
                zone=data.zone,http_zone_key=data.zone.encode("utf-8"),record_time=storage_time(data.record_time),
                created_at=storage_time(now),updated_at=storage_time(now),**{field:supplied.get(field) for field in fields})
        return dict(recordId=row.id,performanceId=parent_id,affectedRecordIds=[row.id],confirmation="business_committed",
            applied=outcome!="duplicate",outcome=outcome,changedFields=[type(data).model_fields[k].alias for k in updates] if outcome=="updated" else []),{
                "performance_id":parent_id,kind+"_record_id":row.id}
    return await transaction(db,envelope,adoption,"process_"+kind,TYPES[kind],apply,parent_id)
