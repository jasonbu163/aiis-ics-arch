"""三类过程受限补缺；父缺失不建receipt，结束父仍可接晚到子记录。"""
from common.exceptions import BusinessException
from app.performance.mapping_error_codes import MappingError
from app.performance.mapping_domain import utc_time
from app.performance.crud import async_process_sample as crud, async_production_observation as parents
from app.performance.services.async_production_observation import transaction
FIELDS = {"temperature": ("set_temp", "max_temp", "min_temp", "avg_temp", "duration"),
          "tension": ("set_tension", "avg_tension", "max_tension", "min_tension"),
          "speed": ("set_speed", "avg_speed", "max_speed")}
async def receive_sample(db, sample, actor, parent_id, kind):
    async def apply(db, sample, digest):
        # Scope is checked at API before SQL. Distinguish absent id from mismatched HTTP parent.
        parent = await parents.by_id(db, sample.equipment_id, parent_id, lock=True)
        if parent is None:
            if await parents.parent_id_exists(db, parent_id):
                raise BusinessException(MappingError.PARENT_MISMATCH, code=409)
            raise BusinessException(MappingError.PARENT_NOT_FOUND, code=404)
        if parent.coil_no != sample.coil_no or parent.http_coil_key != sample.coil_no.encode("utf-8"):
            raise BusinessException(MappingError.PARENT_MISMATCH, code=409)
        fields = FIELDS[kind]
        supplied = {field:getattr(sample, field) for field in fields if field in sample.model_fields_set}
        row = await crud.get_record(db, kind, parent_id, sample)
        outcome = "created"
        if row is None:
            row = await crud.add_record(db, kind, equipment_id=sample.equipment_id, performance_id=parent_id,
                zone=sample.zone, http_zone_key=sample.zone.encode("utf-8"), record_time=sample.record_time,
                **{field:supplied.get(field) for field in fields})
        else:
            for field,value in supplied.items():
                if getattr(row,field) is not None and getattr(row,field) != value:
                    raise BusinessException(MappingError.VALUE_CONFLICT, code=409)
            updates = {field:value for field,value in supplied.items() if getattr(row,field) is None}
            for field,value in updates.items():
                setattr(row,field,value)
            outcome = "updated" if updates else "duplicate"
            await db.flush()
        return dict(record_id=row.id, performance_id=parent_id, record_time=utc_time(sample.record_time), outcome=outcome), {"performance_id":parent_id, kind+"_record_id":row.id}
    return await transaction(db, sample, actor, "process_"+kind, apply, performanceId=parent_id)
