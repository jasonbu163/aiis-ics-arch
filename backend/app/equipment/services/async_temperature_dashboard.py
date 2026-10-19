"""BE003完整样本只读dashboard窄adapter；不改原GET/POST。"""
from app.equipment.crud.async_temperature_sample import list_samples
from app.equipment.temperature_sample_domain import utc_milliseconds, json_number
async def read_dashboard(db, equipment_id, record_id=None, limit=100):
    records = await list_samples(db, equipment_id, record_id, limit)
    zones = [dict(set_temp=json_number(getattr(records[0], f"zone{i}_set")), actual_temp=json_number(getattr(records[0], f"zone{i}_act"))) for i in range(1,6)] if records else []
    history = [dict(record_id=r.id, sampled_at=utc_milliseconds(r.sampled_at), time=utc_milliseconds(r.sampled_at),
        **{f"zone{i}":json_number(getattr(r, f"zone{i}_act")) for i in range(1,6)}) for r in reversed(records)]
    return dict(equipment_id=equipment_id, record_id=records[0].id if records else None,
        sampled_at=utc_milliseconds(records[0].sampled_at) if records else None, heating_zones=zones, temperature_history=history)
