"""单价稳定内置项目键与上海时间边界。"""
from datetime import datetime, timezone

from app.energy.schemas.energy_price import OUTPUT_ZONE, canonical_hour_start, history_bounds


BUILTIN_ITEMS = ("electric", "hydrogen", "argon")


def storage_time(instant):
    return instant.astimezone(OUTPUT_ZONE).replace(tzinfo=None)


def storage_hour(instant):
    return storage_time(canonical_hour_start(instant))


def storage_bounds(day):
    if day is None:
        return None
    start, end = history_bounds(day)
    return (
        storage_time(start.replace(tzinfo=timezone.utc)) if start != datetime.min else datetime.min,
        storage_time(end.replace(tzinfo=timezone.utc)) if end is not None else None,
    )


def range_filters(column, bounds):
    if bounds is None:
        return ()
    start, end = bounds
    return (column >= start,) + ((column < end,) if end is not None else ())
