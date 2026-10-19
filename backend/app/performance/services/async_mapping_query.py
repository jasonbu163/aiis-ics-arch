"""HTTP实绩及过程只读adapter，记录身份/来源/有效重量时间可核对。"""
from common.exceptions import BusinessException
from app.performance.mapping_error_codes import MappingError
from app.performance.mapping_domain import utc_time, json_number
from app.performance.models.performance import Performance
from app.performance.crud import async_production_observation as parents, async_process_sample as processes
from app.performance.services.async_process_sample import FIELDS

def record_out(record):
    result = {column.name:json_number(getattr(record,column.name)) for column in Performance.__table__.columns
              if column.name not in {"http_coil_key"}}
    for key,value in tuple(result.items()):
        if hasattr(value,"isoformat"):
            result[key] = utc_time(value) if key in {"reported_start_time", "reported_end_time", "first_observed_at", "last_observed_at"} else value.isoformat()
    if record.start_time is not None and record.end_time is not None:
        effective_start,effective_end = record.start_time,record.end_time
    elif record.reported_start_time is not None and record.reported_end_time is not None:
        effective_start,effective_end = record.reported_start_time,record.reported_end_time
    else:
        effective_start,effective_end = record.first_observed_at,record.last_observed_at
    manual = record.start_time is not None and record.end_time is not None
    result.update(record_id=record.id, effective_start_time=(effective_start.isoformat() if manual else utc_time(effective_start)) if effective_start else None,
                  effective_end_time=(effective_end.isoformat() if manual else utc_time(effective_end)) if effective_end else None, split_count=0, is_splitted=False)
    return result

async def read_record(db, equipment, record_id):
    record = await parents.by_id(db, equipment, record_id)
    if record is None:
        raise BusinessException(MappingError.PARENT_NOT_FOUND, code=404)
    return record_out(record)

async def read_records(db, query):
    rows, total = await parents.list_records(db, query)
    return dict(equipment_id=query.equipment_id, items=[record_out(r) for r in rows], total=total,
                page=query.page, page_size=query.page_size, total_pages=(total+query.page_size-1)//query.page_size)

async def read_process_data(db, equipment, parent_id):
    await read_record(db,equipment,parent_id)
    result = {}
    for kind in FIELDS:
        rows = await processes.list_records(db,kind,parent_id,equipment)
        result[kind] = [dict(id=r.id, record_id=r.id, equipment_id=r.equipment_id, performance_id=r.performance_id,
            zone=r.zone, record_time=utc_time(r.record_time), **{f:json_number(getattr(r,f)) for f in FIELDS[kind]}) for r in rows]
    return result
